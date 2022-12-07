#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


df = pd.read_html('https://www.basketball-reference.com/leagues/NBA_2023.html')


# In[3]:


len(df)


# In[4]:


df[0].to_csv('standings/east.csv',index = False)
df[1].to_csv('standings/west.csv',index = False)


# In[ ]:




