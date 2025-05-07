#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pandas as pd
from unidecode import unidecode
import re
# URL to the index CSV file
url = 'https://raw.githubusercontent.com/gabriel1200/metric_test/refs/heads/master/index_master.csv'

# Read the CSV file into a DataFrame
index_df = pd.read_csv(url)
index_df=index_df[index_df.year>1990]
index_df=index_df[index_df.team!='TOT']
def remove_acronyms(player_name):
    if isinstance(player_name, str):  # Only process if player_name is a string
        # Define a regex pattern to remove common suffixes/acronyms
        pattern = r'\b(Jr\.|Sr\.| Jr| Sr|II|III|IV|V|VI)\b'
        # Remove accents and non-ASCII characters
        player_name = unidecode(player_name)
        # Use regex to substitute any suffix patterns
        cleaned_name = re.sub(pattern, '', player_name).strip()
        return cleaned_name
    else:
        return player_name  # If not a string (like NaN), return as-is

# Convert non-English characters in the 'player' column to their ASCII/English equivalent
index_df['player']=index_df['player'].astype(str)

index_df['player'] = index_df['player'].apply(lambda x: unidecode(str(x)))
# Display the cleaned 'player' column to verify the conversion
team_acronym_map = {
    'NJN': 'BKN',  # New Jersey Nets -> Brooklyn Nets
    'BRK':'BKN',
    'VAN': 'MEM',  # Vancouver Grizzlies -> Memphis Grizzlies
    'CHA': 'CHA',  # Old Charlotte Hornets -> Modern Charlotte Hornets
    'NOH': 'NOP',  # New Orleans Hornets -> New Orleans Pelicans
    'SEA': 'OKC',  # Seattle SuperSonics -> Oklahoma City Thunder
    'WSB': 'WAS',  # Washington Bullets -> Washington Wizards
    'CHH': 'CHA',  # Charlotte Hornets -> Modern Charlotte Hornets
    'CHO':'CHA',
    'SDC': 'LAC',  # San Diego Clippers -> LA Clippers
    'KCK': 'SAC',  # Kansas City Kings -> Sacramento Kings
    'NOK':'NOP',

    'PHO': 'PHX',
}

index_df['team'] = index_df['team'].replace(team_acronym_map)

# Save the cleaned index DataFrame if necessary

# Proceed with the merging step with the salary data, once the salary data is loaded into 'salary_df'
# Assuming 'salary_df' is already prepared from the salary scraping
# salary_df['Player'] = salary_df['Player'].apply(lambda x: unidecode(str(x)))  # Ensure salary data also has ASCII names
# merged_df = pd.merge(salary_df, index_df, left_on='Player', right_on='player', how='inner')

# Save or process the merged data further if needed
# print(merged_df.head())
def convert_salary(salary_str):
    if isinstance(salary_str, str):  # Only process if salary_str is a string
        # Remove '$' and ',' from the string, then convert to float
        salary_num = float(salary_str.replace('$', '').replace(',', ''))
        return salary_num
    else:
        return salary_str  # If not a string, return as-is (e.g., NaN)


salary=pd.read_csv('nba_salaries_raw.csv')
salary.to_csv('nba_salaries_raw.csv',index=False)

salary=salary[~salary.Salary.isna()]
salary=salary[~salary.Player.isna()]


index_df['player'] = index_df['player'].apply(remove_acronyms)

# Clean 'Player' names in the salary data file
salary.rename(columns={'Player':'player','Team':'team','Year':'year','Salary':'salary'},inplace=True)
salary=salary[salary.player.str.lower()!='totals']

salary['player'] = salary['player'].apply(remove_acronyms)

print(len(salary))

salary['salary'] =salary['salary'].apply(convert_salary)

salary_df=salary.merge(index_df,on=['player','year','team'],how='left')

not_found1=salary_df[salary_df.nba_id.isna()]
not_found1=not_found1[['player','year','team','salary']]
salary_df.dropna(subset='nba_id',inplace=True)
not_found1.sort_values(by='salary')

index_small=index_df[['player','year','nba_id','bref_id','url']].reset_index(drop=True)
index_small['player']=index_small['player'].str.split(' ',expand=True)[0] + ' '+index_small['player'].str.split(' ',expand=True)[1]

index_small['player'] = index_small['player'].str.replace(r'[^a-zA-Z\s]', '', regex=True).str.strip()
index_small=index_small.dropna(subset='player')
not_found1['player'] = not_found1['player'].str.replace(r'[^a-zA-Z\s]', '', regex=True).str.strip()

not_found2=not_found1.merge(index_small,on=['player','year'],how='left')
salary_df=pd.concat([salary_df,not_found2])
salary_df.dropna(subset='nba_id',inplace=True)
salary_df.drop_duplicates(inplace=True)

not_found2=not_found2[not_found2.nba_id.isna()]
not_found2.drop_duplicates(inplace=True)

not_found2=not_found2[['player','year','team','salary']]
print(len(salary_df))
salary_df


# In[2]:


index_small=index_df[['player','year','nba_id','team','bref_id','url']].reset_index(drop=True)

index_small=index_small[~index_small.nba_id.isin(salary_df.nba_id.tolist())]

not_found2['last']= not_found2['player'].str.split(' ',expand=True)[1]+not_found2['team']

index_small['last']= index_small['player'].str.split(' ',expand=True)[1] +index_small['team']

index_small['last']+=index_small['player'].str[0:3]


not_found2['last']+=not_found2['player'].str[0:3]

index_small.dropna(subset='last',inplace=True)

index_small.drop(columns=['player'],inplace=True)

salary2=not_found2.merge(index_small,on=['last','year','team'])
salary2=salary2[~salary2.nba_id.isin(salary_df.nba_id.tolist())]

salary2.drop(columns='last',inplace=True)
#salary2.drop_duplicates(inplace=True)
salary_df=pd.concat([salary_df,salary2])
salary_df.sort_values(by=['team','year','salary'],inplace=True)
salary_df.to_csv('salary_backup.csv',index=False)


# In[3]:


played=index_df.drop_duplicates(subset=['nba_id','year']).reset_index(drop=True)
played.drop(columns=['team'],inplace=True)

played=played[['year','nba_id']]


# In[4]:


played


# In[5]:


temp=salary_df[['player','year','nba_id','salary']]
temp.drop_duplicates(subset=['year','nba_id'],inplace=True)


# In[13]:


to_merge


# In[11]:


to_merge[to_merge.salary.isna()]


# In[8]:


smerge=salary.merge(to_merge,how='left')
smerge.to_csv('nba_salaries_master.csv',index=False)
smerge


# In[18]:


smerge[smerge.player.str.contains('Nicol')]


# In[9]:


cap=pd.read_csv('cap.csv')

capmap=dict(zip(cap['year'],cap['Salary Cap']))
capmap


# In[19]:


smerge['cap']=smerge['year'].map(capmap)
smerge


# In[22]:


smerge['cap%']=100*smerge['salary']/smerge['cap']
smerge.sort_values(by='cap%')


# In[21]:


smerge['cap%'].max()


# In[23]:


smerge.to_csv('nba_salaries.csv',index=False)


# In[ ]:




