#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
import configparser



# In[2]:


url = "https://bball-index.shinyapps.io/Lebron/__sockjs__/n=1X3EzJCDf7I2hrdArE/t=aafccad80f857164d4ddfc525f26a6b7/w=d2402a9b/s=0/396/gvz1w1g2/eventsource"
headers = {
      
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",

        "Connection": "keep-alive",
    }
page = requests.get(url,headers = headers)
soup = BeautifulSoup(page.content, "html.parser")
soup.find('table')


# In[3]:


soup.text


# In[4]:


def scrape_LEBRON():
    headers = {
      
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",

        "Connection": "keep-alive",
    }
    url = 'https://www.bball-index.com/lebron-database/'
    page = requests.get(url,headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(id = 'table_1')
    df = pd.read_html(str(table),displayed_only=False)[0]
    df = df.dropna(subset = 'Player')
    year = df['Season'].str[0:4].astype(int) +1
    df['year'] = year
    df['Player'] = df['Player'].str.lower()
    df = df.rename(columns = {'Team':'team','LEBRON Contract Value':'Value Added'})
    return df
df = scrape_LEBRON()

df.to_csv('lebron.csv',index = False)
df = df[df['Season'] =='2023-24']
df.to_csv('lebron/lebron.csv',index = False)
#df.to_csv('2023/lebron/lebron.csv',index = False)


# In[5]:


old = pd.read_csv('old_lebron.csv')
new = pd.read_csv('lebron.csv')
set(new.columns) - set(old.columns)


# In[6]:


files = glob.glob('epm/*')
try:
    for f in files:
        os.remove(f)
    os.remove(r'C:\Users\gaber\Downloads\EPM data.csv')
except Exception as e:
    print('No file located, proceeding') 
    
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
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.get(epm)
    try:
        # find username/email field and send the username itself to the input field
        driver.find_element("name", "email").click()
        driver.find_element("name", "email").send_keys(username)
        # find password input field and insert password as well
        driver.find_element("name", "password").click()
        driver.find_element("name", "password").send_keys(password)
        # click login button
        xpath ='/html/body/div/div[2]/div/div/div[2]/form/div[2]/div[2]/button'
        wait = WebDriverWait(driver, 10)
        pause = wait.until(EC.presence_of_element_located((By.XPATH,xpath)))

        driver.find_element(By.XPATH, xpath).click()
        
        path2 ='/html/body/div/main/div/div[2]/div[1]/div[6]/span/button'
        #wait = WebDriverWait(driver, 10)
        #pause = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'outlined svelte-aai53c'))) 
        time.sleep(5)
        driver.find_element(By.XPATH, path2).click()
        print('located')

        
        #url_list = [url1,url2,url3,url4,url5]

        #os.remove('epm/epm.csv')
        time.sleep(10)
        #os.rename('epm/EPM data.csv','epm/epm.csv')
        driver.close()
        
    except Exception as e:
        print(e)

load_epm(username,password)


# In[7]:


download_path = r'C:\Users\gaber\Downloads\EPM data.csv'
#replace download path with whatever the file path for your download folder is
df = pd.read_csv(download_path)
df.to_csv('epm/epm.csv',index = False)


# In[ ]:





# In[8]:


'''
for i in range(2013,2022):
        


 
    path = str(i+1)+'/lebron/'
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = df[df['year'] ==i+1]
    frame.to_csv(str(i+1)+'/lebron/lebron.csv',index = False)'''


# In[9]:


df


# In[ ]:




