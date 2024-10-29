#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
'''from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
'''
from pathlib import Path
# Step 1: Create a session and load the page
url1 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=0-2+Feet+-+Very+Tight&PerMode=Totals'
url2 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=2-4+Feet+-+Tight&PerMode=Totals'
url3 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=4-6+Feet+-+Open&PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/opponent-shots-closest-defender?CloseDefDistRange=6%2B+Feet+-+Wide+Open&PerMode=Totals'
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
def get_oppshots(years,ps = False):
    shots = ["0-2%20Feet%20-%20Very%20Tight","2-4%20Feet%20-%20Tight","4-6%20Feet%20-%20Open","6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv','tight.csv','open.csv','wide_open.csv']
    folder = '/opp_shooting/'
    stype ="Regular%20Season"
    if ps == True:
        folder = '/playoffs/opp_shooting/'
        stype ="Playoffs"

    for year in years:
        i = 0
        for shot in shots:
            season = str(year)+'-'+str(year+1 - 2000)
            
            part1 = "https://stats.nba.com/stats/leaguedashoppptshot?CloseDefDistRange="
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
                          
                          }
            new_columns2 = {'FREQ%':'Freq%',

             'TEAM_ABBREVIATION':'TEAM',
                     '3FG FREQ%': '3FG Freq%',
                          'EFG%': 'eFG%',
                           
                          '2FG FREQ%': '2FG Freq%'}
            df = df.rename(columns = new_columns)
            df = df.rename(columns = new_columns2)
            #print(df.columns)

            df = df [['TEAM', 'GP', 'G', 'Freq%', 'FGM', 'FGA', 'FG%', 'eFG%', '2FG Freq%',
       '2FGM', '2FGA', '2FG%', '3FG Freq%', '3PM', '3PA', '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col]*=100
            term = terms[i]
            path = str(year+1)+folder+term
         
            df.to_csv(path,index = False)
            print(path)
            i+=1
get_oppshots([2024],ps=False)


# In[2]:


#url_list = [url1]#
def get_multi(url_list,playoffs = False):
    if playoffs == True:
        p ='/playoffs'
    else:
        p = ''
        
    for i in range(2024,2025):
        
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
    


# In[3]:


#get_multi(url_list,playoffs= False)


# In[4]:


#tables = get_tables(url_list)
#terms = ['opp_shooting/very_tight.csv','opp_shooting/tight.csv','opp_shooting/open.csv','opp_shooting/wide_open.csv']
#terms = ['2023/playoffs/'+t for t in terms]
#jsons =  ['opp_shooting/very_tight.json','opp_shooting/tight.json','opp_shooting/open.json','opp_shooting/wide_open.json']
#for i in range(len(terms)):
#    df = tables[i]
#    df.to_csv(terms[i],index = False)
    #df.to_json(jsons[i])
    #df.to_csv('2023/'+terms[i],index = False)
    #df.to_json('2023/'+jsons[i])


# In[ ]:




