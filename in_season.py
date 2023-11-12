#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import time


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException 
from selenium.webdriver.support.select import Select

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
urls = [url]
paths = [xpath]
data = get_ptables(urls,paths)
df = data[0]
df = df[[col for col in df.columns if ' RANK' not in col]]
df = df.drop(columns=['Unnamed: 0'])
df.to_csv('inseason_2024.csv',index = False)


# In[ ]:





# In[ ]:





# In[ ]:




