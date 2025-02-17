#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import math
import plotly.figure_factory as ff

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union

import requests
from requests.exceptions import RequestException
import time
from bs4 import BeautifulSoup

# Constants
NBA_TEAM_URLS ={
        "ATL": "https://www.spotrac.com/nba/atlanta-hawks/yearly",
        "BOS": "https://www.spotrac.com/nba/boston-celtics/yearly",
        "BKN": "https://www.spotrac.com/nba/brooklyn-nets/yearly",
        "CHA": "https://www.spotrac.com/nba/charlotte-hornets/yearly",
        "CHI": "https://www.spotrac.com/nba/chicago-bulls/yearly",
        "CLE": "https://www.spotrac.com/nba/cleveland-cavaliers/yearly",
        "DAL": "https://www.spotrac.com/nba/dallas-mavericks/yearly",
        "DEN": "https://www.spotrac.com/nba/denver-nuggets/yearly",
        "DET": "https://www.spotrac.com/nba/detroit-pistons/yearly",
        "GSW": "https://www.spotrac.com/nba/golden-state-warriors/yearly",
        "HOU": "https://www.spotrac.com/nba/houston-rockets/yearly",
        "IND": "https://www.spotrac.com/nba/indiana-pacers/yearly",
        "LAC": "https://www.spotrac.com/nba/la-clippers/yearly",
        "LAL": "https://www.spotrac.com/nba/los-angeles-lakers/yearly",
        "MEM": "https://www.spotrac.com/nba/memphis-grizzlies/yearly",
        "MIA": "https://www.spotrac.com/nba/miami-heat/yearly",
        "MIL": "https://www.spotrac.com/nba/milwaukee-bucks/yearly",
        "MIN": "https://www.spotrac.com/nba/minnesota-timberwolves/yearly",
        "NOP": "https://www.spotrac.com/nba/new-orleans-pelicans/yearly",
        "NYK": "https://www.spotrac.com/nba/new-york-knicks/yearly",
        "OKC": "https://www.spotrac.com/nba/oklahoma-city-thunder/yearly",
        "ORL": "https://www.spotrac.com/nba/orlando-magic/yearly",
        "PHI": "https://www.spotrac.com/nba/philadelphia-76ers/yearly",
        "PHX": "https://www.spotrac.com/nba/phoenix-suns/yearly",
        "POR": "https://www.spotrac.com/nba/portland-trail-blazers/yearly",
        "SAC": "https://www.spotrac.com/nba/sacramento-kings/yearly",
        "SAS": "https://www.spotrac.com/nba/san-antonio-spurs/yearly",
        "TOR": "https://www.spotrac.com/nba/toronto-raptors/yearly",
        "UTA": "https://www.spotrac.com/nba/utah-jazz/yearly",
        "WAS": "https://www.spotrac.com/nba/washington-wizards/yearly"
    }

SEASONS = ['2024-25', '2025-26', '2026-27', '2027-28', '2028-29']
EXTRA_SEASONS = ['2029-30', '2030-31']
FREE_AGENT_TYPES = ['UFA', 'RFA']

def get_team_data(url: str, timeout: int = 10) -> List[pd.DataFrame]:
    """
    Safely fetch and parse HTML tables from the team URL.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return pd.read_html(response.text)
    except RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing HTML tables: {e}")
        return []


def clean_player_name(name: str) -> str:
    """
    Clean player names by removing suffixes and extra spaces.
    """
    name = name.split(' ', 1)[1] if ' ' in name else name
    return name.replace('III ', '').replace('II ', '').replace('r. ', '')

def process_salary_value(value: str) -> float:
    """
    Convert salary strings to float values.
    """
    if pd.isna(value) or any(fa_type in str(value) for fa_type in FREE_AGENT_TYPES):
        return 0.0
    
    value = str(value).replace('Ext. Elig.', '').strip()
    value = ''.join(filter(str.isdigit, value))
    return float(value) if value else 0.0

def process_option_type(row: pd.Series) -> str:
    """
    Determine the type of contract option.
    """
    option_type = row['Type']
    if 'PLAYER' in option_type:
        return 'P'
    elif 'CLUB' in option_type:
        return 'T'
    elif 'GUARANTEED' in option_type:
        return 'NG'
    elif 'EXTENSION' in option_type:
        return 'EE'
    elif 'RFA' in option_type:
        return 'RFA'
    elif 'UNREST' in option_type:
        return 'UFA'
    else:
        value = row['Value']
        return f"{option_type}{' ' + value if not pd.isna(value) else ''}"

def get_available_seasons(salary_df: pd.DataFrame) -> List[str]:
    """
    Get list of available seasons from salary data.
    """
    available_seasons = SEASONS.copy()
    for season in EXTRA_SEASONS:
        if season in salary_df.columns:
            available_seasons.append(season)
    return available_seasons

import pandas as pd
import re

def clean_player_name(name: str) -> str:
    """
    Clean player name by removing duplicates.
    Example: "Forrest Trent Forrest" -> "Trent Forrest"
    """
    parts = name.split()
    # Remove duplicates while preserving order
    unique_parts = []
    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)
    return " ".join(unique_parts)

def process_salary_value2(value: str) -> float:
    """
    Process salary value from string format.
    Example: "UFA / $2.1M1.5%" -> 2100000
    Returns None for NaN values.
    """
    if pd.isna(value):
        return None
        
    # Extract dollar amount if present
    match = re.search(r'\$(\d+\.?\d*)M', value)
    if match:
        # Convert millions to actual value
        return float(match.group(1)) * 1_000_000
    return None

def process_cap_holds(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process cap holds table.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing player salary information
    team (str): Team name to be added to the DataFrame
    
    Returns:
    pd.DataFrame: Processed DataFrame with cleaned names and converted salary values
    """
    if df is None:
        return pd.DataFrame()
        
    df = df.copy()
    
    # Ensure column names are standardized
    df.columns = ['Player' if 'player' in col.lower() else col for col in df.columns]
    
    # Clean player names
    df['Player'] = df['Player'].apply(clean_player_name)
    
    # Identify salary columns (those containing year patterns like '2024-25')
    salary_cols = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
    
    # Process salary values for each year column
    for col in salary_cols:
        df[col] = df[col].apply(process_salary_value2)
    
    # Add team column
    df['Team'] = team
    
    # Reorder columns to put Team first, then Player, Pos, Age, followed by salary years
    non_salary_cols = ['Team', 'Player', 'Pos', 'Age']
    ordered_cols = non_salary_cols + [col for col in salary_cols if col in df.columns]
    
    return df[ordered_cols]

def process_dead_money(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process dead money table.
    """
    if df is None:
        return pd.DataFrame()
    
    df = df.copy()
    # Standardize column 
    df.columns = ['Player' if 'player' in col.lower() else col for col in df.columns]
    if 'Player' in df.columns:
        
        
        # Clean player names
        df['Player'] = df['Player'].apply(clean_player_name)
        
        # Process values
        value_cols = [col for col in df.columns if col != 'Player']
        for col in value_cols:
            df[col] = df[col].apply(process_salary_value)
        
        df['Team'] = team
    return df

def process_summary(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process summary table.
    """
    if df is None:
        return pd.DataFrame()
    
    df = df.copy()
    # Process values and add team identifier
    value_cols = df.columns
    for col in value_cols:
        df[col] = df[col].apply(process_salary_value)
    
    df['Team'] = team
    return df

def get_team_data(url: str, timeout: int = 10) -> Tuple[List[pd.DataFrame], List[str]]:
    """
    Fetch and parse HTML tables from the team URL, along with their section headers.
    Returns tuple of (list of dataframes, list of headers)
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tables and their preceding h2 headers
        tables_data = []
        headers = []
        
        # Get all tables
        tables = soup.find_all('table')
        
        for table in tables:
            # Look for the nearest preceding h2
            header = None
            prev_elem = table.find_previous('h2')
            if prev_elem:
                header = prev_elem.get_text(strip=True)
            
            # Parse table into DataFrame
            df = pd.read_html(str(table))[0]
            tables_data.append(df)
            headers.append(header)
        
        return tables_data, headers
        
    except RequestException as e:
        print(f"Error fetching data: {e}")
        return [], []
    except ValueError as e:
        print(f"Error parsing HTML tables: {e}")
        return [], []

def find_table_by_header(dfs: List[pd.DataFrame], headers: List[str], target_header: str) -> Optional[pd.DataFrame]:
    """
    Find a specific table by its h2 header text.
    """
    for df, header in zip(dfs, headers):
        if header and target_header.lower() in header.lower():
            return df
    return None

def process_salary_data(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process and clean salary data.
    """
    # Clean column names
    df.columns = ['Player'] + [col for col in df.columns[1:]]
    
    # Clean player names
    df['Player'] = df['Player'].apply(clean_player_name)
    
    # Process salary values
    seasons = get_available_seasons(df)
    for season in seasons:
        df[season] = df[season].apply(process_salary_value)
    
    df['Team'] = team
    return df

def process_options_data(df: pd.DataFrame, salary_df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process and clean options data.
    """
    df.columns = ['Deadline Date', 'Player', 'Type', 'Value']
    

    
    # Process options
    players = salary_df['Player'].unique()
    seasons = get_available_seasons(salary_df)
    
    data = []
    for player in players:
        player_data = df[df['Player'] == player]
        row = {'Player': player}
        
        for season in seasons:
            row[season] = 0
            season_data = player_data[player_data['Type'].str.contains(season, na=False)]
            if not season_data.empty:
                row[season] = process_option_type(season_data.iloc[0])
        
        data.append(row)
    
    options_df = pd.DataFrame(data, columns=['Player'] + seasons)
    options_df = options_df.drop_duplicates().reset_index(drop=True)
    options_df['Team'] = team
    
    return options_df
def team_books(team: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Get salary, options, cap holds, dead money, and summary data for a given team.
    """
    print(f"Processing {team}...")
    
    # Fetch data
    url = NBA_TEAM_URLS.get(team.upper())
    if not url:
        raise ValueError(f"Invalid team code: {team}")
    
    dfs, headers = get_team_data(url)
    if not dfs:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Find all relevant tables by their h2 headers
    salary_df = find_table_by_header(dfs, headers, "Active Roster")  # or whatever the actual header text is
    options_df = next((df for df in dfs if 'Deadline Date' in df.columns), None)

    cap_holds_df = find_table_by_header(dfs, headers, "Cap Hold")

    dead_money_df = find_table_by_header(dfs, headers, "Dead Money")

    
    summary_df = find_table_by_header(dfs, headers, "Summary")
    if salary_df is None:
        print(f"Required salary table not found for {team}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Process all tables
    salary_df = process_salary_data(salary_df, team)
    options_df = process_options_data(options_df, salary_df, team) if options_df is not None else pd.DataFrame()
    cap_holds_df = process_cap_holds(cap_holds_df, team)
    dead_money_df = process_dead_money(dead_money_df, team)
    summary_df = process_summary(summary_df, team)
    dead_money_df['Team']=team
    cap_holds_df['Team']=team
    summary_df['Team']=team

    return salary_df, options_df, cap_holds_df, dead_money_df, summary_df

def scrape_all_teams(teams: List[str], delay: float = 1.0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Scrape data for all teams with rate limiting.
    """
    salary_dfs = []
    options_dfs = []
    cap_holds_dfs = []
    dead_money_dfs = []
    summary_dfs = []
    
    for team in teams:
        try:
            salary_df, options_df, cap_holds_df, dead_money_df, summary_df = team_books(team)
            
            if not salary_df.empty:
                salary_dfs.append(salary_df)
            if not options_df.empty:
                options_dfs.append(options_df)
            if not cap_holds_df.empty:
                cap_holds_dfs.append(cap_holds_df)
            if not dead_money_df.empty:
                dead_money_dfs.append(dead_money_df)
            if not summary_df.empty:
                summary_dfs.append(summary_df)
                
        except Exception as e:
            print(f"Error processing {team}: {e}")
        
        time.sleep(delay)  # Rate limiting
    
    return (
        pd.concat(salary_dfs) if salary_dfs else pd.DataFrame(),
        pd.concat(options_dfs) if options_dfs else pd.DataFrame(),
        pd.concat(cap_holds_dfs) if cap_holds_dfs else pd.DataFrame(),
        pd.concat(dead_money_dfs) if dead_money_dfs else pd.DataFrame(),
        pd.concat(summary_dfs) if summary_dfs else pd.DataFrame()
    )

# Example usage

teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 
         'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 
         'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
#teams=['ATL']
salary_df, option_df, cap_holds_df, dead_money_df, summary_df = scrape_all_teams(teams)

# Save results
salary_df.to_csv('nba_salaries.csv', index=False)
option_df.to_csv('nba_options.csv', index=False)
cap_holds_df.to_csv('nba_cap_holds.csv', index=False)
dead_money_df.to_csv('nba_dead_money.csv', index=False)
summary_df.to_csv('nba_summary.csv', index=False)


salary_df.to_csv('../web_app/data/nba_salaries.csv', index=False)
option_df.to_csv('../web_app/data/nba_options.csv', index=False)
cap_holds_df.to_csv('../web_app/data/nba_cap_holds.csv', index=False)
dead_money_df.to_csv('../web_app/data/nba_dead_money.csv', index=False)
summary_df.to_csv('../web_app/data/nba_summary.csv', index=False)
print(cap_holds_df)


# In[2]:


temp_df=pd.DataFrame()
temp_df['Player'] = option_df['Player']
seasons = ['2024-25','2025-26','2026-27','2027-28','2028-29']
for season in seasons:
    temp_df[season] = np.where(option_df[season]!='T', 1, 0)


guar = pd.DataFrame()
guar['Player'] = salary_df['Player']
guar['Guaranteed'] = 0
for season in seasons:
    guar['Guaranteed']+= temp_df[season]* salary_df[season]
salary_df = salary_df.merge(guar,on='Player')
salary_df.sort_values(by='Guaranteed',inplace=True)
salary_df
salary_df=salary_df.drop_duplicates(subset=['Player','Team'])
salary_df
option_df=option_df.drop_duplicates(subset=['Player','Team'])
option_df
salary_df.loc[salary_df['Player'].str.contains('Branden Carlson'), '2024-25'] = 990895

option_df.loc[option_df['Player'].str.contains('Scottie Barnes'), '2025-26'] = 0
option_df.loc[option_df['Player'].str.contains('Bradley Beal'), '2026-27'] = 'P'
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2024-25'] = 0
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2025-26'] = 0
option_df.loc[option_df['Player'].str.contains('Julius Randle'), '2026-27'] = 'P'


salary_df.to_csv('nba_salaries.csv',index=False)
option_df.to_csv('nba_summary.csv',index=False)

