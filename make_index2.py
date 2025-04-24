#!/usr/bin/env python
# coding: utf-8

# In[6]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np
from nba_api.stats.endpoints import commonallplayers

# Configuration
class Config:
    # Set to True for playoffs data, False for regular season
    PLAYOFFS_MODE = True
    # Current year to scrape
    CURRENT_YEAR = 2025
    # Current season in NBA API format
    CURRENT_SEASON = "2024-25"
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
    
    # Hard-coded player IDs for players that might be missing
    SEARCH_DICT = {
        "hollaro01": 1641842,
        "sarral01": 1642259,
        "dadiepa01": 1642359,
        "cuiyo01": 1642385,
        "dasiltr01": 1641783,
        "salauti01": 1642275,
        "shannte01": 1630545
    }

# Initialize config
config = Config()
print(f"Running in {'PLAYOFFS' if config.PLAYOFFS_MODE else 'REGULAR SEASON'} mode")

def fetch_data(url):
    """Fetch data from a URL with proper error handling"""
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = 'utf-8'
        if response.status_code != 200:
            print(f"ERROR: Received status code {response.status_code}")
            return None
        return response.text
    except Exception as e:
        print(f"ERROR: Failed to fetch data: {e}")
        return None

def parse_table_headers(table):
    """Parse table headers and return a mapping of column indices to data stats"""
    header_mapping = {}
    headers = table.find('thead').find_all('th')
    
    for i, header in enumerate(headers):
        data_stat = header.get('data-stat')
        if data_stat:
            header_mapping[data_stat] = i
    
    print(f"Found {len(header_mapping)} column headers")
    print(f"Header mapping: {header_mapping}")
    return header_mapping

def get_cell_value(row, header_mapping, stat_name, default_value="0"):
    """Get cell value based on header mapping"""
    cells = row.find_all(['th', 'td'])
    if stat_name in header_mapping and header_mapping[stat_name] < len(cells):
        cell = cells[header_mapping[stat_name]]
        return cell.text.strip() if cell.text.strip() else default_value
    return default_value

def get_player_url(row, header_mapping):
    """Get player URL from the row"""
    cells = row.find_all(['th', 'td'])
    player_index = header_mapping.get('player', 0)
    if player_index < len(cells):
        player_cell = cells[player_index]
        player_link = player_cell.find('a')
        if player_link and player_link.has_attr('href'):
            return "https://www.basketball-reference.com" + player_link['href']
    return "N/A"

def pull_bref_data(totals=False):
    """Pull data from Basketball Reference using dynamic header mapping"""
    leagues = "playoffs" if config.PLAYOFFS_MODE else "leagues"
    frames = []
    
    # Determine URL based on data type
    if totals:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_totals.html"
        data_type = "totals"
    else:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_per_poss.html"
        data_type = "per possession"
    
    # Only scrape current year
    url = url_pattern.format(year=config.CURRENT_YEAR)
    html_content = fetch_data(url)
    if not html_content:
        print(f"Skipping {config.CURRENT_YEAR}, couldn't fetch data")
        return pd.DataFrame()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    if not table:
        print(f"No table found for {config.CURRENT_YEAR}")
        return pd.DataFrame()
    
    # Parse headers to get column mapping
    header_mapping = parse_table_headers(table)
    
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
        # Skip header rows
        if 'thead' in row.get('class', []) or row.get('class') == ['thead']:
            continue
            
        # Get values using header mapping
        player_name = get_cell_value(row, header_mapping, 'player', "N/A")
        player_url = get_player_url(row, header_mapping)
        team_acronym = get_cell_value(row, header_mapping, 'team_id', "N/A")
        
        # Get the stats - handle both normal and per_poss stats
        gp = get_cell_value(row, header_mapping, 'g', "0")
        mp = get_cell_value(row, header_mapping, 'mp', "0")
        
        # Get shooting stats - handle both normal and per_poss stats
        if totals:
            # Total stats use standard column names
            fg = get_cell_value(row, header_mapping, 'fg', "0")
            fga = get_cell_value(row, header_mapping, 'fga', "0")
            tp = get_cell_value(row, header_mapping, 'fg3', "0")  # 3-pointers made
            tpa = get_cell_value(row, header_mapping, 'fg3a', "0")  # 3-point attempts
            ft = get_cell_value(row, header_mapping, 'ft', "0")  # Free throws made
            fta = get_cell_value(row, header_mapping, 'fta', "0")  # Free throw attempts
            pts = get_cell_value(row, header_mapping, 'pts', "0")  # Points
        else:
            # Per possession stats use _per_poss suffix
            fg = get_cell_value(row, header_mapping, 'fg_per_poss', "0")
            fga = get_cell_value(row, header_mapping, 'fga_per_poss', "0")
            tp = get_cell_value(row, header_mapping, 'fg3_per_poss', "0")
            tpa = get_cell_value(row, header_mapping, 'fg3a_per_poss', "0")
            ft = get_cell_value(row, header_mapping, 'ft_per_poss', "0")
            fta = get_cell_value(row, header_mapping, 'fta_per_poss', "0")
            pts = get_cell_value(row, header_mapping, 'pts_per_poss', "0")

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
    
    frames.append(year_data)
    time.sleep(2)  # Be nice to the server
    
    return pd.concat(frames) if frames else pd.DataFrame()

def process_player_ids(df, master_df):
    """Process player IDs using master dataframe and NBA API"""
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
    
    # Find missing IDs
    missing_ids = df[df['nba_id'].isna()].reset_index(drop=True)
    missing_count = len(missing_ids)
    print(f"Found {missing_count} players without NBA IDs")
    
    if missing_count > 0:
        # Try to find IDs using NBA API
        print("Fetching player data from NBA API...")
        try:
            players_data = commonallplayers.CommonAllPlayers(
                is_only_current_season=1, 
                season=config.CURRENT_SEASON
            )
            players_list = players_data.get_data_frames()[0]
            player_names = dict(zip(players_list['DISPLAY_FIRST_LAST'], players_list['PERSON_ID']))
            
            # Map missing IDs
            missing_ids['nba_id'] = missing_ids['player'].map(player_names)
            found_count = missing_ids['nba_id'].notna().sum()
            print(f"Found {found_count} additional IDs from the NBA API")
            
            # Add found players back to dataframe
            if found_count > 0:
                missing_ids_found = missing_ids[missing_ids['nba_id'].notna()]
                df = pd.concat([df.dropna(subset=['nba_id']), missing_ids_found])
                print(f"Added {len(missing_ids_found)} players with newly found IDs")
        except Exception as e:
            print(f"ERROR: Failed to fetch data from NBA API: {e}")
    
    # Map team IDs
    df['team_id'] = df['team'].map(team_dict)
    
    # Count final results
    missing_final = df['nba_id'].isna().sum()
    print(f"Final count: {len(df) - missing_final} players with IDs, {missing_final} still missing")
    
    return df

def calculate_true_shooting(df):
    """Calculate True Shooting Percentage"""
    print("Calculating True Shooting Percentage")
    
    # Clean numeric columns
    numeric_cols = ['FTA', 'FGA', 'PTS', 'G', 'MP']
    for col in numeric_cols:
        df[col] = df[col].replace('', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate TS%
    df['TS%'] = (df['PTS'] / (2 * (df['FGA'] + 0.44 * df['FTA']))) * 100
    
    # Clean up extreme values
    df.replace([np.inf, -np.inf], 0, inplace=True)
    df.loc[df['TS%'] > 150, 'TS%'] = 0
    
    print(f"TS% stats: Min={df['TS%'].min():.2f}, Max={df['TS%'].max():.2f}, Avg={df['TS%'].mean():.2f}")
    
    return df

def update_master_index(index_df, master_df):
    """Update master index with new players"""
    print(f"Updating master index")
    
    # Create copy of current data
    index_copy = index_df[['player', 'url', 'year', 'team', 'bref_id', 'nba_id', 'team_id']]
    
    # Remove current year data from master
    master_df = master_df[master_df.year != config.CURRENT_YEAR]
    
    # Concatenate and deduplicate
    updated_master = pd.concat([master_df, index_copy])
    updated_master.drop_duplicates(inplace=True)
    
    # Save updated master
    updated_master.to_csv(config.index_master_path, index=False)
    updated_master.to_csv(config.index_master_path, index=False)

    
    print(f"Master index updated: {len(updated_master)} total players")
    new_players = len(index_copy[~index_copy['bref_id'].isin(master_df['bref_id'])])
    print(f"Added {new_players} new players to the index")
    
    return updated_master

def update_stats_file(index_df, stats_type):
    """Update either totals or scoring stats file"""
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
    gp = scoring_df[['nba_id', 'Player', 'year', 'G']].reset_index()
    
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
        print(f"No master index found, creating a new one")
        master = pd.DataFrame(columns=['player', 'url', 'year', 'team', 'bref_id', 'nba_id', 'team_id'])
    
    # Step 2: Get totals data
    print("\n--- Processing Totals Data ---")
    totals_frame = pull_bref_data(totals=True)
    if not totals_frame.empty:
        totals_frame = process_player_ids(totals_frame, master)
        totals_frame = calculate_true_shooting(totals_frame)
        master = update_master_index(totals_frame, master)
        update_stats_file(totals_frame, 'totals')
    
    # Step 3: Get per possession data
    print("\n--- Processing Per Possession Data ---")
    scoring_frame = pull_bref_data(totals=False)
    if not scoring_frame.empty:
        scoring_frame = process_player_ids(scoring_frame, master)
        scoring_frame = calculate_true_shooting(scoring_frame)
        update_stats_file(scoring_frame, 'scoring')
    
    # Step 4: Export games data
    print("\n--- Exporting Games Data ---")
    try:
        scoring = pd.read_csv(config.scoring_path)
        export_games_data(scoring, playoffs=config.PLAYOFFS_MODE)
        
        if not config.PLAYOFFS_MODE:
            # Also export playoff games data if in regular season mode
            try:
                ps_scoring = pd.read_csv('scoring_ps.csv')
                export_games_data(ps_scoring, playoffs=True)
            except FileNotFoundError:
                print("No playoffs scoring data found, skipping playoffs games export")
    except FileNotFoundError:
        print(f"No scoring data found at {config.scoring_path}, skipping games export")
    
    print("\n" + "=" * 50)
    print("Scraping process completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()

