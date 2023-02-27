#!/usr/bin/env python
# coding: utf-8

# In[5]:


url = 'https://api.pbpstats.com/get-games/nba?Season=2022-23&SeasonType=Regular+Season'
import json
import requests
import pandas as pd
r = requests.get(url)
data= r.json()


# In[6]:


df = pd.DataFrame(data['results'])
df.to_csv('record/record.csv',index = False)


# In[ ]:




