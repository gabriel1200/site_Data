#!/usr/bin/env python
# coding: utf-8

# In[1]:


link = 'https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-raptor/modern_RAPTOR_by_player.csv'
import pandas as pd
df = pd.read_csv(link)


# In[3]:


df['season'].min()


# In[4]:


df.to_csv('full_raptor.csv',index = False)


# In[5]:


for i in range(2014,2023):
    path = str(i)+'/raptor.csv'
    season =df[df.season==i]
    season.to_csv(path)


# In[ ]:




