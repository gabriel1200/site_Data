#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import time
import requests
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support.select import Select

# Step 1: Create a session and load the page

url1 = 'https://www.nba.com/stats/players/pullup?PerMode=Totals'
url2 = 'https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
url3 = 'https://www.nba.com/stats/players/defense-dash-lt6?PerMode=Totals'
url4 = 'https://www.nba.com/stats/teams/isolation?PerMode=Totals'
url5 = 'https://www.nba.com/stats/players/transition?PerMode=Totals&dir=D&sort=POSS'
'''



# In[2]:


def prep_passing(passing):
    pid = passing['PLAYER_ID']
    tid = passing['TEAM_ID']
    ft_ast = passing['FT_AST']
    passing = passing.drop(columns = ['PLAYER_ID','TEAM_ID','FT_AST'])
    passing.columns = ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'PassesMade', 'PassesReceived',
           'AST', 'SecondaryAST', 'PotentialAST', 'AST PTSCreated', 'ASTAdj',
           'AST ToPass%', 'AST ToPass% Adj']
    passing['PLAYER_ID'] = pid
    passing['TEAM_ID']=tid
    passing['FT_AST'] = ft_ast
    return passing
def format_drives(df):
    df.columns = [col.split('DRIVE_')[-1] for col in df.columns]
    df.columns = [col.split('DRIVE_')[-1] for col in df.columns]
    df.columns = [col.replace('_PCT','%') for col in df.columns]
    replace_columns = {'PASSES':'PASS', 'PASSES%':'PASS%', 'PLAYER_NAME':'PLAYER', 'TEAM_ABBREVIATION':'TEAM', 'TOV':'TO'}
    df = df.rename(columns=replace_columns)
    df = df[['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'DRIVES', 'FGM', 'FGA', 'FG%',
           'FTM', 'FTA', 'FT%', 'PTS', 'PTS%', 'PASS', 'PASS%', 'AST', 'AST%',
           'TO', 'TOV%', 'PF', 'PF%']]
    for col in df:
        if '%' in col:
            df[col]*=100
    return df
def prep_touches(touches):
    pid = touches['PLAYER_ID']
    tid = touches['TEAM_ID']
    touches = touches.drop(columns=['PLAYER_ID','TEAM_ID'])
    touches.columns = ['Player', 'Team', 'GP', 'W', 'L', 'MIN', 'PTS', 'TOUCHES',
       'Front CTTouches', 'Time OfPoss', 'Avg Sec PerTouch',
       'Avg Drib PerTouch', 'PTS PerTouch', 'ElbowTouches', 'PostUps',
       'PaintTouches', 'PTS PerElbow Touch', 'PTS PerPost Touch',
       'PTS PerPaint Touch']
    touches['PLAYER_ID'] = pid
    touches['TEAM_ID']= tid
    return touches
def prep_cs(cs):
    cs =cs.drop(columns=['PLAYER_ID', 'TEAM_ID', 'W','L'])
    cs.columns
    pts = cs['CATCH_SHOOT_PTS']

    cs = cs[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'CATCH_SHOOT_FGM',
           'CATCH_SHOOT_FGA', 'CATCH_SHOOT_FG_PCT',
           'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A', 'CATCH_SHOOT_FG3_PCT',
           'CATCH_SHOOT_EFG_PCT']]
    cs.columns = ['PLAYER', 'TEAM', 'GP', 'MIN',  'FGM', 'FGA', 'FG%', '3PM', '3PA',
           '3P%', 'eFG%']
    cs['PTS'] = pts
    for col in cs:
        if '%' in col:
            cs[col]*=100
    return cs
def prep_elbow(elbow):
    pid = elbow['PLAYER_ID']
    tid = elbow['TEAM_ID']
    elbow = elbow.drop(columns = ['PLAYER_ID','TEAM_ID'])
    elbow.columns = ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'Touches', 'ElbowTouches',
           'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'PTS', 'PTS%', 'PASS',
           'PASS%', 'AST', 'AST%', 'TO', 'TOV%', 'PF', 'PF%']
    elbow['PLAYER_ID'] = pid
    elbow['TEAM_ID']  = tid
    for col in elbow:
        if '%' in col:
            elbow[col]*=100
    return elbow
def prep_post(post):
    pid = post['PLAYER_ID']
    tid = post['TEAM_ID']
    post= post.drop(columns = ['PLAYER_ID','TEAM_ID'])
    post.columns = ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'Touches', 'PostUps', 'FGM',
       'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'PTS', 'PTS%', 'PASS', 'PASS%',
       'AST', 'AST%', 'TO', 'TOV%', 'PF', 'PF%']
    post['PLAYER_ID'] = pid
    post['TEAM_ID']  = tid
    for col in post:
        if '%' in col:
            post[col]*=100
    return post
def prep_paint(paint):
    pid = paint['PLAYER_ID']
    tid = paint['TEAM_ID']
    paint = paint.drop(columns = ['PLAYER_ID','TEAM_ID'])
    paint.columns = ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'Touches', 'PostUps', 'FGM',
       'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'PTS', 'PTS%', 'PASS', 'PASS%',
       'AST', 'AST%', 'TO', 'TOV%', 'PF', 'PF%']
    paint['PLAYER_ID'] = pid
    paint['TEAM_ID']  = tid
    for col in paint:
        if '%' in col:
            paint[col]*=100
    return paint
def prep_pullup(pullup):
    pid = pullup['PLAYER_ID']
    tid = pullup['TEAM_ID']
    points = pullup['PULL_UP_PTS']
    pullup = pullup.drop(columns = ['PLAYER_ID','TEAM_ID','PULL_UP_PTS'])
    pullup.columns = ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN','FGM', 'FGA', 'FG%',
       '3PM', '3PA', '3P%', 'eFG%']
    pullup['PTS'] = points
    pullup['PLAYER_ID'] = pid
    pullup['TEAM_ID']  = tid
    for col in pullup:
        if '%' in col:
            pullup[col]*=100
    return pullup
def get_tracking(years,ps = False):
    stype ="Regular%20Season"
    if ps == True:
        stype="Playoffs"
    frames = []
    shots = ["Drives","CatchShoot","Passing","Possessions","ElbowTouch","PostTouch","PaintTouch","PullUpShot"]
    for year in years:
        season = str(year)+'-'+str(year+1 - 2000)
        for shot in shots:

            part1 = "https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType="

            part2 = "&Season="
            part3="&SeasonSegment=&SeasonType="+stype+"&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="


            url = part1+shot+part2+season+part3
            #url = "https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Drives&Season=2023-24&SeasonSegment=&SeasonType=Regular%20Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
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

            frames.append(df)
    return frames
def tracking_save(years,ps=False):
    if ps == False:
        trail = ''
    else:
        trail='/playoffs'
    for year in years:
        folder = str(year)+trail+'/player_tracking/'
        frames = get_tracking([year-1],ps=ps)
        drives = format_drives(frames[0])
        drives.to_csv(folder+'drives.csv',index = False)
        cs = prep_cs(frames[1])
        cs.to_csv(folder+'cs.csv',index = False)
        passing = prep_passing(frames[2])
        passing.to_csv(folder+'passing.csv',index = False)
        touches = prep_touches(frames[3])
        touches.to_csv(folder+'touches.csv',index = False)

        elbow = prep_elbow(frames[4])
        elbow.to_csv(folder+'elbow.csv',index = False)

        post = prep_post(frames[5])
        post.to_csv(folder+'post_up.csv',index = False)

        paint = prep_paint(frames[6])
        paint.to_csv(folder+'paint.csv',index = False)

        pullup = prep_pullup(frames[7])
        pullup.to_csv(folder+'pullup.csv',index = False)

tracking_save([2024],ps=True)


# In[3]:


year = 2024
path = str(year)+'/player_tracking/pullup.csv'
    
#df2 = pd.read_csv(path)
#df2


# In[4]:


'''
for year in range(2014,2025):
    path = str(year)+'/player_tracking/passing.csv'
    
    df2 = pd.read_csv(path)
    if 'AST PTSCreated.1' in df2.columns:
        print(df2)
        new_df = pd.DataFrame()
        new_df = df2[df2.columns[:-1]]
        #print(new_df)
        old_col = ['ASTAdj', 'AST ToPass%', 'AST ToPass% Adj']
        #df2 = df2.drop(columns = ['AST ToPass% Adj'])
        new_df.columns= ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'PassesMade', 'PassesReceived',
               'AST', 'SecondaryAST', 'PotentialAST', 'AST PTSCreated',
               'ASTAdj', 'AST ToPass%', 'AST ToPass% Adj']
        new_df.to_csv(path, index = False)
for year in range(2014,2024):
    path = str(year)+'/playoffs/player_tracking/passing.csv'
    df2 = pd.read_csv(path)
    if 'AST PTSCreated.1' in df2.columns:
        print(df2)
        new_df = pd.DataFrame()
        new_df = df2[df2.columns[:-1]]
        #print(new_df)
        old_col = ['ASTAdj', 'AST ToPass%', 'AST ToPass% Adj']
        #df2 = df2.drop(columns = ['AST ToPass% Adj'])
        new_df.columns= ['PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'PassesMade', 'PassesReceived',
               'AST', 'SecondaryAST', 'PotentialAST', 'AST PTSCreated',
               'ASTAdj', 'AST ToPass%', 'AST ToPass% Adj']
        new_df.to_csv(path, index = False)
'''


# In[ ]:





# In[5]:


'''
cs ='https://www.nba.com/stats/players/catch-shoot?PerMode=Totals'
pullup ='https://www.nba.com/stats/players/pullup?PerMode=Totals'

touches = 'https://www.nba.com/stats/players/touches?PerMode=Totals'
drives = 'https://www.nba.com/stats/players/drives?PerMode=Totals'

passing = 'https://www.nba.com/stats/players/passing?PerMode=Totals'
paint = 'https://www.nba.com/stats/players/paint-touch?PerMode=Totals'
elbow = 'https://www.nba.com/stats/players/elbow-touch?PerMode=Totals'
#oreb = 'https://www.nba.com/stats/players/offensive-rebounding?PerMode=Totals'
#dreb = 'https://www.nba.com/stats/players/defensive-rebounding?PerMode=Totals'
#shoot_ef = 'https://www.nba.com/stats/players/shooting-efficiency?'
post_up = 'https://www.nba.com/stats/players/tracking-post-ups?PerMode=Totals'
url_list = [drives,touches,cs,pullup,passing,paint,elbow,post_up]
#url_list =[url +'&SeasonType=Playoffs' for url in url_list]
#url_list =[url +'&SeasonType=Regular+Season'for url in url_list]


xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
#xpath2 = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
path_list = [xpath for i in range(len(url_list))]

hurl_list= ['https://www.nba.com/stats/players/hustle?PerMode=Totals']
h_paths = [xpath for i in range(len(hurl_list))]

ps = True
folder_choice = 'player_tracking'
name_list = ['drives','touches','cs','pullup','passing',\
            'paint','elbow','oreb','post_up']
'''


# In[6]:


#get_multi(url_list,path_list,name_list,folder_choice,ps = False,start_year=2023)


# In[ ]:





# In[ ]:





# In[7]:


'''
#url_list = [cs,pullup]

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
def save_tables(folder_choice,tables,year,name_list, playoffs= False):
    if playoffs == True:
        path = str(year)+'/playoffs/'+'/'+folder_choice+'/'
    else:
        path = str(year)+'/'+folder_choice+'/'
    if len(tables)>1:
        table = tables[1]
        #print(table)
        temp = table
        
        temp.columns = temp.columns.droplevel() 
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #temp
        temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        table = temp

        tables[1] = temp
        #print(tables)
        for i in range(len(name_list)):
            #tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
            tables[i].to_csv(path+name_list[i]+'.csv',index = False)
    else:
        table = tables[0]
        #print(table)
        temp = table
        #temp.columns = temp.columns.droplevel() 
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #temp
        #temp = temp.drop(columns = ['Unnamed: 18_level_1','Unnamed: 19_level_1','Unnamed: 20_level_1', 'Unnamed: 21_level_1','Unnamed: 22_level_1'])
        #table = temp

        #tables[0] = temp
        #print(tables)
        for i in range(len(name_list)):
            #tables[i].to_csv('player_tracking/'+name_list[i]+'.csv',index = False)
            tables[i].to_csv(path+name_list[i]+'.csv',index = False)

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
        accept_path = '//*[@id="onetrust-accept-btn-handler"]'
        time.sleep(5)

        if EC.presence_of_element_located((By.XPATH, accept_path)) and cookie_check == False:
            driver.find_element(By.XPATH, accept_path).click() 
            cookie_check = True
            time.sleep(1)
        

        element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        #time.sleep(5)
        if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)
        
        dropdown1 = Select(driver.find_element(By.XPATH, xpath))
        dropdown1.select_by_index(0)

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')
        

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))
        #needed table is at the end
        df= dfs[-1]

       
        data.append(df)
    driver.close()
    return data
def get_multi(url_list,path_list,name_list,folder_choice,ps =False,start_year = 2016,end_year=2024):
    for i in range(start_year,end_year):
        
        season = '&Season='+str(i)+'-'+str(i+1 - 2000)
        year_url = [url+season for url in url_list]
        tables = get_ptables(year_url,path_list)
        year =i+1
        
        save_tables(folder_choice,tables,year,name_list,playoffs = ps)
       
        
frames_normal= []
for i in range(2017,2025):
    path = str(i) + '/hustle/hustle.csv'
    df = pd.read_csv(path)
    df['year'] = i
    frames_normal.append(df)
master= pd.concat(frames_normal)




frames_ps= []
for i in range(2017,2024):
    path = str(i) + '/playoffs/hustle/hustle.csv'
    df = pd.read_csv(path)
    df['year'] = i
    frames_ps.append(df)
master_ps= pd.concat(frames_ps)
master.to_csv('hustle.csv',index = False)

master_ps.to_csv('hustle_ps.csv', index = False)
'''


# In[ ]:




