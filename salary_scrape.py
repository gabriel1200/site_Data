#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

# Dictionary of team acronyms and their respective URLs (without season)
urls_dict = {
    "ATL": "https://hoopshype.com/salaries/atlanta_hawks/",
    "BOS": "https://hoopshype.com/salaries/boston_celtics/",
    "BKN": "https://hoopshype.com/salaries/brooklyn_nets/",
    "CHA": "https://hoopshype.com/salaries/charlotte_hornets/",
    "CHI": "https://hoopshype.com/salaries/chicago_bulls/",
    "CLE": "https://hoopshype.com/salaries/cleveland_cavaliers/",
    "DET": "https://hoopshype.com/salaries/detroit_pistons/",
    "IND": "https://hoopshype.com/salaries/indiana_pacers/",
    "MIA": "https://hoopshype.com/salaries/miami_heat/",
    "MIL": "https://hoopshype.com/salaries/milwaukee_bucks/",
    "NYK": "https://hoopshype.com/salaries/new_york_knicks/",
    "ORL": "https://hoopshype.com/salaries/orlando_magic/",
    "PHI": "https://hoopshype.com/salaries/philadelphia_76ers/",
    "TOR": "https://hoopshype.com/salaries/toronto_raptors/",
    "WAS": "https://hoopshype.com/salaries/washington_wizards/",
    "DAL": "https://hoopshype.com/salaries/dallas_mavericks/",
    "DEN": "https://hoopshype.com/salaries/denver_nuggets/",
    "GSW": "https://hoopshype.com/salaries/golden_state_warriors/",
    "HOU": "https://hoopshype.com/salaries/houston_rockets/",
    "LAC": "https://hoopshype.com/salaries/los_angeles_clippers/",
    "LAL": "https://hoopshype.com/salaries/los_angeles_lakers/",
    "MEM": "https://hoopshype.com/salaries/memphis_grizzlies/",
    "MIN": "https://hoopshype.com/salaries/minnesota_timberwolves/",
    "NOP": "https://hoopshype.com/salaries/new_orleans_pelicans/",
    "OKC": "https://hoopshype.com/salaries/oklahoma_city_thunder/",
    "PHX": "https://hoopshype.com/salaries/phoenix_suns/",
    "POR": "https://hoopshype.com/salaries/portland_trail_blazers/",
    "SAC": "https://hoopshype.com/salaries/sacramento_kings/",
    "SAS": "https://hoopshype.com/salaries/san_antonio_spurs/",
    "UTA": "https://hoopshype.com/salaries/utah_jazz/"
}

# List of years to scrape (from 1990 to 2023)
years = list(range(1991, 2025))

# Initialize an empty DataFrame to store the results
all_data = pd.DataFrame()

# Loop through each team and year, scrape the data, and append to all_data DataFrame
for team, base_url in urls_dict.items():
    for year in years:
        season_str = f"{year-1}-{year}"  # Format the season as "1990-1991"
        url = f"{base_url}{season_str}/"  # Construct the full URL
        
        try:
            # Read the table from the URL
            df = pd.read_html(url)[0]
            
            # Clean up the columns (remove any column with '*')
            df.columns = df.columns.droplevel()  # Remove top level of multi-index columns if present
            df = df[[col for col in df.columns if '*' not in col]]
            
            # Rename columns to 'Player' and 'Salary'
            df.columns = ['Player', 'Salary']
            
            # Add the 'team' and 'year' columns
            df['Team'] = team
            df['Year'] = year
            
            # Append the cleaned dataframe to the all_data dataframe
            all_data = pd.concat([all_data, df], ignore_index=True)
            
            print(f"Scraped {team} for {season_str}")
        except Exception as e:
            print(f"Failed to scrape {team} for {season_str}: {e}")

# Display or save the full scraped data
print(all_data.head())

# Save to a CSV file
all_data.to_csv('nba_salaries_raw.csv', index=False)


# In[2]:


all_data


# In[ ]:




