#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
# Step 1: Create a session and load the page
url1 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url2 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url3 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
url_list = [url1,url2,url3,url4]
url_list =[url +'&SeasonType=Playoffs' for url in url_list]
#url_list =[url +'&SeasonType=Regular+Season'for url in url_list]

def get_tables(url_list):
    data = []
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
    driver = webdriver.Chrome()
    for url in url_list:
        
        driver.get(url)
        print(url)
        # Wait for the page to fully load
        driver.implicitly_wait(20)
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))

        #print(f'Total tables: {len(dfs)}')
        #print(dfs[2].head())

        
        df= dfs[-1]
        #print(df)
        drop = ['Unnamed: 16_level_1', 'Unnamed: 17_level_1', 'Unnamed: 18_level_1']
        df.columns = df.columns.droplevel()
        df = df.drop(columns = drop)
        data.append(df)
    driver.close()
    return data


# In[8]:


#url_list = [url1]#
def get_multi(url_list,playoffs = False):
    if playoffs == True:
        p ='/playoffs'
    else:
        p = ''
        
    for i in range(2022,2023):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        frames = get_tables(year_url)

 
        path = str(i+1)+p+'/opp_shooting/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        #terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
        terms = ['very_tight.csv','tight.csv','open.csv','wide_open.csv']
        terms = [ path+ t for t in terms]
        
        for i in range(len(terms)):
            df = frames[i]
            df.to_csv(terms[i],index = False)


# In[9]:


get_multi(url_list,playoffs= True)


# In[7]:


#tables = get_tables(url_list)
terms = ['opp_shooting/very_tight.csv','opp_shooting/tight.csv','opp_shooting/open.csv','opp_shooting/wide_open.csv']
terms = ['2023/playoffs/'+t for t in terms]
#jsons =  ['opp_shooting/very_tight.json','opp_shooting/tight.json','opp_shooting/open.json','opp_shooting/wide_open.json']
#for i in range(len(terms)):
#    df = tables[i]
#    df.to_csv(terms[i],index = False)
    #df.to_json(jsons[i])
    #df.to_csv('2023/'+terms[i],index = False)
    #df.to_json('2023/'+jsons[i])


# In[ ]:




