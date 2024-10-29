#!/usr/bin/env python
# coding: utf-8

# In[8]:


import requests
from bs4 import BeautifulSoup,Comment
import pandas as pd
import time
# URL of the NBA awards page

# URL of the NBA awards page
award_acronyms = {
    'Most Valuable Player (Michael Jordan Trophy) Table': 'mvp',
    'NBA Most Valuable Player (Michael Jordan Trophy) Table':'nbamvp',
    'ABA Most Valuable Player (Michael Jordan Trophy) Table':'abamvp',
    'Rookie of the Year (Wilt Chamberlain Trophy) Table': 'roy',
    'NBA Rookie of the Year (Wilt Chamberlain Trophy) Table':'nbaroy',
    'ABA Rookie of the Year (Wilt Chamberlain Trophy) Table':'abaroy',
    'All-NBA Teams Table': 'all-nba',
    'All-Defensive Teams Table': 'all-defensive',
    'All-Rookie Teams Table': 'all-rookie',
    'Defensive Player of the Year (Hakeem Olajuwon Trophy) Table': 'dpoy',
    'Sixth Man of the Year (John Havlicek Trophy) Table': '6moy',
    'Most Improved Player (George Mikan Trophy) Table': 'mip',
    'Clutch Player of the Year Table': 'clutch player',
    'Coach of the Year (Red Auerbach Trophy) Table': 'coy'
}
for year in range(1971, 2025):
    url = f"https://www.basketball-reference.com/awards/awards_{year}.html"
    names=[]

    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all the tables on the page, including those in comments
    all_tables = soup.find_all("table", class_="sortable stats_table")
    comment_tables = soup.find_all(string=lambda text: isinstance(text, Comment))


    comment_tables =   [table for table in comment_tables if '<table' in table]

    
    frames = []
    
    # Iterate through the tables and extract the data
    for table in all_tables + comment_tables:
        # Check if the table is inside a comment
        if isinstance(table, Comment):
            # Parse the table from the comment
            table_html = BeautifulSoup(str(table), "html.parser")
     
            table_element = table_html.find("table")
        else:
            table_element = table
        
        # Get the table header (award name)
        award_name = table_element.find("caption").text.strip()

        
        
        # Extract the table data into a pandas DataFrame
        df = pd.read_html(str(table_element))[0]
        df.columns = df.columns.droplevel()
        df['year'] = year

        award = award_acronyms[award_name]
        df['award'] = award

        df.to_csv('awards/'+award+str(year)+'.csv',index=False)
        priny(year)
    time.sleep(10)




# In[4]:


award_acronyms['NBA Most Valuable Player (Michael Jordan Trophy) Table']


# In[ ]:




