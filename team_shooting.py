#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
#from selenium import webdriver
from bs4 import BeautifulSoup
import requests
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
'''
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
    start_year = 2023
    for i in range(start_year,2024):
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
    new_df = pd.concat(df_list)
    new_df['TEAMNAME'] = new_df['TEAM']
    df = pd.read_csv('team_shooting.csv')
    df = df[df.year <=start_year]
    names = dict(zip(df.TEAMNAME,df.TEAM))
    names['Los Angeles Clippers'] = 'LAC'
    names['Charlotte Bobcats'] = 'CHA'

    #names
    print(names)
    final_df = pd.concat([df,new_df])
    final_df.replace({'TEAM':names},inplace=True)
    final_df.loc[final_df['TEAMNAME'] =='Los Angeles Clippers', 'TEAM'] = 'LAC'
    final_df.loc[final_df['TEAMNAME'] =='Charlotte Bobcats', 'TEAM'] = 'CHA'

    return final_df

#df = multiyear_shooting(url_list,playoffs=False)
#print(df)
def get_teamshots(years,ps=False):
    shots = ["0-2%20Feet%20-%20Very%20Tight","2-4%20Feet%20-%20Tight","4-6%20Feet%20-%20Open","6%2B%20Feet%20-%20Wide%20Open"]
    terms = ['very_tight.csv','tight.csv','open.csv','wide_open.csv']
    folder = '/team_shooting/'
    stype = "Regular%20Season"
    if ps== True:
        folder = '/playoffs/team_shooting/'
        stype = "Playoffs"
    for year in years:
        i = 0
        frames = []
        for shot in shots:
            season = str(year)+'-'+str(year+1 - 2000)
            
            part1 = "https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange="
            part2 = "&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="

            part3 = "&SeasonSegment=&SeasonType="+stype+"&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1+shot+part2+season+part3
            #print(url)
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
            print(path)
            df.to_csv(path,index = False)
            frames.append(df)
            #print(df)
            i+=1
        year_df = pd.concat(frames)
        year_df.to_csv(str(year+1)+folder+'team_shooting.csv',index = False)
get_teamshots([2023],ps=True)


# In[2]:


#import pandas as pd
acr_dict = {'San Antonio Spurs': 'SAS',
 'Miami Heat': 'MIA',
 'Indiana Pacers': 'IND',
 'Oklahoma City Thunder': 'OKC',
 'Los Angeles Clippers': 'LAC',
 'Brooklyn Nets': 'BKN',
 'Portland Trail Blazers': 'POR',
 'Washington Wizards': 'WAS',
 'Atlanta Hawks': 'ATL',
 'Golden State Warriors': 'GSW',
 'Dallas Mavericks': 'DAL',
 'Memphis Grizzlies': 'MEM',
 'Houston Rockets': 'HOU',
 'Toronto Raptors': 'TOR',
 'Chicago Bulls': 'CHI',
 'Charlotte Bobcats': 'CHA',
 'Cleveland Cavaliers': 'CLE',
 'Milwaukee Bucks': 'MIL',
 'New Orleans Pelicans': 'NOP',
 'Boston Celtics': 'BOS',
 'Charlotte Hornets': 'CHA',
 'LA Clippers': 'LAC',
 'Detroit Pistons': 'DET',
 'Utah Jazz': 'UTA',
 'Philadelphia 76ers': 'PHI',
 'Minnesota Timberwolves': 'MIN',
 'Denver Nuggets': 'DEN',
 'Orlando Magic': 'ORL',
 'Los Angeles Lakers': 'LAL',
 'Phoenix Suns': 'PHX',
 'New York Knicks': 'NYK',
 'Sacramento Kings': 'SAC'}
name_dict = {'SAS': 'San Antonio Spurs',
 'MIA': 'Miami Heat',
 'IND': 'Indiana Pacers',
 'OKC': 'Oklahoma City Thunder',
 'BKN': 'Brooklyn Nets',
 'POR': 'Portland Trail Blazers',
 'WAS': 'Washington Wizards',
 'ATL': 'Atlanta Hawks',
 'GSW': 'Golden State Warriors',
 'DAL': 'Dallas Mavericks',
 'MEM': 'Memphis Grizzlies',
 'HOU': 'Houston Rockets',
 'TOR': 'Toronto Raptors',
 'CHI': 'Chicago Bulls',
 'CLE': 'Cleveland Cavaliers',
 'MIL': 'Milwaukee Bucks',
 'NOP': 'New Orleans Pelicans',
 'BOS': 'Boston Celtics',
 'CHA': 'Charlotte Hornets',
 'LAC': 'Los Angeles Clippers',
 'DET': 'Detroit Pistons',
 'UTA': 'Utah Jazz',
 'PHI': 'Philadelphia 76ers',
 'MIN': 'Minnesota Timberwolves',
 'DEN': 'Denver Nuggets',
 'ORL': 'Orlando Magic',
 'LAL': 'Los Angeles Lakers',
 'PHX': 'Phoenix Suns',
 'NYK': 'New York Knicks',
 'SAC': 'Sacramento Kings'}

shots = ['wide_open','open','tight','very_tight']
frames = []
for year in range(2014,2025):
    path = str(year)+'/opp_shooting/'
    for shot in shots:
        filepath = path+shot+'.csv'
        df = pd.read_csv(filepath)
        df['shot_coverage'] = shot
        df['year'] = year
        if year <2024:
            df['TEAM'] = df['TEAM'].map(acr_dict)
        df['TEAMNAME'] =df['TEAM'].map(name_dict)
        frames.append(df)
opp_master = pd.concat(frames)


opp_master.to_csv('opp_team_shooting.csv',index=False)
frames = []
for year in range(2014,2025):
    path = str(year)+'/playoffs/opp_shooting/'
    for shot in shots:
        filepath = path+shot+'.csv'
        df = pd.read_csv(filepath)
        df['shot_coverage'] = shot
        df['year'] = year
        if year<2024:
            df['TEAM'] = df['TEAM'].map(acr_dict)
        df['TEAMNAME'] =df['TEAM'].map(name_dict)
        frames.append(df)
opp_master = pd.concat(frames)

opp_master.to_csv('opp_team_shooting_ps.csv',index=False)

frames = []
for year in range(2014,2025):
    path = str(year)+'/opp_shooting/'
    for shot in shots:
        filepath = path+shot+'.csv'
        df = pd.read_csv(filepath)
        df['shot_coverage'] = shot
        df['year'] = year
        if year <2024:
            df['TEAM'] = df['TEAM'].map(acr_dict)
        df['TEAMNAME'] =df['TEAM'].map(name_dict)
        frames.append(df)
opp_master = pd.concat(frames)

#opp_master
frames = []
for year in range(2014,2025):
    path = str(year)+'/team_shooting/'
    for shot in shots:
        filepath = path+shot+'.csv'
        df = pd.read_csv(filepath)
        df['shot_coverage'] = shot
        df['year'] = year
        if year <2024:
            df['TEAM'] = df['TEAM'].map(acr_dict)
        df['TEAMNAME'] =df['TEAM'].map(name_dict)
        frames.append(df)
master = pd.concat(frames)
master.to_csv('team_shooting.csv',index = False)
frames = []
for year in range(2014,2025):
    path = str(year)+'/playoffs/team_shooting/'
    for shot in shots:
        filepath = path+shot+'.csv'
        df = pd.read_csv(filepath)
        df['shot_coverage'] = shot
        df['year'] = year
        if year <2024:
            df['TEAM'] = df['TEAM'].map(acr_dict)
        df['TEAMNAME'] =df['TEAM'].map(name_dict)
        frames.append(df)
master = pd.concat(frames)
master.to_csv('team_shooting_ps.csv',index = False)


# In[3]:


'''
old_df = pd.read_csv('team_shooting.csv')
temp = pd.read_csv('opp_team_shooting.csv')
temp['TEAMNAME'] = temp['TEAM']
temp['TEAM'] = temp['TEAMNAME'].map(name_dict)
temp.to_csv('opp_team_shooting.csv',index = False)
temp = pd.read_csv('opp_team_shooting_ps.csv')
temp['TEAMNAME'] = temp['TEAM']
temp['TEAM'] = temp['TEAMNAME'].map(name_dict)
temp.to_csv('opp_team_shooting_ps.csv',index = False)
'''


# In[4]:


opp_master


# In[ ]:





# In[ ]:




