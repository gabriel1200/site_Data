#!/usr/bin/env python
# coding: utf-8

# In[11]:


import requests
import json
url = 'https://nbacourtoptix.nba.com/api/leaderboards/'
response = requests.get(url)
json = json.loads(response.text)


# In[12]:


import pandas as pd
frames = []
screens =json['ballScreens']
for i in range(len(screens)):
    team = screens[i]
    for p in range(len(team['players'])):
        player = team['players'][p]
        df = pd.DataFrame(json['ballScreens'][i]['players'][p]['screeners'])
        df['receiver'] = json['ballScreens'][i]['players'][p]['playerName']
        df['team'] = team['abbrev']
        frames.append(df)


# In[13]:


final = pd.concat(frames)
final.to_csv('screening/ballscreen.csv',index = False)
final = final.drop(columns = 'playerId')


# In[17]:


def get_combos(player,df):
    return df[(df.playerName.str.lower()==player.lower()) | (df.receiver.str.lower()==player.lower())]
              
get_combos('rudy gobert',final)
    


# In[7]:


final.columns


# In[ ]:




