import pandas as pd
import requests
import io
import os
import sys

# --- CONFIGURATION ---
CONFIG_FILE = "data_urls.txt"
FILE_HISTORY = "lebron.csv"
FILE_INDEX_MASTER = "modern_index.csv"

def get_urls_from_config(filename):
    """Reads URLs from a key=value formatted text file."""
    urls = {}
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        print("Please create this file with lines like: KEY=https://example.com/data.csv")
        return None
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if '=' in line:
                key, value = line.split('=', 1)
                urls[key.strip()] = value.strip()
    return urls

def download_csv(url):
    """Downloads a CSV from a URL and returns a DataFrame."""
    try:
        print(f"Downloading data from {url}...") 
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(io.BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading from provided URL: {e}")
        return None

def main():
    # 1. Load URLs
    urls = get_urls_from_config(CONFIG_FILE)
    if not urls:
        return

    url_stats = urls.get('LEBRON_STATS')
    url_off_roles = urls.get('OFFENSIVE_ROLES')
    url_def_roles = urls.get('DEFENSIVE_ROLES')

    if not all([url_stats, url_off_roles, url_def_roles]):
        print("Error: Missing keys in config file.")
        print("Ensure 'LEBRON_STATS', 'OFFENSIVE_ROLES', and 'DEFENSIVE_ROLES' are set.")
        return

    # 2. Download Data
    print("--- 1. Fetching Data ---")
    df_latest = download_csv(url_stats)
    df_off_roles = download_csv(url_off_roles)
    df_def_roles = download_csv(url_def_roles)
    
    if any(df is None for df in [df_latest, df_off_roles, df_def_roles]):
        print("Failed to download one or more files. Exiting.")
        return

    # 3. Determine Current Season
    if 'Season' not in df_latest.columns:
        print("Error: 'Season' column missing from Lebron Stats data.")
        return
    
    current_season = df_latest['Season'].unique()[0]
    try:
        current_year = int(current_season.split('-')[0]) + 1
    except:
        current_year = None
    
    print(f"Processing Season: {current_season} (Year: {current_year})")

    # 4. Prepare Merge Dataframes
    if 'PLAYER_ID' in df_latest.columns:
        df_latest = df_latest.rename(columns={'PLAYER_ID': 'player_id'})

    # Offensive Roles: Get Role and Games
    off_season = df_off_roles[df_off_roles['Season'] == current_season].copy()
    # Handle duplicate players (if any, keep most minutes)
    if 'nba_min' in off_season.columns:
        off_season = off_season.sort_values('nba_min', ascending=False)
        off_season = off_season.drop_duplicates(subset=['player_id'])
    
    off_merge = off_season[['player_id', 'offensive_role', 'ss_games']]

    # Defensive Roles: Get Role
    def_season = df_def_roles[df_def_roles['Season'] == current_season].copy()
    def_season = def_season.drop_duplicates(subset=['player_id'])
    def_merge = def_season[['player_id', 'defensive_role']]

    # 5. Merge Everything
    print("--- 2. Merging Data ---")
    # Merge Stats + Offensive Roles
    merged_df = pd.merge(df_latest, off_merge, on='player_id', how='left')
    
    # Merge + Defensive Roles
    merged_df = pd.merge(merged_df, def_merge, on='player_id', how='left')

    # 6. Map Columns
    column_mapping = {
        'Season': 'Season',
        'Name': 'Player',
        # 'Team' comes from index later
        'Mins': 'Minutes',
        'offensive_role': 'Offensive Archetype',
        'defensive_role': 'Defensive Role', # New Mapping
        'ss_games': 'Games',
        'LEBRON WAR': 'WAR',
        'LEBRON': 'LEBRON',
        'OLEBRON': 'O-LEBRON',
        'DLEBRON': 'D-LEBRON',
        'player_id': 'NBA ID',
        'Pos': 'Pos'
    }
    
    df_final = merged_df.rename(columns=column_mapping)
    df_final['year'] = current_year

    # Initialize missing columns before index merge
    for col in ['team', 'Pos', 'bref_id', 'Age']:
        if col not in df_final.columns:
            df_final[col] = None

    # 7. Merge Index (Team, Pos, IDs)
    print("--- 3. Mapping Teams & Positions from Index ---")
    if os.path.exists(FILE_INDEX_MASTER):
        try:
            idframe = pd.read_csv(FILE_INDEX_MASTER)
            
            # Create Mappings
            team_map = dict(zip(idframe['nba_id'], idframe['team']))
            pos_map = dict(zip(idframe['nba_id'], idframe['Pos']))
            id_map = dict(zip(idframe['nba_id'], idframe['bref_id']))
            
            # Apply Mappings
            df_final['team'] = df_final['team'].fillna(df_final['NBA ID'].map(team_map))
            df_final['Pos'] = df_final['Pos'].fillna(df_final['NBA ID'].map(pos_map))
            df_final['bref_id'] = df_final['NBA ID'].map(id_map)
            
        except Exception as e:
            print(f"Error reading {FILE_INDEX_MASTER}: {e}")
    else:
        print(f"Warning: {FILE_INDEX_MASTER} not found. 'team' will be missing.")

    # Optional: Fill Age using NBA API
    try:
        from nba_api.stats.endpoints import leaguedashplayerstats
        season_string = f"{current_year-1}-{str(current_year)[-2:]}"
        # Only fetch if we haven't already
        print(f"Fetching ages from NBA API for {season_string}...")
        frames = leaguedashplayerstats.LeagueDashPlayerStats(season=season_string).get_data_frames()
        api_data = frames[0]
        age_map = dict(zip(api_data['PLAYER_ID'], api_data['AGE']))
        df_final['Age'] = df_final['NBA ID'].map(age_map)
    except ImportError:
        pass # Silent fail if not installed
    except Exception as e:
        print(f"Error fetching ages: {e}")

    # Formatting
    if 'Player' in df_final.columns:
        df_final['Player'] = df_final['Player'].str.lower()

    # Final Column Selection
    target_columns = [
        'Season', 'Player', 'team', 'Minutes', 'Pos', 'Offensive Archetype', 
        'WAR', 'LEBRON', 'O-LEBRON', 'D-LEBRON', 'year', 'Defensive Role', 
        'NBA ID', 'bref_id', 'Games', 'Age'
    ]
    
    for col in target_columns:
        if col not in df_final.columns:
            df_final[col] = None
            
    df_final = df_final[target_columns]

    # 8. Update History
    print("--- 4. Saving Files ---")
    if os.path.exists(FILE_HISTORY):
        old_df = pd.read_csv(FILE_HISTORY)
        rows_before = len(old_df)
        # Overwrite current season data
        old_df = old_df[old_df['Season'] != current_season]
        rows_after = len(old_df)
        
        if rows_before != rows_after:
            print(f"Replacing {rows_before - rows_after} existing rows for {current_season}.")
        
        updated_history = pd.concat([old_df, df_final], ignore_index=True)
    else:
        updated_history = df_final

    updated_history.to_csv(FILE_HISTORY, index=False)
    print(f"Done! Updated {FILE_HISTORY} (Total rows: {len(updated_history)})")

if __name__ == "__main__":
    main()