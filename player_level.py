#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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



# In[ ]:


#url_list = [cs,pullup]
from selenium.webdriver.support.select import Select

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def get_ptables(url_list,path_list):
    data = []
    driver = webdriver.Chrome()
    for i in range(len(url_list)):
        url = url_list[i]
        xpath = path_list[i]
        print(url)
        
        driver.get(url)
        element = WebDriverWait(driver, 12).until(
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


# In[ ]:


def get_multi(url_list,path_list):
    for i in range(2018,2022):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        tables = get_ptables(year_url,path_list)
        temp = tables[1]
        temp.columns = temp.columns.droplevel() 
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #temp
        temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        tables[1] = temp

        tables[1] = temp
        path = str(i+1)+'/player_tracking/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        name_list = ['drives','wide_open','close_6','touches','cs','pullup','passing']
        for i in range(len(name_list)):
            tables[i].to_csv(path+name_list[i]+'.csv',index = False)
        
        


# In[ ]:


cs ='https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
pullup ='https://www.nba.com/stats/players/pullup?PerMode=Totals'

touches = 'https://www.nba.com/stats/players/touches?PerMode=Totals'
drives = 'https://www.nba.com/stats/players/drives?PerMode=Totals'

wide_open = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
close = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals&dir=D&sort=PLUSMINUS'
passing = 'https://www.nba.com/stats/players/passing?PerMode=Totals'
url_list = [drives,wide_open,close,touches,cs,pullup,passing]
name_list = ['drives','wide_open','close_6','touches','cs','pullup','passing']
xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
#xpath2 = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
path_list = [xpath for i in range(len(url_list))]


# In[ ]:


#get_multi(url_list,path_list)


# In[ ]:


tables= get_ptables(url_list,path_list)


# In[ ]:


temp = tables[1]
temp.columns = temp.columns.droplevel() 
#temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
#temp
temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
tables[1] = temp

tables[1] = temp
for i in range(len(name_list)):
    tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
    tables[i].to_csv('2023/player_tracking/'+name_list[i]+'.csv',index = False)


# In[ ]:





# In[ ]:




