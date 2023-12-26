#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import time
from unidecode import unidecode

'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support.select import Select
'''
url = 'https://www.nba.com/stats/players/traditional?SeasonType=IST'
xpath = '//*[@id="__next"]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select'
def get_ptables(url_list,path_list):
    data = []
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    cookie_check = False
    for i in range(len(url_list)):
        url = url_list[i]
        xpath = path_list[i]
        print(url)
        
        driver.get(url)
        accept_path = '//*[@id="onetrust-accept-btn-handler"]'
        time.sleep(5)

        if EC.presence_of_element_located((By.XPATH, accept_path)) and cookie_check == False:
            driver.find_element(By.XPATH, accept_path).click() 
            cookie_check = True
            time.sleep(1)
        

        element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath)))
        # Wait for the page to fully load
        #time.sleep(5)
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        
        dropdown1 = Select(driver.find_element(By.XPATH, xpath))
        dropdown1.select_by_index(0)

        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        
        soup = BeautifulSoup(driver.page_source, 'lxml')

        tables = soup.find_all('table')
        

        # Step 3: Read tables with Pandas read_html()
        dfs = pd.read_html(str(tables))
        #needed table is at the end
        df= dfs[-1]

       
        data.append(df)
    driver.close()
    return data
'''
urls = [url]
paths = [xpath]
data = get_ptables(urls,paths)
df = data[0]
df = df[[col for col in df.columns if ' RANK' not in col]]
df = df.drop(columns=['Unnamed: 0'])
df.to_csv('inseason_2024.csv',index = False)
'''


# In[11]:


def get_table(year,minutes,ps = False):
    if ps == False:
        stype = 'leagues'
    else:
        stype='playoffs'
    link_1 = 'https://www.basketball-reference.com/'+stype+'/NBA_'+str(year)+'_totals.html'
    df = pd.read_html(link_1)[0]
   
    df = df[df["MP"].notna()]
    df = df[df['MP'] != 'MP']
    df['MP'] = df['MP'].astype(float)
    df['PTS'] = df['PTS'].astype(float)
    df['FTA'] = df['FTA'].astype(float)
    df['FGA'] = df['FGA'].astype(float)

    df['TS%'] = df['PTS']/(2* (df['FGA'] + .44 *df['FTA'] ))

    df = df[df['MP'] >minutes]
    df['TS%'] *=100
    df['G'] = df['G'].astype(int)
    
    #print(df)
    return [ df[['Player','TS%','PTS','MP','Tm','G','FTA','FGA']],year]
    
def get_table2(year,minutes,ps = False):
    if ps == False:
        stype = 'leagues'
    else:
        stype='playoffs'
    link_1 = 'https://www.basketball-reference.com/'+stype+'/NBA_'+str(year)+'_per_poss.html'
    df = pd.read_html(link_1)[0]
   
    df = df[df["MP"].notna()]
    df = df[df['MP'] != 'MP']
    df['MP'] = df['MP'].astype(float)
    df['PTS'] = df['PTS'].astype(float)
    df['FTA'] = df['FTA'].astype(float)
    df['FGA'] = df['FGA'].astype(float)

    df['TS%'] = df['PTS']/(2* (df['FGA'] + .44 *df['FTA'] ))

    df = df[df['MP'] >minutes]
    df['TS%'] *=100
    df['G'] = df['G'].astype(int)
    return [ df[['Player','TS%','PTS','MP','Tm','G']],year]
    #print(df)
    
year = 2024
minutes = 0
ps = False
if ps == False:
    df = pd.read_csv('scoring.csv')
    df = df[df.year<year]
    new_table,year = get_table2(year,minutes,ps)
    new_table['year'] = year
    df = pd.concat([df,new_table])
    df['year'] = df['year'].astype(int)
    #df =df.drop(columns=['FTA','FGA'])
    df.to_csv('scoring.csv',index=False)
    print(df)
    
    df = pd.read_csv('totals.csv')
    df = df[df.year<year]
    new_table,year = get_table(year,minutes,ps)
    new_table['year'] = year
    df = pd.concat([df,new_table])
    df['year'] = df['year'].astype(int)

    df.to_csv('totals.csv',index = False)
    
elif ps == True:
    df = pd.read_csv('scoring_ps.csv')
    df = df[df.year<year]
    new_table = get_table(year,minutes,ps)
    new_table['year'] = year
    df = pd.concat([df,new_table])
    df.to_csv('scoring_ps.csv',index=False)
    new_table['year'] = year
    
    df = pd.read_csv('totals_ps.csv')
    df = df[df.year<year]
    new_table = get_table2(year,minutes,ps)
    df = pd.concat([df,new_table])
    df.to_csv('totals_ps.csv',index= False)
df


# In[12]:


start_year = 1974
end_year = 2024
averages = pd.read_html('https://www.basketball-reference.com/leagues/NBA_stats_per_game.html#stats', header=1)[0]

#averages= averages.dropna()

averages = averages[averages['Season']!='Season']
averages = averages[averages['PTS']!='Per Game']

averages['PTS'] = averages['PTS'].astype(float)
averages['FGA'] = averages['FGA'].astype(float)
averages['FTA'] = averages['FTA'].astype(float)
averages['TS%'] = averages['PTS']/(2* (averages['FGA'] + .44 *averages['FTA'] ))
averages['TS%'] = averages['PTS']/(2* (averages['FGA'] + .44 *averages['FTA'] ))
averages = averages[['TS%','Season']]
averages['Season'] = averages['Season'].str[:4]
averages['Season'] = averages['Season'].astype(int)
averages['Season']+=1
averages = averages[averages['Season']>=start_year]
averages = averages[averages['Season']<=end_year]
averages = averages.iloc[::-1]


# In[13]:


averages.to_csv('tsavg.csv',index = False)


# In[14]:


df = pd.read_csv('scoring_ps.csv')
df['Player'] = df['Player'].apply(unidecode)
df['Player'] = df['Player'].astype(str)
df.to_csv('scoring_ps.csv',index = False,encoding='utf-8')

df = pd.read_csv('scoring.csv')
df['Player'] = df['Player'].apply(unidecode)
df['Player'] = df['Player'].astype(str)
df.to_csv('scoring.csv',index = False,encoding='utf-8')


# In[9]:


df = pd.read_csv('totals_ps.csv')
df['Player'] = df['Player'].apply(unidecode)
df['Player'] = df['Player'].astype(str)
df.to_csv('totals_ps.csv',index = False,encoding='utf-8')

df = pd.read_csv('totals.csv')
df['Player'] = df['Player'].astype(str)
df['Player'] = df['Player'].apply(unidecode)
df['Player'] = df['Player'].astype(str)
df.to_csv('totals.csv',index = False,encoding='utf-8')


# In[ ]:





# In[ ]:




