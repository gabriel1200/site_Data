#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
url = 'https://www.basketball-reference.com/playoffs/NBA_2023_games.html'
df = pd.read_html(url)[0]
df.to_csv('2023/playoffs/game_log/log.csv')


# In[5]:


df


# In[ ]:




