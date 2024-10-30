#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
#url_list = [url1]#
import pandas as pd
from bs4 import BeautifulSoup
import requests

'''
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service

import time
'''
from pathlib import Path
# Step 1: Create a session and load the page
url4 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url1 = 'https://www.nba.com/stats/players/shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url_list = [url1,url2,url3,url4]

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
#get_playershots(years):

#get_multi(url_list,playoffs = False)
def get_playershots(years,ps = False):
    shots = ["0-2%20Feet%20-%20Very%20Tight","2-4%20Feet%20-%20Tight","4-6%20Feet%20-%20Open","6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv','tight.csv','open.csv','wide_open.csv']
    folder = '/player_shooting/'
    sfolder=''
    stype = "Regular%20Season"
    if ps == True:
        stype="Playoffs"
        sfolder = "/playoffs"
    for year in years:
        i = 0
        for shot in shots:
            season = str(year)+'-'+str(year+1 - 2000)
            part1 = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange="
            part2 = "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="

            part3 = "&SeasonSegment=&SeasonType="+stype+"&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1+shot+part2+season+part3
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
            new_columns = {'FG2A_FREQUENCY':'2FG FREQ%',
             'FG2_PCT':'2FG%',
             'FG2A':'2FGA',
             'FG2M':'2FGM',
             'FG3A_FREQUENCY':'3FG FREQ%',
             'FG3_PCT':'3P%',
             'FG3A':'3PA',
             'FG3M':'3PM',
             'EFG_PCT':'EFG%',
             'FG_PCT':'FG%',
             'FGA_FREQUENCY':'FREQ%',
             'PLAYER_NAME':'PLAYER',
             'PLAYER_LAST_TEAM_ABBREVIATION':'TEAM'}
            df = df.rename(columns = new_columns)

            print(df.columns)
            df = df [['PLAYER_ID','PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'FREQ%', 'FGM', 'FGA', 'FG%',
                   'EFG%', '2FG FREQ%', '2FGM', '2FGA', '2FG%', '3FG FREQ%', '3PM', '3PA',
                   '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col]*=100
            term = terms[i]
            path = str(year+1)+sfolder+folder+term
            df.to_csv(path,index = False)
            i+=1
#get_playershots([i for i in range(2013,2024)],ps=False)
get_playershots([i for i in range(2024,2025)],ps=False)
def master_shooting(playoffs = False):
    data =[]
    for i in range(2014,2026):
        if playoffs == False:
            p = ''
        else:
            p='/playoffs'

        path = str(i)+p+'/player_shooting/'
        files = ['wide_open','open','tight','very_tight']
        for file in files:
            df = pd.read_csv(path+file+'.csv')
            df['year'] = i
            df['shot_type'] =file
            data.append(df)
    master = pd.concat(data)
    return master
master= master_shooting() 
master.to_csv('player_shooting.csv',index = False)


# In[2]:


#master= master_shooting(playoffs=True) 
#master.to_csv('player_shooting_p.csv',index = False)


# In[ ]:





# In[ ]:




