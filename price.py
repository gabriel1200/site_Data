#!/usr/bin/env python
# coding: utf-8

# In[15]:


import pandas as pd
import requests
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np
from bs4 import BeautifulSoup


def get_salaries(team = False):
    if team == False:
        base = 'https://hoopshype.com/salaries/players/'
    else:
        base = 'https://hoopshype.com/salaries/'
        
    salaries = []
    for i in range(2023,2025):
        if i !=2007:
            url = base+str(i) +'-'+str(i+1)
            if i == 2024:
                url=base
            print(url)

            df = pd.read_html(url)[0]
            #print(df)
            df.drop(columns=['Unnamed: 0'],inplace = True)
            #print(df.columns)
            if i<2022:
                df.columns = ['Player','Salary','Inflation_Salary']
                df['Salary'] = df['Salary'].str.replace('\W', '', regex=True)
                df['Inflation_Salary'] = df['Inflation_Salary'].str.replace('\W', '', regex=True)
            else:
                df = df[df.columns[0:2]]
                df.columns = ['Player','Salary']
                df['Salary'] = df['Salary'].str.replace('\W', '', regex=True)
                df['Inflation_Salary'] = df['Salary']
            df['year'] = i+1
            salaries.append(df)
    final = pd.concat(salaries)
    if team == True:
        final.rename(columns={'Player':'Team'},inplace = True)
    return final
        
def games_per_year():
    url = 'https://www.basketball-reference.com/leagues/NBA_stats_per_game.html'
    games = pd.read_html(url)[0]
    games.columns = games.columns.droplevel()
    games = games.dropna(subset='Season')
    games = games[games['Season']!='Season']
    games['Year'] = games['Season'].str[0:4].astype(int)+1
    games['G'] = games['G'].astype(int)
    games = games[['Year','G']]
    return games
name_map = {'LALakers':'LAL', 'Dallas':'DAL', 'NewYork':'NYK', 'Boston':'BOS', 'Cleveland':'CLE',
         'Orlando':'ORL','SanAntonio':'SAS', 'Denver':'DEN', 'Miami':'MIA', 'Washington':'WAS', 
            'Utah':'UTA',
       'NewOrleans':'NOP', 'Chicago':'CHI', 'Houston':'HOU', 'Charlotte':'CHA', 'Toronto':'TOR',
       'Sacramento': 'SAC', 'Milwaukee':'MIL', 'Indiana':'IND', 'Atlanta':'ATL', 'GoldenState':'GSW',
       'Phoenix':'PHX', 'Philadelphia':'PHI', 'Minnesota':'MIN', 'LAClippers':'LAC', 'Detroit':'DET',
       'Brooklyn':'BKN', 'OklahomaCity':'OKC', 'Memphis':'MEM', 'Portland':'POR'}


#lebron = lebron_master()
salaries = get_salaries(team=False)

#print(salaries)
#payroll = get_salaries(team=True)
lebron = pd.read_csv('lebron.csv')
#lebron['Player'] = lebron['Player'].str.split(' ').str[:-1].str.join(' ')
lebron["Player"]= lebron["Player"].str.lower().str.replace("'", "", regex=True)

lebron['Player'] = lebron['Player'].str.split(' ').str[0].str[0:3] +lebron['Player'].str.split(' ').str[1]

#lebron['Player'] = lebron['Player'].str.split(' ').str[0].str[0]+ lebron['Player'].str.split(' ').str[-1]

#lebron['Player']= lebron['Player'].str.split(' ').str[0].str[0]+ lebron['Player'].str.lower().str.replace('\W', '', regex=True)
lebron['Player']= lebron['Player'].str.lower().str.replace('\W', '', regex=True)

salary = get_salaries(team=False)
print(salary.columns)
extra = pd.DataFrame([['Nick Richards',5000000,5000000,2025]], columns=salary.columns)


salary = pd.concat([salary,extra])

#print(salary)
wrong_names = {'Jose Juan Barea':'J.J. Barea','Timothe Luwawu':'Timothe Luwawu-Cabarrot','Dennis Schroeder':'Dennis Schroder','Didier Ilunga-Mbenga':'DJ Mbenga'
              ,'BJ Boston':'Brandon Boston Jr.'}
salary= salary.replace({'Player':wrong_names})

salary['Name'] = salary['Player']
print(salary[salary.Name.str.contains('Nic')])
#salary['team'] = salary['team'].map(name_map)

#salary['Player'] = salary['Player'].str.split(' ').str[0].str[0]+ salary['Player'].str.split(' ').str[-1]
#salary['Player'] = salary['Player'].str.split(' ').str[0] +salary['Player'].str.split(' ').str[1]


salary["Player"]= salary["Player"].str.lower().str.replace("'", "", regex=True)


salary['Player'] = salary['Player'].str.split(' ').str[0].str[0:3]+salary['Player'].str.split(' ').str[1]

salary['Player']= salary['Player'].str.lower().str.replace('\W', '', regex=True)

#getting player salaries

#payroll = pd.read_csv('team_payroll.csv')
names= dict(zip(lebron.Player,lebron.bref_id))
salary['bref_id'] = salary['Player'].map(names)
salary['bref_id']=np.where(salary.Name =='Markieff Morris','morrima02',salary.bref_id)
#salary['bref_id']=np.where(salary.Name =='Josh Richardson','richani01',salary.bref_id)

#salary['team'] = salary['team'].map(name_map)

#print(names)
lebron.rename(columns={'year':'Year'},inplace = True)
lebron.rename(columns={'team':'Team'},inplace = True)
salary.rename(columns={'year':'Year'},inplace = True)

#salary.rename(columns={'team':'team_name'},inplace = True)
#payroll.rename(columns={'year':'Year'},inplace = True)
#salary = salary.rename(columns={'Player':'Name'})
#getting team payroll
salary = salary[salary.Year>=2010]
salary = salary[salary.Name!='Totals']
salary = salary[salary.Name!='totals']

#salary[salary.bref_id.isnull()]

#salary
salary[salary.bref_id.isnull()]['Name'].unique()
lebron = lebron[lebron.Year==2025]
old_ids = lebron.bref_id.tolist()


# In[16]:


salary.columns


# In[17]:


salary.sort_values(by=['Year','Salary'])


# In[18]:


lebron.merge(salary)
new_ids = lebron.bref_id.tolist()
set(old_ids)-set(new_ids)


# In[19]:


salary


# In[20]:


lebron = lebron[lebron.Year==2025]


# In[21]:


lebron['lastname'] = lebron['Player'].str.split(' ').str[-1]
lebron = lebron.rename(columns={'Team':'team'})
short = lebron[['Year','team','lastname','LEBRON']]
short[short.lastname=='giddens']
null = salary[salary.bref_id.isnull()]
null['lastname'] = null['Name'].str.split(' ').str[-1].str.lower()
null[null.lastname=='giddens']
temp = null.merge(short, on = ['Year','lastname'],how='left')
temp[temp.LEBRON.isnull()]


# In[22]:


'''
salaries
current = pd.read_csv('../data/pay_table.csv')
lebron= pd.read_csv('lebron.csv')
print(lebron.columns)
print(current.columns)
print(set(current.columns)-set(lebron.columns))
lebron = lebron[lebron.year==2025]
'''


# In[23]:


lebron.columns


# In[24]:


salary.columns


# In[25]:


#salary = salary.drop(columns=['Player'])

salary.rename(columns={'Year':'year'},inplace=True)
salary['Salary']=salary['Salary'].replace('[\$,]', '', regex=True).astype(float)
salary=salary[salary.year==2025]
year_total = salary.groupby('year')['Salary'].sum().reset_index()

games = games_per_year()
print(games.columns)

games.columns = ['year','G']
year_total = year_total.merge(games)
print(year_total['G'])
#year_total['Salary']/=year_total['G']
year_total['Salary']/=1280
year_total.rename(columns ={'Salary':'Win_Cost'},inplace = True)
year_total.drop_duplicates(inplace=True)
pay_table = salary.merge(year_total)
pay_table.fillna(0,inplace = True)
#pay_table['bref_id'].replace({'richani01':'richajo01'}, inplace=True)


#lebron.drop(columns='Player',inplace=True)
pay_table = pay_table.merge(lebron,how='left',on='bref_id')
print(pay_table.columns)
#pay_table['team'] = pay_table['team_x']
#pay_table = pay_table.drop(columns='team')
pay_table['WAR'] = pay_table['WAR'].fillna(0)
pay_table['WAC']= pay_table['WAR'] - (pay_table['Salary']/pay_table['Win_Cost'])
pay_table = pay_table.sort_values(by='WAC')
temp_bron = pd.read_csv('lebron.csv')
id_list = pay_table['NBA ID'].unique().tolist()
temp_bron = temp_bron[~temp_bron['NBA ID'].isin(id_list) ]

#null_names= dict(zip(temp_bron.Player.str.split(' ').str[0],temp_bron.bref_id))
#temp_data = pd.read_csv('players.csv')

#null = null[['Salary','Inflation_Salary','year','team','Name']]
#null['name'] = null.Name.str.split(' ').str[0]
#null['bref_id'] = null['Name'].map(null_names)
#null[null.bref_id.isnull()]


# In[26]:


print(pay_table.columns)


# In[27]:


pay_table.columns#pay_table['WAR'] = pay_table['LEBRON WAR']
pay_table['Team']=pay_table['team']
pay_table['Player'] = pay_table['Player_x']
pay_table.drop(columns=[

 'Player_x',
 'Player_y',

 'lastname',
],inplace=True)
pay_table[pay_table.Year==2025]

pay_table[pay_table.bref_id=='thompkl01']


# In[28]:


old_pay = pd.read_csv('pay_table.csv')
print((old_pay.columns))


# In[29]:


pay_table = pay_table.drop_duplicates(subset='bref_id')
filt = pay_table[pay_table.LEBRON.isnull()]
filt


# In[ ]:





# In[30]:


pay_table[~pay_table.LEBRON.isnull()]


# In[31]:


filt = pay_table[~pay_table.LEBRON.isnull()]
not_found = set(old_ids)-set(filt.bref_id.tolist())



lebron[lebron.bref_id.isin(not_found)]
index=pd.read_csv('index_master.csv')


index_id=dict(zip(index.bref_id,index.nba_id))


# In[32]:


#old_pay = old_pay[old_pay.Year!=2025]
#old_pay.drop(columns='Unnamed: 0',inplace = True)
pay_table.loc[pay_table['Name'] == 'Tidjane Salaun', 'NBA ID'] = 1642275
pay_table.loc[pay_table['Name'] == 'Tidjane Salaun', 'bref_id'] = "salauti01"

pay_table['NBA ID'] = pay_table['bref_id'].map(index_id)

print(pay_table[pay_table['NBA ID'].isna()])

pay_table['NBA ID']=pay_table['NBA ID'].astype(int)


new_pay = pd.concat([old_pay,pay_table])
new_pay['NBA ID'] = new_pay['bref_id'].map(index_id)

print(new_pay[new_pay['NBA ID'].isna()])

new_pay



new_pay


# In[33]:


new_pay.to_csv('../web_app/data/pay_table.csv',index=False)


# In[34]:


print(pay_table)


# In[35]:


new_pay['year'].unique()


# In[ ]:




