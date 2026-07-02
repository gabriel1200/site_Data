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

    url_stats = urls.get('IMPACT_METRICS')
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

    # 3. Handle Seasons
    if 'Season' not in df_latest.columns:
        print("Error: 'Season' column missing from Lebron Stats data.")
        return
    
    # Get a list of all seasons present in the downloaded data
    downloaded_seasons = df_latest['Season'].unique().tolist()
    print(f"Processing Seasons: {downloaded_seasons}")

    # 4. Prepare Merge Dataframes
    if 'PLAYER_ID' in df_latest.columns:
        df_latest = df_latest.rename(columns={'PLAYER_ID': 'player_id'})

    # Offensive Roles
    # Handle duplicate players per season
    if 'nba_min' in df_off_roles.columns:
        df_off_roles = df_off_roles.sort_values(['Season', 'nba_min'], ascending=[True, False])
    df_off_roles = df_off_roles.drop_duplicates(subset=['Season', 'player_id'])
    
    # Keep Season in the merge frames
    off_merge = df_off_roles[['Season', 'player_id', 'offensive_role', 'ss_games']]

    # Defensive Roles
    df_def_roles = df_def_roles.drop_duplicates(subset=['Season', 'player_id'])
    def_merge = df_def_roles[['Season', 'player_id', 'defensive_role']]

    # 5. Merge Everything
    print("--- 2. Merging Data ---")
    # Merge Stats + Offensive Roles on BOTH Season and player_id
    merged_df = pd.merge(df_latest, off_merge, on=['Season', 'player_id'], how='left')
    
    # Merge + Defensive Roles on BOTH Season and player_id
    merged_df = pd.merge(merged_df, def_merge, on=['Season', 'player_id'], how='left')

    # 6. Map Columns
    column_mapping = {
        'Season': 'Season',
        'player_name': 'Player', 
        'Mins': 'Minutes',
        'offensive_role': 'Offensive Archetype',
        'defensive_role': 'Defensive Role', 
        'ss_games': 'Games',
        'LEBRON_WAR': 'WAR', 
        'LEBRON': 'LEBRON',
        'OLEBRON': 'O-LEBRON',
        'DLEBRON': 'D-LEBRON',
        'player_id': 'NBA ID',
        'Pos': 'Pos'
    }
    
    # Fallback mappings for single-season files
    if 'Name' in merged_df.columns and 'player_name' not in merged_df.columns:
        column_mapping['Name'] = 'Player'
        del column_mapping['player_name']
        
    if 'LEBRON WAR' in merged_df.columns and 'LEBRON_WAR' not in merged_df.columns:
        column_mapping['LEBRON WAR'] = 'WAR'
        del column_mapping['LEBRON_WAR']

    df_final = merged_df.rename(columns=column_mapping)
    
    # Calculate Year for all rows dynamically
    def get_year(season_str):
        try:
            return int(str(season_str).split('-')[0]) + 1
        except:
            return None
            
    df_final['year'] = df_final['Season'].apply(get_year)

    # Initialize missing columns before index merge
    for col in ['team', 'Pos', 'bref_id', 'Age']:
        if col not in df_final.columns:
            df_final[col] = None

    # 7. Merge Index (Team, Pos, IDs)
    print("--- 3. Mapping Teams & Positions from Index ---")
    if os.path.exists(FILE_INDEX_MASTER):
        try:
            idframe = pd.read_csv(FILE_INDEX_MASTER)
            team_map = dict(zip(idframe['nba_id'], idframe['team']))
            pos_map = dict(zip(idframe['nba_id'], idframe['Pos']))
            id_map = dict(zip(idframe['nba_id'], idframe['bref_id']))
            
            df_final['team'] = df_final['team'].fillna(df_final['NBA ID'].map(team_map))
            df_final['Pos'] = df_final['Pos'].fillna(df_final['NBA ID'].map(pos_map))
            df_final['bref_id'] = df_final['NBA ID'].map(id_map)
        except Exception as e:
            print(f"Error reading {FILE_INDEX_MASTER}: {e}")
    else:
        print(f"Warning: {FILE_INDEX_MASTER} not found. 'team' will be missing.")

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
        
        # Keep old rows that are NOT in the downloaded seasons (e.g., 2010 to 2012)
        old_df_kept = old_df[~old_df['Season'].isin(downloaded_seasons)]
        
        # Append the new processed multi-season data
        updated_history = pd.concat([old_df_kept, df_final], ignore_index=True)
        print(f"Kept {len(old_df_kept)} old rows. Added/Updated {len(df_final)} rows.")
    else:
        updated_history = df_final

    updated_history.to_csv(FILE_HISTORY, index=False)
    print(f"Done! Updated {FILE_HISTORY} (Total rows: {len(updated_history)})")

if __name__ == "__main__":
    main()