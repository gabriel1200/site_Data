#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
#from selenium import webdriver
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
# Step 1: Create a session and load the page
'''
url1 = 'https://www.nba.com/stats/players/pullup?PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/isolation?PerMode=Totals'
url5 = 'https://www.nba.com/stats/players/transition?PerMode=Totals&dir=D&sort=POSS'
'''
cs ='https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
pullup ='https://www.nba.com/stats/players/pullup?PerMode=Totals'

handoff = 'https://www.nba.com/stats/teams/hand-off?PerMode=Totals'
iso ='https://www.nba.com/stats/teams/isolation?PerMode=Totals'
trans ='https://www.nba.com/stats/teams/transition?PerMode=Totals'
bh='https://www.nba.com/stats/teams/ball-handler?PerMode=Totals'
rollman = 'https://www.nba.com/stats/teams/roll-man?PerMode=Totals'
postup = 'https://www.nba.com/stats/teams/playtype-post-up?PerMode=Totals'
spotup = 'https://www.nba.com/stats/teams/spot-up?PerMode=Totals'
cut = 'https://www.nba.com/stats/teams/cut?PerMode=Totals'
offscreen = 'https://www.nba.com/stats/teams/off-screen?PerMode=Totals'
putbacks = 'https://www.nba.com/stats/teams/putbacks?PerMode=Totals'
misc = 'https://www.nba.com/stats/teams/playtype-misc?PerMode=Totals'
#drives = 'https://www.nba.com/stats/teams/drives?PerMode=Totals'
#url_list = [url1,url2,url3,url4,url5]
url_list=[handoff,iso,trans,bh,rollman,postup,spotup,cut,offscreen,putbacks,misc]
#url_list =[url +'&SeasonType=Playoffs' for url in url_list]
url_list =[url +'&SeasonType=Regular+Season'for url in url_list]
#add tag specifying that the url list is for the regular seasonx
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
#url_list = [cs,pullup]

def get_playtypes(years,ps= False,p_or_t='t',defense= False):
    field_side = "offensive"
    if defense == True:
        field_side= "defensive"
    if p_or_t =='p':
        type ='P'
    else:
        type='T'
    stype = "Regular+Season"
    trail =''
    if ps == True:
        stype = "Playoffs"
        trail='/playoffs'
    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",

        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }
    playtypes = ['Transition','PRBallHandler','Spotup','Isolation','PRRollman','Postup','Misc','OffRebound','Cut','Handoff','OffScreen',]
    terms = ['trans.csv','bh.csv','spotup.csv','iso.csv','rollman.csv','postup.csv','misc.csv','putback.csv','cut.csv','handoff.csv','offscreen.csv']
    plays = ['tran','pr_ball','spot','iso','pr_roll','post','misc','oreb','cut','hand_off','off_screen']

    frames = []
    data_columns= ['TEAM', 'GP', 'POSS', 'FREQ%', 'PPP', 'PTS', 'FGM', 'FGA', 'FG%',
       'EFG%', 'FTFREQ%', 'TOVFREQ%', 'SFFREQ%', 'AND ONEFREQ%', 'SCOREFREQ%',
       'PERCENTILE']
    if type =="P":
        data_columns= ['PLAYER_NAME','PLAYER_ID','TEAM','TEAM_ID', 'GP', 'POSS', 'FREQ%',
                   'PPP', 'PTS', 'FGM', 'FGA', 'FG%','EFG%', 'FTFREQ%', 'TOVFREQ%', 'SFFREQ%', 'AND ONEFREQ%', 'SCOREFREQ%','PERCENTILE']
        
    for year in years:
        ssn = str(year)+'-'+str(year+1 - 2000)
        i = 0
        for play in playtypes:
            
            half1 = "https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode=Totals&PlayType="+play+"&PlayerOrTeam="+type+"&SeasonType="+stype+"&SeasonYear="
            half2 = "&TypeGrouping="+field_side
            term = terms[i]
            url = (
                        
                        half1+ str(ssn)+half2
                        
                    )
            #print(url)
            print(url)
            json = requests.get(url,headers = headers).json()
            data = json["resultSets"][0]["rowSet"]
            
            columns = json["resultSets"][0]["headers"]
            time.sleep(2)

            df2 = pd.DataFrame.from_records(data, columns=columns)
                #df2.columns
          
            df2 = df2.rename(columns={'TEAM_NAME':'TEAM','POSS_PCT':'FREQ%','EFG_PCT':'EFG%','FG_PCT':'FG%',
                                          
                                          'TOV_POSS_PCT':'TOVFREQ%','PLUSONE_POSS_PCT':'AND ONEFREQ%','FT_POSS_PCT':'FTFREQ%','SCORE_POSS_PCT':'SCOREFREQ%','SF_POSS_PCT':'SFFREQ%'})
            for col in df2.columns:
                if '%' in col or 'PERC' in col:
                    df2[col]*=100
            #print(df2)
            path = str(year+1)+trail+'/playtype/'+term
          
            df2 = df2.round(2)
            
            df2 = df2[data_columns]
            
            #print(df2)
            if p_or_t.lower() =='t':
                if defense == False:
                    df2.to_csv(path,index = False)
                    
                
                df2['playtype'] = plays[i]
                df2['year']=year+1
                 
                frames.append(df2)
            else:
                #print(df2)
                df2['playtype'] = plays[i]
                df2['year']=year+1
                print(len(df2))
                frames.append(df2)
          
            i+=1
            
        if p_or_t.lower() =='p':
            data = pd.concat(frames)
            
            map_terms ={
            'PLAYER_NAME': 'Player',
                 'TEAM_ID':'team_id',
          
            'TEAM': 'Team',
            'GP': 'GP',
            'POSS': 'Poss',
            'FREQ%': '% Time',
            'PPP': 'PPP',
            'PTS': 'Points',
            'FGM': 'FGM',
            'FGA': 'FGA',
            'FG%': 'FG%',
            'EFG%': 'aFG%',
            'FTFREQ%': '%FT',
            'TOVFREQ%': '%TO',
            'SFFREQ%': '%SF',
            'AND ONEFREQ%': 'AND ONEFREQ%',
            'SCOREFREQ%': '%Score',
            'PERCENTILE': 'Percentile',
            'playtype': 'playtype'
        }

            data.rename(columns=map_terms,inplace=True)
            return data
        else:
             data = pd.concat(frames)
             map_terms ={
    
            'PTS':'Points',
            'TEAM': 'full_name'}
             data.rename(columns=map_terms,inplace=True)
             team_dict= {'New York Knicks': 'NYK',
             'New Orleans Pelicans': 'NOP',
             'Oklahoma City Thunder': 'OKC',
             'Golden State Warriors': 'GSW',
             'Brooklyn Nets': 'BKN',
             'Houston Rockets': 'HOU',
             'Miami Heat': 'MIA',
             'Phoenix Suns': 'PHX',
             'Philadelphia 76ers': 'PHI',
             'Sacramento Kings': 'SAC',
             'Los Angeles Clippers': 'LAC',
             'LA Clippers':'LAC',
             'Cleveland Cavaliers': 'CLE',
             'Detroit Pistons': 'DET',
             'Los Angeles Lakers': 'LAL',
             'Denver Nuggets': 'DEN',
             'Orlando Magic': 'ORL',
             'Indiana Pacers': 'IND',
             'Boston Celtics': 'BOS',
             'Toronto Raptors': 'TOR',
             'Charlotte Bobcats': 'CHA',
             'Washington Wizards': 'WAS',
             'Milwaukee Bucks': 'MIL',
             'Minnesota Timberwolves': 'MIN',
             'Atlanta Hawks': 'ATL',
             'Portland Trail Blazers': 'POR',
             'Memphis Grizzlies': 'MEM',
             'San Antonio Spurs': 'SAS',
             'Dallas Mavericks': 'DAL',
             'Utah Jazz': 'UTA',
             'Chicago Bulls': 'CHI',
             'Charlotte Hornets': 'CHA'}
            
             data['Team'] = data['full_name'].map(team_dict)
            
             return data

def update_player_master(year,ps=False):
    trail = ''
    if ps == True:
        trail ='_p'
    years=[year-1]
    frames = get_playtypes(years,ps=ps,p_or_t='p') 
    print('playtype'+trail+'.csv')

    old =pd.read_csv('playtype'+trail+'.csv')
    old = old[old.year!=year]
    print(frames.columns)
    new = pd.concat([old,frames])
    new.to_csv('playtype'+trail+'.csv',index=False)
    return new
playoffs = True
new = update_player_master(2025,ps=playoffs)

#new2 = update_player_master(2025,ps=False)

years = [2024]

offense = get_playtypes(years,ps=playoffs)
defense = get_playtypes([2024],ps=playoffs,defense=True)
def update_team_masters(year,offense,defense,ps=False):
    trail = ''
    if ps == True:
        trail='_p'
    offpath= 'teamplay'+trail+'.csv'
    defpath='teamplayd'+trail+'.csv'
    old_off =pd.read_csv(offpath)
    old_def =pd.read_csv(defpath)

    old_off = old_off[old_off.year!=year]

    new_off = pd.concat([old_off,offense])

    old_def = old_def[old_def.year!=year]

    new_def = pd.concat([old_def,defense])
    #new_def.drop(columns=['TEAM','PTS'],inplace=True)
    #new_off.drop(columns=['TEAM','PTS'],inplace=True)

    new_off.to_csv(offpath,index=False)
    new_def.to_csv(defpath,index=False)
update_team_masters(2025,offense,defense,ps=playoffs)


# In[2]:


#url_list = [url1]#
def get_multi(url_list,playoffs = False):
    if playoffs == True:
        p ='/playoffs/'
    else:
        p=''
    # get table per year, create corresponding directory if it doesn't exist
    
    for i in range(2023,2024):
        
        season = '&SeasonYear='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        frames = get_tables(year_url)

 
        path = str(i+1)+p+'/playtype/'
        output_dir = Path(path)
        output_dir.mkdir(parents=True, exist_ok=True)
        #terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
        terms = ['handoff.csv','iso.csv','trans.csv','bh.csv','rollman.csv','postup.csv','spotup.csv',
                 'cut.csv','offscreen.csv','putback.csv','misc.csv']
        terms = [ path+t for t in terms]
        
        for i in range(len(terms)):
            df = frames[i]
            df.to_csv(terms[i],index = False)


# In[3]:


#get_multi(url_list,playoffs = False)


# In[4]:


#terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
#frames = get_tables(url_list)
terms = ['playtype/handoff.csv','playtype/iso.csv','playtype/trans.csv','playtype/bh.csv','playtype/rollman.csv','playtype/postup.csv','playtype/spotup.csv',
         'playtype/cut.csv','playtype/offscreen.csv','playtype/putback.csv','playtype/misc.csv','playtype/drives.csv']


# In[5]:


#df = pd.read_csv('2024/playtype/spotup.csv')
#df


# In[6]:


def add_synergy():
    df = pd.read_csv('../synergy/full_data/playtype_p.csv')
    for i in range(2014,2024):
        path = str(i)+'/playoffs/synergy/'
        isExist = os.path.exists(path)
        if not isExist:

       # Create a new directory because it does not exist
           os.makedirs(path)
        year_df = df[df.year == i]
        print(year_df.head())
        year_df.to_csv(path+'playtype.csv')


# In[7]:


def create_macro(data,play,playlist):
        num_col = ['% Time', 'PPP', 'Points', 'FGM', 'FGA','FG%', 'aFG%', '%FT', '%TO', '%SF', '%Score','Poss','GP']
        perc = [ 'PPP','FG%', 'aFG%', '%FT', '%TO', '%SF', '%Score']

        print(len(data.columns))
     
        data = data.loc[data.playtype.isin(playlist)]
        #data['playtype'] = play
        #data['GP']/=3
        group = data.groupby(['Player','Team','year'])
        s_list = []
        #print(p_df)
        for col in num_col:
            if col in perc:
                series =group.apply(w_avg, col, 'Poss')
            #poss = pd.Series([sum(df['Poss'])], index=['Poss'])
            #series = pd.concat([series,poss],keys =['series'])
            #print(series)
        #print(series)

            elif col =='GP':
                series = group.mean()[col]
                print(series)
         
            else:
                series = group.sum()[col]
            s_list.append(series)

        player_df = pd.concat(s_list)
        print(len(player_df.columns))
        player_df.columns = num_col
        #print(player_df)
        new_data = player_df.reset_index()
        new_data['playtype'] = play
        
        return new_data
def w_avg(df, values, weights):
    #print(values)
    #print(weights)

    d = df[values]
    w = df[weights]
    if values == 'Poss':

        return d.sum()
    
    return (d * w).sum() / w.sum()
ps=True
if ps ==False:
    df = pd.read_csv('playtype.csv')
    print(df.columns)
    #year = 2024
    #df=df[df.year==year].reset_index(drop=True)
    data_names = {'pr_ball':'on_ball','iso':'on_ball','pr_roll':'play_finish','post':'on_ball','hand_off':'motion'
                ,'oreb':'play_finish','cut':'play_finish','off_screen':'motion','spot':'play_finish','tran':'tran','misc':'misc'}
    df['playtype'] = df['playtype'].map(data_names)
    pstyle= df.groupby(['Player','Team','GP','PLAYER_ID','playtype','year','TEAM_NAME','team_id']).sum()[['Poss','% Time','FGM','FGA','Points']].reset_index()
    pstyle['PPP'] = pstyle['Points']/pstyle['Poss']

    #pstyle.to_csv('play_style_p.csv',index=False)
    pstyle.to_csv('playstyle.csv',index=False)
else:
    df = pd.read_csv('playtype_p.csv')
    print(df.columns)
    #year = 2024
    #df=df[df.year==year].reset_index(drop=True)
    data_names = {'pr_ball':'on_ball','iso':'on_ball','pr_roll':'play_finish','post':'on_ball','hand_off':'motion'
                ,'oreb':'play_finish','cut':'play_finish','off_screen':'motion','spot':'play_finish','tran':'tran','misc':'misc'}
    df['playtype'] = df['playtype'].map(data_names)
    pstyle= df.groupby(['Player','Team','GP','PLAYER_ID','playtype','year','TEAM_NAME','team_id']).sum()[['Poss','% Time','FGM','FGA','Points']].reset_index()
    pstyle['PPP'] = pstyle['Points']/pstyle['Poss']

    pstyle.to_csv('play_style_p.csv',index=False)
    #pstyle.to_csv('playstyle.csv',index=False)


# In[8]:


pstyle[pstyle.year==2014]


# In[9]:


team_dict= {'New York Knicks': 'NYK',
             'New Orleans Pelicans': 'NOP',
             'Oklahoma City Thunder': 'OKC',
             'Golden State Warriors': 'GSW',
             'Brooklyn Nets': 'BKN',
             'Houston Rockets': 'HOU',
             'Miami Heat': 'MIA',
             'Phoenix Suns': 'PHX',
             'Philadelphia 76ers': 'PHI',
             'Sacramento Kings': 'SAC',
             'Los Angeles Clippers': 'LAC',
             'LA Clippers':'LAC',
             'Cleveland Cavaliers': 'CLE',
             'Detroit Pistons': 'DET',
             'Los Angeles Lakers': 'LAL',
             'Denver Nuggets': 'DEN',
             'Orlando Magic': 'ORL',
             'Indiana Pacers': 'IND',
             'Boston Celtics': 'BOS',
             'Toronto Raptors': 'TOR',
             'Charlotte Bobcats': 'CHA',
             'Washington Wizards': 'WAS',
             'Milwaukee Bucks': 'MIL',
             'Minnesota Timberwolves': 'MIN',
             'Atlanta Hawks': 'ATL',
             'Portland Trail Blazers': 'POR',
             'Memphis Grizzlies': 'MEM',
             'San Antonio Spurs': 'SAS',
             'Dallas Mavericks': 'DAL',
             'Utah Jazz': 'UTA',
             'Chicago Bulls': 'CHI',
             'Charlotte Hornets': 'CHA'}
temp=pd.read_csv('teamplay_p.csv')

temp['Team']=temp['full_name'].map(team_dict)
temp.to_csv('teamplay_p.csv',index=False)


temp=pd.read_csv('teamplayd_p.csv')

temp['Team']=temp['full_name'].map(team_dict)
temp.to_csv('teamplayd_p.csv',index=False)


# In[10]:


'''
old['Player'].value_counts()
old=pd.read_csv('playtype.csv')
old = old[old.year==2024]
temp = pd.read_csv('playtype_backup.csv')
temp = temp[temp.year==2024]
id_map=dict(zip(old['Player'],old['PLAYER_ID']))
temp['PLAYER_ID'] = temp['Player'].map(id_map)
trans = pd.concat([old,temp])

trans = trans.drop_duplicates(subset=['Player','Team','GP','playtype','year'])
backed = pd.read_csv('playtype.csv')
backed = backed[backed.year<2024]
new_save = pd.concat([backed,trans])
new_save.to_csv('playtype.csv',index=False)
df = pd.read_csv('playtype.csv')
print(df.columns)
year = 2024
df=df[df.year==year].reset_index(drop=True)
data_names = {'pr_ball':'on_ball','iso':'on_ball','pr_roll':'play_finish','post':'on_ball','hand_off':'motion'
               ,'oreb':'play_finish','cut':'play_finish','off_screen':'motion','spot':'play_finish','tran':'tran','misc':'misc'}
df['playtype'] = df['playtype'].map(data_names)
pstyle= df.groupby(['Player','Team','GP','PLAYER_ID','playtype','year']).sum()[['Poss','% Time','FGM','FGA','Points']].reset_index()
pstyle['PPP'] = pstyle['Points']/pstyle['Poss']
oldstyle = pd.read_csv('play_style.csv')
oldstyle = oldstyle[oldstyle.year!=year]


newstyle = pd.concat([oldstyle,pstyle])
newstyle.to_csv('play_style.csv',index=False)
'''


# In[ ]:





# In[ ]:





# In[11]:


'''
df=pd.read_csv('playtype.csv')
df=df[df.year>2013]
df.to_csv('playtype.csv',index=False)
'''


# In[ ]:




