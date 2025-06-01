#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import math
import plotly.figure_factory as ff

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

import numpy as np




import pandas as pd
import re

def clean_player_name(name: str) -> str:
    """
    Cleans player names by removing common suffixes (Jr., II, III, etc.) from the start
    and standardizing format.

    Args:
        name (str): Player name to clean

    Returns:
        str: Cleaned player name
    """
    # List of common name suffixes to remove
    suffixes = ['Jr.', 'Jr', 'II', 'III', 'IV', 'Sr.', 'Sr']

    # Split the name into parts
    name_parts = name.split()

    # If the first part is a suffix, remove it
    if name_parts and name_parts[0] in suffixes:
        name_parts = name_parts[1:]

    # Rejoin the name parts
    cleaned_name = ' '.join(name_parts)

    # Remove any double spaces
    cleaned_name = ' '.join(cleaned_name.split())

    return cleaned_name
def clean_seasonal_salaries(data, seasonlist,header='Dead Money'):
    """
    Cleans salary data for specified seasons within the Dead Money section

    Parameters:
    data (dict): Input data containing Dead Money section
    seasonlist (list): List of seasons to process

    Returns:
    pd.DataFrame: DataFrame with cleaned numerical salary values for all seasons
    """
    if 'Dead Money' not in data:
        return pd.DataFrame()

    dead = data[header].copy()

    for season in seasonlist:
        if season not in dead.columns:
            continue

        # Fill NA values
        dead[season] = dead[season].fillna('0')

        # Remove 'Ext. Elig.' and strip whitespace
        dead[season] = dead[season].str.replace('Ext. Elig.', '', regex=False).str.strip()

        # Convert strings to numeric values
        dead[season] = dead[season].apply(lambda x: convert_salary_string(x))

        # Ensure integer type
        dead[season] = dead[season].replace('', 0)
        dead[season] = dead[season].astype(int)

    return dead
def convert_salary_string2(salary_str):
    """
    Convert salary strings to decimal values, handling both million and thousand scale values.

    Args:
        salary_str: String representation of salary (e.g., "$724,883", "$1,234,567")

    Returns:
        float: Converted salary value
    """
    if isinstance(salary_str, (int, float)):
        return float(salary_str)

    if not salary_str or pd.isna(salary_str):
        return 0.0

    # Remove non-numeric characters except commas
    cleaned = re.sub(r'[^\d,]', '', str(salary_str))

    if not cleaned:
        return 0.0

    # Split by commas to count the number groups
    parts = cleaned.split(',')

    if len(parts) == 1:  # No commas, direct conversion
        return float(parts[0])

    # Join all parts and convert to number
    number = float(''.join(parts))

    # If the number is unreasonably large (over 100 million), 
    # assume it should be scaled down
    if number > 100000000:  # 100 million threshold
        return number / 10

    return number

def convert_salary_string(value):
    """
    Converts a salary string to a pure number, handling percentage suffixes for any size number
    """
    if pd.isna(value) or value == '':
        return '0'

    if isinstance(value, (int, float)):
        return str(int(value))

    value_str = str(value)
    cutoff=1
    if len(value_str)>15:
        cutoff=2

    # Check for special strings
    strings_to_check = ['UFA', 'RFA', 'NA', 'N/A']
    if any(s in value_str for s in strings_to_check):
        return '0'

    # First, remove $ and commas
    value_str = value_str.replace('$', '').replace(',', '')

    # Find where the decimal point is (indicating start of percentage)
    decimal_index = value_str.find('.')
    if decimal_index != -1:
        # Take everything up to the last 8 digits before the decimal
        # (changed from 7 to 8 to capture the correct number of digits)
        non_decimal_part = value_str[:decimal_index]

        value_str = non_decimal_part[:-cutoff]  # Remove last 2 digits instead of 1

    # Remove any remaining non-digits
    clean_value = ''.join(c for c in value_str if c.isdigit())
    return clean_value if clean_value else '0'



# Usage

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
        data_dict={}

        for table in tables:
            # Look for the nearest preceding h2
            header = None
            prev_elem = table.find_previous('h2')
            if prev_elem:
                header = prev_elem.get_text(strip=True)

            # Parse table into DataFrame
            df = pd.read_html(str(table))[0]
            data_dict[header]=df

        return data_dict

    except RequestException as e:
        print(f"Error fetching data: {e}")
        return [], []
    except ValueError as e:
        print(f"Error parsing HTML tables: {e}")
        return [], []
# Populate the new DataFrame with player options and team options
def team_books(team):
    print(team)
    nba_team_urls = {
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


    url = nba_team_urls[team.upper()]    
    data = get_team_data(url)

    df = data['Upcoming Deadlines']
    salary_df = data['Active Roster']

    columns = ['Player']
    for col in salary_df.columns[1:]:
        columns.append(col)

    df.columns = ['Deadline Date', 'Player', 'Type', 'Value']
    salary_df.columns = columns

    # Clean player names in both DataFrames
    salary_df['Player'] = salary_df['Player'].str.split(' ').str[1:].str.join(' ').apply(clean_player_name)
    df['Player'] = df['Player'].apply(clean_player_name)

    seasons = ['2024-25', '2025-26', '2026-27', '2027-28', '2028-29']
    extra_seasons = ['2029-30', '2030-31']
    for seas in extra_seasons:
        if seas in salary_df.columns:
            seasons.append(seas)

    strings_to_check = ['UFA', 'RFA']
    for season in seasons:
        salary_df[season] = salary_df[season].fillna('')
        salary_df[season] = salary_df[season].str.replace('Ext. Elig.', '', regex=False).str.strip()
        salary_df[season] = salary_df[season].apply(lambda x: '0' if any(s in x for s in strings_to_check) else x)
        salary_df[season] = salary_df[season].fillna('0')
        salary_df[season] = salary_df[season].apply(convert_salary_string)
        salary_df[season] = salary_df[season].str.replace(r'\D', '', regex=True)
        salary_df[season] = salary_df[season].replace('', 0)

    if 'Dead Money' in data.keys():
        seasonlist = ['2024-25', '2025-26', '2026-27', '2027-28', '2028-29', '2029-30']
        dead = clean_seasonal_salaries(data, seasonlist)
        alldead = pd.DataFrame()

        for season in seasonlist:
            if season in dead.columns:
                alldead[season] = [dead[season].sum()]
        alldead['Player'] = ['Dead Cap']
        alldead.reset_index(inplace=True)
        salary_df = pd.concat([salary_df, alldead])

    players = salary_df['Player'].unique()
    data = []

    for player in players:
        player_data = df[df['Player'] == player]
        row = {'Player': player}
        for season in seasons:
            if season in salary_df.columns:
                row[season] = 0
                season_data = player_data[player_data['Type'].str.contains(season)]
                if not season_data.empty:
                    if 'PLAYER' in season_data['Type'].values[0]:
                        row[season] = 'P'
                    elif 'CLUB' in season_data['Type'].values[0]:
                        row[season] = 'T'
                    elif 'GUARANTEED' in season_data['Type'].values[0]:
                        row[season] = 'NG'
                    elif 'EXTENSION' in season_data['Type'].values[0]:
                        row[season] = 'EE'
                    elif 'RFA' in season_data['Type'].values[0]:
                        row[season] = 'RFA'
                    elif 'UNREST' in season_data['Type'].values[0]:
                        row[season] = 'UFA'
                    else:
                        row[season] = season_data['Type'].values[0] + (' ' + season_data['Value'].values[0] if not pd.isna(season_data['Value'].values[0]) else '')
                data.append(row)

    new_df = pd.DataFrame(columns=['Player'] + seasons, data=data)
    new_df = new_df.drop_duplicates().reset_index(drop=True)
    salary_df = salary_df.drop_duplicates().reset_index(drop=True)

    for season in seasons:
        salary_df[season] = salary_df[season].astype(float)

    salary_df['Team'] = team
    new_df['Team'] = team

    return salary_df, new_df
teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
#teams=['MIA']
salary=[]
options=[]
for team in teams:
    salary_df,option_df =team_books(team)
    salary.append(salary_df)
    options.append(option_df)

salary_df = pd.concat(salary)
option_df = pd.concat(options)
#salary_df.to_csv('salary.csv',index=False)
option_df


# In[2]:


salary_df


# In[3]:


test1 = "$2,087,5191.5%"
test2 = "$39,256,08327.9%"
print(convert_salary_string(test1))  # Should be '2087519'
print(convert_salary_string(test2))


# In[4]:


temp_df=pd.DataFrame()
temp_df['Player'] = option_df['Player']
seasons = ['2024-25','2025-26','2026-27','2027-28','2028-29']
for season in seasons:
    temp_df[season] = np.where(option_df[season]!='T', 1, 0)


guar = pd.DataFrame()
guar['Player'] = salary_df['Player']


guar['Guaranteed'] = 0

print(guar)
print(temp_df)
print(salary_df)
for season in seasons:
    guar['Guaranteed']+= temp_df[season]* salary_df[season]
salary_df = salary_df.merge(guar,on='Player')
salary_df.sort_values(by='Guaranteed',inplace=True)
salary_df
salary_df=salary_df.drop_duplicates(subset=['Player','Team'])
salary_df
option_df=option_df.drop_duplicates(subset=['Player','Team'])
option_df

salary_df.loc[salary_df['Player'].str.contains('Quinten Post'), '2024-25'] = 438930

#salary_df.loc[salary_df['Player'].str.contains('Branden Carlson'), '2024-25'] = 990895

option_df.loc[option_df['Player'].str.contains('Scottie Barnes'), '2025-26'] = 0
option_df.loc[option_df['Player'].str.contains('Bradley Beal'), '2026-27'] = 'P'
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2024-25'] = 0
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2025-26'] = 0
option_df.loc[option_df['Player'].str.contains('Julius Randle'), '2026-27'] = 'P'



# In[ ]:





# In[5]:


salary_df.to_csv('salary.csv',index=False)
option_df.to_csv('option.csv',index=False)
#salary_df.to_csv('../data/salary.csv',index=False)
#option_df.to_csv('../data/option.csv',index=False)
salary_df[salary_df.Team=='OKC']


# In[6]:


'''
dfs =pd.read_html('https://basketball.realgm.com/nba/info/salary_cap')
cap = dfs[0]
cap.columns = cap.columns.droplevel()
cap.columns
columns = [ 'Salary Cap', 'Luxury Tax', '1st Apron', '2nd Apron', 'BAE',
       'Standard / Non-Taxpayer', 'Taxpayer', 'Team Room / Under Cap']
for col in columns:
    cap[col] = cap[col].str.replace(r'\D', '', regex=True)
    cap[col] = cap[col].astype(float)
#cap.to_csv('../data/cap.csv',index=False)
'''


# In[7]:


'''
df = pd.read_csv('../data/lebron.csv')
jrue =df[df['NBA ID']==201950]

df =df[df['NBA ID']!=201950]


jrue['Player'] = 'jrue holiday'

df =pd.concat([df,jrue]).reset_index(drop=True)
df.sort_values(['year','Player'],inplace=True)
df.to_csv('../data/lebron.csv',index=False)
'''


# In[8]:


'''
cap=pd.read_csv('../data/cap.csv')
cap['year'] = cap['Season'].str.split('-').str[1:].str.join('')
cap['year'] = cap['year'].astype(int)
cap.to_csv('../data/cap.csv',index=False)
'''


# In[9]:


# Let's test both cases
test1 = "$2,087,5191.5%"
test2 = "$39,256,08327.9%"
print(convert_salary_string(test1))  # Should be '2087519'
print(convert_salary_string(test2))  # Should be '39256083'


# In[ ]:




