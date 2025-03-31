#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Populate the new DataFrame with player options and team options
import pandas as pd
import math
import plotly.figure_factory as ff

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import pandas as pd

def team_books(team):
    print(f"Getting salary data for {team}")
    
    nba_team_urls = {
        "ATL": "https://www.spotrac.com/nba/atlanta-hawks/yearly",
        "BOS": "https://www.spotrac.com/nba/boston-celtics/yearly",
        "BKN": "https://www.spotrac.com/nba/brooklyn-nets/yearly",
        "CHA": "https://www.spotrac.com/nba/charlotte-hornets/yearly",
        "CHI": "https://www.spotrac.com/nba/chicago-bulls/yearly",
        "CLE": "https://www.spotrac.com/nba/cleveland-cavaliers/yearly",
        "DAL": "https://www.spotrac.com/nba/dallas-mavericks/yearly",
        "DEN": "https://www.spotrac.com/nba/denver-nuggets/yearly",
        "DET": "https://www.spotrac.com/nba/detroit-pistons/yearly",
        "GSW": "https://www.spotrac.com/nba/golden-state-warriors/yearly",
        "HOU": "https://www.spotrac.com/nba/houston-rockets/yearly",
        "IND": "https://www.spotrac.com/nba/indiana-pacers/yearly",
        "LAC": "https://www.spotrac.com/nba/la-clippers/yearly",
        "LAL": "https://www.spotrac.com/nba/los-angeles-lakers/yearly",
        "MEM": "https://www.spotrac.com/nba/memphis-grizzlies/yearly",
        "MIA": "https://www.spotrac.com/nba/miami-heat/yearly",
        "MIL": "https://www.spotrac.com/nba/milwaukee-bucks/yearly",
        "MIN": "https://www.spotrac.com/nba/minnesota-timberwolves/yearly",
        "NOP": "https://www.spotrac.com/nba/new-orleans-pelicans/yearly",
        "NYK": "https://www.spotrac.com/nba/new-york-knicks/yearly",
        "OKC": "https://www.spotrac.com/nba/oklahoma-city-thunder/yearly",
        "ORL": "https://www.spotrac.com/nba/orlando-magic/yearly",
        "PHI": "https://www.spotrac.com/nba/philadelphia-76ers/yearly",
        "PHX": "https://www.spotrac.com/nba/phoenix-suns/yearly",
        "POR": "https://www.spotrac.com/nba/portland-trail-blazers/yearly",
        "SAC": "https://www.spotrac.com/nba/sacramento-kings/yearly",
        "SAS": "https://www.spotrac.com/nba/san-antonio-spurs/yearly",
        "TOR": "https://www.spotrac.com/nba/toronto-raptors/yearly",
        "UTA": "https://www.spotrac.com/nba/utah-jazz/yearly",
        "WAS": "https://www.spotrac.com/nba/washington-wizards/yearly"
    }
    
    
    url = nba_team_urls[team.upper()]
    
    # Make the HTTP request
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all table bodies
    tbodies = soup.find_all('tbody')
    
    # Lists to store link data
    texts = []
    hrefs = []
    
    # Process each tbody
    for tbody in tbodies:
        # Find all td elements that contain links
        td_with_links = tbody.find_all('td')
        
        for td in td_with_links:
            # Find all anchor tags within the td
            links = td.find_all('a')
            
            # Extract hrefs from the links
            for link in links:
                href = link.get('href')
                if href and href != 'javascript:void(0)':  # Only add valid links
                    texts.append(link.text.strip())
                    hrefs.append(href)
    
    # Create DataFrame from the collected data
    links_df = pd.DataFrame({
        'text': texts,
        'href': hrefs
    })
    
    # Get the original table data as well
    tables_df= pd.read_html(url)
    links_df.rename(columns={'text':'name','href':'url'},inplace=True)

    links_df['id']=links_df['url'].str.split('id/').str[-1]
    
    return links_df

# Example usage


# Display the links DataFrame
teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
'''
salary_frames=[]
for team in teams:
    frame=team_books(team)
    frame['team']=team
    salary_frames.append(frame)
    

salary_master=pd.concat(salary_frames)
salary_master.to_csv('salary_id.csv',index=False)
'''


# In[2]:


salary_master=pd.read_csv('salary_id.csv')
salary_master.drop_duplicates(inplace=True)
print(len(salary_master))
index=pd.read_csv('index_master.csv')

index=index[index.year>2010]

mydict=dict(zip(index['player'].str.lower(),index['nba_id']))

salary_master['nba_id']=salary_master['name'].str.lower().map(mydict)
salary_master


salary_master[salary_master.nba_id.isna()]


# In[3]:


import pandas as pd
from fuzzywuzzy import fuzz
from unidecode import unidecode
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from unidecode import unidecode
import numpy as np

def match_names(salary_df, index_df, threshold=85):
    """
    Match names between two dataframes using fuzzy string matching and containment checking.
    Checks if salary names are contained within index names to handle cases where salary names
    are partial versions of the full names in the index.
    
    Parameters:
    -----------
    salary_df : DataFrame
        DataFrame containing salary information with 'name' column
    index_df : DataFrame
        DataFrame containing index information with 'player' and 'nba_id' columns
    threshold : int
        Minimum similarity score (0-100) required for a match
        
    Returns:
    --------
    DataFrame
        Original salary DataFrame with matched nba_ids
    dict
        Dictionary of name mappings for manual verification
    """
    
    def clean_name(name):
        # Convert to lowercase, remove accents and extra whitespace
        return unidecode(str(name).lower().strip())
    
    # Clean names in both dataframes
    salary_names = salary_df['name'].apply(clean_name)
    index_names = index_df['player'].apply(clean_name)
    
    # Create dictionary for exact matches first
    exact_matches = dict(zip(index_names, index_df['nba_id']))
    
    # Initialize results
    matched_ids = []
    name_mappings = {}
    
    # For each salary name, find the best match
    for salary_name in salary_names:
        # Try exact match first
        if salary_name in exact_matches:
            matched_ids.append(exact_matches[salary_name])
            name_mappings[salary_name] = {
                'matched_to': salary_name,
                'score': 100,
                'nba_id': exact_matches[salary_name],
                'match_type': 'exact'
            }
            continue
            
        # If no exact match, try containment and fuzzy matching
        max_score = 0
        best_match = None
        best_id = None
        match_type = None
        
        for idx_name, nba_id in zip(index_names, index_df['nba_id']):
            # Check if salary name is contained within index name
            if salary_name in idx_name:
                # Calculate containment score based on length ratio
                length_ratio = len(salary_name) / len(idx_name)
                # Only consider containment if the salary name is at least 50% of the index name length
                if length_ratio >= 0.5:
                    score = 100 * length_ratio
                    if score > max_score:
                        max_score = score
                        best_match = idx_name
                        best_id = nba_id
                        match_type = 'containment'
            
            # If no containment match, try fuzzy matching
            if match_type is None:
                score = fuzz.ratio(salary_name, idx_name)
                if score > max_score:
                    max_score = score
                    best_match = idx_name
                    best_id = nba_id
                    match_type = 'fuzzy'
        
        # If we found a good match
        if max_score >= threshold:
            matched_ids.append(best_id)
            name_mappings[salary_name] = {
                'matched_to': best_match,
                'score': max_score,
                'nba_id': best_id,
                'match_type': match_type
            }
        else:
            matched_ids.append(None)
            name_mappings[salary_name] = {
                'matched_to': None,
                'score': None,
                'nba_id': None,
                'match_type': None
            }
    
    # Create new dataframe with matches
    result_df = salary_df.copy()
    result_df['nba_id'] = matched_ids
    
    return result_df, name_mappings

# Example usage:
# First, install required packages:
# pip install fuzzywuzzy python-Levenshtein unidecode

salary_master = pd.read_csv('salary_id.csv')
index = pd.read_csv('index_master.csv')
index = index[index.year > 2016]

# Match names
matched_df, mappings = match_names(salary_master, index)

# Show unmatched names
unmatched = matched_df[matched_df.nba_id.isna()]
print(f"Total unmatched names: {len(unmatched)}")

# Show some example mappings for verification
problematic_matches = {
    name: info for name, info in mappings.items() 
    if info['score'] is not None and info['score'] < 95
}


# In[4]:


matched_df.drop_duplicates(inplace=True)


# In[5]:


nonmatched=matched_df[matched_df.nba_id.isna()]


# In[6]:


import pandas as pd
import re

def standardize_names(df, name_column):
    """
    Standardizes player names with enhanced handling of special cases.
    """
    def clean_name(name):
        # Initial cleanup
        name = str(name).strip()
        
        # Fix specific formatting issues
        name_fixes = {
            'ilva  Tristan Da Silva': 'Tristan Da Silva',
            'r  Brandon Boston Jr': 'Brandon Boston Jr.',
            'Bub Carrington': 'Ja\'Von Carrington',
            'G.G. Jackson': 'Gregory Jackson II',
            'Nah\'Shon Hyland': 'Bones Hyland',
            'Sviatoslav Mykhailiuk': 'Svi Mykhailiuk',
            'N\'Faly Dante': 'NFaly Dante'  # Remove apostrophe
        }
        
        if name in name_fixes:
            return name_fixes[name]
            
        # Handle suffixes consistently
        suffix_map = {
            r'Jr\.?$': 'Jr.',  # Standardize Jr. suffix
            r'Sr\.?$': 'Sr.',  # Standardize Sr. suffix
            r'III$': 'III',    # Keep III
            r'II$': 'II',      # Keep II
            r'IV$': 'IV',      # Keep IV
            r'V$': 'V'         # Keep V
        }
        
        # Apply suffix standardization
        cleaned_name = name
        for pattern, replacement in suffix_map.items():
            if re.search(pattern, cleaned_name, flags=re.IGNORECASE):
                # Remove the suffix first
                base_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE).strip()
                # Add back the standardized suffix
                cleaned_name = f"{base_name} {replacement}"
        
        # Clean up extra spaces
        cleaned_name = ' '.join(cleaned_name.split())
        
        return cleaned_name
    
    # Create a copy of the dataframe
    result_df = df.copy()
    
    # Store original names and create standardized versions
    result_df['original_name'] = result_df[name_column]
    result_df['standardized_name'] = result_df[name_column].apply(clean_name)
    
    return result_df

# Apply the enhanced standardization

salary=pd.read_csv('salary.csv')
option=pd.read_csv('option.csv')

option_rename={}
seasons=['2024-25', '2025-26', '2026-27', '2027-28', '2028-29', '2029-30', '2030-31']

for season in seasons:
    option_rename[season]='option_'+season


option.rename(columns=option_rename,inplace=True)


salary=salary.merge(option, on =['Player','Team'])
print(salary.columns)
matched_df['Player']=matched_df['name']
salary_standardized = standardize_names(salary, 'Player')
matched_df_standardized = standardize_names(matched_df, 'Player')

# Merge using standardized names
merged = salary_standardized.merge(
    matched_df_standardized,
    left_on='standardized_name',
    right_on='standardized_name',
    how='left'
)

# Clean up the merged dataframe
merged = merged.drop(['Player_y', 'standardized_name'], axis=1)

print(merged)
merged = merged.rename(columns={
    'original_name_x': 'Player',
    'original_name_y': 'matched_name'
})



nba_ids = {
    'Mohamed Bamba': '1628964',
    'Cameron Thomas': '1630560',
    "Nah'Shon Hyland": '1630538',
    'Sviatoslav Mykhailiuk': '1629004',
    'Kenyon Martin Jr.': '1630231',
    'Nikola Topic':'1642260',

    'DaRon Holmes II':'1641747',
     'G.G. Jackson':'1641713'

}
# Check remaining unmatched players
unmatched = merged[merged['nba_id'].isna()]
def map_additional_ids(df, id_mapping):
    """
    Maps additional NBA IDs to players in the dataframe.
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame containing player information
    id_mapping : dict
        Dictionary mapping player names to NBA IDs
        
    Returns:
    --------
    DataFrame
        Updated DataFrame with mapped NBA IDs
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # For each player in the mapping
    for player, nba_id in id_mapping.items():
        # Update the nba_id where the player name matches
        mask = result_df['Player'] == player
        result_df.loc[mask, 'nba_id'] = nba_id
    
    return result_df

# Apply the mapping
merged = map_additional_ids(merged, nba_ids)

# Verify the updates
for player in nba_ids.keys():
    player_row = merged[merged['Player'] == player]
    if not player_row.empty:
        print(f"Player: {player}")
        print(f"NBA ID: {player_row['nba_id'].iloc[0]}")
        print("---")

# Show remaining unmatched players
unmatched = merged[merged['nba_id'].isna()]
print("\nRemaining unmatched players:")
print(unmatched['Player'].sort_values())


# In[7]:


unmatched


# In[8]:


merged.drop(columns='Player_x',inplace=True)
merged.to_csv('salary_spread.csv')
merged


# In[9]:


merged.columns


# In[ ]:




