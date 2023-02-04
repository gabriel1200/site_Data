#!/usr/bin/env python
# coding: utf-8

# In[19]:


import requests
import pandas as pd
players_response = requests.get("https://api.pbpstats.com/get-all-players-for-league/nba")
players = players_response.json()
#players["players"]


# In[20]:


df = pd.DataFrame(players)


# In[21]:


df.index.name = 'id'


# In[22]:


df.reset_index(inplace=True)


# In[23]:


df


# In[24]:


df.to_csv('names.csv',index = False)


# In[ ]:




