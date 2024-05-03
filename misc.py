#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
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
def get_tables(url_list):
    xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[3]/table'
    data = []
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)

    for url in url_list:
        print(url)
        
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        driver.implicitly_wait(20)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))

        df= dfs[-1]

        data.append(df)
    driver.close()
    return data
def get_playtypes(years,ps= False,p_or_t='p'):
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
    plays = ['tran','pr_ball','spot','iso','roll','post','misc','oreb','cut','handoff','off_screen']

    frames = []
    data_columns= ['TEAM', 'GP', 'POSS', 'FREQ%', 'PPP', 'PTS', 'FGM', 'FGA', 'FG%',
       'EFG%', 'FTFREQ%', 'TOVFREQ%', 'SFFREQ%', 'AND ONEFREQ%', 'SCOREFREQ%',
       'PERCENTILE']
    if type =="P":
        data_columns= ['PLAYER_NAME','PLAYER_ID','TEAM', 'GP', 'POSS', 'FREQ%',
                   'PPP', 'PTS', 'FGM', 'FGA', 'FG%','EFG%', 'FTFREQ%', 'TOVFREQ%', 'SFFREQ%', 'AND ONEFREQ%', 'SCOREFREQ%','PERCENTILE']
        
    for year in years:
        ssn = str(year)+'-'+str(year+1 - 2000)
        i = 0
        for play in playtypes:
            half1 = "https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode=Totals&PlayType="+play+"&PlayerOrTeam="+type+"&SeasonType="+stype+"&SeasonYear="
            half2 = "&TypeGrouping=offensive"
            term = terms[i]
            url = (
                        
                        half1+ str(ssn)+half2
                        
                    )
            #print(url)
            json = requests.get(url,headers = headers).json()
            data = json["resultSets"][0]["rowSet"]
            
            columns = json["resultSets"][0]["headers"]

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
                df2.to_csv(path,index = False)
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
years = [2023]
get_playtypes(years,ps=True)
def update_player_master(year,ps=False):
    trail = ''
    if ps == True:
        trail ='_p'
    years=[year-1]
    frames = get_playtypes(years,ps=ps,p_or_t='p')

    old =pd.read_csv('playtype'+trail+'.csv')
    old = old[old.year!=year]
    print(frames.columns)
    new = pd.concat([old,frames])
    new.to_csv('playtype'+trail+'.csv',index=False)
    return new
new = update_player_master(2024,ps=True)
new


# In[2]:


new['year']


# In[3]:


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


# In[4]:


#get_multi(url_list,playoffs = False)


# In[5]:


#terms = ['data/teampullup.csv','data/teamcatchshoot.csv','data/teamundersix.csv','data/teamiso.csv','data/teamtransition.csv']
#frames = get_tables(url_list)
terms = ['playtype/handoff.csv','playtype/iso.csv','playtype/trans.csv','playtype/bh.csv','playtype/rollman.csv','playtype/postup.csv','playtype/spotup.csv',
         'playtype/cut.csv','playtype/offscreen.csv','playtype/putback.csv','playtype/misc.csv','playtype/drives.csv']


# In[6]:


#df = pd.read_csv('2024/playtype/spotup.csv')
#df


# In[7]:


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


# In[8]:


df = pd.read_csv('playtype.csv')
print(df['playtype'].unique())


# In[ ]:





# In[ ]:





# In[ ]:




