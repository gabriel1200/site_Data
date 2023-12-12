#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import time
import requests

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support.select import Select

# Step 1: Create a session and load the page
'''
url1 = 'https://www.nba.com/stats/players/pullup?PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/isolation?PerMode=Totals'
url5 = 'https://www.nba.com/stats/players/transition?PerMode=Totals&dir=D&sort=POSS'
'''



# In[6]:


headers = {
                    "Host": "stats.nba.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",

                    "Connection": "keep-alive",
                    "Referer": "https://stats.nba.com/"
                }
url = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Passing&Season=2023-24&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
json = requests.get(url,headers = headers).json()
data = json["resultSets"][0]["rowSet"]
columns = json["resultSets"][0]["headers"]
df = pd.DataFrame.from_records(data, columns=columns)
df


# In[5]:


df['FT_AST'].max()


# In[ ]:


#url_list = [cs,pullup]

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
def save_tables(folder_choice,tables,year,name_list, playoffs= False):
    if playoffs == True:
        path = str(year)+'/playoffs/'+'/'+folder_choice+'/'
    else:
        path = str(year)+'/'+folder_choice+'/'
    if len(tables)>1:
        table = tables[1]
        #print(table)
        temp = table
        temp.columns = temp.columns.droplevel() 
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #temp
        temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        table = temp

        tables[1] = temp
        #print(tables)
        for i in range(len(name_list)):
            #tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
            tables[i].to_csv(path+name_list[i]+'.csv',index = False)
    else:
        table = tables[0]
        #print(table)
        temp = table
        #temp.columns = temp.columns.droplevel() 
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #temp
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #table = temp

        #tables[0] = temp
        #print(tables)
        for i in range(len(name_list)):
            #tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
            tables[i].to_csv(path+name_list[i]+'.csv',index = False)

def get_ptables(url_list,path_list):
    data = []
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    cookie_check = False
    for i in range(len(url_list)):
        url = url_list[i]
        xpath = path_list[i]
        print(url)
        
        driver.get(url)
        accept_path = '//*[@id="onetrust-accept-btn-handler"]'
        time.sleep(5)

        if EC.presence_of_element_located((By.XPATH, accept_path)) and cookie_check == False:
            driver.find_element(By.XPATH, accept_path).click() 
            cookie_check = True
            time.sleep(1)
        

        element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        #time.sleep(5)
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
        #needed table is at the end
        df= dfs[-1]

       
        data.append(df)
    driver.close()
    return data


# In[ ]:


def get_multi(url_list,path_list,name_list,folder_choice,ps =False,start_year = 2016,end_year=2024):
    for i in range(start_year,end_year):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        tables = get_ptables(year_url,path_list)
        year =i+1
        
        save_tables(folder_choice,tables,year,name_list,playoffs = ps)
       
        


# In[ ]:


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
#url_list =[url +'&SeasonType=Regular+Season'for url in url_list]


xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
#xpath2 = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
path_list = [xpath for i in range(len(url_list))]

hurl_list= ['https://www.nba.com/stats/players/hustle?PerMode=Totals']
h_paths = [xpath for i in range(len(hurl_list))]

ps = True


# In[ ]:


folder_choice = 'player_tracking'
name_list = ['drives','wide_open','close_6','touches','cs','pullup','passing',\
            'paint','elbow','oreb','dreb','shoot_ef','post_up']
get_multi(url_list,path_list,name_list,folder_choice,ps = False,start_year=2023)


# In[ ]:


#get_multi(url_list,path_list,name_list,folder_choice,ps = False,start_year=2023)
folder_choice = 'hustle'
name_list = ['hustle']
hurl_list =[url +'&SeasonType=Playoffs' for url in hurl_list]
#get_multi(hurl_list,h_paths,name_list,folder_choice,ps = False,start_year=2023)

#get_multi(hurl_list,h_paths,name_list,folder_choice,ps = True,start_year=2018,end_year=2024)


# In[ ]:





# In[6]:


frames_normal= []
for i in range(2017,2025):
    path = str(i) + '/hustle/hustle.csv'
    df = pd.read_csv(path)
    df['year'] = i
    frames_normal.append(df)
master= pd.concat(frames_normal)




frames_ps= []
for i in range(2017,2024):
    path = str(i) + '/playoffs/hustle/hustle.csv'
    df = pd.read_csv(path)
    df['year'] = i
    frames_ps.append(df)
master_ps= pd.concat(frames_ps)
master.to_csv('hustle.csv',index = False)

master_ps.to_csv('hustle_ps.csv', index = False)


# In[ ]:




