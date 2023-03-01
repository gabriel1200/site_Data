#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests


# In[2]:


url = "https://api.pbpstats.com/get-totals/nba"
params = {
    "Season": "2022-23",
    "SeasonType": "Regular Season",
    "Type": "Player"
}
response = requests.get(url, params=params)
response_json = response.json()
player_stats = response_json["multi_row_table_data"]
df = pd.DataFrame(player_stats)
col = ['Name','Minutes','Points','FG2M', 'FG2A', 'FG3M', 'FG3A', 'TsPct','AssistPoints','AtRimAssists','ShortMidRangeAssists', 'LongMidRangeAssists','Corner3Assists','Arc3Assists','LostBallSteals', 'LiveBallTurnovers', 'BadPassOutOfBoundsTurnovers', 'BadPassTurnovers',
       'DeadBallTurnovers', 'LostBallOutOfBoundsTurnovers', 'LostBallTurnovers', 'StepOutOfBoundsTurnovers', 'Travels', 'Turnovers','OffensiveGoaltends','FTA','OffPoss',
 'DefPoss','TotalPoss']
df[col].to_csv('wowy/player_small.csv',index = False)
df.to_csv('wowy/player_large.csv',index = False)


# In[3]:


def get_sheets(season):
    frames = []
    for i in range(2000,2023):
        url = "https://api.pbpstats.com/get-totals/nba"
        params = {
            "Season": str(i) +"-" +str(i+1)[2:],
            "SeasonType":season,
            "Type": "Team"
        }
        response = requests.get(url, params=params)
        response_json = response.json()
        #print(response_json)
        team_stats = response_json["multi_row_table_data"]
        df = pd.DataFrame(team_stats)
        #print(df.head(1))
        df['year'] = i +1
        frames.append(df)
    return frames


# In[4]:


#rframes = get_sheets('Regular Season')
#pframes = get_sheets('Playoffs')


# In[5]:


#pdf = pd.concat(pframes)
#rdf = pd.concat(rframes)


# In[6]:


#pdf.to_csv('pbp/team_playoff.csv',index = False)
#rdf.to_csv('pbp/team_regular.csv',index = False)


# In[ ]:





# In[89]:


rdf = pd.read_csv('pbp/team_regular.csv')
pdf = pd.read_csv('pbp/team_playoff.csv')
rdf['ortg'] = (100*rdf['Points']/rdf['OffPoss']).round(2)
rdf['drtg'] = (100*rdf['OpponentPoints']/rdf['DefPoss']).round(2)

pdf['ortg'] = (100*pdf['Points']/pdf['OffPoss']).round(2)
pdf['drtg'] = (100*pdf['OpponentPoints']/pdf['DefPoss']).round(2)
col = [ 'SecondsPerPossOff',
 'SecondsPerPossDef',
 'SecondsExcludingORebsPerPossOff',
 'SecondsExcludingORebsPerPossDef',
      'ortg',
      'drtg',
       'Pace',
      'Name',
       'year'
      ]
pdf = pdf[col]

rdf = rdf[col]

df = rdf.merge(pdf, on =['Name','year'],suffixes=('_r', '_p'),how = 'left')
#ofspeed = 'SecondsExcludingORebsPerPossOff'
#dfspeed = 'SecondsExcludingORebsPerPossDef'
ofspeed= 'SecondsPerPossOff'
dfspeed ='SecondsPerPossDef'


# In[90]:


rdf['Pace']


# In[91]:


df = df.dropna(subset ='drtg_p')


# In[92]:


df['speed_change'] =df[ofspeed+'_p'] - df[ofspeed+'_r'] 
df['def_speed_change'] =df[dfspeed+'_p'] - df[dfspeed+'_r'] 
#change in speed between regular season and postseason
df['ortg_change'] = df['ortg_r'] - df['ortg_p']
df['drtg_change'] = df['drtg_r'] - df['drtg_p']
df['pace_change'] = df['Pace_r'] - df['Pace_p']
#change in ortg between regular & post seasons


# In[93]:


df[['pace_change','year']]


# In[94]:


print(df['ortg_r'].corr(df[ofspeed+'_r']))
print(df['ortg_p'].corr(df[ofspeed+'_p']))
print(df['ortg_p'].corr(df[ofspeed+'_r']))


# In[95]:


df.plot.scatter(x='ortg_r',y=ofspeed+'_r')


# In[96]:


#print(df['drtg_r'].corr(df[dfspeed+'_r']))
print(df[dfspeed+'_p'].corr(df['drtg_p']))


# In[97]:


df.plot.scatter(x='speed_change',y='drtg_change')


# In[98]:


reg_speed = rdf.groupby('year')['Pace'].mean()

pos_speed = pdf.groupby('year')['Pace'].mean()
pos_speed - reg_speed


# In[99]:


def_reg = rdf.groupby('year')[dfspeed].mean()

def_pos = pdf.groupby('year')[dfspeed].mean()
def_pos - def_reg


# In[88]:


off_reg = rdf.groupby('year')[ofspeed].mean()

off_pos = pdf.groupby('year')[ofspeed].mean()
off_pos - def_reg


# In[59]:


rdf[rdf.year ==2023][['Name','drtg']].sort_values(by = 'drtg')
test = [x for x in rdf.columns if 'speed' in x.lower()]
test


# In[103]:


series = pd.read_csv('../playoffs/series_ratings.csv')


# In[104]:


test = df[df.year==2022]
test[[ofspeed+'_p',ofspeed+'_r']]


# In[61]:


rdf.columns


# In[ ]:




