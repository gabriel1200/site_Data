#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
# URL of the local HTML file being served
df=pd.read_csv('lebron_link25.csv')
df['year']=2025
df
df.dropna(subset=['Name'],inplace=True)
old_df=pd.read_csv('lebron.csv')
old_df=old_df[old_df.year<2025]
old_df
column_mapping = {
    'Season': 'Season',
    'Name': 'Player',
    'Team': 'team',
    'Minutes': 'Minutes',
    'Position': 'Pos',
    'offensiveArchetype': 'Offensive Archetype',
    'LEBRON_WAR': 'WAR',
    'LEBRON': 'LEBRON',
    'OLEBRON': 'O-LEBRON',
    'DLEBRON': 'D-LEBRON',
    'defensive_role': 'Defensive Role',
    'PLAYER_ID': 'NBA ID',
    'G': 'Games',
    # 'bref_id' and 'Age' omitted intentionally
}
df.rename(columns=column_mapping,inplace=True)

samecolumns =set(old_df.columns) - (set(old_df.columns)-set(df.columns))
samecolumns
df=df[list(samecolumns)]
print(old_df.columns)

def update(year):
    season_string = str(year-1) +'-'+str(year)[-2::]
    print(season_string)
    frames = leaguedashplayerstats.LeagueDashPlayerStats(season=season_string).get_data_frames()
    df = frames[0]

    return dict(zip(df['PLAYER_ID'],df['AGE']))
ages = update(2025)
df['Age']=df['NBA ID'].map(ages)
idframe=pd.read_csv('index_master.csv')
id_map = dict(zip(idframe['nba_id'],idframe['bref_id']))

df['bref_id']=df['NBA ID'].map(id_map)
df['Player']=df['Player'].str.lower()

newframe = pd.concat([old_df,df])
newframe.to_csv('lebron.csv',index=False)
newframe.to_csv('../web_app/data/lebron.csv',index=False)

newframe


# In[ ]:





# In[ ]:



