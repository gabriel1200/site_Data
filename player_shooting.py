#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import os
#url_list = [url1]#
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time

from pathlib import Path
# Step 1: Create a session and load the page
url4 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url1 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url_list = [url1,url2,url3,url4]
#url_list = url_list.reverse()
print(url_list)
#url_list =[url +'&SeasonType=Playoffs' for url in url_list]
#url_list =[url +'&SeasonType=Regular+Season'for url in url_list]
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_tables(url_list):
    data = []
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)

    #driver = webdriver.Chrome()
    for url in url_list:
        
        driver.get(url)
        print(url)
        # Wait for the page to fully load
        driver.implicitly_wait(20)
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        driver.implicitly_wait(10)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        time.sleep(10)
        dropdown1 = Select(driver.find_element(By.XPATH, xpath))
        dropdown1.select_by_index(0)

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')
        

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))

        #print(f'Total tables: {len(dfs)}')
        #print(dfs[2].head())

        
        df= dfs[-1]
        print(len(df))
        #print(df)
    
        df.columns = df.columns.droplevel()
        drop = [ 'Unnamed: 18_level_1', 'Unnamed: 19_level_1','Unnamed: 20_level_1','Unnamed: 21_level_1','Unnamed: 22_level_1']
        df = df.drop(columns = drop)
        #df = df.drop(columns = drop)
        data.append(df)
    driver.close()
    return data
def get_multi(url_list,playoffs = False):
    if playoffs == True:
        p ='/playoffs'
        url_list =[url +'&SeasonType=Playoffs' for url in url_list]
    else:
        p = ''
        url_list =[url +'&SeasonType=Regular+Season'for url in url_list]
        
    for i in range(2023,2024):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        frames = get_tables(year_url)

 
        path = str(i+1)+p+'/player_shooting/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        #terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
        terms = ['very_tight.csv','tight.csv','open.csv','wide_open.csv']
        terms = [ path+ t for t in terms]
        
        for i in range(len(terms)):
            df = frames[i]
            #print(df)
            #print(terms[i])
            df.to_csv(terms[i],index = False)

#get_multi(url_list)
get_multi(url_list,playoffs = False)


# In[ ]:


def master_shooting(playoffs = False):
    data =[]
    for i in range(2014,2024):
        if playoffs == False:
            p = ''
        else:
            p='/playoffs'

        path = str(i)+p+'/player_shooting/'
        files = ['wide_open','open','tight','very_tight']
        for file in files:
            df = pd.read_csv(path+file+'.csv.')
            df['year'] = i
            df['shot_type'] =file
            data.append(df)
    master = pd.concat(data)
    return master
master= master_shooting() 
master.to_csv('player_shooting.csv',index = False)


# In[ ]:




