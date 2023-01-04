#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

# Step 1: Create a session and load the page
url1 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url2 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url3 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
url_list = [url1,url2,url3,url4]
def get_tables(url_list):
    data = []
    for url in url_list:
        driver = webdriver.Chrome()
        driver.get(url)

        # Wait for the page to fully load
        driver.implicitly_wait(10)

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))

        #print(f'Total tables: {len(dfs)}')
        #print(dfs[2].head())

        driver.close()
        df= dfs[-1]
        drop = ['Unnamed: 16_level_1', 'Unnamed: 17_level_1', 'Unnamed: 18_level_1']
        df.columns = df.columns.droplevel()
        df = df.drop(columns = drop)
        data.append(df)
    return data


# In[2]:


tables = get_tables(url_list)
terms = ['opp_shooting/very_tight.csv','opp_shooting/tight.csv','opp_shooting/open.csv','opp_shooting/wide_open.csv']
jsons =  ['opp_shooting/very_tight.json','opp_shooting/tight.json','opp_shooting/open.json','opp_shooting/wide_open.json']
for i in range(len(terms)):
    df = tables[i]
    df.to_csv(terms[i],index = False)
    df.to_json(jsons[i])


# In[3]:


tables[0].to_json(orient="records")


# In[ ]:





# In[11]:


len(tables)


# In[ ]:


tables[1]


# In[ ]:




