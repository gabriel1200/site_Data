#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import pandas as pd

def gen_master(ps=False):
    count=0
    files = ['dfg', 'rimdfg']
    end_year = 2025
    master_df = pd.DataFrame()

    all_frames=[]
    for file in files:
        dfs = []
        for year in range(2014, end_year):

            if ps == False:
                path = f"{year}/defense/{file}.csv"
            else:
                path = f"{year}/playoffs/defense/{file}.csv"

            df = pd.read_csv(path)
            print(f"Processing {file} for {year}")

            # Standardize column names based on file type
            if file == 'dfg':

                df = df[['nba_id','team_id','PLAYER', 'TEAM', 'DFG%','DFGA','DFGM','DIFF%', 'year']]  # Overall DFG contested
                df = df.rename(columns={'DFG%': 'overall_dfg%','DFGA':'all_dfga','DFGM':'all_dfgm','TEAM':'Team','DIFF%':'dif%'})


            elif file == 'rim_acc':
                #df=df.sort_values(by='MinutesOn',ascending=False)
                #df.drop_duplicates(subset='Name',inplace=True)
                df = df[['Name', 'On', 'Off', 'Year','Team']]  # Rim accuracy on and of
                df = df.rename(columns={'Name': 'PLAYER', 'On': 'rim_acc_on', 'Off': 'rim_acc_off','Year':'year'})
            elif file == 'rimdfg':

                df = df[['PLAYER', 'DFG%','DFGA','DFGM' ,'year','nba_id','DIFF%', 'team_id']]  # Rim DFG contested
                df = df.rename(columns={'FREQ%': 'rim_freq','DFG%': 'rim_dfg%','DFGA':'rim_dfga','DFGM':'rim_dfgm','TEAM':'Team','DIFF%':'rim_dif%'})
                count+=len(df)
            elif file == 'rimfreq':
                #df=df.sort_values(by='MinutesOn',ascending=False)
                #df.drop_duplicates(subset='Name',inplace=True)
                df = df[['Name', 'On', 'Off', 'Year','Team']]  # Rim frequency on and off
                df = df.rename(columns={'Name': 'PLAYER', 'On': 'rim_freq_on', 'Off': 'rim_freq_off','Year':'year'})
            dfs.append(df)
        frame=pd.concat(dfs)
        all_frames.append(frame)
    master=all_frames[0]
    print(master.columns)
    for frame in all_frames[1:]:
        master=master.merge(frame,on=['PLAYER','year','nba_id','team_id'])
    print(count)





    # Save master file
    return master

# Usage
df = gen_master(ps=False)
df


# In[8]:


df.drop_duplicates()


# In[9]:


df.to_csv('defense_master.csv',index=False)


# In[10]:


df = gen_master(ps=True)
df.to_csv('defense_master_ps.csv',index=False)
df


# In[ ]:




