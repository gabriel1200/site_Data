#!/usr/bin/env python
# coding: utf-8

# In[27]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
# Step 1: Create a session and load the page
url1 = 'https://www.nba.com/stats/teams/shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url2 = 'https://www.nba.com/stats/teams/shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url3 = 'https://www.nba.com/stats/teams/shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
url_list = [url1,url2,url3,url4]
#url_list =[url +'&SeasonType=Playoffs' for url in url_list]
url_list =[url +'&SeasonType=Regular+Season'for url in url_list]

def get_tables(url_list):
    data = []
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
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
#url_list = [url1]#
def multiyear_shooting(url_list,team_round=0,playoffs = True):
    df_list = []

    for i in range(2023,2024):
        year = i+1
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        if team_round!=0:
            year_url = [url + '&PORound='+str(team_round) for url in year_url]
        frames = get_tables(year_url)

 
        path = str(i+1)+'/playoff_shooting/round'+str(team_round)+'/'
        if playoffs == False:
            path = str(i+1)+'/team_shooting/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        #terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
        terms = ['very_tight','tight','open','wide_open']
        
        
        for k in range(len(terms)):
            
            frames[k]['shot_coverage'] = terms[k]
            if playoffs == True:
                frames[k]['round'] = team_round
            frames[k]['year'] = year
        df = pd.concat(frames)
        df.to_csv(path+'team_shooting.csv',index = False)
        df_list.append(df)
    final_df = pd.concat(df_list)
    return final_df

df = multiyear_shooting(url_list,playoffs=False)


# In[28]:


df.to_csv('team_shooting.csv',index = False)


# In[ ]:




