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
    # 1. Load URLs from secure file
    urls = get_urls_from_config(CONFIG_FILE)
    if not urls:
        return

    url_stats = urls.get('LEBRON_STATS')
    url_roles = urls.get('OFFENSIVE_ROLES')

    if not url_stats or not url_roles:
        print("Error: Missing required keys in config file.")
        print("Ensure data_urls.txt contains 'LEBRON_STATS' and 'OFFENSIVE_ROLES'.")
        return

    # 2. Download Data
    print("Fetching Latest Lebron Stats...")
    df_latest = download_csv(url_stats)
    
    print("Fetching Offensive Roles...")
    df_roles = download_csv(url_roles)
    
    if df_latest is None or df_roles is None:
        print("Failed to download necessary files. Exiting.")
        return

    # 3. Determine Current Season & Year
    if 'Season' not in df_latest.columns:
        print("Error: 'Season' column missing from Lebron Stats data.")
        return
        
    current_season = df_latest['Season'].unique()[0]
    try:
        current_year = int(current_season.split('-')[0]) + 1
    except:
        print(f"Could not parse year from season: {current_season}")
        current_year = None
    
    print(f"Processing data for Season: {current_season} (Year: {current_year})")

    # 4. Process Offensive Roles
    # Filter for the current season
    roles_season = df_roles[df_roles['Season'] == current_season].copy()
    
    # Select needed columns: ID, Role, and Games
    # Note: 'offensive_roles_only.csv' does NOT have Team, so we only get role and games here
    roles_season = roles_season[['player_id', 'offensive_role', 'ss_games']]
    
    # 5. Merge Stats with Roles
    if 'PLAYER_ID' in df_latest.columns:
        df_latest = df_latest.rename(columns={'PLAYER_ID': 'player_id'})
    
    merged_df = pd.merge(df_latest, roles_season, on='player_id', how='left')

    # 6. Map Columns to lebron.csv Schema
    column_mapping = {
        'Season': 'Season',
        'Name': 'Player',
        # 'Team' is NOT in the source files, will come from index
        'Mins': 'Minutes',
        'offensive_role': 'Offensive Archetype', 
        'ss_games': 'Games',         # Mapping ss_games -> Games
        'LEBRON WAR': 'WAR',
        'LEBRON': 'LEBRON',
        'OLEBRON': 'O-LEBRON',
        'DLEBRON': 'D-LEBRON',
        'player_id': 'NBA ID',
        'Pos': 'Pos'
    }
    
    df_final = merged_df.rename(columns=column_mapping)
    
    # Initialize columns that might be missing
    for col in ['Pos', 'team', 'Defensive Role', 'Age', 'bref_id']:
        if col not in df_final.columns:
            df_final[col] = None
    
    # Add derived columns
    df_final['year'] = current_year

    # --- STEP 7: Merge Team, Pos, and ID from modern_index.csv ---
    if os.path.exists(FILE_INDEX_MASTER):
        try:
            print(f"Loading {FILE_INDEX_MASTER} for Team, Position, and ID mapping...")
            idframe = pd.read_csv(FILE_INDEX_MASTER)
            
            # Create Mappings
            # Key: nba_id
            pos_map = dict(zip(idframe['nba_id'], idframe['Pos']))
            team_map = dict(zip(idframe['nba_id'], idframe['team']))
            id_map = dict(zip(idframe['nba_id'], idframe['bref_id']))
            
            # Map values
            df_final['bref_id'] = df_final['NBA ID'].map(id_map)
            
            # Fill 'team' from index (CRITICAL since roles file lacks team)
            df_final['team'] = df_final['team'].fillna(df_final['NBA ID'].map(team_map))
            
            # Fill 'Pos' from index
            df_final['Pos'] = df_final['Pos'].fillna(df_final['NBA ID'].map(pos_map))
            
        except Exception as e:
            print(f"Error reading {FILE_INDEX_MASTER}: {e}")
    else:
        print(f"Warning: {FILE_INDEX_MASTER} not found. 'team' and 'Pos' will likely be missing!")

    # Optional: Fill Age using NBA API
    try:
        from nba_api.stats.endpoints import leaguedashplayerstats
        print("Fetching ages from NBA API...")
        season_string = f"{current_year-1}-{str(current_year)[-2:]}"
        frames = leaguedashplayerstats.LeagueDashPlayerStats(season=season_string).get_data_frames()
        api_data = frames[0]
        age_map = dict(zip(api_data['PLAYER_ID'], api_data['AGE']))
        df_final['Age'] = df_final['NBA ID'].map(age_map)
    except ImportError:
        print("Note: 'nba_api' not installed. Skipping Age update.")
    except Exception as e:
        print(f"Error fetching ages: {e}")

    # Clean up names
    if 'Player' in df_final.columns:
        df_final['Player'] = df_final['Player'].str.lower()

    # Select and Order Columns
    target_columns = [
        'Season', 'Player', 'team', 'Minutes', 'Pos', 'Offensive Archetype', 
        'WAR', 'LEBRON', 'O-LEBRON', 'D-LEBRON', 'year', 'Defensive Role', 
        'NBA ID', 'bref_id', 'Games', 'Age'
    ]
    
    # Final check for missing columns
    for col in target_columns:
        if col not in df_final.columns:
            df_final[col] = None
            
    df_final = df_final[target_columns]

    # 8. Update History File
    if os.path.exists(FILE_HISTORY):
        old_df = pd.read_csv(FILE_HISTORY)
        
        # Remove existing rows for this season to avoid duplicates
        rows_before = len(old_df)
        old_df = old_df[old_df['Season'] != current_season]
        rows_after = len(old_df)
        
        if rows_before != rows_after:
            print(f"Removed {rows_before - rows_after} existing rows for {current_season} to overwrite.")
        
        updated_history = pd.concat([old_df, df_final], ignore_index=True)
    else:
        print("No existing history file found. Creating new one.")
        updated_history = df_final

    # 9. Save
    updated_history.to_csv(FILE_HISTORY, index=False)
    print(f"Success! Updated {FILE_HISTORY}. Total rows: {len(updated_history)}")

if __name__ == "__main__":
    main()