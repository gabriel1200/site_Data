#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import time
from pathlib import Path

def get_playtypes(years, ps=False, p_or_t='t', defense=False):
    """
    Fetches play-by-play data from the NBA stats API for specified years.

    Args:
        years (list): A list of years to fetch data for (e.g., [2024] for the 2024-25 season).
        ps (bool): If True, fetches playoff data; otherwise, regular season.
        p_or_t (str): 'p' for player stats, 't' for team stats.
        defense (bool): If True, fetches defensive stats.

    Returns:
        pandas.DataFrame: A DataFrame containing the fetched and processed data.
    """
    field_side = "offensive"
    if defense:
        field_side = "defensive"
    
    entity_type = 'T'
    if p_or_t.lower() == 'p':
        entity_type = 'P'

    season_type = "Regular+Season"
    if ps:
        season_type = "Playoffs"

    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }

    playtypes = ['Transition', 'PRBallHandler', 'Spotup', 'Isolation', 'PRRollman', 'Postup', 'Misc', 'OffRebound', 'Cut', 'Handoff', 'OffScreen']
    plays = ['tran', 'pr_ball', 'spot', 'iso', 'pr_roll', 'post', 'misc', 'oreb', 'cut', 'hand_off', 'off_screen']
    
    all_frames = []

    for year in years:
        season_str = f"{year}-{str(year+1)[-2:]}"
        print(f"Fetching data for {season_str} {season_type}...")

        for play, play_name in zip(playtypes, plays):
            url = (
                f"https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode=Totals&PlayType={play}"
                f"&PlayerOrTeam={entity_type}&SeasonType={season_type}&SeasonYear={season_str}"
                f"&TypeGrouping={field_side}"
            )
            
            print(f"Fetching {play_name} data...")
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                json_data = response.json()
                data = json_data["resultSets"][0]["rowSet"]
                columns = json_data["resultSets"][0]["headers"]
                time.sleep(2) # Be courteous to the API

                df = pd.DataFrame.from_records(data, columns=columns)
                df.rename(columns={
                    'TEAM_NAME': 'TEAM', 'POSS_PCT': 'FREQ%', 'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%',
                    'TOV_POSS_PCT': 'TOVFREQ%', 'PLUSONE_POSS_PCT': 'AND ONEFREQ%', 'FT_POSS_PCT': 'FTFREQ%',
                    'SCORE_POSS_PCT': 'SCOREFREQ%', 'SF_POSS_PCT': 'SFFREQ%'
                }, inplace=True)

                for col in df.columns:
                    if '%' in col or 'PERC' in col:
                        df[col] *= 100
                
                df['playtype'] = play_name
                df['year'] = year + 1
                all_frames.append(df)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {url}: {e}")
                continue

    if not all_frames:
        return pd.DataFrame()

    full_data = pd.concat(all_frames, ignore_index=True)

    if p_or_t.lower() == 'p':
        map_terms = {
            'PLAYER_NAME': 'Player', 'TEAM_ID': 'team_id', 'TEAM': 'Team', 'GP': 'GP', 'POSS': 'Poss',
            'FREQ%': '% Time', 'PPP': 'PPP', 'PTS': 'Points', 'FGM': 'FGM', 'FGA': 'FGA', 'FG%': 'FG%',
            'EFG%': 'aFG%', 'FTFREQ%': '%FT', 'TOVFREQ%': '%TO', 'SFFREQ%': '%SF', 
            'AND ONEFREQ%': 'AND ONEFREQ%', 'SCOREFREQ%': '%Score', 'PERCENTILE': 'Percentile'
        }
        full_data.rename(columns=map_terms, inplace=True)
    else: # Team data
        team_dict = {
            'New York Knicks': 'NYK', 'New Orleans Pelicans': 'NOP', 'Oklahoma City Thunder': 'OKC',
            'Golden State Warriors': 'GSW', 'Brooklyn Nets': 'BKN', 'Houston Rockets': 'HOU',
            'Miami Heat': 'MIA', 'Phoenix Suns': 'PHX', 'Philadelphia 76ers': 'PHI',
            'Sacramento Kings': 'SAC', 'Los Angeles Clippers': 'LAC', 'LA Clippers': 'LAC',
            'Cleveland Cavaliers': 'CLE', 'Detroit Pistons': 'DET', 'Los Angeles Lakers': 'LAL',
            'Denver Nuggets': 'DEN', 'Orlando Magic': 'ORL', 'Indiana Pacers': 'IND',
            'Boston Celtics': 'BOS', 'Toronto Raptors': 'TOR', 'Charlotte Bobcats': 'CHA',
            'Washington Wizards': 'WAS', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
            'Atlanta Hawks': 'ATL', 'Portland Trail Blazers': 'POR', 'Memphis Grizzlies': 'MEM',
            'San Antonio Spurs': 'SAS', 'Dallas Mavericks': 'DAL', 'Utah Jazz': 'UTA',
            'Chicago Bulls': 'CHI', 'Charlotte Hornets': 'CHA'
        }
        full_data.rename(columns={'PTS': 'Points', 'TEAM': 'full_name'}, inplace=True)
        full_data['Team'] = full_data['full_name'].map(team_dict)
    
    return full_data

def update_master_file(year, file_path, fetch_function, **fetch_kwargs):
    """
    Updates a master CSV file with new data for a given year.

    Args:
        year (int): The calendar year to update (e.g., 2025).
        file_path (str): The path to the master CSV file.
        fetch_function (function): The function used to fetch new data.
        **fetch_kwargs: Keyword arguments to pass to the fetch_function.
    """
    print(f"Updating {file_path} for year {year}...")
    # The API uses the start year of the season (e.g., 2024 for 2024-25 season)
    season_start_year = year - 1
    new_data = fetch_function(years=[season_start_year], **fetch_kwargs)

    if new_data.empty:
        print(f"No new data found for year {year}. Halting update for {file_path}.")
        return

    try:
        old_data = pd.read_csv(file_path)
        # Remove any existing data for the year to avoid duplication
        old_data = old_data[old_data.year != year]
        combined_data = pd.concat([old_data, new_data], ignore_index=True)
    except FileNotFoundError:
        print(f"{file_path} not found. Creating a new file.")
        combined_data = new_data

    combined_data.sort_values(by='year', inplace=True)
    combined_data.to_csv(file_path, index=False)
    print(f"Successfully updated {file_path}.")

def generate_and_update_playstyle(year, ps=False):
    """
    Generates playstyle summaries and updates the corresponding master file.
    """
    trail = '_p' if ps else ''
    playtype_file = f'playtype{trail}.csv'
    playstyle_file = 'playstyle_p.csv' if ps else 'playstyle.csv'

    print(f"Generating and updating {playstyle_file} for year {year}...")
    
    try:
        df = pd.read_csv(playtype_file)
    except FileNotFoundError:
        print(f"Error: {playtype_file} not found. Cannot generate playstyle data.")
        return

    # Filter for the year we want to process
    df_year = df[df.year == year].copy()

    if df_year.empty:
        print(f"No data found for the year {year} in {playtype_file}. Skipping update.")
        return

    data_names = {
        'pr_ball': 'on_ball', 'iso': 'on_ball', 'pr_roll': 'play_finish', 'post': 'on_ball',
        'hand_off': 'motion', 'oreb': 'play_finish', 'cut': 'play_finish', 'off_screen': 'motion',
        'spot': 'play_finish', 'tran': 'tran', 'misc': 'misc'
    }
    df_year['playtype'] = df_year['playtype'].map(data_names)
    
    # Group and aggregate the data for the new year
    pstyle_year = df_year.groupby(
        ['Player', 'Team', 'GP', 'PLAYER_ID', 'playtype', 'year']
    ).agg(
        Poss=('Poss', 'sum'),
        Time_Percent=('% Time', 'sum'),
        FGM=('FGM', 'sum'),
        FGA=('FGA', 'sum'),
        Points=('Points', 'sum')
    ).reset_index()

    pstyle_year.rename(columns={'Time_Percent': '% Time'}, inplace=True)
    pstyle_year['PPP'] = (pstyle_year['Points'] / pstyle_year['Poss']).fillna(0)
    
    # Update the master playstyle file
    try:
        old_pstyle = pd.read_csv(playstyle_file)
        old_pstyle = old_pstyle[old_pstyle.year != year]
        new_pstyle = pd.concat([old_pstyle, pstyle_year], ignore_index=True)
    except FileNotFoundError:
        print(f"{playstyle_file} not found. Creating a new file.")
        new_pstyle = pstyle_year

    new_pstyle.sort_values(by='year', inplace=True)
    new_pstyle.to_csv(playstyle_file, index=False)
    print(f"Successfully updated {playstyle_file}.")


# --- Main Execution Block ---
if __name__ == "__main__":
    YEAR_TO_UPDATE = 2025

    # 1. Update master player playtype files (playtype.csv, playtype_p.csv)
    update_master_file(YEAR_TO_UPDATE, 'playtype.csv', get_playtypes, p_or_t='p', ps=False)
    update_master_file(YEAR_TO_UPDATE, 'playtype_p.csv', get_playtypes, p_or_t='p', ps=True)
    
    # 2. Update master team playtype files (teamplay.csv, teamplayd.csv, etc.)
    update_master_file(YEAR_TO_UPDATE, 'teamplay.csv', get_playtypes, p_or_t='t', ps=False, defense=False)
    update_master_file(YEAR_TO_UPDATE, 'teamplayd.csv', get_playtypes, p_or_t='t', ps=False, defense=True)
    update_master_file(YEAR_TO_UPDATE, 'teamplay_p.csv', get_playtypes, p_or_t='t', ps=True, defense=False)
    update_master_file(YEAR_TO_UPDATE, 'teamplayd_p.csv', get_playtypes, p_or_t='t', ps=True, defense=True)

    # 3. Generate and update aggregated playstyle files from the master files
    generate_and_update_playstyle(YEAR_TO_UPDATE, ps=False)
    generate_and_update_playstyle(YEAR_TO_UPDATE, ps=True)

    print("\nScript finished.")


