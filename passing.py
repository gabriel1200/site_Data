#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import unicodedata
import requests
import json
import math
#df = pd.read_csv('../../league_wide/wowy/player_large.csv')
def passing_data(ps = False,update=True):
    url = 'https://api.pbpstats.com/get-totals/nba'
    stype = 'Regular Season'
    trail = ''
    if ps == True:
        stype='Playoffs'
        trail ='/playoffs'
    frames = []
    start_year = 2014
    if update == True:
        df = pd.read_csv('passing.csv')
        df = df[df.year<2024]
        frames.append(df)
        start_year=2024
    print(start_year)
    for year in range(start_year,2025):
        #print(str(year-1)+'-'+str(year)[-2:])

        params = {
            "Season": str(year-1)+'-'+str(year)[-2:],
            "SeasonType": stype,
            "Type": 'Player'
        }
        response = requests.get(url, params=params)
        response_json = response.json()
        df = response_json["multi_row_table_data"]
        
        df = pd.DataFrame(df)
        #print(df['Time Of Poss'])
        #print(df.head)

        df2 = pd.read_csv(str(year)+trail+'/player_tracking/passing.csv')

        df2.rename(columns = {'PLAYER':'Name'}, inplace = True)
        df3 =  pd.read_csv(str(year)+trail+'/player_tracking/touches.csv')
        df3.rename(columns = {'Player':'Name'}, inplace = True)
        two = df.merge(df2,on='Name',how ='left',suffixes=('', '_y'))
        #print(two.columns)
        #print(df2.columns)
        #print(df2.columns)
        merged = two.merge(df3,on='Name',how ='left',suffixes=('', '_y'))
        pre = []
        post= []
        for col in merged.columns:
            if "\xa0" in col:
                pre.append(col)
                norm=  unicodedata.normalize('NFKD', col)

                merged.rename(columns = {col:norm}, inplace = True)
        merged = merged.fillna(0)
        merged['Points Unassisted'] = merged['PtsUnassisted2s']+merged['PtsUnassisted3s']
        merged['UAFGM'] = (merged['PtsUnassisted2s']/2)+(merged['PtsUnassisted3s']/3)
        merged['UAPTS'] = merged['Points Unassisted'] 
        merged['on-ball-time'] = merged['Time OfPoss']
        merged['High Value Assist %'] = 100* (merged['ThreePtAssists'] +merged['AtRimAssists'])/merged['Assists']

        merged['on-ball-time%'] = 100* 2* (merged['Time OfPoss'])/(merged['Minutes'])
        merged['TSA'] = (merged['Points']/ (merged['TsPct']*2))
        
        
        merged['Potential Assists'] = merged['PotentialAST']
        merged['Passes'] = merged['PassesMade']
        
        merged['PotAss/Passes'] = merged['Potential Assists']/merged['Passes']
        #merged['Assist PPP'] = merged['Potential Assists']/(75* merged['Assists']/merged['OffPoss'])
        merged['Assist PPP'] = (merged['AST PTSCreated'])/merged['Potential Assists']
        #merged['TOUCHES'] = merged['TOUCHES']/merged['GP']	
        merged['POT_AST_PER_MIN'] = merged['Potential Assists']/(merged['on-ball-time'])
        merged['year'] = year
        #print(*merged['Fg3Pct'])
        #three_p=  (2/(1+math.e**-merged['FG3A'].sum())-1)*(merged['Fg3Pct'].mean()
        #merged['Box Creation'] = merged['Assists']*0.1843+(merged['Points']+merged['Turnovers'])*0.0969-2.3021*(three_p)+0.0582*(merged['Assists'] *(merged['Points']+merged['Turnovers'])*three_p)-1.1942
        frames.append(merged)
        print('Season done ' +str(year))
    df = pd.concat(frames)
    return df

passing = passing_data()
passing_ps = passing_data(ps=True)
#merged['testas'] = merged['TwoPtAssists']*2+ merged['ThreePtAssists']*3


# In[2]:


columns = ['EntityId','Name','Points','on-ball-time%','on-ball-time','UAPTS','TSA','OffPoss','Potential Assists','Travels','TsPct',
        'Turnovers','Passes','PassesReceived','PotAss/Passes','UAFGM','High Value Assist %','Assist PPP','TOUCHES','Avg Sec PerTouch',
           'AST PTSCreated','Assists','SecondaryAST','POT_AST_PER_MIN','ThreePtAssists','AtRimAssists','Time OfPoss','ASTAdj','BadPassTurnovers',
       'Avg Drib PerTouch','PtsUnassisted2s','PtsUnassisted3s','Fg3Pct','FG3A','FG3M','OffPoss','GP','Minutes','year']
rs=passing[columns]
ps=passing_ps[columns]
rs.to_csv('passing.csv',index =False)
ps.to_csv('passing_ps.csv',index = False)
#print(rs.sort_values(by=)


# In[3]:


avg = pd.read_html('https://www.basketball-reference.com/leagues/NBA_stats_per_poss.html')[0]
avg.columns = avg.columns.droplevel()
avg = avg.dropna(subset='Season')
avg = avg[avg.Season!='Season']

avg = avg.dropna()
avg['PTS'] = avg['PTS'].astype(float)
avg['FGA'] = avg['FGA'].astype(float)
avg['FTA'] = avg['FTA'].astype(float)

#avg.head(87)


# In[4]:


avg['TS%'] = avg['PTS']/(2*(avg['FGA']+.44*avg['FTA']))
#avg


# In[5]:


avg.to_csv('avg_shooting.csv',index = False)
avg = avg[['Season','ORtg']]
avg.to_csv('team_avg.csv',index = False)


# In[ ]:





# In[ ]:




