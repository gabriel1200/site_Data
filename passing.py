#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import unicodedata
import requests
import json
import math
import time
import sys
#df = pd.read_csv('../../league_wide/wowy/player_large.csv')
def passing_data(ps=False, update=True):
    url = 'https://api.pbpstats.com/get-totals/nba'
    stype = 'Regular Season'
    folder = 'tracking'
    
    if ps:
        stype = 'Playoffs'
        folder = 'tracking_ps'

    frames = []
    start_year = 2014
    
    if update:
        df = pd.read_csv('passing.csv')
        df = df[df.year < 2025]
        frames.append(df)
        start_year = 2025

    print(start_year)

    for year in range(start_year, 2026):
        time.sleep(1)
        # Prepare API call
        season=str(year-1)+"-"+str(year)[-2:]
        params = {
            "Season": season,
            "SeasonType": stype,
            "Type": "Player"
        }
        response = requests.get(url, params=params)
        response_json = response.json()
        df = response_json["multi_row_table_data"]
        df = pd.DataFrame(df)
        df.rename(columns={'EntityId':'PLAYER_ID'},inplace=True)

        # Load the unified passing and touches data from the common files
        passing_file_path = f'{folder}/passing.csv'
        touches_file_path = f'{folder}/touches.csv'
        print(passing_file_path)
        print(touches_file_path)

        df2 = pd.read_csv(passing_file_path)
        df2.rename(columns={'PLAYER': 'Name'}, inplace=True)


        df3 = pd.read_csv(touches_file_path)

        df2=df2[df2.year==year]
        df3=df3[df3.year==year]
        df['nba_id']=df['PLAYER_ID'].astype(int)
        df2['nba_id']=df2['PLAYER_ID'].astype(int)
        df3['nba_id']=df3['PLAYER_ID'].astype(int)

        df.drop(columns=['PLAYER_ID'],inplace=True)
        df2.drop(columns=['PLAYER_ID','GP'],inplace=True)
        df3.drop(columns=['PLAYER_ID'],inplace=True)
        df3.rename(columns={'Player': 'Name'}, inplace=True)

        # Merging data
        merged = df.merge(df2, on='nba_id', how='left')
        merged = merged.merge(df3, on='nba_id', how='left')

        # Cleaning up column names and calculating additional fields

        merged = merged.fillna(0)
        merged['Points Unassisted'] = merged['PtsUnassisted2s'] + merged['PtsUnassisted3s']
        merged['UAFGM'] = (merged['PtsUnassisted2s'] / 2) + (merged['PtsUnassisted3s'] / 3)
        merged['UAPTS'] = merged['Points Unassisted']
        merged['on-ball-time'] = merged['TIME_OF_POSS']
        merged['High Value Assist %'] = 100 * (merged['ThreePtAssists'] + merged['AtRimAssists']) / merged['Assists']
        merged['on-ball-time%'] = 100 * 2 * (merged['TIME_OF_POSS']) / (merged['Minutes'])
        merged['TSA'] = (merged['Points'] / (merged['TsPct'] * 2))
        merged['Potential Assists'] = merged['POTENTIAL_AST']
        merged['Passes'] = merged['PASSES_MADE']
        merged['PotAss/Passes'] = merged['POTENTIAL_AST'] / merged['Passes']
        merged['Assist PPP'] = (merged['AST_PTS_CREATED']) / merged['POTENTIAL_AST']
        merged['POT_AST_PER_MIN'] = merged['POTENTIAL_AST'] / (merged['on-ball-time'])
        merged['year'] = year

        frames.append(merged)
        print(f'Season done {year}')
    
    df = pd.concat(frames)
    return df


#passing = passing_data()
passing= passing_data(ps=False,update=True)
#merged['testas'] = merged['TwoPtAssists']*2+ merged['ThreePtAssists']*3
print(passing.columns)
columns = ['nba_id','Name','Points','on-ball-time%','on-ball-time','UAPTS','TSA','OffPoss','Potential Assists','Travels','TsPct',
            'Turnovers','Passes','PASSES_RECEIVED','PotAss/Passes','UAFGM','High Value Assist %','Assist PPP','TOUCHES','AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH', 'PTS_PER_TOUCH',
                'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED', 'AST_ADJ', 'AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ','Assists','POT_AST_PER_MIN','ThreePtAssists','AtRimAssists','BadPassTurnovers',
           'BadPassSteals','BadPassOutOfBoundsTurnovers',
                   'PtsUnassisted2s','PtsUnassisted3s','Fg3Pct','FG3A','FG3M','OffPoss','GP','Minutes','year']
#rs=passing[columns]
rs=passing[columns]
#rs.to_csv('passing.csv',index =False)
rs.to_csv('passing.csv',index = False)



#passing= passing_data(ps=True,update=False)
#merged['testas'] = merged['TwoPtAssists']*2+ merged['ThreePtAssists']*3

#rs=passing[columns]
#ps=passing[columns]
#rs.to_csv('passing.csv',index =False)
#ps.to_csv('passing_ps.csv',index = False)


# In[2]:


for col in passing:
    if 'bad' in col.lower():
        print(col)


# In[3]:


avg = pd.read_html('https://www.basketball-reference.com/leagues/NBA_stats_per_poss.html')[0]
avg.columns = avg.columns.droplevel()
avg = avg.dropna(subset='Season')
avg = avg[avg.Season!='Season']

avg = avg.dropna()
avg['PTS'] = avg['PTS'].astype(float)
avg['FGA'] = avg['FGA'].astype(float)
avg['FTA'] = avg['FTA'].astype(float)

#avg.head(87)


# In[4]:


avg['TS%'] = avg['PTS']/(2*(avg['FGA']+.44*avg['FTA']))
#avg


# In[5]:


avg.to_csv('avg_shooting.csv',index = False)
avg = avg[['Season','ORtg']]
avg.to_csv('team_avg.csv',index = False)


# In[ ]:





# In[ ]:




