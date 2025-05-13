#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
ps=True
def get_tracking(years, ps=False):
    stype = "Regular%20Season"
    if ps:
        stype = "Playoffs"
    
    shots = ["Drives", "CatchShoot", "Passing", "Possessions", "ElbowTouch", "PostTouch", "PaintTouch", "PullUpShot"]
    
    # Dictionary to store dataframes for each shot category
    category_frames = {shot: [] for shot in shots}

    for year in years:
        season = str(year) + '-' + str(year + 1 - 2000)
        
        for shot in shots:
            part1 = "https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType="
            part2 = "&Season="
            part3 = "&SeasonSegment=&SeasonType=" + stype + "&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
            
            url = part1 + shot + part2 + season + part3

            headers = {
                "Host": "stats.nba.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://stats.nba.com/"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json = response.json()
                data = json["resultSets"][0]["rowSet"]
                columns = json["resultSets"][0]["headers"]
                df = pd.DataFrame.from_records(data, columns=columns)
                df["Season"] = season  # Add season column
                df['year']=year+1
                # Append the dataframe for this shot category to the respective list
                category_frames[shot].append(df)
            else:
                print(f"Failed to retrieve data for shot type {shot} in season {season}")

    return category_frames

current_year=2013
years=[i for i in range(current_year,2025)]
if ps ==False:
    category_frames=get_tracking(years,ps=ps)
else:
    category_frames_ps=get_tracking(years,ps=True)


# In[2]:


category_maps = {
    "Drives": 'drives.csv',
    "CatchShoot": 'catchshoot.csv',
    "Passing": 'passing.csv',
    "Possessions": 'touches.csv',
    "ElbowTouch": 'elbow.csv',
    "PostTouch": 'post.csv',
    "PaintTouch": 'paint.csv',
    "PullUpShot": 'pullup.csv'
}

if ps == False:
    for cat in category_frames.keys():

        file='tracking/'+category_maps[cat]
        old_df=pd.read_csv(file)
        old_df=old_df[old_df.year!=current_year+1]
        new_df=pd.concat(category_frames[cat])

        df =pd.concat([old_df,new_df])
        df.to_csv(file,index=False)

else:

    for cat in category_frames_ps.keys():

        file='tracking_ps/'+category_maps[cat]

        df =pd.concat(category_frames_ps[cat])
        df.to_csv(file,index=False)


# In[ ]:




