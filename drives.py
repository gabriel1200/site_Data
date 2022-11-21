#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

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


# In[9]:


year = 2014
for df in frames:
    df['year'] = year
    df.to_csv(str(year)+'drives.csv',index = False)
    year+=1
    


# In[12]:


drives = pd.concat(frames)


# In[29]:


drives = drives[drives.year != 2020]


# In[26]:


test = get_tables(['https://www.nba.com/stats/teams/drives?Season=2021-22&PerMode=PerGame'])


# In[36]:


test['year'] = 2020


# In[34]:





# In[39]:


drives = drives.dropna(subset = ['year'])
drives


# In[40]:


drives = pd.concat([drives,test])
drives


# In[41]:


drives['year'] = drives['year'].astype(int)


# In[42]:


drives.to_csv('drives.csv',index = False)


# In[43]:


df = pd.read_csv('drives.csv')


# In[61]:


drives


# In[64]:


by_year = drives.groupby('year').max()[['DRIVES','FTA','PF','PTS%','Team']]


# In[65]:


by_year['ftperdrive'] = by_year['FTA']/by_year['DRIVES']


# In[66]:


by_year


# In[83]:


drives.groupby(["year","Team"]).max()["DRIVES"]


# In[86]:


drives.groupby(['year','DRIVES']).head(1)
drives.columns


# In[85]:


drives.sort_values(by ='DRIVES',ascending = False)


# In[88]:


drives = drives.drop(columns = ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs','Fri', 'Sat'])


# In[91]:


drives = drives.sort_values(by = 'DRIVES',ascending = False)


# In[93]:


drives.to_csv('drives.csv',index = False)


# In[116]:


drives.iloc[drives.reset_index().groupby(['year'])['DRIVES'].idxmax()]


# In[112]:


drives.groupby(['year'])['DRIVES'].idxmax(axis = 0)


# In[121]:


drives[drives.year == 2014]


# In[ ]:




