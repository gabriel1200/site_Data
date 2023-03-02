#!/usr/bin/env python
# coding: utf-8

# In[167]:


import pandas as pd
import requests


# In[168]:


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


# In[169]:


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


# In[170]:


#rframes = get_sheets('Regular Season')
#pframes = get_sheets('Playoffs')


# In[171]:


#pdf = pd.concat(pframes)
#rdf = pd.concat(rframes)


# In[172]:


#pdf.to_csv('pbp/team_playoff.csv',index = False)
#rdf.to_csv('pbp/team_regular.csv',index = False)


# In[ ]:





# In[198]:


rdf = pd.read_csv('pbp/team_regular.csv')
pdf = pd.read_csv('pbp/team_playoff.csv')

rdf['ortg'] = (100*rdf['Points']/rdf['OffPoss']).round(2)
rdf['drtg'] = (100*rdf['OpponentPoints']/rdf['DefPoss']).round(2)
#calculating team offensive & defensive rating
pdf['ortg'] = (100*pdf['Points']/pdf['OffPoss']).round(2)
pdf['drtg'] = (100*pdf['OpponentPoints']/pdf['DefPoss']).round(2)




# In[ ]:





# In[220]:


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
ofspeed = 'SecondsExcludingORebsPerPossOff'
dfspeed = 'SecondsExcludingORebsPerPossDef'
#ofspeed= 'SecondsPerPossOff'
#dfspeed ='SecondsPerPossDef'
def relative_average(df,term,new_term):
    #print(df[term+'_r'])
    ave = term+'_ave'
    rortg = df.groupby('year')[term+'_r'].mean().reset_index()
    rortg = rortg.rename(columns={term+'_r':ave})
    df = df.merge(rortg,on ='year',how ='left')
    df[new_term+'_r'] = df[term+'_r'] - df[ave]
    df[new_term+'_p'] = df[term+'_p'] - df[ave]
    return df
df = relative_average(df,'ortg','rortg')
df = relative_average(df,ofspeed,'r'+ofspeed)
df = relative_average(df,dfspeed,'r'+dfspeed)
df = relative_average(df,'Pace','rPace')


# In[221]:


df.columns


# In[222]:


df['rPace_r']


# In[224]:


df = df.dropna(subset ='drtg_p')


# In[225]:


df['off_speed_change'] =df['r'+ofspeed+'_p'] - df['r'+ofspeed+'_r'] 
df['def_speed_change'] =df['r'+dfspeed+'_p'] - df['r'+dfspeed+'_r'] 

defense_change = 'def_speed_change'
offense_change = 'off_speed_change'
#change in speed between regular season and postseason
df['ortg_change'] = df['ortg_p'] - df['ortg_r']
df['drtg_change'] = df['drtg_r'] - df['drtg_p']
df['pace_change'] = df['Pace_r'] - df['Pace_p']
#change in ortg between regular & post seasons


# In[228]:


more_speed = df[df[offense_change]<0]
more_speed[more_speed['ortg_change']<0][['Name','year','ortg_p','ortg_r','ortg_change','rortg_r','rortg_p',offense_change]]['rortg_r']


# In[227]:


df['Pace_r'].min()


# In[185]:


less_speed = df[df[offense_change]>0]
#4.686911426639622 for the group that improved
#-3.6838927727916846 for the group that declined


# In[187]:


print('Teams that sped up had a rortg of '+str(more_speed['rortg_r'].mean().round(2)) +' in the regular season')
print('Teams that slowed down had a rortg of '+str(less_speed['rortg_r'].mean().round(2)) +' in the regular season')

print('The average playoff team had a rortg of '+str(df['rortg_r'].mean().round(2))+' in the regular season')


# In[66]:


def_speed = df[df[defense_change]<0]
def_speed[def_speed['drtg_change']>0][['Name','year','drtg_p','drtg_r','drtg_change']]


# In[67]:


def_speed['drtg_change'].mean()


# In[68]:


df['drtg_change'].mean()


# In[229]:


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


df.plot.scatter(x='def_speed_change',y='drtg_change')


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


# In[232]:


df = df.sort_values(by='rPace_r',ascending = False)
fastest = df.head(int(len(df)/10))
slowest = df.tail(len(df)-int(len(df)/10))


# In[244]:


fastest.to_csv('fastest.csv',index = False)


# In[241]:


print('The fastest 10% of teams in terms of regular season relative pace fell by '+str(fastest['ortg_change'].mean().round(2)))
print('The other 90% of teams in terms of regular season relative pace fell by '+str(slowest['ortg_change'].mean().round(2)))


# In[235]:


df['ortg_change'].mean()


# In[236]:


slowest['ortg_change'].mean()


# In[ ]:




