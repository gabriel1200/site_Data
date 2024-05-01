#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import os
#url_list = [url1]#
import pandas as pd
from bs4 import BeautifulSoup
import requests
def get_dribbleshots(years,ps = False):
    dribbles=['0%20Dribbles','1%20Dribble','2%20Dribbles','3-6%20Dribbles','7%2B%20Dribbles']
    terms = ['0','1','2','3_6','7+']
    folder = '/player_shooting/'
    sfolder=''
    stype = "Regular%20Season"
    if ps == True:
        stype="Playoffs"
        sfolder = "/playoffs"
    dataframe=[]
    for year in years:
        i = 0
        for dribble in dribbles:
            #print(dribble)
            season = str(year)+'-'+str(year+1 - 2000)
            part1 = "https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange="
            part2 = "&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season="

            part3 = "&SeasonSegment=&SeasonType="+stype+"&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=&VsConference=&VsDivision=&Weight="
            url = part1+dribble+part2+season+part3
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
            print(json.keys())
            data = json["resultSets"][0]["rowSet"]
            columns = json["resultSets"][0]["headers"]
            df = pd.DataFrame.from_records(data, columns=columns)
            json = requests.get(url,headers = headers).json()
            data = json['resultSets'][0]["rowSet"]
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
            df = df [['PLAYER', 'TEAM', 'AGE', 'GP', 'G', 'FREQ%', 'FGM', 'FGA', 'FG%',
                   'EFG%', '2FG FREQ%', '2FGM', '2FGA', '2FG%', '3FG FREQ%', '3PM', '3PA',
                   '3P%']]
            for col in df.columns:
                if '%' in col or 'PERC' in col:
                    df[col]*=100
            term = terms[i]
            df['dribbles'] = term
            df['year']=year+1
            dataframe.append(df)

            i+=1
        return pd.concat(dataframe)

def master_dribble(year,ps = False):
    trail='_ps'
    if ps == False:
        trail=''
    old = pd.read_csv('dribbleshot'+trail+'.csv')
    df = get_dribbleshots([year],ps=True)
    year+=1

    old = old[old.year!=year]
    new_master = pd.concat([old,df])
    new_master.to_csv('dribbleshot'+trail+'.csv',index=False)
    return new_master
df = master_dribble(2023,ps=True)
df


# In[15]:


df


# In[ ]:




