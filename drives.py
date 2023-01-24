#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from pathlib import Path


# Step 1: Create a session and load the page
def years(start_year, end_year):
    urls = []
    for year in range(start_year,end_year +1):
        url = 'https://www.nba.com/stats/teams/drives?Season='+str(year-1)+'-'+str((year)%2000)+'&PerMode=PerGame'
        urls.append(url)
    return urls
url_list = years(2014,2023)
def get_tables(url_list):
    data = []
    for url in url_list:
        print(url)
        driver = webdriver.Chrome()
        driver.get(url)

        # Wait for the page to fully load
        driver.implicitly_wait(8)

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))

        #print(f'Total tables: {len(dfs)}')
        #print(dfs[2].head())
    
        driver.close()
        #return dfs
        df= dfs[-1]
        #drop = ['Unnamed: 16_level_1', 'Unnamed: 17_level_1', 'Unnamed: 18_level_1']
        #df.columns = df.columns.droplevel()
        #df = df.drop(columns = drop)
        data.append(df)
    return data
frames = get_tables(url_list)


# In[ ]:


year = 2014
for df in frames:
    df['year'] = year
    df.to_csv(str(year)+'drives.csv',index = False)
    year+=1
    


# In[ ]:


drives = pd.concat(frames)


# In[ ]:


drives = drives[drives.year != 2020]


# In[ ]:


test = get_tables(['https://www.nba.com/stats/teams/drives?Season=2021-22&PerMode=PerGame'])


# In[ ]:


test['year'] = 2020


# In[ ]:





# In[ ]:


drives = drives.dropna(subset = ['year'])
drives


# In[ ]:


drives = pd.concat([drives,test])
drives


# In[ ]:


drives['year'] = drives['year'].astype(int)


# In[ ]:


drives.to_csv('drives.csv',index = False)


# In[ ]:


df = pd.read_csv('drives.csv')


# In[ ]:


drives


# In[ ]:


by_year = drives.groupby('year').max()[['DRIVES','FTA','PF','PTS%','Team']]


# In[ ]:


by_year['ftperdrive'] = by_year['FTA']/by_year['DRIVES']


# In[ ]:


by_year


# In[ ]:


drives.groupby(["year","Team"]).max()["DRIVES"]


# In[ ]:


drives.groupby(['year','DRIVES']).head(1)
drives.columns


# In[ ]:


drives.sort_values(by ='DRIVES',ascending = False)


# In[ ]:


drives = drives.drop(columns = ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs','Fri', 'Sat'])


# In[ ]:


drives = drives.sort_values(by = 'DRIVES',ascending = False)


# In[ ]:


drives.to_csv('drives.csv',index = False)


# In[ ]:


drives.iloc[drives.reset_index().groupby(['year'])['DRIVES'].idxmax()]


# In[ ]:


drives.groupby(['year'])['DRIVES'].idxmax(axis = 0)


# In[ ]:


drives[drives.year == 2014]


# In[ ]:




