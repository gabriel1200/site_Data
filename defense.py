#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
import time
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
'''


# In[22]:


def pull_data(url):
    headers = {
                                    "Host": "stats.nba.com",
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                                    "Accept": "application/json, text/plain, */*",
                                    "Accept-Language": "en-US,en;q=0.5",
                                    "Accept-Encoding": "gzip, deflate, br",

                                    "Connection": "keep-alive",
                                    "Referer": "https://stats.nba.com/"
                                }
    json = requests.get(url,headers = headers).json()
    data = json["resultSets"][0]["rowSet"]
    columns = json["resultSets"][0]["headers"]
    df = pd.DataFrame.from_records(data, columns=columns)
    return df
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
def update_master(master_file,new_file,year):
    df = pd.read_csv(new_file)
    old = pd.read_csv(master_file)
    old = old[old.year!=year]
    df['year'] = year
    old = pd.concat([old,df])
    old.to_csv(master_file,index = False)
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

        # Wait for the page to fully load

        driver.implicitly_wait(10)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        accept_path = '//*[@id="onetrust-accept-btn-handler"]'
        time.sleep(4)
        if EC.presence_of_element_located((By.XPATH, accept_path)) and cookie_check == False:
            driver.find_element(By.XPATH, accept_path).click() 
            cookie_check = True
            time.sleep(1)
        element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        
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
def get_defense(url,year,ps = False):
    
    defense = url
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
    df['year'] = year
    return df
def prep_dfg(dfg):
    dfg = dfg.drop(columns = ['CLOSE_DEF_PERSON_ID','PLAYER_LAST_TEAM_ID'])
    dfg.columns = ['PLAYER', 'TEAM', 'AGE', 'POSITION', 'GP', 'G', 'FREQ%', 'DFGM', 'DFGA',
       'DFG%', 'FG%', 'DIFF%']
    for col in dfg:
        if '%' in col:
            dfg[col]*=100
    return dfg
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
    for season in range(start_year,2025):
        if (season)%100 <=9:
            zero = '0'
        else:
            zero = ''
        season_s = str(season-1)+'-'+zero+str((season)%100)
        print(season_s)
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
            #print(df)
            #break
            #print(df)
            frames.append(df)
        print(season)
    return pd.concat(frames)
def update_log(filename,stat,ps = False):

    df = wowy_statlog(stat,2024,ps)
    df.to_csv(filename,index =False)
    
#stat = 'FG2APctBlocked'
# At Rim Shot Frequency - Defense
stat= "AtRimAccuracyOpponent"
filename = '2024/defense/rim_acc.csv'
update_log(filename,stat)
#filename = '2023/playoffs/defense/rim_acc_p.csv'


#update_log(filename,stat,ps = False)
#update_master('rim_acc.csv',filename)

stat2 ="AtRimFrequencyOpponent"


#update_log(filename,stat2)

#filename = '2023/playoffs/defense/rimfreq_p.csv'
filename = '2024/defense/rimfreq.csv'
update_log(filename,stat2,ps = False)

def update_dash():
    
    url="https://stats.nba.com/stats/leaguedashptdefend?College=&Conference=&Country=&DateFrom=&DateTo=&DefenseCategory=Overall&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season=2023-24&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="

    df = pull_data(url)
    df = prep_dfg(df)
    old = pd.read_csv('dfg.csv')
    old = old[old.year!=2023]
    df['year'] = 2024
    df = df.round(2)
    old = pd.concat([old,df])
    old.to_csv('dfg.csv',index = False)
    
    df.to_csv('2024/defense/dfg.csv',index = False)
    
    url = "https://stats.nba.com/stats/leaguedashptdefend?College=&Conference=&Country=&DateFrom=&DateTo=&DefenseCategory=Less%20Than%206Ft&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season=2023-24&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
    
    df = pull_data(url)
    df = prep_dfg(df)
    old = pd.read_csv('rimdfg.csv')
    old = old[old.year!=2024]
    df['year'] = 2024
    df = df.round(2)
    old = pd.concat([old,df])
    old.to_csv('rimdfg.csv',index = False)
    df.to_csv('2024/defense/rimdfg.csv',index = False)
    

#update_master('rimfreq.csv',filename)
update_dash()
#year = 2023
#filename = '2023/defense/rim_acc.csv'
#update_master('rim_acc.csv',filename,year)
#year = 2023
#filename = '2023/defense/rimfreq.csv'
#update_master('rimfreq.csv',filename,year)
year =2024
filename = '2024/defense/rimfreq.csv'
update_master('rimfreq.csv',filename,year)
filename = '2024/defense/dfg.csv'
update_master('dfg.csv',filename,year)
filename = '2024/defense/rimdfg.csv'
update_master('rimdfg.csv',filename,year)
filename = '2024/defense/rim_acc.csv'
update_master('rim_acc.csv',filename,year)


# In[8]:


def create_folders(new_folder):
    for year in range(2014,2024):
        path = str(year) +'/'+new_folder+'/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = str(year) +'/playoffs'+'/'+new_folder+'/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)

create_folders('hustle')
masters =['rimfreq','rim_acc','dfg']
#temp = pd.read_csv('dfg_p.csv')
#temp = temp.rename(columns = {'year':'Year'})
#temp.to_csv('dfg_p.csv',index = False)
def update_masters(year,masters,ps = False):
    
    if ps == False:
        trail = ''
        path = str(year)+'/defense/'
    else:
        trail = '_p'
        path = str(year)+'/playoffs/defense/'
    for file in masters:
        print(file)
        df = pd.read_csv(file+trail+'.csv')
        df = df[df.year<year]
        new = pd.read_csv(path+file+trail+'.csv')
        df = pd.concat([df,new])
        df.to_csv(file+trail+'csv',index = False)
#update_masters(2023,masters,ps = False)
#temp = pd.read_csv('dfg_p.csv')
#temp = temp.rename(columns = {'Year':'year'})
#temp.to_csv('dfg_p.csv',index = False)     


# In[9]:


'''
filename = 'dfg_p.csv'
df = pd.read_csv(filename)
for year in range(2014,2024):
    ps = '/playoffs/'
    #ps = ''
    path = str(year) +ps+'/defense/'
    year_df = df[df.year==year]
    print(year_df)
    year_df.to_csv(path+'dfg.csv',index = False)
'''  

