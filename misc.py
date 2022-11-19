#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

# Step 1: Create a session and load the page
url1 = 'https://www.nba.com/stats/players/pullup?PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/isolation?PerMode=Totals'
url5 = 'https://www.nba.com/stats/players/transition?PerMode=Totals&dir=D&sort=POSS'
url_list = [url1,url2,url3,url4,url5]
#url_list=[url5]
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


# In[2]:


#url_list = [url1]
frames = get_tables(url_list)


# In[3]:


terms = ['data/pullup.csv','data/catchshoot.csv','data/undersix.csv','data/iso.csv','data/transition.csv']

for i in range(len(terms)):
    df = frames[i]
    df.to_csv(terms[i],index = False)
   


# In[5]:





# In[ ]:




