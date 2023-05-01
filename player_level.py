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



# In[2]:


#url_list = [cs,pullup]
from selenium.webdriver.support.select import Select

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
def save_tables(tables,year, playoffs= False):
    if playoffs == True:
        path = str(year)+'/playoffs/player_tracking/'
    else:
        path = str(year)+'/player_tracking/'
    temp = tables[1]
    temp.columns = temp.columns.droplevel() 
    #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
    #temp
    temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
    tables[1] = temp

    tables[1] = temp
    for i in range(len(name_list)):
        #tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
        tables[i].to_csv(path+name_list[i]+'.csv',index = False)

def get_ptables(url_list,path_list):
    data = []
    driver = webdriver.Chrome()
    for i in range(len(url_list)):
        url = url_list[i]
        xpath = path_list[i]
        print(url)
        
        driver.get(url)
        element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        driver.implicitly_wait(10)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        
        dropdown1 = Select(driver.find_element(By.XPATH, xpath))
        dropdown1.select_by_index(0)

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


# In[3]:


def get_multi(url_list,path_list,ps =False):
    for i in range(2014,2023):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        tables = get_ptables(year_url,path_list)
        year =i+1
        save_tables(tables,year,playoffs = ps)
        


# In[4]:


cs ='https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
pullup ='https://www.nba.com/stats/players/pullup?PerMode=Totals'

touches = 'https://www.nba.com/stats/players/touches?PerMode=Totals'
drives = 'https://www.nba.com/stats/players/drives?PerMode=Totals'

wide_open = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
close = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals&dir=D&sort=PLUSMINUS'
passing = 'https://www.nba.com/stats/players/passing?PerMode=Totals'
paint = 'https://www.nba.com/stats/players/paint-touch?PerMode=Totals'
elbow = 'https://www.nba.com/stats/players/elbow-touch?PerMode=Totals'
oreb = 'https://www.nba.com/stats/players/offensive-rebounding?PerMode=Totals'
dreb = 'https://www.nba.com/stats/players/defensive-rebounding?PerMode=Totals'
shoot_ef = 'https://www.nba.com/stats/players/shooting-efficiency?'
post_up = 'https://www.nba.com/stats/players/tracking-post-ups?PerMode=Totals'
url_list = [drives,wide_open,close,touches,cs,pullup,passing,paint,elbow,oreb,dreb,shoot_ef,post_up]
#url_list =[url +'&SeasonType=Playoffs' for url in url_list]
url_list =[url +'&SeasonType=Regular+Season'for url in url_list]

name_list = ['drives','wide_open','close_6','touches','cs','pullup','passing',\
            'paint','elbow','oreb','dreb','shoot_ef','post_up']
xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
#xpath2 = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
path_list = [xpath for i in range(len(url_list))]
ps = False


# In[5]:


url_list


# In[6]:


get_multi(url_list,path_list,ps = ps)


# In[ ]:


tables= get_ptables(url_list,path_list)


# In[ ]:


year = 2023

save_tables(tables,year,playoffs = True)


# In[ ]:




