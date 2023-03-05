#!/usr/bin/env python
# coding: utf-8

# In[30]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path


from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import time
import shutil
import glob
files = glob.glob('epm/*')
for f in files:
    os.remove(f)
    
config = configparser.RawConfigParser()
config.read('conf.cfg')
    
details_dict = dict(config.items('LOGIN'))

username = details_dict['username']
password = details_dict['password']


def load_epm(username,password):
    options=webdriver.ChromeOptions()
    # Step 1: Create a session and load the page
    epm = 'https://dunksandthrees.com/epm'
    directory =  str(os.getcwd()) +'\epm'
    pref={"download.default_directory":directory}
    #example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
    options.add_experimental_option("prefs",pref)
    driver = webdriver.Chrome(options=options)
    driver.get(epm)
    try:
        # find username/email field and send the username itself to the input field
        driver.find_element("name", "email").send_keys(username)
        # find password input field and insert password as well
        driver.find_element("name", "password").send_keys(password)
        # click login button
        xpath ='/html/body/div/div[2]/div/div/div[2]/form/div[2]/div[2]/button'
        wait = WebDriverWait(driver, 10)
        pause = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))

        driver.find_element(By.XPATH, xpath).click()

        path2 ='/html/body/div/main/div/div[2]/div[1]/div[7]/span/button'
        pause = wait.until(EC.presence_of_element_located((By.XPATH,path2)))        

        driver.find_element(By.XPATH, path2).click()
        #url_list = [url1,url2,url3,url4,url5]

        time.sleep(10)
        #os.remove('epm/epm.csv')
        os.rename('epm/EPM data.csv','epm/epm.csv')
        driver.close()
    except Exception as e:
        print('Driver Failed')
load_epm(username,password)


# In[32]:


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


# In[18]:





# In[19]:





# In[20]:


'''
for i in range(2013,2022):
        


 
    path = str(i+1)+'/lebron/'
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = df[df['year'] ==i+1]
    frame.to_csv(str(i+1)+'/lebron/lebron.csv',index = False)'''


# In[7]:


df


# In[31]:


def get_tables(url_list):
    data = []
    driver = webdriver.Chrome()
    for url in url_list:
        print(url)
        
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #w_path = '//*[@id="player-stats"]/div[2]/table/tbody/tr[480]'
        w_path = '/html/body/div/main/div/div[2]/div[1]/div[3]/table/tfoot'
        xpath = '/html/body/div/main/div/div[2]/div[1]/div[3]'
        
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
        driver.execute_script("return arguments[0].scrollIntoView(true);", elem)
  
        # Wait for the page to fully load
        #print(elem.text)
        #elem = driver.find_element(By.XPATH,xpath)
        #driver.implicitly_wait(40)
        #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)",elem)

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
    df = elem[0]
    df.columns = df.columns.droplevel()
    df = df.rename(columns = {'Player':'PLAYER'})
    df = df.dropna(subset = 'PLAYER')
    df = df[df.PLAYER != 'PLAYER']
    df.to_csv('epm_temp.csv',index = False)
    df = pd.read_csv('epm_temp.csv')
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
    df.to_csv('epm/epm.csv',index = False)


# In[ ]:




