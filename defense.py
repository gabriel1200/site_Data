#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import string
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
#url_list = [cs,pullup]



# In[ ]:


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
    #dfg = dfg.drop(columns = ['CLOSE_DEF_PERSON_ID','PLAYER_LAST_TEAM_ID'])
    print(dfg.columns)
    dfg = dfg.rename(columns={'DIFF%':'Diff%'})
    dfg.columns = ['PLAYER_ID','PLAYER', 'TEAM_ID','TEAM', 'POSITION', 'AGE','GP', 'G', 'FREQ%', 'DFGM', 'DFGA',
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
    for season in range(start_year,2026):
        if (season)%100 <=9:
            zero = '0'
        else:
            zero = ''
        season_s = str(season-1)+'-'+zero+str((season)%100)
        print(season_s)
        url = "https://api.pbpstats.com/get-on-off/nba/stat"
        for team in team_dict.keys():
            time.sleep(3)
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
            print(df.columns)
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

    df = wowy_statlog(stat,2025,ps)
    df.to_csv(filename,index =False)

#stat = 'FG2APctBlocked'
# At Rim Shot Frequency - Defense
stat= "AtRimAccuracyOpponent"
filename = '2025/defense/rim_acc.csv'
update_log(filename,stat,ps=False)
#filename = '2025/playoffs/defense/rim_acc.csv'


#update_log(filename,stat,ps = True)
#update_master('rim_acc.csv',filename)

stat2 ="AtRimFrequencyOpponent"


#update_log(filename,stat2)
filename = '2025/defense/rimfreq.csv'


update_log(filename,stat2,ps = False)
#filename = '2025/playoffs/defense/rimfreq.csv'
#update_log(filename,stat2,ps = True)

def update_dash(ps = False):
    stype = 'Regular%20Season'
    if ps == True:
        stype='Playoffs'

    url="https://stats.nba.com/stats/leaguedashptdefend?College=&Conference=&Country=&DateFrom=&DateTo=&DefenseCategory=Overall&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season=2023-24&SeasonSegment=&SeasonType="+stype+"&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="

    df = pull_data(url)
    df = prep_dfg(df)
    #old = pd.read_csv('dfg.csv')
    #old = old[old.year!=2024]
    df['year'] = 2025
    df = df.round(2)
    #old = pd.concat([old,df])
    #old.to_csv('dfg.csv',index = False)
    if ps == True:
         df.to_csv('2025/playoffs/defense/dfg.csv',index = False)
    else:
        df.to_csv('2025/defense/dfg.csv',index = False)

    url = "https://stats.nba.com/stats/leaguedashptdefend?College=&Conference=&Country=&DateFrom=&DateTo=&DefenseCategory=Less%20Than%206Ft&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season=2023-24&SeasonSegment=&SeasonType="+stype+"&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="

    df = pull_data(url)
    df = prep_dfg(df)
    #old = pd.read_csv('rimdfg.csv')
    #old = old[old.year!=2024]
    df['year'] = 2025
    df = df.round(2)
    #old = pd.concat([old,df])
    #old.to_csv('rimdfg.csv',index = False)
    if ps == True:
        df.to_csv('2025/playoffs/defense/rimdfg.csv',index = False)
    else:
        df.to_csv('2025/defense/rimdfg.csv',index = False)


#update_master('rimfreq.csv',filename)
update_dash()

#update_dash(ps = True)
#year = 2023
#filename = '2023/defense/rim_acc.csv'
#update_master('rim_acc.csv',filename,year)
#year = 2023
#filename = '2023/defense/rimfreq.csv'
#update_master('rimfreq.csv',filename,year)

'''
year =2024
filename = '2024/defense/rimfreq.csv'
update_master('rimfreq.csv',filename,year)
filename = '2024/defense/dfg.csv'
update_master('dfg.csv',filename,year)
filename = '2024/defense/rimdfg.csv'
update_master('rimdfg.csv',filename,year)
filename = '2024/defense/rim_acc.csv'
update_master('rim_acc.csv',filename,year)
'''


# In[ ]:


def create_folders(new_folder):
    for year in range(2014,2024):
        path = str(year) +'/'+new_folder+'/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = str(year) +'/playoffs'+'/'+new_folder+'/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)

#create_folders('hustle')
masters =['rimfreq','rim_acc','dfg','rimdfg']
#temp = pd.read_csv('dfg_p.csv')
#temp = temp.rename(columns = {'year':'Year'})
#temp.to_csv('dfg_p.csv',index = False)
def update_masters(masters,ps = False):
    trail = ''
    end_year = 2026
    if ps == True:
        end_year =2026
        trail = '_p'
    frames1 = []
    frames2=[]
    frames3= []
    frames4=[]
    frames = [frames1,frames2,frames3,frames4]
    i = 0
    for year in range(2014,end_year):

        if ps == False:

            path = str(year)+'/defense/'
        else:

            path = str(year)+'/playoffs/defense/'
        for file in masters:
            print(file)
            df = pd.read_csv(path+file+'.csv')
            frames[i].append(df)
            i=(i+1)%4

    for i in range(len(masters)):
        masterframe = pd.concat(frames[i])
        masterframe.to_csv(masters[i]+trail+'.csv',index = False)
        print(masterframe)
update_masters(masters,ps = False)
#update_masters(masters,ps = True)

#temp = pd.read_csv('dfg_p.csv')
#temp = temp.rename(columns = {'Year':'year'})
#temp.to_csv('dfg_p.csv',index = False)     


# In[ ]:


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

