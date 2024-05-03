#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests


# In[3]:


url = "https://api.pbpstats.com/get-totals/nba"
params = {
    "Season": "2023-24",
    "SeasonType": "Regular Season",
    "Type": "Player"
}
response = requests.get(url, params=params)
response_json = response.json()
player_stats = response_json["multi_row_table_data"]
df = pd.DataFrame(player_stats)

col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','Arc3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss','PtsAssisted2s',
'PtsUnassisted2s',
'PtsAssisted3s',
'PtsUnassisted3s',
 'DefPoss','TotalPoss']
df[col].to_csv('wowy/player_small.csv',index = False)
#df[col].to_csv('2024/player_tracking/player_small.csv',index = False)
df.to_csv('wowy/player_large.csv',index = False)
year = 2024
df['year'] = year
shotzone = df[['Name','EntityId','TeamId','TeamAbbreviation','GamesPlayed','OffPoss','DefPoss','Minutes','FtPoints','FTA','AtRimFGA','AtRimFGM','AtRimAccuracy','ShortMidRangeFGA','ShortMidRangeFGM',
        'ShortMidRangeAccuracy','ShortMidRangeFrequency','LongMidRangeFGM','LongMidRangeFGA','FG2A','FG2M','FG3A','NonHeaveFg3Pct','NonHeaveArc3FGA','HeaveAttempts','Corner3FGA','Corner3FGM','NonHeaveFg3Pct'
                ,'NonHeaveArc3FGM','TsPct','Points','EfgPct','SecondChanceEfgPct','PenaltyEfgPct','SecondChanceTsPct','PenaltyTsPct','SecondChanceShotQualityAvg','PenaltyShotQualityAvg','ShotQualityAvg','year']]

#shotzone
old = pd.read_csv('shotzone.csv')

old = old.rename(columns = {'NonHeaveFg3Pct.1':'NonHeaveFg3Pct'})

old = old[old.year<year]
shots = []
shots.append(old)
shots.append(shotzone)
master = pd.concat(shots)
master.to_csv('shotzone.csv',index = False)

url = "https://api.pbpstats.com/get-totals/nba"
params = {
    "Season": "2023-24",
    "SeasonType": "Playoffs",
    "Type": "Player"
}
response = requests.get(url, params=params)
response_json = response.json()
player_stats = response_json["multi_row_table_data"]
df = pd.DataFrame(player_stats)

col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','Arc3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss','PtsAssisted2s',
'PtsUnassisted2s',
'PtsAssisted3s',
'PtsUnassisted3s',
 'DefPoss','TotalPoss']
df[col].to_csv('wowy/player_small_ps.csv',index = False)
#df[col].to_csv('2024/player_tracking/player_small.csv',index = False)
df.to_csv('wowy/player_large_ps.csv',index = False)
year = 2024
df['year'] = year
shotzone = df[['Name','EntityId','TeamId','TeamAbbreviation','GamesPlayed','OffPoss','DefPoss','Minutes','FtPoints','FTA','AtRimFGA','AtRimFGM','AtRimAccuracy','ShortMidRangeFGA','ShortMidRangeFGM',
        'ShortMidRangeAccuracy','ShortMidRangeFrequency','LongMidRangeFGM','LongMidRangeFGA','FG2A','FG2M','FG3A','NonHeaveFg3Pct','NonHeaveArc3FGA','HeaveAttempts','Corner3FGA','Corner3FGM','NonHeaveFg3Pct'
                ,'NonHeaveArc3FGM','TsPct','Points','EfgPct','SecondChanceEfgPct','PenaltyEfgPct','SecondChanceTsPct','PenaltyTsPct','SecondChanceShotQualityAvg','PenaltyShotQualityAvg','ShotQualityAvg','year']]

#shotzone
old = pd.read_csv('shotzone_ps.csv')

old = old.rename(columns = {'NonHeaveFg3Pct.1':'NonHeaveFg3Pct'})

old = old[old.year<year]
shots = []
shots.append(old)
shots.append(shotzone)
master = pd.concat(shots)
master.to_csv('shotzone_ps.csv',index = False)
print('ShotZone Player')


# In[ ]:





# In[ ]:





# In[2]:


def team_shotzone(year,ps = False):
    stype="Playoffs"
    if ps == False:
        stype="Regular Season"
    season = str(year)+'-'+str(year+1)[-2:]

                               
        
    url = "https://api.pbpstats.com/get-totals/nba"
    params = {
        "Season": season,
        "SeasonType": stype,
        "Type": "Team"
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    player_stats = response_json["multi_row_table_data"]
    df = pd.DataFrame(player_stats)
    shotzone = df[['Name','EntityId','TeamId','TeamAbbreviation','GamesPlayed','OffPoss','DefPoss','FtPoints','FTA','AtRimFGA','AtRimFGM','AtRimAccuracy','ShortMidRangeFGA','ShortMidRangeFGM',
            'ShortMidRangeAccuracy','ShortMidRangeFrequency','LongMidRangeFGM','LongMidRangeFGA','FG2A','FG2M','FG3A','NonHeaveFg3Pct','NonHeaveArc3FGA','HeaveAttempts','Corner3FGA','Corner3FGM'
                    ,'NonHeaveArc3FGM','TsPct','Points','EfgPct','SecondChanceEfgPct','PenaltyEfgPct','SecondChanceTsPct','PenaltyTsPct','SecondChanceShotQualityAvg','PenaltyShotQualityAvg','ShotQualityAvg']].reset_index(drop=True)
    shotzone['year']=year+1
    shotzone = shotzone.reset_index(drop=True)
    return shotzone


def update_team(year,ps=False):
    trail = ''
    if ps == True:
        trail='_ps'
    teamdf = team_shotzone(year,ps=ps)
    print(teamdf.columns)
    year+=1
    old_df =pd.read_csv('team_shotzone'+trail+'.csv')
    print(old.columns)
    old_df = old_df[old_df.year!=year].reset_index(drop=True)
    new=pd.concat([old_df,teamdf])
    new.to_csv('team_shotzone'+trail+'.csv',index=False)
    return new
newdf = update_team(2023,ps=True)
newdf


# In[4]:


#df.to_csv('shotzone.csv',index = False)


# In[ ]:




