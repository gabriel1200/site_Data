#!/usr/bin/env python
# coding: utf-8

# In[12]:


import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import string
#url_list = [cs,pullup]
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import requests

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
def get_index():
    teams_response = requests.get("https://api.pbpstats.com/get-teams/nba")
    teams = teams_response.json()
    team_dict = {}
    for team in teams['teams']:
        team_dict[team['text']] = team['id']
    players_response = requests.get("https://api.pbpstats.com/get-all-players-for-league/nba")
    players = players_response.json()["players"]
    player_dict = dict([(player.lower(),num) for num,player in players.items()])
  
    return player_dict,team_dict

def get_ptables(url_list,path_list):
    data = []
    driver = webdriver.Chrome()
    for i in range(len(url_list)):
        url = url_list[i]
        xpath = path_list[i]
        print(url)
        
        driver.get(url)
        element = WebDriverWait(driver, 20).until(
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
def get_defense(year,ps = False):
    
    defense = 'https://www.nba.com/stats/players/defense-dash-overall?PerMode=Totals'
    url_list = [defense]
    #url_list =[url +'&SeasonType=Regular+Season'for url in url_list]
    url_list =[defense+'&Season='+str(year)+'-'+str(year+1 - 2000)]
    if ps == False:
        url_list =[url +'&SeasonType=Regular+Season'for url in url_list]
        path = str(year+1) +'/defense/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = path+ 'dfg.csv'
    else:
        url_list = [ url+'&SeasonType=Playoffs'for url in url_list]
        path = str(year+1) + '/playoffs/'+'defense/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = path+'dfg_p.csv'
   
        

    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
    #xpath2 = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
    path_list = [xpath for i in range(len(url_list))]
    frames = get_ptables(url_list,path_list)
    df = frames[0]
    df.to_csv(filename,index = False)
def wowy_statlog(stat,start_year,ps =False):
    if ps == False:
        s_type = 'Regular Season'
    elif ps == 'all':
        s_type = 'All'
    else:
        s_type = 'Playoffs'
        print('Playoffs')
    player_dict,team_dict= get_index()
    frames = []
    for season in range(start_year,2024):
        if (season)%100 <=9:
            zero = '0'
        else:
            zero = ''
        season_s = str(season-1)+'-'+zero+str((season)%100)
        url = "https://api.pbpstats.com/get-on-off/nba/stat"
        for team in team_dict.keys():
            params = {
                "Season": season_s,
                "SeasonType": s_type,
                "TeamId": team_dict[team],
                "Stat": stat, # for all options for Stat, see the list below

            }
            response = requests.get(url, params=params)
            response_json = response.json()
            #print(response_json)
            df = pd.DataFrame(response_json['results'])
            df['Team'] = team
            df['Year'] = season
            df['Season'] = season_s
            #break
            #print(df)
            frames.append(df)
        print(season)
    return pd.concat(frames)
def update_log(filename,stat,ps = False):

    df = wowy_statlog(stat,2023,ps)
    df.to_csv(filename,index =False)
    
#stat = 'FG2APctBlocked'
# At Rim Shot Frequency - Defense
stat= "AtRimAccuracyOpponent"
filename = '2023/defense/rim_acc.csv'
#update_log(filename,stat)
filename = '2023/playoffs/defense/rim_acc_p.csv'


update_log(filename,stat,ps = True)

stat2 ="AtRimFrequencyOpponent"

filename = '2023/defense/rimfreq.csv'
#update_log(filename,stat2)

filename = '2023/playoffs/defense/rimfreq_p.csv'
update_log(filename,stat2,ps = True)

get_defense(2022,ps=True)


# In[11]:


def create_folders():
    for year in range(2014,2024):
        path = str(year) +'/defense/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = str(year) +'/playoffs'+'/defense/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
# create_folders()


# In[27]:


'''
filename = 'dfg_p.csv'
df = pd.read_csv(filename)
for year in range(2014,2024):
    path = str(year) +'/playoffs/'+'/defense/'
    year_df = df[df.year==year]
    print(year_df)
    year_df.to_csv(path+'dfg.csv',index = False)
  '''      


# In[ ]:




