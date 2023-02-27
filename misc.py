#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 

# Step 1: Create a session and load the page
'''
url1 = 'https://www.nba.com/stats/players/pullup?PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/isolation?PerMode=Totals'
url5 = 'https://www.nba.com/stats/players/transition?PerMode=Totals&dir=D&sort=POSS'
'''
cs ='https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
pullup ='https://www.nba.com/stats/players/pullup?PerMode=Totals'

handoff = 'https://www.nba.com/stats/teams/hand-off?PerMode=Totals'
iso ='https://www.nba.com/stats/teams/isolation?PerMode=Totals'
trans ='https://www.nba.com/stats/teams/transition?PerMode=Totals'
bh='https://www.nba.com/stats/teams/ball-handler?PerMode=Totals'
rollman = 'https://www.nba.com/stats/teams/roll-man?PerMode=Totals'
postup = 'https://www.nba.com/stats/teams/playtype-post-up?PerMode=Totals'
spotup = 'https://www.nba.com/stats/teams/spot-up?PerMode=Totals'
cut = 'https://www.nba.com/stats/teams/cut?PerMode=Totals'
offscreen = 'https://www.nba.com/stats/teams/off-screen?PerMode=Totals'
putbacks = 'https://www.nba.com/stats/teams/putbacks?PerMode=Totals'
misc = 'https://www.nba.com/stats/teams/playtype-misc?PerMode=Totals'
drives = 'https://www.nba.com/stats/teams/drives?PerMode=Totals'
#url_list = [url1,url2,url3,url4,url5]
url_list=[handoff,iso,trans,bh,rollman,postup,spotup,cut,offscreen,putbacks,misc,drives]
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
#url_list = [cs,pullup]
def get_tables(url_list):
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
    data = []
    driver = webdriver.Chrome()
    for url in url_list:
        print(url)
        
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        driver.implicitly_wait(20)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))
        #print(dfs)

        #print(f'Total tables: {len(dfs)}')
        #print(dfs[2].head())
    
        
        #return dfs
        df= dfs[-1]
        #drop = ['Unnamed: 16_level_1', 'Unnamed: 17_level_1', 'Unnamed: 18_level_1']
        #df.columns = df.columns.droplevel()
        #df = df.drop(columns = drop)
        data.append(df)
    driver.close()
    return data


# In[2]:


#url_list = [url1]#
def get_multi(url_list):
    for i in range(2013,2022):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        frames = get_tables(year_url)

 
        path = str(i+1)+'/playtype/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        #terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
        terms = ['playtype/handoff.csv','playtype/iso.csv','playtype/trans.csv','playtype/bh.csv','playtype/rollman.csv','playtype/postup.csv','playtype/spotup.csv',
                 'playtype/cut.csv','playtype/offscreen.csv','playtype/putback.csv','playtype/misc.csv','playtype/drives.csv']
        terms = [ str(i+1)+'/'+t for t in terms]
        
        for i in range(len(terms)):
            df = frames[i]
            df.to_csv(terms[i],index = False)


# In[3]:


#get_multi(url_list)


# In[4]:


#terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
frames = get_tables(url_list)
terms = ['playtype/handoff.csv','playtype/iso.csv','playtype/trans.csv','playtype/bh.csv','playtype/rollman.csv','playtype/postup.csv','playtype/spotup.csv',
         'playtype/cut.csv','playtype/offscreen.csv','playtype/putback.csv','playtype/misc.csv','playtype/drives.csv']


# In[5]:


for i in range(len(terms)):
    df = frames[i]
    df.to_csv(terms[i],index = False)
    df.to_csv('2023/'+terms[i],index = False)
   


# In[ ]:




