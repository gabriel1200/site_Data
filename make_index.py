#!/usr/bin/env python
# coding: utf-8

# In[41]:


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

ps = True
if ps:
    trail='_ps'
else:
    trail=''
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


index_frame=pull_bref(ps=ps,totals=True)
print(index_frame)
index_frame['bref_id']=index_frame['url'].str.split('/',expand=True)[5]
index_frame['bref_id']=index_frame['bref_id'].str.split('.',expand=True)[0]
master = pd.read_csv('index_master'+trail+'.csv')
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
master.to_csv('index_master'+trail+'.csv',index=False)
index_frame.dropna(subset='bref_id',inplace=True)
index_frame['FTA']=index_frame['FTA'].astype(int)
index_frame['FGA']=index_frame['FGA'].astype(int)

index_frame['PTS']=index_frame['PTS'].astype(int)
year=2025
old_scoring=pd.read_csv('totals'+trail+'.csv')
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

new_scoring.to_csv('totals'+trail+'.csv',index=False)
new_scoring[new_scoring.nba_id==2544]


# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
# Assuming other necessary imports like nba_api are handled in your full script

# --- Adjusted pull_bref_score function ---
def pull_bref_score(ps=False, totals=False): # totals parameter retained but not used for specific data-stat names here
    """
    Scrapes basketball-reference.com for player statistics using data-stat attributes.
    Fetches per-100-possessions data by default from league-wide pages.
    """
    leagues_or_playoffs = "playoffs" if ps else "leagues"
    frames = []

    # Helper function to extract stat value using data-stat attribute
    def get_stat_from_row(row_obj, stat_name, default_value="0"):
        cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
        if cell:
            # .text gets the text content, strip() removes leading/trailing whitespace
            text_content = cell.text.strip()
            # If text_content is not empty, return it, otherwise return default_value
            return text_content if text_content else default_value
        return default_value

    # Helper function to extract player URL
    def get_player_url_from_row(row_obj, stat_name="player", default_value="N/A"):
        cell = row_obj.find(['td', 'th'], {'data-stat': stat_name})
        if cell and cell.a and 'href' in cell.a.attrs:
            return "https://www.basketball-reference.com" + cell.a['href']
        return default_value

    # Current date is May 2025. The 2024-2025 NBA season is represented by year 2025 on Basketball-Reference.
    # The loop range(2025, 2026) correctly targets this season.
    for year_to_scrape in range(2025, 2026): # Processes only the year 2025
        url = f"https://www.basketball-reference.com/{leagues_or_playoffs}/NBA_{year_to_scrape}_per_poss.html"
        print(f"Fetching data from: {url}")

        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status() # Check for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue # Skip to the next year

        response.encoding = 'utf-8' # Ensure correct encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # The main table for per_poss stats usually has id="per_poss_stats"
        table = soup.find('table', id='per_poss_stats')
        if not table:
            table = soup.find('table') # Fallback if specific id isn't found

        if not table:
            print(f"No data table found on {url}")
            continue

        tbody = table.find('tbody')
        if not tbody:
            print(f"No tbody found in table on {url}")
            continue

        rows = tbody.find_all('tr')

        data_for_year = []
        print(f"Processing {len(rows)} rows for year {year_to_scrape}...")
        for i, row_obj in enumerate(rows):
            # Skip header rows often class 'thead' or if they don't have actual cells for players
            if 'thead' in row_obj.get('class', []):
                continue

            player_name = get_stat_from_row(row_obj, "player", "N/A")

            # Skip rows that are not actual player data rows
            if player_name == "N/A" or player_name == "Player" or not player_name.strip():
                continue

            # For team acronym, use a more distinct default if not found
            team_acronym = get_stat_from_row(row_obj, "team_id", default_value="UNK") # "UNK" for Unknown team

            player_url = get_player_url_from_row(row_obj, "player")

            # Fetching stats using their data-stat attributes from the per_poss page
            gp = get_stat_from_row(row_obj, "g")         # Games Played
            mp = get_stat_from_row(row_obj, "mp")         # Minutes Played (total for season on per_poss)

            fga = get_stat_from_row(row_obj, "fga_per_poss")
            fg = get_stat_from_row(row_obj, "fg_per_poss")
            tpa = get_stat_from_row(row_obj, "fg3a_per_poss") # 3-Point Attempts
            tp = get_stat_from_row(row_obj, "fg3_per_poss")  # 3-Point Made
            fta = get_stat_from_row(row_obj, "fta_per_poss")
            ft = get_stat_from_row(row_obj, "ft_per_poss")
            pts = get_stat_from_row(row_obj, "pts_per_poss")

            data_for_year.append([
                player_name, player_url, team_acronym, year_to_scrape, gp, mp, 
                fga, fg, tpa, tp, fta, ft, pts
            ])

        if not data_for_year:
            print(f"No player data extracted for year {year_to_scrape}.")
            continue

        year_df = pd.DataFrame(
            data=data_for_year, 
            columns=['player', 'url', 'team', 'year', 'G', 'MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT', 'PTS']
        )
        frames.append(year_df)

        if not year_df.empty:
            print(f"First player processed for year {year_to_scrape}:")
            print(year_df.iloc[0])
            # You can add more debug prints here, e.g., to check unique team values:
            # print(f"Unique team acronyms found for {year_to_scrape}: {year_df['team'].unique()}")
        else:
            print(f"No data parsed into DataFrame for year {year_to_scrape}.")

        print(f"Year {year_to_scrape} data processing complete. Found {len(year_df)} players.")
        time.sleep(3) # Maintain a respectful delay

    if not frames:
        print("No data collected across all years. Returning an empty DataFrame.")
        return pd.DataFrame(columns=['player', 'url', 'team', 'year', 'G', 'MP', 'FGA', 'FG', '3PA', '3P', 'FTA', 'FT', 'PTS'])

    return pd.concat(frames)

# --- Example of how to call and test (ensure other parts of your script are set up) ---
# ps_setting = False 
# master_df = pd.DataFrame({'bref_id': [], 'nba_id': [], 'team':[], 'team_id':[]}) # Placeholder
# trail_str = "_test" # Placeholder

# print("Starting data pull...")
# main_index_frame = pull_bref_score(ps=ps_setting)

# if not main_index_frame.empty:
# print("\n--- DataFrame Head ---")
# print(main_index_frame.head())
# print("\n--- DataFrame Info ---")
# print(main_index_frame.info())
# print("\n--- Unique Teams Extracted ---")
# print(main_index_frame['team'].value_counts()) # Show counts of each team acronym
# else:
# print("Resulting DataFrame is empty.")

# ... (rest of your data processing logic)
index_frame=pull_bref_score(ps=ps)
for col in index_frame:
    print(col)
    print(index_frame[col].iloc[0])
print('original')
print(index_frame)
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
    "salauti01":1642275,
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
notfound['nba_id']=notfound['player'].map(player_names)
notfound.dropna(inplace=True)
index_frame.dropna(inplace=True)


index_frame=pd.concat([index_frame,notfound])

index_frame['team_id']=index_frame['team'].map(team_dict)

index_frame.dropna(subset='bref_id',inplace=True)
index_frame.fillna(0,inplace=True)

index_frame.replace('',0,inplace=True)
index_frame['FTA']=index_frame['FTA'].astype(float)
index_frame['FGA']=index_frame['FGA'].astype(float)

index_frame['PTS']=index_frame['PTS'].astype(float)

year=2025
print(trail)
old_scoring=pd.read_csv('scoring'+trail+'.csv')
old_scoring=old_scoring[old_scoring.year<year]
old_scoring.columns

index_frame['TS%'] = (index_frame['PTS'] / (2 * (index_frame['FGA'] + 0.44 * index_frame['FTA']))) * 100

# Select and rename columns to match scoring.csv
new_df = index_frame[['player', 'TS%', 'PTS', 'MP', 'team', 'G', 'year', 'nba_id']].copy()
print('former scoring')
print(new_df)
new_df = new_df.rename(columns={
    'player': 'Player',
    'team': 'Tm'
})

# Display the resulting DataFrame
new_scoring=pd.concat([old_scoring,new_df])

new_scoring.fillna(0,inplace=True)
new_scoring.loc[new_scoring['TS%'] > 150, 'TS%'] = 0

new_scoring.to_csv('scoring'+trail+'.csv',index=False)

new_scoring=pd.read_csv('scoring.csv')
print(new_scoring.head(40))
gp=new_scoring[['nba_id','Player','year','G']].reset_index()
gp.to_csv('../player_sheets/lineups/games.csv',index=False)

ps_scoring=pd.read_csv('scoring_ps.csv')
ps_scoring.fillna(0,inplace=True)
ps_scoring.loc[ps_scoring['TS%'] > 150, 'TS%'] = 0


ps_gp=ps_scoring[['nba_id','Player','year','G']].reset_index()
ps_gp.to_csv('../player_sheets/lineups/ps_games.csv',index=False)
ps_gp.to_csv('../extra_data/wowy_leverage/ps_games.csv',index=False)
ps_gp
ps_scoring


# In[37]:


scoring=pd.read_csv('scoring_ps.csv')
scoring=scoring[scoring.year==2025]
scoring_team_map=dict(zip(scoring.nba_id,scoring.Tm))
scoring_totals=pd.read_csv('totals_ps.csv')
new_totals=scoring_totals[scoring_totals.year==2025]
new_totals.drop(columns={'Tm'},inplace=True)
new_totals['Tm']=new_totals['nba_id'].map(scoring_team_map)
new_totals

old_totals=scoring_totals[scoring_totals.year<2025]

totals=pd.concat([old_totals,new_totals])
totals.to_csv('totals_ps.csv',index=False)
totals


# In[39]:


scoring

