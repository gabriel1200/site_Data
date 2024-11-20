#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import math
import plotly.figure_factory as ff

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np

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
    dfs = pd.read_html(url)
    count = 0
    count_save = 0
    
    for df in dfs:
        
        if 'Deadline Date' in df.columns:
            count_save=count
        count+=1
            
    df = dfs[count_save]
  

    salary_df = dfs[0]

    

  
    columns = ['Player']
    for col in salary_df.columns[1:]:
        columns.append(col)
    #print(df.columns)
    df.columns=['Deadline Date', 'Player', 'Type', 'Value']
   
    salary_df.columns =columns
    
    
    salary_df['Player'] = salary_df['Player'].str.split(' ').str[1:].str.join(' ')
   
    
    salary_df['Player'] = salary_df['Player'].str.replace('III ', '')
    salary_df['Player'] = salary_df['Player'].str.replace('II ', '')
    seasons= ['2024-25','2025-26','2026-27','2027-28','2028-29']
    extra_seasons = ['2029-30','2030-31']
    for seas in extra_seasons:
        if seas in salary_df.columns:
            seasons.append(seas)
    # List of strings to check for
    strings_to_check = ['UFA','RFA']
    for season in seasons:
        salary_df[season] = salary_df[season].fillna('')
        




        
        #
    
    # Replace the value with 0 if any of the strings are present

    
        
    
    for season in seasons:

        
    
        salary_df[season] = salary_df[season].apply(lambda x: '0' if any(s in x for s in strings_to_check) else x)
        salary_df[season]=salary_df[season].fillna('0')
        salary_df[season] = salary_df[season].str.split(',').str[0:2].str.join('') +salary_df[season].str.split(',').str[2:3].str.join('').str[0:3]
        salary_df[season] = salary_df[season].str.replace(r'\D', '', regex=True)
        
        salary_df[season] = salary_df[season].replace('',0)
    
    
    salary_df['Player']=salary_df['Player'].str[1:]
    players = salary_df['Player'].unique()
    

    #salary_df = pd.concat([salary_df,cap_hold]).reset_index(drop=True)
    
    data=[]
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
                    elif 'CLUB' in  season_data['Type'].values[0]:
                        row[season] = 'T'
                    elif 'GUARANTEED' in season_data['Type'].values[0]:
                        row[season]='NG'
                    elif 'EXTENSION' in season_data['Type'].values[0]:
                        row[season]='EE'
                    elif 'RFA' in season_data['Type'].values[0]:
                        row[season]='RFA'
                    elif 'UNREST' in season_data['Type'].values[0]:
                        row[season]='UFA'
                    else:
                    
                        row[season] = season_data['Type'].values[0] + (' ' + season_data['Value'].values[0] if not pd.isna(season_data['Value'].values[0]) else '')
                data.append(row)
            
    
    
    # Display the new organized DataFrame
    new_df = pd.DataFrame(columns=['Player'] + seasons,data=data)
    new_df=new_df.drop_duplicates().reset_index(drop=True)
    #new_df = pd.concat([new_df,cap_options]).reset_index(drop=True)
    for season in seasons:
        salary_df[season] = salary_df[season].astype(float)

    #salary_df['Team']='GSW'
    #new_df['Team']='GSW'
    

    salary_df['Player'] = salary_df['Player'].str.replace('r. ','',regex=False)
    new_df['Player'] = new_df['Player'].str.replace('r. ','',regex=False)

    salary_df['Team']=team
    new_df['Team']=team

    return salary_df,new_df
teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
#teams=['UTA']
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


salary_df[salary_df.Team=='UTA']


# In[3]:


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


# In[4]:


salary_df=salary_df.drop_duplicates(subset=['Player','Team'])
salary_df
option_df=option_df.drop_duplicates(subset=['Player','Team'])
option_df


# In[5]:


option_df.loc[option_df['Player'].str.contains('Scottie Barnes'), '2025-26'] = 0
option_df.loc[option_df['Player'].str.contains('Julius Randle'), '2025-26'] = 'P'
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2024-25'] = 0
option_df.loc[option_df['Player'].str.contains('Jalen Brunson'), '2025-26'] = 0


# In[6]:


salary_df.to_csv('salary.csv',index=False)
option_df.to_csv('option.csv',index=False)
#salary_df.to_csv('../data/salary.csv',index=False)
#option_df.to_csv('../data/option.csv',index=False)


# In[7]:


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


# In[8]:


'''
df = pd.read_csv('../data/lebron.csv')
jrue =df[df['NBA ID']==201950]

df =df[df['NBA ID']!=201950]


jrue['Player'] = 'jrue holiday'

df =pd.concat([df,jrue]).reset_index(drop=True)
df.sort_values(['year','Player'],inplace=True)
df.to_csv('../data/lebron.csv',index=False)
'''


# In[9]:


'''
cap=pd.read_csv('../data/cap.csv')
cap['year'] = cap['Season'].str.split('-').str[1:].str.join('')
cap['year'] = cap['year'].astype(int)
cap.to_csv('../data/cap.csv',index=False)
'''


# In[ ]:




