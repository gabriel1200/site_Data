#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path


from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support import expected_conditions as EC
import requests


# Step 1: Create a session and load the page
epm = 'https://dunksandthrees.com/epm?season=2023'

#url_list = [url1,url2,url3,url4,url5]

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
#url_list = [cs,pullup]
def get_tables(url_list):
    data = []
    driver = webdriver.Chrome()
    for url in url_list:
        print(url)
        
        driver.get(url)
        w_path = '//*[@id="player-stats"]/div[2]/table/tbody/tr[480]'
        xpath = '//*[@id="player-stats"]/div[2]/table'
        #button_path = '/html/body/div/main/div/div[3]/div[2]/table/thead/tr[2]/th[8]'
        '''
        try:
            elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH,xpath)))
            
        finally:
            driver.quit()
        
        '''
        #'''
        wait = WebDriverWait(driver, 10)
        result = wait.until(EC.presence_of_element_located((By.XPATH,w_path)))
        elem = driver.find_element(By.XPATH,xpath)
        
        # Wait for the page to fully load
        #print(elem.text)
        #elem = driver.find_element(By.XPATH,xpath)
        #driver.implicitly_wait(40)
        #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)",elem)
        driver.implicitly_wait(40)
       
        '''if check_exists_by_xpath(driver, "//a[contains(text(),'>')]/preceding-sibling::a[1]"):
            number_of_pages = int(driver.find_element(By.XPATH, "//a[contains(text(),'>')]/preceding-sibling::a[1]").text)
            print(number_of_pages)'''
        # Step 2: Parse HTML code and grab tables with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        
        #return elem
        #rows = soup.find_all('tr')
        #print(rows)
        #return rows
        tables = soup.find_all('table')
        #vals = soup.find_all('td',class_ = 'player_name')
        #print(len(vals))
        #print(vals)
        # Step 3: Read tables with Pandas read_html()
        df = pd.read_html(str(tables))[0]
        #print(dfs)
        data.append(df)
    driver.close()
    return data
elem = get_tables([epm])


# In[4]:


df = elem[0]
df.columns = df.columns.droplevel()
df = df.dropna(subset = 'PLAYER')
df = df[df.PLAYER != 'PLAYER']
df.to_csv('epm_temp.csv',index = False)
df = pd.read_csv('epm_temp.csv')


# In[5]:


new_columns = []
columns = df.columns
for col in columns:
   # print(col)
    #print(df[col].dtype)
    if df[col].dtype == 'object':
       
        if '%' in df.loc[1][col]:
            df[[col,col+'_per']] = df[col].str.split("%",expand=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col+'_per'] = pd.to_numeric(df[col+'_per'], errors='coerce')
#df[['PLAYER','POS']] = df['PLAYER'].str.split('·',expand = True)
#df['PLAYER'] = df['PLAYER'].str.replace(' ', '')
df['pos'] = df['PLAYER'].str.split("·",expand = True)[1]

df['PLAYER'] = df['PLAYER'].str.split("·",expand = True)[0]
df['team'] = df['PLAYER'].str[-4:-1]
df['PLAYER'] =  df['PLAYER'].str[:-4]
df = df.round(2)
df.columns = [x.lower() for x in df.columns]


# In[6]:


df.to_csv('epm/epm.csv',index = False)


# In[7]:


def scrape_LEBRON():
    url = 'https://www.bball-index.com/lebron-database/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(id = 'table_1')
    df = pd.read_html(str(table),displayed_only=False)[0]
    df = df.dropna(subset = 'Player')
    year = df['Season'].str[0:4].astype(int) +1
    df['year'] = year
    df['Player'] = df['Player'].str.lower()
    df = df.rename(columns = {'Team':'team'})
    return df
df = scrape_LEBRON()


df = df[df['Season'] =='2022-23']
df.to_csv('lebron/lebron.csv',index = False)
df.to_csv('2023/lebron/lebron.csv',index = False)


# In[10]:


'''
for i in range(2013,2022):
        


 
    path = str(i+1)+'/lebron/'
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = df[df['year'] ==i+1]
    frame.to_csv(str(i+1)+'/lebron/lebron.csv',index = False)'''


# In[7]:


df


# In[ ]:




