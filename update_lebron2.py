import pandas as pd
import requests
import io
import os
import sys

# --- CONFIGURATION ---
CONFIG_FILE = "data_urls.txt"
FILE_HISTORY = "lebron.csv"
FILE_INDEX_MASTER = "modern_index.csv" # Updated to your new index file

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
        print(f"Downloading data...") 
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
    # Extract year (e.g., '2025-26' -> 2026)
    try:
        current_year = int(current_season.split('-')[0]) + 1
    except:
        print(f"Could not parse year from season: {current_season}")
        current_year = None
    
    print(f"Processing data for Season: {current_season} (Year: {current_year})")

    # 4. Process Offensive Roles (Source for Team & Archetype)
    roles_season = df_roles[df_roles['Season'] == current_season].copy()
    
    # Handle duplicates: Keep the team where the player had the most minutes
    if 'nba_min' in roles_season.columns:
        roles_season = roles_season.sort_values('nba_min', ascending=False)
        roles_season = roles_season.drop_duplicates(subset=['player_id'])
    
    roles_season = roles_season[['player_id', 'Team', 'offensive_role']]
    
    # 5. Merge Stats with Roles
    if 'PLAYER_ID' in df_latest.columns:
        df_latest = df_latest.rename(columns={'PLAYER_ID': 'player_id'})
    
    merged_df = pd.merge(df_latest, roles_season, on='player_id', how='left')

    # 6. Map Columns to lebron.csv Schema
    column_mapping = {
        'Season': 'Season',
        'Name': 'Player',
        'Team': 'team',              
        'Mins': 'Minutes',
        'offensive_role': 'Offensive Archetype', 
        'LEBRON WAR': 'WAR',
        'LEBRON': 'LEBRON',
        'OLEBRON': 'O-LEBRON',
        'DLEBRON': 'D-LEBRON',
        'player_id': 'NBA ID',
        # 'Pos' might be here in the future
        'Pos': 'Pos' 
    }
    
    df_final = merged_df.rename(columns=column_mapping)
    
    # Ensure 'Pos' column exists even if rename didn't find it
    if 'Pos' not in df_final.columns:
        df_final['Pos'] = None

    # Add derived/missing columns
    df_final['year'] = current_year
    
    # Initialize other missing columns
    for col in ['Defensive Role', 'Games', 'Age', 'bref_id']:
        df_final[col] = None

    # --- NEW STEP: Merge Pos and bref_id from modern_index.csv ---
    if os.path.exists(FILE_INDEX_MASTER):
        try:
            print(f"Loading {FILE_INDEX_MASTER} for Position and ID mapping...")
            idframe = pd.read_csv(FILE_INDEX_MASTER)
            
            # Create Mappings
            # key: nba_id -> value: Pos
            pos_map = dict(zip(idframe['nba_id'], idframe['Pos']))
            # key: nba_id -> value: bref_id
            id_map = dict(zip(idframe['nba_id'], idframe['bref_id']))
            
            # Map bref_id
            df_final['bref_id'] = df_final['NBA ID'].map(id_map)
            
            # Map Pos (Future Proofing Logic)
            # If 'Pos' is already filled (from source), keep it. 
            # If it's NaN/None, fill it from the map.
            df_final['Pos'] = df_final['Pos'].fillna(df_final['NBA ID'].map(pos_map))
            
        except Exception as e:
            print(f"Error reading {FILE_INDEX_MASTER}: {e}")
    else:
        print(f"Warning: {FILE_INDEX_MASTER} not found. Positions may be missing.")

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

    # 7. Update History File
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

    # 8. Save
    updated_history.to_csv(FILE_HISTORY, index=False)
    print(f"Success! Updated {FILE_HISTORY}. Total rows: {len(updated_history)}")

if __name__ == "__main__":
    main()