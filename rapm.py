#!/usr/bin/env python
# coding: utf-8

# In[12]:


from selenium import webdriver
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
import time
from unidecode import unidecode
import pandas as pd
import json
import urllib


# In[15]:


print(data[0].keys())


# In[49]:


def fiveyear():
    chunk = 0
    all_found=False
    frames = []
    while all_found == False:

        print(chunk)
        url= "https://www.thespax.com/wp-admin/admin-ajax.php?action=wp_ajax_ninja_tables_public_action&table_id=4332&target_action=get-all-data&default_sorting=old_first&skip_rows=0&limit_rows=0&chunk_number="+str(chunk)+"&ninja_table_public_nonce=4d7647466f"
        response = requests.get(url)
        if chunk<6:
            data = response.json()
            df = pd.json_normalize(data, meta=['options', 'value',[ 'player'], ['seasons'], ['rapm'], ['periodrank'],['overallrank'],['___id___']])
            df.drop(columns='options.classes',inplace=True)
            df.columns=['player','seasons','poss','rapm','period_rank','overallrank','id']
            frames.append(df)
            chunk+=1

        else:
            all_found=True
    rapm = pd.concat(frames)
    return rapm
rapm = fiveyear()


# In[53]:


rapm['poss'] = rapm['poss'].astype(int)
rapm.to_csv('rapm_5year.csv',index= False)


# In[55]:


rapm.sort_values(by='poss',ascending = False).head(25)


# In[42]:


response.status_code.dtpe


# In[ ]:




