#!/usr/bin/env python
# coding: utf-8

"""
CONSOLIDATED NBA SCRAPING SCRIPT
This script merges all individual scraping files (player shooting, team shooting,
opponent shooting, hustle, tracking, dribble, playtypes, and pbpstats)
into one master file.

Set the configuration variables in Section 2 to control which season to update.
"""

# ==============================================================================
# SECTION 1: IMPORTS
# ==============================================================================

import pandas as pd
import requests
import time
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Imports for (currently unused) Selenium functions
'''
from selenium import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
'''

# ==============================================================================
# SECTION 2: CENTRAL CONFIGURATION
# ==============================================================================

# Set the *start* year of the season you want to scrape.
# (e.g., 2024 for the 2024-25 season)
YEAR_TO_SCRAPE = 2025

# Set the season type
# True = Playoffs
# False = Regular Season
IS_PLAYOFFS = False

# --- Derived Variables (Do not change) ---
SEASON_END_YEAR = YEAR_TO_SCRAPE + 1
SEASON_STR_NBA = f"{YEAR_TO_SCRAPE}-{str(SEASON_END_YEAR)[-2:]}"
SEASON_TYPE_STR_NBA = "Playoffs" if IS_PLAYOFFS else "Regular%20Season"
SEASON_TYPE_STR_PBP = "Playoffs" if IS_PLAYOFFS else "Regular Season"
TRAIL_SUFFIX = '_ps' if IS_PLAYOFFS else ''

# ==============================================================================
# SECTION 3: GLOBAL HELPERS
# ==============================================================================

# For new_tracking.py
CATEGORY_MAPS = {
    "Drives": 'drives.csv',
    "CatchShoot": 'catchshoot.csv',
    "Passing": 'passing.csv',
    "Possessions": 'touches.csv',
    "ElbowTouch": 'elbow.csv',
    "PostTouch": 'post.csv',
    "PaintTouch": 'paint.csv',
    "PullUpShot": 'pullup.csv'
}

# For team_shooting.py
ACR_DICT = {
    'San Antonio Spurs': 'SAS', 'Miami Heat': 'MIA', 'Indiana Pacers': 'IND',
    'Oklahoma City Thunder': 'OKC', 'Los Angeles Clippers': 'LAC', 'Brooklyn Nets': 'BKN',
    'Portland Trail Blazers': 'POR', 'Washington Wizards': 'WAS', 'Atlanta Hawks': 'ATL',
    'Golden State Warriors': 'GSW', 'Dallas Mavericks': 'DAL', 'Memphis Grizzlies': 'MEM',
    'Houston Rockets': 'HOU', 'Toronto Raptors': 'TOR', 'Chicago Bulls': 'CHI',
    'Charlotte Bobcats': 'CHA', 'Cleveland Cavaliers': 'CLE', 'Milwaukee Bucks': 'MIL',
    'New Orleans Pelicans': 'NOP', 'Boston Celtics': 'BOS', 'Charlotte Hornets': 'CHA',
    'LA Clippers': 'LAC', 'Detroit Pistons': 'DET', 'Utah Jazz': 'UTA',
    'Philadelphia 76ers': 'PHI', 'Minnesota Timberwolves': 'MIN', 'Denver Nuggets': 'DEN',
    'Orlando Magic': 'ORL', 'Los Angeles Lakers': 'LAL', 'Phoenix Suns': 'PHX',
    'New York Knicks': 'NYK', 'Sacramento Kings': 'SAC'
}

NAME_DICT = {
    'SAS': 'San Antonio Spurs', 'MIA': 'Miami Heat', 'IND': 'Indiana Pacers',
    'OKC': 'Oklahoma City Thunder', 'BKN': 'Brooklyn Nets', 'POR': 'Portland Trail Blazers',
    'WAS': 'Washington Wizards', 'ATL': 'Atlanta Hawks', 'GSW': 'Golden State Warriors',
    'DAL': 'Dallas Mavericks', 'MEM': 'Memphis Grizzlies', 'HOU': 'Houston Rockets',
    'TOR': 'Toronto Raptors', 'CHI': 'Chicago Bulls', 'CLE': 'Cleveland Cavaliers',
    'MIL': 'Milwaukee Bucks', 'NOP': 'New Orleans Pelicans', 'BOS': 'Boston Celtics',
    'CHA': 'Charlotte Hornets', 'LAC': 'Los Angeles Clippers', 'DET': 'Detroit Pistons',
    'UTA': 'Utah Jazz', 'PHI': 'Philadelphia 76ers', 'MIN': 'Minnesota Timberwolves',
    'DEN': 'Denver Nuggets', 'ORL': 'Orlando Magic', 'LAL': 'Los Angeles Lakers',
    'PHX': 'Phoenix Suns', 'NYK': 'New York Knicks', 'SAC': 'Sacramento Kings'
}

# For underground.py (pbpstats)
PBP_PLAYER_COLS_SMALL = [
    'Name', 'Minutes', 'Points', 'FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct',
    'AssistPoints', 'AtRimAssists', 'ShortMidRangeAssists', 'LongMidRangeAssists',
    'Corner3Assists', 'Arc3Assists', 'LostBallSteals', 'LiveBallTurnovers',
    'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers', 'DeadBallTurnovers',
    'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers',
    'Travels', 'Turnovers', 'OffensiveGoaltends', 'FTA', 'OffPoss', 'PtsAssisted2s',
    'PtsUnassisted2s', 'PtsAssisted3s', 'PtsUnassisted3s', 'DefPoss', 'TotalPoss'
]

PBP_PLAYER_COLS_SHOTZONE = [
    'Name', 'EntityId', 'TeamId', 'TeamAbbreviation', 'GamesPlayed', 'OffPoss',
    'DefPoss', 'Minutes', 'FtPoints', 'FTA', 'AtRimFGA', 'AtRimFGM', 'AtRimAccuracy',
    'ShortMidRangeFGA', 'ShortMidRangeFGM', 'ShortMidRangeAccuracy',
    'ShortMidRangeFrequency', 'LongMidRangeFGM', 'LongMidRangeFGA', 'FG2A', 'FG2M',
    'FG3A',  'NonHeaveArc3FGA', 'HeaveAttempts', 'Corner3FGA',
    'Corner3FGM', 'NonHeaveFg3Pct', 'NonHeaveArc3FGM', 'TsPct', 'Points', 'EfgPct',
    'SecondChanceEfgPct', 'PenaltyEfgPct', 'SecondChanceTsPct', 'PenaltyTsPct',
    'SecondChanceShotQualityAvg', 'PenaltyShotQualityAvg', 'ShotQualityAvg', 'year'
]

PBP_TEAM_COLS_SHOTZONE = [
    'Name', 'EntityId', 'TeamId', 'TeamAbbreviation', 'GamesPlayed', 'OffPoss',
    'DefPoss', 'FtPoints', 'FTA', 'AtRimFGA', 'AtRimFGM', 'AtRimAccuracy',
    'ShortMidRangeFGA', 'ShortMidRangeFGM', 'ShortMidRangeAccuracy',
    'ShortMidRangeFrequency', 'LongMidRangeFGM', 'LongMidRangeFGA', 'FG2A',
    'FG2M', 'FG3A', 'NonHeaveFg3Pct', 'NonHeaveArc3FGA', 'HeaveAttempts',
    'Corner3FGA', 'Corner3FGM', 'NonHeaveArc3FGM', 'TsPct', 'Points',
    'EfgPct', 'SecondChanceEfgPct', 'PenaltyEfgPct', 'SecondChanceTsPct',
    'PenaltyTsPct', 'SecondChanceShotQualityAvg', 'PenaltyShotQualityAvg',
    'ShotQualityAvg'
]


# ==============================================================================
# SECTION 4: FUNCTION LIBRARY
# (All functions from the original files)
# ==============================================================================

# ------------------------------------------------------------------------------
# 4.1. Functions from scrape_shooting.py (Opponent) & team_shooting.py
# ------------------------------------------------------------------------------

def get_oppshots(years, ps=False):
    """
    Scrapes opponent shooting data from stats.nba.com JSON endpoint.
    (From scrape_shooting.py)
    """
    shots = ["0-2%20Feet%20-%20Very%20Tight", "2-4%20Feet%20-%20Tight", "4-6%20Feet%20-%20Open", "6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv', 'tight.csv', 'open.csv', 'wide_open.csv']
    folder = '/opp_shooting/'
    stype = "Regular%20Season"
    if ps:
        folder = '/playoffs/opp_shooting/'
        stype = "Playoffs"

    for year in years:
        i = 0
        for shot in shots:
            season = str(year) + '-' + str(year + 1 - 2000)

            part1 = "https://stats.nba.com/stats/leaguedashoppptshot?CloseDefDistRange="
            part2 = "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1 + shot + part2 + season + part3
            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }
            json_data = requests.get(url, headers=headers).json()
            data = json_data["resultSets"][0]["rowSet"]
            columns = json_data["resultSets"][0]["headers"]
            df = pd.DataFrame.from_records(data, columns=columns)
            new_columns = {
                'FG2A_FREQUENCY': '2FG FREQ%', 'FG2_PCT': '2FG%', 'FG2A': '2FGA', 'FG2M': '2FGM',
                'FG3A_FREQUENCY': '3FG FREQ%', 'FG3_PCT': '3P%', 'FG3A': '3PA', 'FG3M': '3PM',
                'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%', 'FGA_FREQUENCY': 'FREQ%',
            }
            new_columns2 = {
                'FREQ%': 'Freq%', 'TEAM_ABBREVIATION': 'TEAM', '3FG FREQ%': '3FG Freq%',
                'EFG%': 'eFG%', '2FG FREQ%': '2FG Freq%'
            }
            df = df.rename(columns=new_columns)
            df = df.rename(columns=new_columns2)
            
            df = df[['TEAM', 'GP', 'G', 'Freq%', 'FGM', 'FGA', 'FG%', 'eFG%', '2FG Freq%',
                     '2FGM', '2FGA', '2FG%', '3FG Freq%', '3PM', '3PA', '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col] *= 100
            term = terms[i]
            path_str = str(year + 1) + folder
            Path(path_str).mkdir(parents=True, exist_ok=True) # Ensure directory exists
            path = path_str + term

            df.to_csv(path, index=False)
            print(f"Saved opponent shooting: {path}")
            i += 1

def get_teamshots(years, ps=False):
    """
    Scrapes offensive team shooting data from stats.nba.com JSON endpoint.
    (From team_shooting.py)
    """
    shots = ["0-2%20Feet%20-%20Very%20Tight", "2-4%20Feet%20-%20Tight", "4-6%20Feet%20-%20Open", "6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv', 'tight.csv', 'open.csv', 'wide_open.csv']
    folder = '/team_shooting/'
    stype = "Regular%20Season"
    if ps:
        folder = '/playoffs/team_shooting/'
        stype = "Playoffs"
        
    for year in years:
        i = 0
        frames = []
        for shot in shots:
            season = str(year) + '-' + str(year + 1 - 2000)

            part1 = "https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange="
            part2 = "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1 + shot + part2 + season + part3
            
            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }
            json_data = requests.get(url, headers=headers).json()
            data = json_data["resultSets"][0]["rowSet"]
            columns = json_data["resultSets"][0]["headers"]
            df = pd.DataFrame.from_records(data, columns=columns)
            new_columns = {
                'FG2A_FREQUENCY': '2FG FREQ%', 'FG2_PCT': '2FG%', 'FG2A': '2FGA', 'FG2M': '2FGM',
                'FG3A_FREQUENCY': '3FG FREQ%', 'FG3_PCT': '3P%', 'FG3A': '3PA', 'FG3M': '3PM',
                'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%', 'FGA_FREQUENCY': 'FREQ%',
            }
            new_columns2 = {
                'FREQ%': 'Freq%', 'TEAM_ABBREVIATION': 'TEAM', '3FG FREQ%': '3FG Freq%',
                'EFG%': 'eFG%', '2FG FREQ%': '2FG Freq%'
            }
            df = df.rename(columns=new_columns)
            df = df.rename(columns=new_columns2)
            
            df = df[['TEAM', 'GP', 'G', 'Freq%', 'FGM', 'FGA', 'FG%', 'eFG%', '2FG Freq%',
                     '2FGM', '2FGA', '2FG%', '3FG Freq%', '3PM', '3PA', '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col] *= 100
            term = terms[i]
            path_str = str(year + 1) + folder
            Path(path_str).mkdir(parents=True, exist_ok=True) # Ensure directory exists
            path = path_str + term
            
            print(f"Saved team shooting: {path}")
            df.to_csv(path, index=False)
            frames.append(df)
            i += 1
        
        # This part was in team_shooting.py but not scrape_shooting.py
        # It creates an additional combined file for the year.
        year_df = pd.concat(frames)
        year_df.to_csv(str(year + 1) + folder + 'team_shooting.csv', index=False)
        print(f"Saved combined: {str(year + 1) + folder}team_shooting.csv")


# --- Unused Selenium-based functions (from original files) ---

def get_tables(url_list):
    """
    (From scrape_shooting.py - USES SELENIUM)
    """
    data = []
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
    # options = webdriver.FirefoxOptions()
    # driver = webdriver.Firefox(options=options)
    print("WARNING: get_tables uses Selenium, which is currently commented out.")
    return [] # Return empty to avoid crash
    
    for url in url_list:
        driver.get(url)
        print(url)
        driver.implicitly_wait(20)
        # element = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.XPATH, xpath)))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tables = soup.find_all('table')
        dfs = pd.read_html(str(tables))
        df = dfs[-1]
        drop = ['Unnamed: 16_level_1', 'Unnamed: 17_level_1', 'Unnamed: 18_level_1']
        df.columns = df.columns.droplevel()
        df = df.drop(columns=drop)
        data.append(df)
    driver.close()
    return data

def get_multi_opp_shooting_selenium(url_list, playoffs=False):
    """
    (From scrape_shooting.py - USES SELENIUM)
    """
    if playoffs:
        p = '/playoffs'
    else:
        p = ''

    for i in range(2024, 2025):
        season = '&Season=' + str(i) + '-' + str(i + 1 - 2000)
        year_url = [url + season for url in url_list]
        frames = get_tables(year_url) # Requires Selenium
        path = str(i + 1) + p + '/opp_shooting/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        terms = ['very_tight.csv', 'tight.csv', 'open.csv', 'wide_open.csv']
        terms = [path + t for t in terms]
        for i in range(len(terms)):
            df = frames[i]
            df.to_csv(terms[i], index=False)

def multiyear_shooting_selenium(url_list, team_round=0, playoffs=True):
    """
    (From team_shooting.py - USES SELENIUM)
    """
    df_list = []
    start_year = 2023
    for i in range(start_year, 2024):
        year = i + 1
        season = '&Season=' + str(i) + '-' + str(i + 1 - 2000)
        year_url = [url + season for url in url_list]
        if team_round != 0:
            year_url = [url + '&PORound=' + str(team_round) for url in year_url]
        
        frames = get_tables(year_url) # Requires Selenium

        path = str(i + 1) + '/playoff_shooting/round' + str(team_round) + '/'
        if playoffs == False:
            path = str(i + 1) + '/team_shooting/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        terms = ['very_tight', 'tight', 'open', 'wide_open']

        for k in range(len(terms)):
            frames[k]['shot_coverage'] = terms[k]
            if playoffs:
                frames[k]['round'] = team_round
            frames[k]['year'] = year
        df = pd.concat(frames)
        df.to_csv(path + 'team_shooting.csv', index=False)
        df_list.append(df)
        
    new_df = pd.concat(df_list)
    new_df['TEAMNAME'] = new_df['TEAM']
    df = pd.read_csv('team_shooting.csv')
    df = df[df.year <= start_year]
    names = dict(zip(df.TEAMNAME, df.TEAM))
    names['Los Angeles Clippers'] = 'LAC'
    names['Charlotte Bobcats'] = 'CHA'

    final_df = pd.concat([df, new_df])
    final_df.replace({'TEAM': names}, inplace=True)
    final_df.loc[final_df['TEAMNAME'] == 'Los Angeles Clippers', 'TEAM'] = 'LAC'
    final_df.loc[final_df['TEAMNAME'] == 'Charlotte Bobcats', 'TEAM'] = 'CHA'
    return final_df

# ------------------------------------------------------------------------------
# 4.2. Functions from player_shooting.py
# ------------------------------------------------------------------------------

def get_playershots(years, ps=False):
    """
    Scrapes player shooting data from stats.nba.com JSON endpoint.
    (From player_shooting.py)
    """
    shots = ["0-2%20Feet%20-%20Very%20Tight", "2-4%20Feet%20-%20Tight", "4-6%20Feet%20-%20Open", "6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv', 'tight.csv', 'open.csv', 'wide_open.csv']
    folder = '/player_shooting/'
    sfolder = ''
    stype = "Regular%20Season"
    if ps:
        stype = "Playoffs"
        sfolder = "/playoffs"
        
    for year in years:
        i = 0
        for shot in shots:
            season = str(year) + '-' + str(year + 1 - 2000)
            part1 = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange="
            part2 = "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1 + shot + part2 + season + part3
            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }
            json_data = requests.get(url, headers=headers).json()
            data = json_data["resultSets"][0]["rowSet"]
            columns = json_data["resultSets"][0]["headers"]
            df = pd.DataFrame.from_records(data, columns=columns)
            new_columns = {
                'FG2A_FREQUENCY': '2FG FREQ%', 'FG2_PCT': '2FG%', 'FG2A': '2FGA', 'FG2M': '2FGM',
                'FG3A_FREQUENCY': '3FG FREQ%', 'FG3_PCT': '3P%', 'FG3A': '3PA', 'FG3M': '3PM',
                'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%', 'FGA_FREQUENCY': 'FREQ%',
                'PLAYER_NAME': 'PLAYER', 'PLAYER_LAST_TEAM_ABBREVIATION': 'TEAM'
            }
            df = df.rename(columns=new_columns)
            
            df = df[['PLAYER_ID', 'PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'FREQ%', 'FGM', 'FGA', 'FG%',
                     'EFG%', '2FG FREQ%', '2FGM', '2FGA', '2FG%', '3FG FREQ%', '3PM', '3PA',
                     '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col] *= 100
            term = terms[i]
            
            path_str = str(year + 1) + sfolder + folder
            Path(path_str).mkdir(parents=True, exist_ok=True) # Ensure directory exists
            path = path_str + term
            
            df.to_csv(path, index=False)
            print(f"Saved player shooting: {path}")
            i += 1

def master_shooting(playoffs=False):
    """
    Compiles all individual player shooting CSVs into a master file.
    (From player_shooting.py)
    """
    data = []
    p = '/playoffs' if playoffs else ''
    
    # Reads folders from 2014 up to and including the latest season end year
    for i in range(2014, SEASON_END_YEAR + 1): 
        path = str(i) + p + '/player_shooting/'
        files = ['wide_open', 'open', 'tight', 'very_tight']
        for file in files:
            try:
                df = pd.read_csv(path + file + '.csv')
                df['year'] = i
                df['shot_type'] = file
                data.append(df)
            except FileNotFoundError:
                print(f"Warning: File not found and skipped: {path + file + '.csv'}")
                
    if not data:
        print("No data found to compile for master_shooting.")
        return pd.DataFrame()
        
    master = pd.concat(data)
    return master

# ------------------------------------------------------------------------------
# 4.3. Functions from hustle.py
# ------------------------------------------------------------------------------

def get_hustle(year, ps=False):
    """
    Fetches hustle, speed/distance, and advanced stats for a given *season end year*.
    (From hustle.py)
    """
    stype = "Playoffs" if ps else "Regular%20Season"
    
    # 'year' is season end year (e.g., 2025). API needs start year (2024).
    season = str(year - 1) + '-' + str(year)[-2:]
    
    url_hustle = f'https://stats.nba.com/stats/leaguehustlestatsplayer?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&TeamID=0&VsConference=&VsDivision=&Weight='
    url_speed = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=SpeedDistance&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
    url_advanced = f"https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
    
    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }

    print(f"Fetching hustle stats for {season} {stype}...")
    json_hustle = requests.get(url_hustle, headers=headers).json()
    data_hustle = json_hustle["resultSets"][0]["rowSet"]
    columns_hustle = json_hustle["resultSets"][0]["headers"]
    df_hustle = pd.DataFrame(data_hustle, columns=columns_hustle)
    
    time.sleep(2)
    
    print(f"Fetching speed/distance stats for {season} {stype}...")
    json_speed = requests.get(url_speed, headers=headers).json()
    data_speed = json_speed["resultSets"][0]["rowSet"]
    columns_speed = json_speed["resultSets"][0]["headers"]
    df_speed = pd.DataFrame(data_speed, columns=columns_speed)
    
    time.sleep(2)

    print(f"Fetching advanced (possessions) stats for {season} {stype}...")
    json_adv = requests.get(url_advanced, headers=headers).json()
    data_adv = json_adv["resultSets"][0]["rowSet"]
    columns_adv = json_adv["resultSets"][0]["headers"]
    df_adv = pd.DataFrame(data_adv, columns=columns_adv)

    # Combine the dataframes
    if 'MIN' in df_hustle.columns:
        df_hustle.drop(columns=['MIN'], inplace=True)
    
    df_adv = df_adv[['PLAYER_ID', 'POSS']]

    # Get unique columns from df_speed
    collist = [col for col in df_speed.columns if col not in df_hustle.columns]
    collist.append('PLAYER_ID')
    df_speed_unique = df_speed[collist]
    
    combo_df = df_hustle.merge(df_speed_unique, on=['PLAYER_ID'])
    combo_df = combo_df.merge(df_adv, on=['PLAYER_ID'])
    combo_df['year'] = year # Save with season end year
    
    print(f"Fetched {len(combo_df)} records for hustle.")
    return combo_df

# ------------------------------------------------------------------------------
# 4.4. Functions from new_tracking.py
# ------------------------------------------------------------------------------

def get_tracking(years, ps=False):
    """
    Fetches various tracking stats categories for a list of *start years*.
    (From new_tracking.py)
    """
    stype = "Playoffs" if ps else "Regular%20Season"
    
    shots = ["Drives", "CatchShoot", "Passing", "Possessions", "ElbowTouch", "PostTouch", "PaintTouch", "PullUpShot"]
    
    # Dictionary to store dataframes for each shot category
    category_frames = {shot: [] for shot in shots}

    for year in years:
        season = str(year) + '-' + str(year + 1 - 2000)
        print(f"Fetching tracking data for {season} {stype}...")

        for shot in shots:
            part1 = "https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType="
            part2 = "&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
            
            url = part1 + shot + part2 + season + part3

            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }

            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    json_data = response.json()
                    data = json_data["resultSets"][0]["rowSet"]
                    columns = json_data["resultSets"][0]["headers"]
                    df = pd.DataFrame.from_records(data, columns=columns)
                    df["Season"] = season  # Add season column
                    df['year'] = year + 1 # Save with season end year
                    category_frames[shot].append(df)
                    print(f"  - Fetched {shot}")
                else:
                    print(f"Failed to retrieve data for shot type {shot} in season {season}")
            except Exception as e:
                print(f"Error fetching {shot} for {season}: {e}")
            
            time.sleep(2) # Be courteous

    return category_frames

# ------------------------------------------------------------------------------
# 4.5. Functions from dribble.py
# ------------------------------------------------------------------------------

def get_dribbleshots(years, ps=False):
    """
    Scrapes player shooting data by dribbles.
    (From dribble.py)
    """
    dribbles = ['0%20Dribbles', '1%20Dribble', '2%20Dribbles', '3-6%20Dribbles', '7%2B%20Dribbles']
    terms = ['0', '1', '2', '3_6', '7+']
    stype = "Playoffs" if ps else "Regular%20Season"
    
    dataframe = []
    for year in years:
        i = 0
        for dribble in dribbles:
            season = str(year) + '-' + str(year + 1 - 2000)
            print(f"Fetching dribble shots for {season} {stype} - {terms[i]} dribbles")
            
            part1 = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange="
            part2 = "&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1 + dribble + part2 + season + part3
            
            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }
            
            try:
                json_data = requests.get(url, headers=headers).json()
                data = json_data["resultSets"][0]["rowSet"]
                columns = json_data["resultSets"][0]["headers"]
                df = pd.DataFrame.from_records(data, columns=columns)
                
                new_columns = {
                    'FG2A_FREQUENCY': '2FG FREQ%', 'FG2_PCT': '2FG%', 'FG2A': '2FGA', 'FG2M': '2FGM',
                    'FG3A_FREQUENCY': '3FG FREQ%', 'FG3_PCT': '3P%', 'FG3A': '3PA', 'FG3M': '3PM',
                    'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%', 'FGA_FREQUENCY': 'FREQ%',
                    'PLAYER_NAME': 'PLAYER', 'PLAYER_LAST_TEAM_ABBREVIATION': 'TEAM'
                }
                df = df.rename(columns=new_columns)
                df = df[['PLAYER_ID', 'PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'FREQ%', 'FGM', 'FGA', 'FG%',
                         'EFG%', '2FG FREQ%', '2FGM', '2FGA', '2FG%', '3FG FREQ%', '3PM', '3PA', '3P%']]
                
                for col in df.columns:
                    if '%' in col or 'PERC' in col:
                        df[col] *= 100
                
                term = terms[i]
                df['dribbles'] = term
                df['year'] = year + 1 # Save with season end year
                dataframe.append(df)
            except Exception as e:
                print(f"Error fetching dribble data: {e}")

            time.sleep(1)
            i += 1
            
    return pd.concat(dataframe) if dataframe else pd.DataFrame()

def master_dribble(year, ps=False):
    """
    Updates the master dribble shot file for a given *start year*.
    (From dribble.py)
    """
    trail = '_ps' if ps else ''
    filename = f'dribbleshot{trail}.csv'
    
    try:
        old = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"{filename} not found, creating new file.")
        old = pd.DataFrame()

    df = get_dribbleshots([year], ps=ps) # Pass start year
    
    season_end_year = year + 1 # Data is saved with end year
    
    old = old[old.year != season_end_year] # Remove year being updated
    new_master = pd.concat([old, df])
    new_master.to_csv(filename, index=False)
    print(f"Updated {filename}")
    return new_master

def get_dribbleshots2(years, ps=False):
    """
    Scrapes player catch & shoot AND pullup data by dribbles.
    (From dribble.py)
    """
    dribbles = ['0%20Dribbles', '1%20Dribble', '2%20Dribbles', '3-6%20Dribbles', '7%2B%20Dribbles']
    terms = ['0', '1', '2', '3_6', '7+']
    stype = "Playoffs" if ps else "Regular%20Season"
    
    dataframe = []
    for year in years:
        i = 0
        for dribble in dribbles:
            season = str(year) + '-' + str(year + 1 - 2000)
            print(f"Fetching C&S/Pullup for {season} {stype} - {terms[i]} dribbles")
            
            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }
            
            # --- Catch and Shoot ---
            part1_cs = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange="
            part2_cs = "&GameScope=&GameSegment=&GeneralRange=Catch%20and%20Shoot&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3_cs = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url_cs = part1_cs + dribble + part2_cs + season + part3_cs
            
            try:
                json_cs = requests.get(url_cs, headers=headers).json()
                data_cs = json_cs["resultSets"][0]["rowSet"]
                columns_cs = json_cs["resultSets"][0]["headers"]
                df_cs = pd.DataFrame.from_records(data_cs, columns=columns_cs)
            except Exception as e:
                print(f"  - Error fetching C&S data: {e}")
                df_cs = pd.DataFrame() # Create empty
                
            time.sleep(2)

            # --- Pullups ---
            part1_pull = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange="
            part2_pull = "&GameScope=&GameSegment=&GeneralRange=Pullups&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="
            part3_pull = "&SeasonSegment=&SeasonType=" + stype + "&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url_pull = part1_pull + dribble + part2_pull + season + part3_pull
            
            try:
                json_pull = requests.get(url_pull, headers=headers).json()
                data_pull = json_pull["resultSets"][0]["rowSet"]
                columns_pull = json_pull["resultSets"][0]["headers"]
                df_pull = pd.DataFrame.from_records(data_pull, columns=columns_pull)
            except Exception as e:
                print(f"  - Error fetching Pullup data: {e}")
                df_pull = pd.DataFrame() # Create empty

            time.sleep(2)

            # --- Process Both ---
            new_columns = {
                'FG2A_FREQUENCY': '2FG FREQ%', 'FG2_PCT': '2FG%', 'FG2A': '2FGA', 'FG2M': '2FGM',
                'FG3A_FREQUENCY': '3FG FREQ%', 'FG3_PCT': '3P%', 'FG3A': '3PA', 'FG3M': '3PM',
                'EFG_PCT': 'EFG%', 'FG_PCT': 'FG%', 'FGA_FREQUENCY': 'FREQ%',
                'PLAYER_NAME': 'PLAYER', 'PLAYER_LAST_TEAM_ABBREVIATION': 'TEAM'
            }
            
            cols_to_keep = ['PLAYER_ID', 'PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'FREQ%', 'FGM', 'FGA', 'FG%',
                            'EFG%', '2FG FREQ%', '2FGM', '2FGA', '2FG%', '3FG FREQ%', '3PM', '3PA', '3P%']
            
            term = terms[i]

            if not df_cs.empty:
                df_cs = df_cs.rename(columns=new_columns)
                df_cs = df_cs[cols_to_keep]
                for col in df_cs.columns:
                    if '%' in col or 'PERC' in col:
                        df_cs[col] *= 100
                df_cs['dribbles'] = term
                df_cs['year'] = year + 1 # Save with season end year
                dataframe.append(df_cs)
                
            if not df_pull.empty:
                df_pull = df_pull.rename(columns=new_columns)
                df_pull = df_pull[cols_to_keep]
                for col in df_pull.columns:
                    if '%' in col or 'PERC' in col:
                        df_pull[col] *= 100
                df_pull['dribbles'] = term
                df_pull['year'] = year + 1 # Save with season end year
                dataframe.append(df_pull)
            
            i += 1
            
    return pd.concat(dataframe) if dataframe else pd.DataFrame()

def master_jump(year, ps=False):
    """
    Updates the master jump shot file for a given *start year*.
    (From dribble.py)
    """
    trail = '_ps' if ps else ''
    filename = f'jumpdribble{trail}.csv'

    try:
        old = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"{filename} not found, creating new file.")
        old = pd.DataFrame()

    df = get_dribbleshots2([year], ps=ps) # Pass start year
    
    if df.empty:
        print(f"No new data for jumpdribble, skipping update for {filename}")
        return old

    data_col = ['FGM', 'FGA', '2FGM', '2FGA', '3PM', '3PA']
    for col in data_col:
        df[col] = df[col].astype(int)

    # Group C&S and Pullups together
    df2 = df.groupby(['PLAYER_ID', 'PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'dribbles', 'year']).sum(numeric_only=True).reset_index()

    season_end_year = year + 1 # Data is saved with end year

    old = old[old.year != season_end_year] # Remove year being updated
    old = old.dropna(subset='year')
    
    new_master = pd.concat([old, df2])
    new_master.to_csv(filename, index=False)
    print(f"Updated {filename}")
    return new_master

# ------------------------------------------------------------------------------
# 4.6. Functions from misc.py (Playtypes)
# ------------------------------------------------------------------------------

def get_playtypes(years, ps=False, p_or_t='t', defense=False):
    """
    Fetches play-by-play data from the NBA stats API for specified *start years*.
    (From misc.py)
    """
    field_side = "offensive"
    if defense:
        field_side = "defensive"
    
    entity_type = 'T'
    if p_or_t.lower() == 'p':
        entity_type = 'P'

    season_type = "Playoffs" if ps else "Regular+Season"

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
        print(f"Fetching playtype data for {season_str} {season_type} ({field_side}, {entity_type})...")

        for play, play_name in zip(playtypes, plays):
            url = (
                f"https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode=Totals&PlayType={play}"
                f"&PlayerOrTeam={entity_type}&SeasonType={season_type}&SeasonYear={season_str}"
                f"&TypeGrouping={field_side}"
            )
            
            print(f"  - Fetching {play_name} data...")
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
                df['year'] = year + 1 # Save with season end year
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
        team_dict = NAME_DICT # Use global helper
        full_data.rename(columns={'PTS': 'Points', 'TEAM': 'full_name'}, inplace=True)
        full_data['Team'] = full_data['TEAM_ABBREVIATION']
    
    return full_data

def update_master_file(year, file_path, fetch_function, **fetch_kwargs):
    """
    Updates a master CSV file with new data for a given *season end year*.
    (From misc.py)
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
        
        is_player_data = 'PLAYER_ID' in new_data.columns and fetch_kwargs.get('p_or_t', 't').lower() == 'p'
        
        if is_player_data:
            print(f"Applying refined player data logic for {file_path}...")
            
            existing_year_data = old_data[old_data.year == year].copy()
            print(f"Found {len(existing_year_data)} existing records for year {year}")
            
            old_data_without_year = old_data[old_data.year != year]
            
            new_combinations = set(zip(new_data['PLAYER_ID'], new_data['playtype']))
            existing_combinations = set(zip(existing_year_data['PLAYER_ID'], existing_year_data['playtype']))
            
            missing_combinations = existing_combinations - new_combinations
            print(f"Found {len(missing_combinations)} player-playtype combinations to preserve from existing data")
            
            if missing_combinations and not existing_year_data.empty:
                missing_mask = existing_year_data.apply(
                    lambda row: (row['PLAYER_ID'], row['playtype']) in missing_combinations, 
                    axis=1
                )
                preserved_data = existing_year_data[missing_mask]
                print(f"Preserving {len(preserved_data)} records from existing data")
            else:
                preserved_data = pd.DataFrame()
            
            frames_to_combine = [old_data_without_year, new_data]
            if not preserved_data.empty:
                frames_to_combine.append(preserved_data)
            
            combined_data = pd.concat(frames_to_combine, ignore_index=True)
            print(f"Final dataset has {len(combined_data)} total records")
            
        else:
            # Original logic for team data
            old_data_without_year = old_data[old_data.year != year]
            combined_data = pd.concat([old_data_without_year, new_data], ignore_index=True)
            
    except FileNotFoundError:
        print(f"{file_path} not found. Creating a new file.")
        combined_data = new_data

    combined_data.sort_values(by='year', inplace=True)
    combined_data.to_csv(file_path, index=False)
    print(f"Successfully updated {file_path}.")

def generate_and_update_playstyle(year, ps=False):
    """
    Generates playstyle summaries for a *season end year* and updates the master file.
    (From misc.py)
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

# ------------------------------------------------------------------------------
# 4.7. Functions from underground.py (PBPStats)
# ------------------------------------------------------------------------------

def team_shotzone(year, ps=False, vs=False):
    """
    Fetches team shotzone data from pbpstats API for a given *start year*.
    (From underground.py)
    """
    stype = "Playoffs" if ps else "Regular Season"
    season = str(year) + '-' + str(year + 1)[-2:]
    
    dtype = "Team"
    if vs:
        dtype = "Opponent"
        
    print(f"Fetching pbpstats team shotzone for {season} {stype} (Type: {dtype})")
    
    url = "https://api.pbpstats.com/get-totals/nba"
    params = {
        "Season": season,
        "SeasonType": stype,
        "Type": dtype
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_json = response.json()
        player_stats = response_json["multi_row_table_data"]
        time.sleep(2)

        df = pd.DataFrame(player_stats)
        shotzone = df[PBP_TEAM_COLS_SHOTZONE].reset_index(drop=True)
        shotzone['year'] = year + 1 # Save with season end year
        return shotzone.reset_index(drop=True)
    except Exception as e:
        print(f"Error fetching pbpstats team shotzone: {e}")
        return pd.DataFrame()


def update_team(year, ps=False, vs=False):
    """
    Updates the master team shotzone file for a given *start year*.
    (From underground.py)
    """
    trail = ''
    if vs:
        trail = '_vs'
    if ps:
        trail += '_ps'
        
    filename = f'team_shotzone{trail}.csv'
    
    teamdf = team_shotzone(year, ps=ps, vs=vs) # Pass start year
    if teamdf.empty:
        print(f"No new data for {filename}, skipping update.")
        return

    season_end_year = year + 1 # Data is saved with end year
    
    try:
        old_df = pd.read_csv(filename)
        old_df = old_df[old_df.year != season_end_year].reset_index(drop=True)
    except FileNotFoundError:
        print(f"{filename} not found, creating new file.")
        old_df = pd.DataFrame()
        
    new_df = pd.concat([old_df, teamdf])
    new_df.to_csv(filename, index=False)
    print(f"Updated {filename}")
    return new_df


# ==============================================================================
# SECTION 5: MASTER EXECUTION WRAPPERS
# (These functions organize the calls based on the central config)
# ==============================================================================

def run_team_and_opp_shooting_updates(year_to_scrape, season_end_year, ps):
    """
    Executes all logic from team_shooting.py and scrape_shooting.py
    """
    print("\n--- [STARTING] Team & Opponent Shooting ---")
    
    # 1. Scrape new data for offensive team shooting
    print("Fetching offensive team shooting...")
    get_teamshots([year_to_scrape], ps=ps)
    
    # 2. Scrape new data for opponent team shooting
    print("Fetching opponent team shooting...")
    get_oppshots([year_to_scrape], ps=ps)
    
    # 3. Re-compile all 4 master files
    print("Compiling all master team/opponent shooting files...")
    shots = ['wide_open', 'open', 'tight', 'very_tight']
    year_range = range(2014, season_end_year + 1) # 2014 to current

    # --- Opponent Regular Season ---
    frames_opp_rs = []
    for year in year_range:
        path = f"{year}/opp_shooting/"
        for shot in shots:
            filepath = path + shot + '.csv'
            try:
                df = pd.read_csv(filepath)
                df['shot_coverage'] = shot
                df['year'] = year
                if year < 2024:
                    df['TEAM'] = df['TEAM'].map(ACR_DICT)
                df['TEAMNAME'] = df['TEAM'].map(NAME_DICT)
                frames_opp_rs.append(df)
            except FileNotFoundError:
                print(f"Skipping not found: {filepath}")
    if frames_opp_rs:
        opp_master_rs = pd.concat(frames_opp_rs)
        opp_master_rs.to_csv('opp_team_shooting.csv', index=False)
        print("Updated opp_team_shooting.csv")

    # --- Opponent Playoffs ---
    frames_opp_ps = []
    for year in year_range:
        path = f"{year}/playoffs/opp_shooting/"
        for shot in shots:
            filepath = path + shot + '.csv'
            try:
                df = pd.read_csv(filepath)
                df['shot_coverage'] = shot
                df['year'] = year
                if year < 2024:
                    df['TEAM'] = df['TEAM'].map(ACR_DICT)
                df['TEAMNAME'] = df['TEAM'].map(NAME_DICT)
                frames_opp_ps.append(df)
            except FileNotFoundError:
                print(f"Skipping not found: {filepath}")
    if frames_opp_ps:
        opp_master_ps = pd.concat(frames_opp_ps)
        opp_master_ps.to_csv('opp_team_shooting_ps.csv', index=False)
        print("Updated opp_team_shooting_ps.csv")

    # --- Team Regular Season ---
    frames_team_rs = []
    for year in year_range:
        path = f"{year}/team_shooting/"
        for shot in shots:
            filepath = path + shot + '.csv'
            try:
                df = pd.read_csv(filepath)
                df['shot_coverage'] = shot
                df['year'] = year
                if year < 2024:
                    df['TEAM'] = df['TEAM'].map(ACR_DICT)
                df['TEAMNAME'] = df['TEAM'].map(NAME_DICT)
                frames_team_rs.append(df)
            except FileNotFoundError:
                print(f"Skipping not found: {filepath}")
    if frames_team_rs:
        master_rs = pd.concat(frames_team_rs)
        master_rs.to_csv('team_shooting.csv', index=False)
        print("Updated team_shooting.csv")

    # --- Team Playoffs ---
    frames_team_ps = []
    for year in year_range:
        path = f"{year}/playoffs/team_shooting/"
        for shot in shots:
            filepath = path + shot + '.csv'
            try:
                df = pd.read_csv(filepath)
                df['shot_coverage'] = shot
                df['year'] = year
                if year < 2024:
                    df['TEAM'] = df['TEAM'].map(ACR_DICT)
                df['TEAMNAME'] = df['TEAM'].map(NAME_DICT)
                frames_team_ps.append(df)
            except FileNotFoundError:
                print(f"Skipping not found: {filepath}")
    if frames_team_ps:
        master_ps = pd.concat(frames_team_ps)
        master_ps.to_csv('team_shooting_ps.csv', index=False)
        print("Updated team_shooting_ps.csv")
    
    print("--- [FINISHED] Team & Opponent Shooting ---")

def run_player_shooting_updates(year_to_scrape, ps):
    """
    Executes all logic from player_shooting.py
    """
    print("\n--- [STARTING] Player Shooting ---")
    
    # 1. Scrape new data and save to year-specific folder
    get_playershots([year_to_scrape], ps=ps) # Scrapes 2024-25, saves to '2025/' folder
    
    # 2. Re-compile master file
    print("Compiling Master Player Shooting file...")
    master = master_shooting(playoffs=ps) # Reads all folders including '2025/'
    
    if not master.empty:
        suffix = '_p' if ps else ''
        filename = f'player_shooting{suffix}.csv'
        master.to_csv(filename, index=False)
        print(f"Saved {filename}")
        
    print("--- [FINISHED] Player Shooting ---")
    
def run_hustle_updates(season_end_year, ps):
    """
    Executes all logic from hustle.py
    """
    print("\n--- [STARTING] Hustle Stats ---")
    
    trail = '_ps' if ps else ''
    filename = f'hustle{trail}.csv'
    
    data_rs = []
    try:
        old_df = pd.read_csv(filename)
        old_df = old_df[old_df.year < season_end_year] # Use config year
        data_rs.append(old_df)
    except FileNotFoundError:
        print(f"{filename} not found, creating new file.")
    
    # Scrape only the target year
    df = get_hustle(season_end_year, ps=ps) # year=2025 scrapes 2024-25
    
    if not df.empty:
        data_rs.append(df)
        hustle = pd.concat(data_rs)
        hustle.to_csv(filename, index=False)
        print(f"Updated {filename}")
    else:
        print(f"No new hustle data found. {filename} not updated.")

    print("--- [FINISHED] Hustle Stats ---")

def run_tracking_updates(year_to_scrape, season_end_year, ps):
    """
    Executes all logic from new_tracking.py
    """
    print("\n--- [STARTING] Player Tracking Stats ---")
    
    # 1. Fetch new data for the single year
    category_frames = get_tracking([year_to_scrape], ps=ps)
    
    file_prefix = 'tracking_ps/' if ps else 'tracking/'
    Path(file_prefix).mkdir(parents=True, exist_ok=True) # Ensure directory exists

    for cat in category_frames.keys():
        file = file_prefix + CATEGORY_MAPS[cat]
        
        if not category_frames[cat]:
            print(f"No new data for {cat}, skipping {file}")
            continue
            
        new_df = pd.concat(category_frames[cat])

        # 3. Load old data and remove the year we are updating
        try:
            old_df = pd.read_csv(file)
            old_df = old_df[old_df.year != season_end_year] 
        except FileNotFoundError:
            print(f"{file} not found, creating new file.")
            old_df = pd.DataFrame()

        # 4. Combine and save
        df = pd.concat([old_df, new_df])
        df.sort_values(by='year', inplace=True)
        df.to_csv(file, index=False)
        print(f"Updated {file}")
        
    print("--- [FINISHED] Player Tracking Stats ---")

def run_dribble_updates(year_to_scrape, ps):
    """
    Executes all logic from dribble.py
    """
    print("\n--- [STARTING] Dribble Shooting ---")
    
    # 1. Update master dribble file
    print("Updating general dribble shots...")
    master_dribble(year_to_scrape, ps=ps)
    
    # 2. Update master jump shot (C&S / Pullup) by dribble file
    print("Updating jump shot dribble shots...")
    master_jump(year_to_scrape, ps=ps)
    
    print("--- [FINISHED] Dribble Shooting ---")

def run_playtype_updates(season_end_year, ps):
    """
    Executes all logic from misc.py
    """
    print("\n--- [STARTING] Play Type Stats ---")
    
    if ps:
        # --- PLAYOFFS ---
        print("Updating player playtype (Playoffs)...")
        update_master_file(season_end_year, 'playtype_p.csv', get_playtypes, p_or_t='p', ps=True)
        
        print("Updating team playtype (Playoffs Off)...")
        update_master_file(season_end_year, 'teamplay_p.csv', get_playtypes, p_or_t='t', ps=True, defense=False)
        print("Updating team playtype (Playoffs Def)...")
        update_master_file(season_end_year, 'teamplayd_p.csv', get_playtypes, p_or_t='t', ps=True, defense=True)

        print("Generating playstyle (Playoffs)...")
        generate_and_update_playstyle(season_end_year, ps=True)
    else:
        # --- REGULAR SEASON ---
        print("Updating player playtype (Reg)...")
        update_master_file(season_end_year, 'playtype.csv', get_playtypes, p_or_t='p', ps=False)

        print("Updating team playtype (Reg Off)...")
        update_master_file(season_end_year, 'teamplay.csv', get_playtypes, p_or_t='t', ps=False, defense=False)
        print("Updating team playtype (Reg Def)...")
        update_master_file(season_end_year, 'teamplayd.csv', get_playtypes, p_or_t='t', ps=False, defense=True)

        print("Generating playstyle (Reg)...")
        generate_and_update_playstyle(season_end_year, ps=False)
        
    print("--- [FINISHED] Play Type Stats ---")

def run_underground_updates(year_to_scrape, season_str, season_end_year, ps):
    """
    Executes all logic from underground.py
    """
    print("\n--- [STARTING] Underground (PBPStats) ---")
    
    season_type = "Playoffs" if ps else "Regular Season"
    trail = '_ps' if ps else ''
    
    # 1. Player Stats Update
    print(f"Fetching pbpstats player totals for {season_str} {season_type}...")
    url = "https://api.pbpstats.com/get-totals/nba"
    params = {
        "Season": season_str,
        "SeasonType": season_type,
        "Type": "Player"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_json = response.json()
        player_stats = response_json["multi_row_table_data"]
        time.sleep(2)
        df = pd.DataFrame(player_stats)
    except Exception as e:
        print(f"Failed to get PBPStats player data: {e}. Skipping...")
        df = pd.DataFrame()

    if not df.empty:
        # Save small and large files
        Path('wowy/').mkdir(parents=True, exist_ok=True)
        df[PBP_PLAYER_COLS_SMALL].to_csv(f'wowy/player_small{trail}.csv', index=False)
        df.to_csv(f'wowy/player_large{trail}.csv', index=False)
        print(f"Saved wowy/player_small{trail}.csv and wowy/player_large{trail}.csv")

        # Update player shotzone
        df['year'] = season_end_year
        # Filter df columns to only those in PBP_PLAYER_COLS_SHOTZONE
        cols_to_use = [col for col in PBP_PLAYER_COLS_SHOTZONE if col in df.columns]
        shotzone = df[cols_to_use]
        
        shotzone_filename = f'shotzone{trail}.csv'
        try:
            old = pd.read_csv(shotzone_filename)
            old = old.rename(columns={'NonHeaveFg3Pct.1': 'NonHeaveFg3Pct'})
            old = old[old.year < season_end_year]
        except FileNotFoundError:
            print(f"{shotzone_filename} not found, creating new file.")
            old = pd.DataFrame()
            
        master = pd.concat([old, shotzone])
        master.to_csv(shotzone_filename, index=False)
        print(f"Updated {shotzone_filename}")
        
        # 2. Update Possessions file
        print("Updating possessions file...")
        poss = pd.read_csv(shotzone_filename)
        poss = poss[['EntityId', 'OffPoss', 'DefPoss', 'year']]
        poss.rename(columns={'EntityId': 'PLAYER_ID'}, inplace=True)
        poss['Poss'] = poss['OffPoss'] + poss['DefPoss']
        poss.to_csv(f'poss{trail}.csv', index=False)
        print(f"Updated poss{trail}.csv")

    # 3. Team Shotzone Updates
    print("Updating team shotzone (for)...")
    update_team(year_to_scrape, ps=ps, vs=False)
    print("Updating team shotzone (vs)...")
    update_team(year_to_scrape, ps=ps, vs=True)
    
    print("--- [FINISHED] Underground (PBPStats) ---")
    

# ==============================================================================
# SECTION 6: MAIN EXECUTION BLOCK
# ==============================================================================

def main():
    """
    Main function to run all scraping tasks based on the central configuration.
    """
    print(f"--- STARTING MASTER SCRAPE ---")
    print(f"Season: {SEASON_STR_NBA}")
    print(f"Type: {SEASON_TYPE_STR_PBP}")
    print(f"---------------------------------")

    # Run Team & Opponent Shooting (from team_shooting.py, scrape_shooting.py)
    # This scrapes new data AND recompiles the master files
    run_team_and_opp_shooting_updates(YEAR_TO_SCRAPE, SEASON_END_YEAR, IS_PLAYOFFS)

    # Run Player Shooting (from player_shooting.py)
    # This scrapes new data AND recompiles the master file
    run_player_shooting_updates(YEAR_TO_SCRAPE, IS_PLAYOFFS)

    # Run Hustle Stats (from hustle.py)
    # This scrapes new data AND updates the master file
    run_hustle_updates(SEASON_END_YEAR, IS_PLAYOFFS)

    # Run Player Tracking (from new_tracking.py)
    # This scrapes new data AND updates the master files
    run_tracking_updates(YEAR_TO_SCRAPE, SEASON_END_YEAR, IS_PLAYOFFS)

    # Run Dribble Stats (from dribble.py)
    # This scrapes new data AND updates the master files
    run_dribble_updates(YEAR_TO_SCRAPE, IS_PLAYOFFS)

    # Run Play Type Stats (from misc.py)
    # This scrapes new data AND updates all master files (player/team, off/def)
    run_playtype_updates(SEASON_END_YEAR, IS_PLAYOFFS)

    # Run PBPStats (from underground.py)
    # This scrapes new data AND updates all master files (player/team)
    run_underground_updates(YEAR_TO_SCRAPE, SEASON_STR_NBA, SEASON_END_YEAR, IS_PLAYOFFS)

    print(f"\n---------------------------------")
    print(f"--- MASTER SCRAPE COMPLETE ---")
    print(f"All files updated for {SEASON_STR_NBA} {SEASON_TYPE_STR_PBP}.")
    print(f"---------------------------------")


if __name__ == "__main__":
    main()