#!/usr/bin/env python
# coding: utf-8

# In[6]:


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
#print(df.columns)
col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','Arc3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss','PtsAssisted2s',
'PtsUnassisted2s',
'PtsAssisted3s',
'PtsUnassisted3s',
 'DefPoss','TotalPoss']
df[col].to_csv('wowy/player_small.csv',index = False)
#df[col].to_csv('2024/player_tracking/player_small.csv',index = False)
df.to_csv('wowy/player_large.csv',index = False)



# In[ ]:




