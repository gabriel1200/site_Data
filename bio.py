import pandas as pd
import requests 
import time

# Changed to Playoffs
url='https://stats.nba.com/stats/leaguedashplayerbiostats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=F&Season=2025-26&SeasonSegment=&SeasonType=Playoffs&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='

def pull_data(url):
    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }
    json = requests.get(url,headers = headers).json()

    if len(json["resultSets"])== 1:
        data = json["resultSets"][0]["rowSet"]
        columns = json["resultSets"][0]["headers"]
        df = pd.DataFrame.from_records(data, columns=columns)
    else:
        data = json["resultSets"]["rowSet"]
        columns = json["resultSets"]["headers"][1]['columnNames']
        df = pd.DataFrame.from_records(data, columns=columns)

    time.sleep(.2)
    return df

frame = pull_data(url)
print(frame.columns)
print(frame)


#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np
import sys
from nba_api.stats.endpoints import commonallplayers 

class Config:
    """
    Central configuration class for the scraper.
    """
    # Set to True for playoffs data
    PLAYOFFS_MODE = True 
    
    CURRENT_YEAR = 2026
    CURRENT_SEASON = "2025-26"
    
    @property
    def trail(self):
        return '_ps' if self.PLAYOFFS_MODE else ''

    @property
    def totals_path(self):
        return f'totals{self.trail}.csv'

    SEARCH_DICT = {}

config = Config()

# --- Utility Functions ---
def fetch_data(url):
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = 'utf-8'
        response.raise_for_status() 
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch data: {e}")
        return None

def get_stat_from_row(row_obj, stat_name, default_value="0"):
    cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
    if cell:
        text_content = cell.text.strip()
        return text_content if text_content else default_value
    return default_value

# FIX: Change default from "name_display" to "player"
def get_player_url_from_row(row_obj, stat_name="player", default_value="N/A"):
    cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
    if cell and cell.a and 'href' in cell.a.attrs:
        return "https://www.basketball-reference.com" + cell.a['href']
    return default_value

# --- Core Logic Function ---
def pull_bref_data(totals=False):
    leagues = "playoffs" if config.PLAYOFFS_MODE else "leagues"
    frames = []

    if totals:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_totals.html"
        data_type = "totals"
        stat_suffix = ""
        pts_stat = "pts"
    else:
        url_pattern = f"https://www.basketball-reference.com/{leagues}/NBA_{{year}}_per_poss.html"
        data_type = "per possession"
        stat_suffix = "_per_poss"
        pts_stat = "pts_per_poss"

    url = url_pattern.format(year=config.CURRENT_YEAR)
    html_content = fetch_data(url)
    if not html_content:
        print(f"Skipping {config.CURRENT_YEAR}, couldn't fetch data")
        return pd.DataFrame()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    table_id = "totals_stats" if totals else "per_poss_stats"
    table = soup.find('table', id=table_id)
    if not table:
        table = soup.find('table') 
    
    if not table:
        print(f"No table found for {config.CURRENT_YEAR}")
        return pd.DataFrame()

    tbody = table.find('tbody')
    if not tbody:
        print(f"No table body found for {config.CURRENT_YEAR}")
        return pd.DataFrame()

    rows = tbody.find_all('tr')
    print(f"Found {len(rows)} player entries for {config.CURRENT_YEAR}")

    data = []
    for row in rows:
        if 'thead' in row.get('class', []):
            continue

        # FIX: Changed from 'name_display' to 'player'
        player_name = get_stat_from_row(row, 'player', "N/A")
        
        if player_name == "N/A" or player_name == "Player":
            continue
            
        # FIX: Explicitly passing 'player'
        player_url = get_player_url_from_row(row, 'player')
        
        # FIX: Changed from 'team_name_abbr' to 'team_id'
        team_acronym = get_stat_from_row(row, 'team_id', "N/A")
        
        position = get_stat_from_row(row, 'pos', "N/A")
        gp = get_stat_from_row(row, 'g', "0")
        mp = get_stat_from_row(row, 'mp', "0")

        fg = get_stat_from_row(row, f'fg{stat_suffix}', "0")
        fga = get_stat_from_row(row, f'fga{stat_suffix}', "0")
        tp = get_stat_from_row(row, f'fg3{stat_suffix}', "0")
        tpa = get_stat_from_row(row, f'fg3a{stat_suffix}', "0")
        ft = get_stat_from_row(row, f'ft{stat_suffix}', "0")
        fta = get_stat_from_row(row, f'fta{stat_suffix}', "0")
        pts = get_stat_from_row(row, pts_stat, "0")

        data.append([
            player_name, player_url, team_acronym, config.CURRENT_YEAR, 
            position, 
            gp, mp, fga, fg, tpa, tp, fta, ft, pts
        ])

    year_data = pd.DataFrame(
        data=data, 
        columns=['player', 'url', 'team', 'year', 'Pos', 'G', 'MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT', 'PTS']
    )

    if not year_data.empty:
        print(f"Successfully processed {len(year_data)} players for {config.CURRENT_YEAR} ({data_type})")
    else:
        print(f"WARNING: No data found for {config.CURRENT_YEAR}")
        if not config.PLAYOFFS_MODE:
             print("This may be normal if the regular season has not started.")
        return pd.DataFrame()

    frames.append(year_data)
    time.sleep(2)

    return pd.concat(frames) if frames else pd.DataFrame()


if __name__ == "__main__":
    totals_data_with_pos = pull_bref_data(totals=True)
    
    if not totals_data_with_pos.empty:
        totals_data_with_pos['bref_id']= totals_data_with_pos['url'].str.split('/').str[-1]
        totals_data_with_pos['bref_id']= totals_data_with_pos['bref_id'].str.split('.').str[0]
        
        totals_data_with_pos=totals_data_with_pos[['Pos','bref_id']]
        
        # Pulling the playoff index
        index_master = pd.read_csv('https://raw.githubusercontent.com/gabriel1200/site_Data/refs/heads/master/index_master_ps.csv')
        index_master = index_master[index_master.year==2026]

        player_index = index_master.merge(totals_data_with_pos,on='bref_id')
        
        # Save to a modern playoff index
        player_index.to_csv('modern_index_ps.csv',index=False)