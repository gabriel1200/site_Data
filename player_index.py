#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd

from nba_api.stats.endpoints import playerfantasyprofile,playerdashboardbyteamperformance,leaguedashplayerstats

def update(year):
    season_string = year
    print(season_string)
    frames = leaguedashplayerstats.LeagueDashPlayerStats(season=season_string,league_id_nullable=10).get_data_frames()
    df = frames[0]
    df['year'] = year
    df['GROUP_SET'] = 'Players'
    #df = df.drop(columns=['TEAM_ABBREVIATION','AGE'])
    old = pd.read_csv('windex.csv')
    old = old[old.year!=year]
    
    to_save = pd.concat([old,df])
    to_save.drop(columns=[col for col in to_save.columns if 'Unnamed' in col],inplace = True)
    return to_save
def update2(year):
    season_string = year
    print(season_string)
    frames = leaguedashplayerstats.LeagueDashPlayerStats(season=season_string,league_id_nullable=10,season_type_all_star="Playoffs").get_data_frames()
    df = frames[0]
    df['year'] = year
    df['GROUP_SET'] = 'Players'
    #df = df.drop(columns=['TEAM_ABBREVIATION','AGE'])
    old = pd.read_csv('windex_ps.csv')
    old = old[old.year!=year]
    
    to_save = pd.concat([old,df])
    to_save.drop(columns=[col for col in to_save.columns if 'Unnamed' in col],inplace = True)
    return to_save
to_save= update(2024)
to_save.to_csv('windex.csv',index=False)
#to_save2= update(2024)

#to_save2.to_csv('windex_ps.csv',index=False)


# In[ ]:




