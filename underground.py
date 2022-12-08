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


# In[15]:


len(player_stats)


# In[25]:





# In[19]:


df = pd.DataFrame(player_stats)


# In[ ]:





# In[33]:


col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss',
 'DefPoss','TotalPoss']


# In[34]:


df[col].to_csv('wowy/player_small.csv',index = False)


# In[35]:


df.to_csv('wowy/player_large.csv',index = False)


# In[36]:


df[df.Name == 'Jalen Duren']


# In[37]:


player_stats[162]


# In[ ]:





# In[ ]:




