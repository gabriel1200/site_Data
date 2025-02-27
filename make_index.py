#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup,Comment
import pandas as pd
import time
import os
import sys
import unicodedata
import re
# URL of the NBA awards page
import numpy as np
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.static import players,teams

# Get current season year in the format "2023-24" for example

# URL of the NBA awards page
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup


def pull_bref(ps=False,totals=False):
    leagues = "playoffs" if ps else "leagues"
    frames = []
    for year in range(2025, 2026):
        if totals ==True:
            url = f"https://www.basketball-reference.com/{leagues}/NBA_{year}_totals.html"
            pt_index=28
        else:
            url = f"https://www.basketball-reference.com/{leagues}/NBA_{year}_per_poss.html"
            pt_index=28
        print(url)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the specific table
        table = soup.find('table')
        
        # Get all rows from the table body
        rows = table.find('tbody').find_all('tr')
        
        # Define the data structure to store extracted rows
        data = []
        for row in rows:
            cells = row.find_all('td')
            if cells:
                # Extract player name, url, team, and stats required
                player_cell = cells[0]
                player_name = player_cell.text if player_cell.text else "N/A"  # Player name
                player_url = "https://www.basketball-reference.com" + player_cell.a['href'] if player_cell.a else "N/A"  # Player URL
                team_acronym = cells[2].text if cells[2].text else "N/A"  # Team acronym
                
                gp = cells[4].text if len(cells) > 4 else "0"  # Minutes played
                mp = cells[6].text if len(cells) > 6 else "0"  # Minutes played

                # Columns required for True Shooting Percentage calculation
                fga = cells[8].text if len(cells) > 8 else "0"  # Field Goal Attempts
                fg = cells[7].text if len(cells) > 7 else "0"   # Field Goals Made
                tpa = cells[11].text if len(cells) > 11 else "0" # Three-Point Attempts
                tp = cells[10].text if len(cells) > 10 else "0"  # Three-Point Made
                fta = cells[18].text if len(cells) > 18 else "0" # Free Throw Attempts
                ft = cells[17].text if len(cells) > 17 else "0"  # Free Throws Made
                pts = cells[pt_index].text if len(cells) > pt_index else "0"  #
                
                data.append([
                    player_name, player_url, team_acronym, year, gp,mp, fga, fg, tpa, tp, fta, ft,pts
                ])
        
        # Create DataFrame for the current year
        year_data = pd.DataFrame(
            data=data, 
            columns=['player', 'url', 'team', 'year', 'G','MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT','PTS']
        )
        frames.append(year_data)
        print(f"Year {year} data added.")
        time.sleep(2)
    
    return pd.concat(frames)


index_frame=pull_bref(ps=False,totals=True)
index_frame['bref_id']=index_frame['url'].str.split('/',expand=True)[5]
index_frame['bref_id']=index_frame['bref_id'].str.split('.',expand=True)[0]
master = pd.read_csv('index_master.csv')
match_dict=dict(zip(master['bref_id'],master['nba_id']))

team_dict=dict(zip(master['team'],master['team_id']))

search_dict={
    "hollaro01": 1641842,
    "sarral01": 1642259,
    "dadiepa01": 1642359,
    "cuiyo01": 1642385,
    "dasiltr01": 1641783,
    "shannte01":1630545

}
match_dict.update(search_dict)
index_frame['nba_id']=index_frame['bref_id'].map(match_dict)



current_season = "2024-25"  # Update this to the current season if needed

# Fetch all players for the current season
players_data = commonallplayers.CommonAllPlayers(is_only_current_season=1, season=current_season)
players_list = players_data.get_data_frames()[0]

# Display a list of player names
player_names = dict(zip(players_list['DISPLAY_FIRST_LAST'],players_list['PERSON_ID']))

notfound=index_frame[index_frame.year==2025].reset_index(drop=True)
notfound=index_frame[index_frame.nba_id.isna()].reset_index(drop=True)
print(notfound)
notfound['nba_id']=notfound['player'].map(player_names)
notfound.dropna(inplace=True)
index_frame.dropna(inplace=True)



index_frame=pd.concat([index_frame,notfound])
index_frame['team_id']=index_frame['team'].map(team_dict)
index_copy = index_frame[['player', 'url', 'year', 'team', 'bref_id', 'nba_id', 'team_id']]
master=master[master.year!=2025]
master=pd.concat([master,index_copy])
master.drop_duplicates(inplace=True)
master.to_csv('index_master.csv',index=False)
index_frame.dropna(subset='bref_id',inplace=True)
index_frame['FTA']=index_frame['FTA'].astype(int)
index_frame['FGA']=index_frame['FGA'].astype(int)

index_frame['PTS']=index_frame['PTS'].astype(int)
year=2025
old_scoring=pd.read_csv('totals.csv')
old_scoring=old_scoring[old_scoring.year<year]
old_scoring.columns

index_frame['TS%'] = (index_frame['PTS'] / (2 * (index_frame['FGA'] + 0.44 * index_frame['FTA']))) * 100

# Select and rename columns to match scoring.csv
new_df = index_frame[['player', 'TS%', 'PTS', 'MP', 'team', 'G', 'FTA','FGA','year', 'nba_id']].copy()
new_df = new_df.rename(columns={
    'player': 'Player',
    'team': 'Tm'
})

# Display the resulting DataFrame
new_scoring=pd.concat([old_scoring,new_df])
new_scoring.fillna(0,inplace=True)
new_scoring.replace([np.inf, -np.inf], 0, inplace=True)
new_scoring.loc[new_scoring['TS%'] > 150, 'TS%'] = 0

new_scoring.to_csv('totals.csv',index=False)
new_scoring[new_scoring.nba_id==2544]


# In[2]:


def pull_bref_score(ps=False,totals=False):
    leagues = "playoffs" if ps else "leagues"
    frames = []
    for year in range(2025, 2026):
   
        url = f"https://www.basketball-reference.com/{leagues}/NBA_{year}_per_poss.html"

        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the specific table
        table = soup.find('table')
        
        # Get all rows from the table body
        rows = table.find('tbody').find_all('tr')
        
        # Define the data structure to store extracted rows
        data = []
        for row in rows:
            cells = row.find_all('td')
            if cells:
                pt_index=28
                # Extract player name, url, team, and stats required
                player_cell = cells[0]
                player_name = player_cell.text if player_cell.text else "N/A"  # Player name
                player_url = "https://www.basketball-reference.com" + player_cell.a['href'] if player_cell.a else "N/A"  # Player URL
                team_acronym = cells[2].text if cells[2].text else "N/A"  # Team acronym
                
                gp = cells[4].text if len(cells) > 4 else "0"  # Minutes played
                mp = cells[6].text if len(cells) > 6 else "0"  # Minutes played

                # Columns required for True Shooting Percentage calculation
                fga = cells[8].text if len(cells) > 8 else "0"  # Field Goal Attempts
                fg = cells[7].text if len(cells) > 7 else "0"   # Field Goals Made
                tpa = cells[11].text if len(cells) > 11 else "0" # Three-Point Attempts
                tp = cells[10].text if len(cells) > 10 else "0"  # Three-Point Made
                fta = cells[21].text if len(cells) > 21 else "0" # Free Throw Attempts
                ft = cells[20].text if len(cells) > 20 else "0"  # Free Throws Made
                pts = cells[pt_index].text if len(cells) > pt_index else "0"  # Free Throws Made
                
                data.append([
                    player_name, player_url, team_acronym, year, gp,mp, fga, fg, tpa, tp, fta, ft,pts
                ])
        
        # Create DataFrame for the current year
        year_data = pd.DataFrame(
            data=data, 
            columns=['player', 'url', 'team', 'year', 'G','MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT','PTS']
        )
        frames.append(year_data)
        print(year_data.iloc[0])
        print(f"Year {year} data added.")
        time.sleep(2)
    
    return pd.concat(frames)
index_frame=pull_bref_score(ps=False)
index_frame['bref_id']=index_frame['url'].str.split('/',expand=True)[5]
index_frame['bref_id']=index_frame['bref_id'].str.split('.',expand=True)[0]

match_dict=dict(zip(master['bref_id'],master['nba_id']))

team_dict=dict(zip(master['team'],master['team_id']))

search_dict={
    "hollaro01": 1641842,
    "sarral01": 1642259,
    "dadiepa01": 1642359,
    "cuiyo01": 1642385,
    "dasiltr01": 1641783,
    "salauti01":1642275

}
match_dict.update(search_dict)
index_frame['nba_id']=index_frame['bref_id'].map(match_dict)

current_season = "2024-25"  # Update this to the current season if needed

# Fetch all players for the current season
players_data = commonallplayers.CommonAllPlayers(is_only_current_season=1, season=current_season)
players_list = players_data.get_data_frames()[0]

# Display a list of player names
player_names = dict(zip(players_list['DISPLAY_FIRST_LAST'],players_list['PERSON_ID']))

notfound=index_frame[index_frame.year==2025].reset_index(drop=True)
notfound=index_frame[index_frame.nba_id.isna()].reset_index(drop=True)
notfound['nba_id']=notfound['player'].map(player_names)
notfound.dropna(inplace=True)
index_frame.dropna(inplace=True)



index_frame=pd.concat([index_frame,notfound])

index_frame['team_id']=index_frame['team'].map(team_dict)

index_frame.dropna(subset='bref_id',inplace=True)
index_frame.fillna(0,inplace=True)
print(index_frame)
index_frame.replace('',0,inplace=True)
index_frame['FTA']=index_frame['FTA'].astype(float)
index_frame['FGA']=index_frame['FGA'].astype(float)

index_frame['PTS']=index_frame['PTS'].astype(float)
year=2025
old_scoring=pd.read_csv('scoring.csv')
old_scoring=old_scoring[old_scoring.year<year]
old_scoring.columns

index_frame['TS%'] = (index_frame['PTS'] / (2 * (index_frame['FGA'] + 0.44 * index_frame['FTA']))) * 100

# Select and rename columns to match scoring.csv
new_df = index_frame[['player', 'TS%', 'PTS', 'MP', 'team', 'G', 'year', 'nba_id']].copy()
new_df = new_df.rename(columns={
    'player': 'Player',
    'team': 'Tm'
})

# Display the resulting DataFrame
new_scoring=pd.concat([old_scoring,new_df])
new_scoring.fillna(0,inplace=True)
new_scoring.loc[new_scoring['TS%'] > 150, 'TS%'] = 0

new_scoring.to_csv('scoring.csv',index=False)
gp=new_scoring[['nba_id','Player','year','G']].reset_index()
gp.to_csv('../player_sheets/lineups/games.csv',index=False)

ps_scoring=pd.read_csv('scoring_ps.csv')
ps_scoring.fillna(0,inplace=True)
ps_scoring.loc[ps_scoring['TS%'] > 150, 'TS%'] = 0


ps_gp=ps_scoring[['nba_id','Player','year','G']].reset_index()
ps_gp.to_csv('../player_sheets/lineups/ps_games.csv',index=False)
ps_gp.to_csv('../extra_data/wowy_leverage/ps_games.csv',index=False)


# In[3]:


scoring=pd.read_csv('scoring.csv')
scoring[scoring.year==2024]


# In[ ]:




