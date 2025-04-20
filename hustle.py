#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests

def get_hustle(year,ps=False):
    stype="Playoffs"
    if ps == False:
        stype="Regular%20Season"
    season = str(year-1) +'-'+ str(year)[-2:]
    url = 'https://stats.nba.com/stats/leaguehustlestatsplayer?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season='+season+'&SeasonSegment=&SeasonType='+stype +'&TeamID=0&VsConference=&VsDivision=&Weight='

    url2 = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=SpeedDistance&Season='+season+'&SeasonSegment=&SeasonType='+stype+'&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
    #url3 = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&MeasureType=Advanced='+season+'&SeasonSegment=&SeasonType='+stype+'&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
    url3="https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season="+season+"&SeasonSegment=&SeasonType="+stype+"&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
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
    df = pd.DataFrame(data, columns=columns)
    print(df)
    #return df

    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",

        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }
    json = requests.get(url2,headers = headers).json()
    data = json["resultSets"][0]["rowSet"]
    #print(len(data))
    print('Data Length')
                
    columns = json["resultSets"][0]["headers"]
    #print(columns)
    #print(data)
    
    df2 = pd.DataFrame(data, columns=columns)
    df.drop(columns=['MIN'],inplace=True)
    print('Data Length')
    print(len(df))
    print(len(df2))

    
    print('Frame Length')
    
    json = requests.get(url3,headers = headers).json()
    data = json["resultSets"][0]["rowSet"]
    
    print('Data Length')
                
    columns = json["resultSets"][0]["headers"]
    #print(columns)
    #print(data)
    
    df3 = pd.DataFrame(data, columns=columns)
    print(df3.columns)
    print(len(df3))
    df3 = df3[['PLAYER_ID','POSS']]
    
    
    
    collist=[col for col in df2.columns if col not in df.columns]
    collist.append('PLAYER_ID')
    df2=df2[collist]
    combo_df = df.merge(df2,on=['PLAYER_ID'])
    
    print(combo_df)
    combo_df = combo_df.merge(df3)
    print(combo_df)
    combo_df['year'] = year
    
    print(len(combo_df))
    return combo_df
def hustle_master(ps=False):
    trail = '_ps'
    pfolder='/'
    pfolder='/playoffs/'
    if ps == False:
        trail = ''
        pfolder='/'
        
    data_rs = []
    old_df=pd.read_csv('hustle.csv')
    old_df=old_df[old_df.year<2025]
    data_rs.append(old_df)
    for year in range(2025,2026):

        df = get_hustle(year,ps=ps)

        data_rs.append(df)
    hustle = pd.concat(data_rs)

    hustle.to_csv('hustle'+trail+'.csv',index = False)
    return hustle
ps=True
hustle = hustle_master(ps=ps)
hustle


# In[2]:


print(hustle.columns)


# In[ ]:




