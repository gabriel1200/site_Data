#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nba_api.stats.static import players,teams
import pandas as pd
import requests
import sys
import os
import time
from datetime import datetime

def format_date_to_url(date):
    # Convert date from YYYYMMDD to datetime object
    date_obj = datetime.strptime(str(date), '%Y%m%d')
    
    # Format the date as MM%2FDD%2FYYYY
    formatted_date = date_obj.strftime('%m%%2F%d%%2F%Y')
    
    return formatted_date

# Example usage

def pull_data(url):
    headers = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/",
        "Origin": "https://stats.nba.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    json = requests.get(url,headers = headers).json()

    if len(json["resultSets"])== 1:

        
        data = json["resultSets"][0]["rowSet"]
        #print(data)
        columns = json["resultSets"][0]["headers"]
        #print(columns)
        
        df = pd.DataFrame.from_records(data, columns=columns)
    else:

        data = json["resultSets"]["rowSet"]
        #print(json)
        columns = json["resultSets"]["headers"][1]['columnNames']
        #print(columns)
        df = pd.DataFrame.from_records(data, columns=columns)

    time.sleep(1.2)
    return df


def pull_game_level(dateframe, start_year,end_year,ps=False,unit='Player'):
    stype = 'Regular%20Season'
    trail=''
    if ps == True:
        stype='{stype}'
        trail='ps'
    if unit.lower()=='team':
        trail+='_team'
    dframes = []
    shotcolumns = ['FGA_FREQUENCY', 'FGM', 'FGA', 'FG_PCT', 'EFG_PCT', 'FG2A_FREQUENCY', 'FG2M', 'FG2A', 'FG2_PCT', 
                   'FG3A_FREQUENCY', 'FG3M', 'FG3A', 'FG3_PCT']
    
 
    for year in range(start_year, end_year):
        count=0
        countframe=dateframe[dateframe.year==year].reset_index()
        print(len(dateframe))
        print(len(countframe))
        year_frame=[]
        test = False
        game_date = 20241208
        if test != False:
            countframe=countframe[countframe.GAME_DATE<game_date]

        year_dates = countframe['GAME_DATE'].unique().tolist()
        if os.path.exists('year_files/'+str(year)+trail+'_games.csv'):
            df= pd.read_csv('year_files/'+str(year)+trail+'_games.csv')
            df['date']=df['date'].astype(int)
            df.sort_values(by='date',ascending=False)
            df.drop_duplicates(subset=['date','PLAYER_ID','TEAM_ID'],inplace=True)
            if test != False:
                df=df[df.date<game_date]
            
            year_frame.append(df)

            year_dates=[int(date) for date in year_dates if date not in df['date'].unique().tolist()]
            year_dates=year_dates[::-1]
            

        season = str(year - 1) + '-' + str(year)[-2:]
        print(year_dates)

        try:

            date = ''


            url = f'https://stats.nba.com/stats/leaguedashteamstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
        
            df = pull_data(url)
            print(df)
            print('frame1')

            url2 = f'https://stats.nba.com/stats/leaguedashteamstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df2 = pull_data(url2)
            print(df2)
            print('frame2')

                 
            url3 = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam={unit}&PlayerPosition=&PtMeasureType=Passing&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df3 = pull_data(url3)

            print(df3)
            print('frame3')


            url4 = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam={unit}&PlayerPosition=&PtMeasureType=Drives&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df4 = pull_data(url4)

            print(df4)
            print('frame4')


            url5 = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam={unit}&PlayerPosition=&PtMeasureType=Possessions&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df5 = pull_data(url5)

            print(df5)
            print('frame5')


            url6 = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam={unit}&PlayerPosition=&PtMeasureType=Rebounding&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df6 = pull_data(url6)

            print(df6)
            print('frame6')
            shots = ["0-2%20Feet%20-%20Very%20Tight","2-4%20Feet%20-%20Tight","4-6%20Feet%20-%20Open","6%2B%20Feet%20-%20Wide%20Open"]
            shot=shots[0]
            url7 = (
                f'https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange={shot}'
                f'&College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick='
                f'&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange='
                f'&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0'
                f'&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience='
                f'&PlayerPosition=&Season={season}'
                f'&SeasonSegment=&SeasonType={stype}&ShotClockRange='
                f'&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange='
                f'&VsConference=&VsDivision=&Weight='
            )
            df7 = pull_data(url7)


    
            term = 'very_tight_'
            df7.rename(columns={col: term + col for col in shotcolumns}, inplace=True)
            
            shot=shots[1]
            url8 = (
                f'https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange={shot}'
                f'&College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick='
                f'&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange='
                f'&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0'
                f'&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience='
                f'&PlayerPosition=&Season={season}'
                f'&SeasonSegment=&SeasonType={stype}&ShotClockRange='
                f'&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange='
                f'&VsConference=&VsDivision=&Weight='
            )
            df8 = pull_data(url8)

            term = 'tight_'
            df8.rename(columns={col: term + col for col in shotcolumns},inplace=True)

            print(df8)
            print('frame8')
            shot=shots[2]
            url9 = (
                f'https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange={shot}'
                f'&College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick='
                f'&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange='
                f'&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0'
                f'&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience='
                f'&PlayerPosition=&Season={season}'
                f'&SeasonSegment=&SeasonType={stype}&ShotClockRange='
                f'&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange='
                f'&VsConference=&VsDivision=&Weight='
            )
            df9 = pull_data(url9)

            term = 'open_'
            df9.rename(columns={col: term + col for col in shotcolumns},inplace=True)

            print(df9)
            print('frame9')
            shot=shots[3]
            url10 = (
                f'https://stats.nba.com/stats/leaguedashteamptshot?CloseDefDistRange={shot}'
                f'&College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick='
                f'&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange='
                f'&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0'
                f'&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience='
                f'&PlayerPosition=&Season={season}'
                f'&SeasonSegment=&SeasonType={stype}&ShotClockRange='
                f'&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange='
                f'&VsConference=&VsDivision=&Weight='
            )
            df10 = pull_data(url10)

            term = 'wide_open_'
            df10.rename(columns={col: term + col for col in shotcolumns},inplace=True)


            print(df10)
            print('frame10')
            
            url11 = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=' + date + '&DateTo=' + date + '&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=PullUpShot&Season=' + season + '&SeasonSegment=&SeasonType='+stype+'&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df11 = pull_data(url11) 
            shotcolumns2=shotcolumns+['EFG%']
            term='pullup_'
            df11.rename(columns={col: term + col for col in shotcolumns2},inplace=True)

            print(df11)
            print('frame11')
            
            url12 = 'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=' + date + '&DateTo=' + date + '&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Team&PlayerPosition=&PtMeasureType=Efficiency&Season=' + season + '&SeasonSegment=&SeasonType='+stype+'&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='


            df12 = pull_data(url12) 


            print(df12)
            print('frame12')
            
            url13=f"https://stats.nba.com/stats/leaguedashteamshotlocations?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&DistanceRange=By%20Zone&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
            
            df13=pull_data(url13)

            zone_columns=[ 'TEAM_ID', 'TEAM_ABBREVIATION',
             'RA_FGM', 'RA_FGA', 'RA_FG_PCT',               # Restricted Area
             'ITP_FGM', 'ITP_FGA', 'ITP_FG_PCT',             # In The Paint (Non-RA)
             'MID_FGM', 'MID_FGA', 'MID_FG_PCT',             # Mid Range
             'LEFT_CORNER_3_FGM', 'LEFT_CORNER_3_FGA', 'LEFT_CORNER_3_FG_PCT',  # Left Corner 3
             'RIGHT_CORNER_3_FGM', 'RIGHT_CORNER_3_FGA', 'RIGHT_CORNER_3_FG_PCT', # Right Corner 3
      

                           # All Corner 3s
             'ABOVE_BREAK_3_FGM', 'ABOVE_BREAK_3_FGA', 'ABOVE_BREAK_3_FG_PCT', 
                   'BACKCOURT_FGM', 'BACKCOURT_FGA', 'BACKCOURT_FG_PCT', # Right Corner 3
                          
                          'CORNER_3_FGM', 'CORNER_3_FGA', 'CORNER_3_FG_PCT'  ]  # Above the Break 3

            df13.columns=zone_columns


            print(df13)
            print('frame13')
            
            url14=f"https://stats.nba.com/stats/leaguedashptteamdefend?College=&Conference=&Country=&DateFrom{date}=&DateTo={date}&DefenseCategory=Less%20Than%206Ft&Division=&DraftPick=&DraftYear=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
            df14=pull_data(url14)
            print(df14)
            print('frame14')
            
            url15=f"https://stats.nba.com/stats/leaguedashteamshotlocations?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&DistanceRange=5ft%20Range&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType={stype}&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
            df15=pull_data(url15)
            print(df15.columns)
            df15.columns=['TEAM_ID', 'TEAM_NAME', 
             'FGM_LT_5', 'FGA_LT_5', 'FGP_LT_5',      # Less than 5 feet
             'FGM_5_9', 'FGA_5_9', 'FGP_5_9',         # 5-9 feet
             'FGM_10_14', 'FGA_10_14', 'FGP_10_14',   # 10-14 feet
             'FGM_15_19', 'FGA_15_19', 'FGP_15_19',   # 15-19 feet
             'FGM_20_24', 'FGA_20_24', 'FGP_20_24',   # 20-24 feet
             'FGM_25_29', 'FGA_25_29', 'FGP_25_29',   # 25-29 feet
             'FGM_30_34', 'FGA_30_34', 'FGP_30_34',   # 30-34 feet
             'FGM_35_39', 'FGA_35_39', 'FGP_35_39',   # 35-39 feet
             'FGM_40_PLUS', 'FGA_40_PLUS', 'FGP_40_PLUS'  # 40+ feet
            ]
            print(df15)
            print('frame15')
            url16 = f'https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=&PerMode=Totals&PlayerExperience=&PlayerOrTeam={unit}&PlayerPosition=&PtMeasureType=CatchShoot&Season={season}&SeasonSegment=&SeasonType={stype}&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df16=pull_data(url16)


            print(df16)
            print('frame16')
            url17 = f'https://stats.nba.com/stats/leaguedashteamstats?College=&Conference=&Country=&DateFrom={date}&DateTo={date}&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Advanced&Month=0&OpponentTeamID=0&Outcome=&PORound=&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType=Playoffs&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
            df17 = pull_data(url17)
            df17=df17[['TEAM_ID','POSS']]
            df17.columns=['TEAM_ID','team_poss']

            poss_map=dict(zip(df17['TEAM_ID'],df17['team_poss']  ))

            df['team_poss']=df['TEAM_ID'].map(poss_map)
            df['team_poss']=df['TEAM_ID'].map(poss_map)
           
            frames = [df2, df3, df4, df5, df6, df7, df8, df9, df10,df11,df12,df13,df14,df15,df16]
            for frame in frames:
                
                joined_columns = set(frame.columns) - set(df.columns)
                joined_columns = list(joined_columns)
                joined_columns.append('TEAM_ID')
                frame = frame[joined_columns]

                df = df.merge(frame, on='TEAM_ID',how='left').reset_index(drop=True)

            df['year'] = year
            df['date']=date_num
  
            year_frame.append(df)
            count+=1
            print(date_num)
            sys.exit()
            if count %10==0:
        
                yeardata=pd.concat(year_frame)
                print(len(yeardata))
                yeardata['playoffs']=ps
                yeardata.to_csv(str(year)+trail+'_games.csv',index=False)
        except Exception as e:
            print(str(e))
            
            print(str(date_num))
            time.sleep(1)
            sys.exit()
            
    

        yeardata=pd.concat(year_frame)
        print(len(yeardata))
        yeardata['playoffs']=ps
        yeardata.to_csv('year_files/'+str(year)+trail+'_games.csv',index=False)
        dframes.append(yeardata)
        print(f"Year: {year}")

    total = pd.concat(dframes)
    return total


start_year=2024
end_year=2026



def get_dates(start_year,end_year):
    dates=[]
    for year in range(start_year,end_year):
    
        for team in teams.get_teams():
            team_id=team['id']
            path = '../../shot_data/team/'+str(year)+'/'+str(team_id)+'.csv'
            if os.path.exists(path):
                df=pd.read_csv(path)
    
                df=df[['PLAYER_ID','TEAM_ID','HTM','VTM','GAME_DATE','GAME_ID']]
                df.sort_values(by='GAME_DATE',inplace=True)
                df.drop_duplicates(inplace=True)
                df['year']=year
                dates.append(df)
    return pd.concat(dates)
dateframe=get_dates(start_year,end_year)

dates=dateframe['GAME_DATE'].unique().tolist()
dates.sort()
df= pull_game_level(dateframe,start_year,end_year,unit='Team')
#data=pull_game_level(dates)
df
df.drop_duplicates(subset=['PLAYER_ID','TEAM_ID','date'])


# In[ ]:




