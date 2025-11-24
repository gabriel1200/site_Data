#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

from bs4 import BeautifulSoup
from pathlib import Path
import time
import requests
end_year=2026


# In[ ]:


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
    df = df[['PLAYER_ID','PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'DRIVES', 'FGM', 'FGA', 'FG%',
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
    cs =cs.drop(columns=['TEAM_ID', 'W','L'])
    pid=cs['PLAYER_ID']
    cs.columns
    pts = cs['CATCH_SHOOT_PTS']

    cs = cs[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'CATCH_SHOOT_FGM',
           'CATCH_SHOOT_FGA', 'CATCH_SHOOT_FG_PCT',
           'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A', 'CATCH_SHOOT_FG3_PCT',
           'CATCH_SHOOT_EFG_PCT']]
    cs.columns = ['PLAYER', 'TEAM', 'GP', 'MIN',  'FGM', 'FGA', 'FG%', '3PM', '3PA',
           '3P%', 'eFG%']
    cs['PTS'] = pts
    cs['PLAYER_ID']=pid
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
def tracking_master(years,ps=False):
    if ps == False:
        trail = ''
    else:
        trail='/playoffs'

    all_frames = []
    for year in years:
        folder = str(year)+trail+'/player_tracking/'

        drives = pd.read_csv(folder+'drives.csv')
        drives['type']='drives'
        drives['Volume']= drives['DRIVES']

        cs = pd.read_csv(folder+'cs.csv')
        cs['type']='cs'
        elbow = pd.read_csv(folder+'elbow.csv')
        elbow['type']='elbow'
        post = pd.read_csv(folder+'post_up.csv')
        post['type']='post_up'
        pullup = pd.read_csv(folder+'pullup.csv')
        pullup['type']='pullup'
        paint= pd.read_csv(folder+'drives.csv')
        paint['type']='paint'
        year_master = pd.concat([drives,cs,elbow,paint,pullup,post])
        year_master['year']=year

        all_frames.append(year_master)
    return pd.concat(all_frames)
ps = False
trail =''
trail2=''
if ps == True:
    trail='_p'
    trail2='_ps'

tracking_save([i for i in range(end_year-1,end_year+1)],ps=ps)

#tracking_save([i for i in range(2014,2025)],ps=True)

new_master = tracking_master([i for i in range(2014,end_year+1)],ps=ps)
new_master.to_csv('tracking'+trail2+'.csv',index=False)


# In[ ]:


to_save=['PLAYER_ID','PLAYER', 'TEAM', 'GP', 'W', 'L', 'MIN', 'DRIVES', 'FGM', 'FGA', 'FG%',
       'FTM', 'FTA', 'FT%', 'PTS', 'PTS%', 'PASS', 'PASS%', 'AST', 'AST%',
       'TO', 'TOV%', 'PF', 'PF%', 'type', '3PM', '3PA', '3P%', 'eFG%',
       'Touches','year']
new_master = new_master[to_save]
new_master.to_csv('tracking'+trail+'.csv',index=False)


# In[ ]:




