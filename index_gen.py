#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np
import sys
from nba_api.stats.endpoints import commonallplayers

# Configuration
class Config:
    """
    Central configuration class for the scraper.
    """
    # Set to True for playoffs data, False for regular season
    PLAYOFFS_MODE = False 
    
    # --- Configuration Updated from test_index.py ---
    # Current year to scrape (e.g., 2026 for 2025-26 season)
    CURRENT_YEAR = 2026
    # Current season in NBA API format
    CURRENT_SEASON = "2025-26" # 2026-1 = 2025, 26 from 2026
    
    # File paths with dynamic playoff suffix
    @property
    def trail(self):
        return '_ps' if self.PLAYOFFS_MODE else ''

    @property
    def index_master_path(self):
        return f'index_master{self.trail}.csv'

    @property
    def totals_path(self):
        return f'totals{self.trail}.csv'

    @property
    def scoring_path(self):
        return f'scoring{self.trail}.csv'

    # --- Merged SEARCH_DICT from both files ---
    # Hard-coded player IDs for players that might be missing
    SEARCH_DICT = {
        # From test_index.py
        "hollaro01": 1641842,
        "sarral01": 1642259,
        "dadiepa01": 1642359,
        "cuiyo01": 1642385,
        "dasiltr01": 1641783,
        "shannte01": 1630545,
        "demineg01": 1642856,
        "claytwa01": 1642383,
        "jonesda06": 1642357,
        "konanya01": 1642949,
        "traorno01": 1642849,
        # From make_index2.py
        "salauti01": 1642275,
        "sengual01": 1630578,
        "willije02": 1631466
    }

# Initialize config
config = Config()

# --- Utility Functions (from make_index2.py) ---

def fetch_data(url):
    """Fetch data from a URL with proper error handling"""
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = 'utf-8'
        response.raise_for_status() # Check for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch data: {e}")
        return None

# --- Robust Scraping Helpers (from test_index.py's pull_bref_score) ---

def get_stat_from_row(row_obj, stat_name, default_value="0"):
    """
    Extracts a stat value from a table row <tr> using its 'data-stat' attribute.
    This is more robust than using column indices.
    """
    cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
    if cell:
        # .text gets the text content, strip() removes leading/trailing whitespace
        text_content = cell.text.strip()
        # If text_content is not empty, return it, otherwise return default_value
        return text_content if text_content else default_value
    return default_value

def get_player_url_from_row(row_obj, stat_name="name_display", default_value="N/A"):
    """
    Extracts the player's b-ref URL from the row.
    Uses 'name_display' as corrected in test_index.py.
    """
    cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
    if cell and cell.a and 'href' in cell.a.attrs:
        return "https://www.basketball-reference.com" + cell.a['href']
    return default_value

# --- Core Logic Functions (Structure from make_index2.py) ---

def pull_bref_data(totals=False):
    """
    Pull data from Basketball Reference using the robust 'data-stat' scraping method.
    """
    leagues = "playoffs" if config.PLAYOFFS_MODE else "leagues"
    frames = []

    # Determine URL and stat names based on data type
    if totals:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_totals.html"
        data_type = "totals"
        stat_suffix = ""
        pts_stat = "pts"
    else:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_per_poss.html"
        data_type = "per possession"
        stat_suffix = "_per_poss"
        pts_stat = "pts_per_poss" # 'pts' is also on per_poss page, but this is explicit

    # Only scrape current year
    url = url_pattern.format(year=config.CURRENT_YEAR)
    html_content = fetch_data(url)
    if not html_content:
        print(f"Skipping {config.CURRENT_YEAR}, couldn't fetch data")
        return pd.DataFrame()

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main data table
    table_id = "totals_stats" if totals else "per_poss_stats"
    table = soup.find('table', id=table_id)
    if not table:
        table = soup.find('table') # Fallback
    
    if not table:
        print(f"No table found for {config.CURRENT_YEAR}")
        return pd.DataFrame()

    # Find table body
    tbody = table.find('tbody')
    if not tbody:
        print(f"No table body found for {config.CURRENT_YEAR}")
        return pd.DataFrame()

    # Get all rows
    rows = tbody.find_all('tr')
    print(f"Found {len(rows)} player entries for {config.CURRENT_YEAR}")

    # Extract data
    data = []
    for row in rows:
        # Skip header rows that are sometimes repeated in the body
        if 'thead' in row.get('class', []):
            continue

        # Get values using robust helper functions
        # Using 'name_display' and 'team_name_abbr' as corrected in test_index.py
        player_name = get_stat_from_row(row, 'name_display', "N/A")
        
        # Skip non-player rows (like "Player" headers)
        if player_name == "N/A" or player_name == "Player":
            continue
            
        player_url = get_player_url_from_row(row, 'name_display')
        team_acronym = get_stat_from_row(row, 'team_name_abbr', "N/A")
        
        gp = get_stat_from_row(row, 'g', "0")
        mp = get_stat_from_row(row, 'mp', "0")

        # Get shooting stats with dynamic suffixes
        fg = get_stat_from_row(row, f'fg{stat_suffix}', "0")
        fga = get_stat_from_row(row, f'fga{stat_suffix}', "0")
        tp = get_stat_from_row(row, f'fg3{stat_suffix}', "0")  # 3-pointers made
        tpa = get_stat_from_row(row, f'fg3a{stat_suffix}', "0") # 3-point attempts
        ft = get_stat_from_row(row, f'ft{stat_suffix}', "0")  # Free throws made
        fta = get_stat_from_row(row, f'fta{stat_suffix}', "0") # Free throw attempts
        pts = get_stat_from_row(row, pts_stat, "0")       # Points

        data.append([
            player_name, player_url, team_acronym, config.CURRENT_YEAR, 
            gp, mp, fga, fg, tpa, tp, fta, ft, pts
        ])

    # Create DataFrame
    year_data = pd.DataFrame(
        data=data, 
        columns=['player', 'url', 'team', 'year', 'G', 'MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT', 'PTS']
    )

    if not year_data.empty:
        print(f"Successfully processed {len(year_data)} players for {config.CURRENT_YEAR} ({data_type})")
        if len(year_data) > 0:
            print(f"Sample player: {year_data.iloc[0]['player']} - {year_data.iloc[0]['team']}")
    else:
        print(f"WARNING: No data found for {config.CURRENT_YEAR}")
        # This can happen if the season hasn't started
        if not config.PLAYOFFS_MODE:
             print("This may be normal if the regular season has not started.")
        return pd.DataFrame() # Return empty frame

    frames.append(year_data)
    time.sleep(2)  # Be nice to the server

    return pd.concat(frames) if frames else pd.DataFrame()

def process_player_ids(df, master_df):
    """Process player IDs using master dataframe and NBA API"""
    if df.empty:
        print("Player ID processing skipped: DataFrame is empty.")
        return df
        
    print(f"Processing player IDs for {len(df)} players")

    # Extract Basketball Reference IDs
    df['bref_id'] = df['url'].str.split('/', expand=True)[5].str.split('.', expand=True)[0]

    # Create ID mapping dictionary from master
    match_dict = dict(zip(master_df['bref_id'], master_df['nba_id']))
    team_dict = dict(zip(master_df['team'], master_df['team_id']))

    # Add hardcoded IDs
    match_dict.update(config.SEARCH_DICT)

    # Map IDs to dataframe
    df['nba_id'] = df['bref_id'].map(match_dict)

    # --- Robust ID Matching (from test_index.py's "REPLACEMENT BLOCK") ---
    
    # 1. Identify players *still* missing an nba_id
    missing_mask = df['nba_id'].isna()
    players_missing_bref_id = df[missing_mask]
    
    if players_missing_bref_id.empty:
        print("\n--- All players successfully matched by bref_id. ---\n")
        df['team_id'] = df['team'].map(team_dict)
        return df

    # 2. Attempt to fill missing IDs using the NBA API
    print(f"\n--- {len(players_missing_bref_id)} players failed bref_id match. Attempting name match... ---")
    
    try:
        players_data = commonallplayers.CommonAllPlayers(
            is_only_current_season=1, 
            season=config.CURRENT_SEASON
        )
        players_list = players_data.get_data_frames()[0]
        # Create a lookup dictionary from 'DISPLAY_FIRST_LAST' to 'PERSON_ID'
        player_names_map = dict(zip(players_list['DISPLAY_FIRST_LAST'], players_list['PERSON_ID']))
        print(f"Found {len(player_names_map)} active players in NBA API.")
    except Exception as e:
        print(f"ERROR: Could not fetch player list from NBA API for season {config.CURRENT_SEASON}.")
        print(f"Error details: {e}")
        print("Will only use existing master list for matching.")
        player_names_map = {} # Create empty dict so the script doesn't fail

    if player_names_map:
        # 3. Apply the name map to the missing players
        df.loc[missing_mask, 'nba_id'] = df.loc[missing_mask, 'player'].map(player_names_map)
        
        # 4. Identify players *STILL* missing an nba_id after *both* attempts
        still_missing_mask = df['nba_id'].isna()
        final_unmatched_players = df[still_missing_mask]
        
        if not final_unmatched_players.empty:
            print("\n" + "="*60)
            print("  WARNING: Could not find matching NBA ID for the following players:")
            print("  (These players will be DROPPED from the final stats files)")
            print("="*60)
            for _, row in final_unmatched_players.iterrows():
                print(f"  - Player (b-ref): '{row['player']}' (Team: {row['team']}, URL: {row['url']})")
            print("="*60 + "\n")
        else:
            print("--- All players successfully matched by name. ---\n")

    # Map team IDs
    df['team_id'] = df['team'].map(team_dict)
    
    # Drop any players we couldn't find an ID for
    initial_count = len(df)
    df.dropna(subset=['nba_id'], inplace=True)
    final_count = len(df)

    if initial_count > final_count:
        print(f"Dropped {initial_count - final_count} unmatched players.")
        
    print(f"Final count: {len(df)} players with IDs")

    return df

def calculate_true_shooting(df):
    """Calculate True Shooting Percentage"""
    if df.empty:
        print("TS% calculation skipped: DataFrame is empty.")
        return df
        
    print("Calculating True Shooting Percentage")

    # Clean numeric columns
    numeric_cols = ['FTA', 'FGA', 'PTS', 'G', 'MP']
    for col in numeric_cols:
        df[col] = df[col].replace('', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Calculate TS%
    # Use np.where to avoid division by zero
    denominator = 2 * (df['FGA'] + 0.44 * df['FTA'])
    df['TS%'] = np.where(
        denominator > 0,
        (df['PTS'] / denominator) * 100,
        0
    )

    # Clean up extreme values
    df.replace([np.inf, -np.inf], 0, inplace=True)
    df.loc[df['TS%'] > 150, 'TS%'] = 0

    print(f"TS% stats: Min={df['TS%'].min():.2f}, Max={df['TS%'].max():.2f}, Avg={df['TS%'].mean():.2f}")

    return df

def update_master_index(index_df, master_df):
    """Update master index with new players"""
    if index_df.empty:
        print("Master index update skipped: DataFrame is empty.")
        return master_df
        
    print(f"Updating master index")

    # Create copy of current data
    # Fixed duplicated line from make_index2.py
    index_copy = index_df[['player', 'url', 'year', 'team', 'bref_id', 'nba_id', 'team_id']].copy()

    # Ensure correct types before merge
    index_copy['year'] = index_copy['year'].astype(int)
    index_copy['nba_id'] = pd.to_numeric(index_copy['nba_id'], errors='coerce').astype('Int64')
    index_copy['team_id'] = pd.to_numeric(index_copy['team_id'], errors='coerce').astype('Int64')

    master_df['year'] = master_df['year'].astype(int)
    master_df['nba_id'] = pd.to_numeric(master_df['nba_id'], errors='coerce').astype('Int64')
    master_df['team_id'] = pd.to_numeric(master_df['team_id'], errors='coerce').astype('Int64')

    # Remove current year data from master
    master_df = master_df[master_df.year != config.CURRENT_YEAR].copy()

    # Concatenate and deduplicate
    updated_master = pd.concat([master_df, index_copy])
    updated_master.drop_duplicates(subset=['bref_id', 'year', 'team'], inplace=True)

    # Save updated master
    updated_master.to_csv(config.index_master_path, index=False)
    
    if config.PLAYOFFS_MODE:
        team_master = updated_master[['team','team_id','year']].reset_index(drop=True)
        team_master.drop_duplicates(inplace=True)
        team_master.to_csv('team_index_ps.csv',index=False)

    print(f"Master index updated: {len(updated_master)} total entries")
    new_players = len(index_copy[~index_copy['bref_id'].isin(master_df['bref_id'])])
    print(f"Added {new_players} new players to the index")

    return updated_master

def update_stats_file(index_df, stats_type):
    """Update either totals or scoring stats file"""
    if index_df.empty:
        print(f"Stats file update skipped for '{stats_type}': DataFrame is empty.")
        return
        
    print(f"Updating {stats_type} stats file")

    # Set file path based on stats type
    if stats_type == 'totals':
        file_path = config.totals_path
        columns = ['player', 'TS%', 'PTS', 'MP', 'team', 'G', 'FTA', 'FGA', 'year', 'nba_id']
    else:  # scoring
        file_path = config.scoring_path
        columns = ['player', 'TS%', 'PTS', 'MP', 'team', 'G', 'year', 'nba_id']

    # Read existing data
    try:
        old_stats = pd.read_csv(file_path)
        old_stats = old_stats[old_stats.year < config.CURRENT_YEAR]
        print(f"Read {len(old_stats)} existing stat entries from {file_path}")
    except FileNotFoundError:
        print(f"No existing stats file found at {file_path}, creating new file")
        old_stats = pd.DataFrame()

    # Select required columns
    new_df = index_df[columns].copy()

    # Rename columns
    new_df = new_df.rename(columns={
        'player': 'Player',
        'team': 'Tm'
    })

    # Combine old and new data
    new_stats = pd.concat([old_stats, new_df])

    # Final cleanup
    new_stats.fillna(0, inplace=True)
    new_stats.replace([np.inf, -np.inf], 0, inplace=True)
    new_stats.loc[new_stats['TS%'] > 150, 'TS%'] = 0

    # Save updated stats
    new_stats.to_csv(file_path, index=False)

    print(f"Updated {stats_type} stats: {len(new_df)} new entries, {len(new_stats)} total entries")

    return new_stats

def export_games_data(scoring_df, playoffs=False):
    """Export games played data for other parts of the application"""
    gp = scoring_df[['nba_id', 'Player', 'year', 'G']].reset_index(drop=True)

    if playoffs:
        output_path = '../player_sheets/lineups/ps_games.csv'
        extra_path = '../extra_data/wowy_leverage/ps_games.csv'
        gp.to_csv(output_path, index=False)
        gp.to_csv(extra_path, index=False)
        print(f"Exported playoffs games data to {output_path} and {extra_path}")
    else:
        output_path = '../player_sheets/lineups/games.csv'
        gp.to_csv(output_path, index=False)
        print(f"Exported regular season games data to {output_path}")

    print(f"Games data exported: {len(gp)} player entries")

def main():
    print("=" * 50)
    print(f"NBA Data Scraper - {config.CURRENT_SEASON} {'Playoffs' if config.PLAYOFFS_MODE else 'Regular Season'}")
    print("=" * 50)

    # Step 1: Load master index
    try:
        master = pd.read_csv(config.index_master_path)
        print(f"Loaded master index with {len(master)} entries")
    except FileNotFoundError:
        print(f"No master index found at '{config.index_master_path}', creating a new one")
        master = pd.DataFrame(columns=['player', 'url', 'year', 'team', 'bref_id', 'nba_id', 'team_id'])

    # Step 2: Get totals data
    print("\n--- Processing Totals Data ---")
    totals_frame = pull_bref_data(totals=True)
    if not totals_frame.empty:
        totals_frame = process_player_ids(totals_frame, master)
        totals_frame = calculate_true_shooting(totals_frame)
        master = update_master_index(totals_frame, master) # Update master with totals data
        update_stats_file(totals_frame, 'totals')
    else:
        print("No totals data found. Skipping processing.")

    # Step 3: Get per possession data
    print("\n--- Processing Per Possession Data (Scoring) ---")
    scoring_frame = pull_bref_data(totals=False)
    if not scoring_frame.empty:
        scoring_frame = process_player_ids(scoring_frame, master) # Use updated master
        scoring_frame = calculate_true_shooting(scoring_frame)
        update_stats_file(scoring_frame, 'scoring')
    else:
        print("No scoring (per-poss) data found. Skipping processing.")

    # Step 4: Export games data
    # This block is from test_index.py, integrated into the main flow
    print("\n--- Exporting Games Data ---")
    try:
        # Export regular season games
        reg_scoring = pd.read_csv(config.scoring_path)
        export_games_data(reg_scoring, playoffs=False)
    except FileNotFoundError:
        print(f"No regular season scoring data found at {config.scoring_path}, skipping games export")
        
    try:
        # Always try to export playoff games data
        ps_scoring = pd.read_csv('scoring_ps.csv')
        export_games_data(ps_scoring, playoffs=True)
    except FileNotFoundError:
        print("No playoffs scoring data found, skipping playoffs games export")


    print("\n" + "=" * 50)
    print("Scraping process completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()