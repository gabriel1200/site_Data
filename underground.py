#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests


# In[2]:


url = "https://api.pbpstats.com/get-totals/nba"
params = {
    "Season": "2022-23",
    "SeasonType": "Regular Season",
    "Type": "Player"
}
response = requests.get(url, params=params)
response_json = response.json()
player_stats = response_json["multi_row_table_data"]


# In[3]:


len(player_stats)


# In[ ]:





# In[4]:


df = pd.DataFrame(player_stats)


# In[ ]:





# In[5]:


col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','Arc3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss',
 'DefPoss','TotalPoss']


# In[6]:


df[col].to_csv('wowy/player_small.csv',index = False)


# In[7]:


df.to_csv('wowy/player_large.csv',index = False)


# In[8]:


df[df.Name == 'Giannis Antetokounmpo']['Arc3Assists']


# In[10]:


list(df.columns)


# In[ ]:





# In[ ]:




