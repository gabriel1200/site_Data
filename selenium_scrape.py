import pandas as pd
import math
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import time
import re

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

def setup_driver(headless=True):
    """
    Set up Chrome WebDriver with optimal settings
    
    Args:
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        webdriver.Chrome: Configured Chrome driver
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # Add other useful options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Faster loading
    chrome_options.add_argument("--disable-javascript")  # If JS not needed
    
    # User agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def clean_player_name(name: str) -> str:
    """
    Cleans player names by removing common suffixes (Jr., II, III, etc.)
    regardless of their position in the string.
    
    Args:
        name (str): Player name to clean
        
    Returns:
        str: Cleaned player name
    """
    # List of common name suffixes to remove
    suffixes = {'Jr.', 'Jr', 'II', 'III', 'IV', 'Sr.', 'Sr'}

    # Split the name into parts and remove any suffix
    name_parts = [part for part in name.split() if part not in suffixes]
    
    # Rejoin the cleaned name
    cleaned_name = ' '.join(name_parts)
    
    return cleaned_name


def clean_seasonal_salaries(data, seasonlist, header='Dead Money'):
    """
    Cleans salary data for specified seasons within the Dead Money section
    
    Parameters:
    data (dict): Input data containing Dead Money section
    seasonlist (list): List of seasons to process
    
    Returns:
    pd.DataFrame: DataFrame with cleaned numerical salary values for all seasons
    """
    if 'Dead Money' not in data:
        return pd.DataFrame()
        
    dead = data[header].copy()
    
    for season in seasonlist:
        if season not in dead.columns:
            continue
            
        # Fill NA values
        dead[season] = dead[season].fillna('0')
        
        # Remove 'Ext. Elig.' and strip whitespace
        dead[season] = dead[season].str.replace('Ext. Elig.', '', regex=False).str.strip()
        
        # Convert strings to numeric values
        dead[season] = dead[season].apply(lambda x: convert_salary_string(x))
        
        # Ensure integer type
        dead[season] = dead[season].replace('', 0)
        dead[season] = dead[season].astype(int)
    
    return dead

def convert_salary_string2(salary_str):
    """
    Convert salary strings to decimal values, handling both million and thousand scale values.
    
    Args:
        salary_str: String representation of salary (e.g., "$724,883", "$1,234,567")
    
    Returns:
        float: Converted salary value
    """
    if isinstance(salary_str, (int, float)):
        return float(salary_str)
    
    if not salary_str or pd.isna(salary_str):
        return 0.0
        
    # Remove non-numeric characters except commas
    cleaned = re.sub(r'[^\d,]', '', str(salary_str))
    
    if not cleaned:
        return 0.0
    
    # Split by commas to count the number groups
    parts = cleaned.split(',')
    
    if len(parts) == 1:  # No commas, direct conversion
        return float(parts[0])
    
    # Join all parts and convert to number
    number = float(''.join(parts))
    
    # If the number is unreasonably large (over 100 million), 
    # assume it should be scaled down
    if number > 100000000:  # 100 million threshold
        return number / 10
        
    return number

def convert_salary_string(value):
    """
    Converts a salary string to a pure number, handling percentage suffixes for any size number
    """
    if pd.isna(value) or value == '':
        return '0'
    
    if isinstance(value, (int, float)):
        return str(int(value))
    
    value_str = str(value)
    cutoff = 1
    if len(value_str) > 15:
        cutoff = 2
    
    # Check for special strings
    strings_to_check = ['UFA', 'RFA', 'NA', 'N/A']
    if any(s in value_str for s in strings_to_check):
        return '0'
    
    # First, remove $ and commas
    value_str = value_str.replace('$', '').replace(',', '')
    
    # Find where the decimal point is (indicating start of percentage)
    decimal_index = value_str.find('.')
    if decimal_index != -1:
        # Take everything up to the last 8 digits before the decimal
        # (changed from 7 to 8 to capture the correct number of digits)
        non_decimal_part = value_str[:decimal_index]
        value_str = non_decimal_part[:-cutoff]  # Remove last 2 digits instead of 1
 
    # Remove any remaining non-digits
    clean_value = ''.join(c for c in value_str if c.isdigit())
    return clean_value if clean_value else '0'

def get_team_data(url: str, driver: webdriver.Chrome = None, timeout: int = 10) -> Dict[str, pd.DataFrame]:
    """
    Fetch and parse HTML tables from the team URL using Selenium, along with their section headers.
    Returns dictionary of {header: dataframe}
    
    Args:
        url (str): URL to scrape
        driver (webdriver.Chrome): Selenium driver instance (optional)
        timeout (int): Timeout in seconds
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping headers to DataFrames
    """
    close_driver = False
    if driver is None:
        driver = setup_driver()
        close_driver = True
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load completely
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Additional wait to ensure all content is loaded
        time.sleep(2)
        
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all tables and their preceding h2 headers
        tables = soup.find_all('table')
        data_dict = {}
        
        for table in tables:
            # Look for the nearest preceding h2
            header = None
            prev_elem = table.find_previous('h2')
            if prev_elem:
                header = prev_elem.get_text(strip=True)
            
            # Parse table into DataFrame
            try:
                df = pd.read_html(str(table))[0]

                data_dict[header] = df
            except ValueError as e:
                print(f"Error parsing table with header '{header}': {e}")
                continue
        
        return data_dict
        
    except TimeoutException as e:
        print(f"Timeout waiting for page to load: {e}")
        return {}
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}
    finally:
        if close_driver:
            driver.quit()

def team_books(team, driver=None):
    """
    Get team salary and option data using Selenium
    
    Args:
        team (str): Team abbreviation
        driver (webdriver.Chrome): Optional Selenium driver instance
        
    Returns:
        tuple: (salary_df, option_df) - DataFrames containing salary and option data
    """
    print(team)
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
    data = get_team_data(url, driver)

    if 'Upcoming Deadlines' not in data or 'Active Roster' not in data:
        print(f"Warning: Required data sections not found for {team}")
        return pd.DataFrame(), pd.DataFrame()

    df = data['Upcoming Deadlines']
    salary_df = data['Active Roster']

    columns = ['Player']
    for col in salary_df.columns[1:]:
        columns.append(col)
    
    df.columns = ['Deadline Date', 'Player', 'Type', 'Value']
    salary_df.columns = columns

    # Clean player names in both DataFrames
    salary_df['Player'] = salary_df['Player'].str.split(' ').str[1:].str.join(' ').apply(clean_player_name)
    df['Player'] = df['Player'].apply(clean_player_name)

    seasons = ['2024-25', '2025-26', '2026-27', '2027-28', '2028-29']
    extra_seasons = ['2029-30', '2030-31']
    for seas in extra_seasons:
        if seas in salary_df.columns:
            seasons.append(seas)

    strings_to_check = ['UFA', 'RFA']
    for season in seasons:
        if season in salary_df.columns:
            salary_df[season] = salary_df[season].fillna('')
            salary_df[season] = salary_df[season].str.replace('Ext. Elig.', '', regex=False).str.strip()
            salary_df[season] = salary_df[season].apply(lambda x: '0' if any(s in x for s in strings_to_check) else x)
            salary_df[season] = salary_df[season].fillna('0')
            salary_df[season] = salary_df[season].apply(convert_salary_string)
            salary_df[season] = salary_df[season].str.replace(r'\D', '', regex=True)
            salary_df[season] = salary_df[season].replace('', 0)

    if 'Dead Money' in data.keys():
        seasonlist = ['2024-25', '2025-26', '2026-27', '2027-28', '2028-29', '2029-30']
        dead = clean_seasonal_salaries(data, seasonlist)
        alldead = pd.DataFrame()
        
        for season in seasonlist:
            if season in dead.columns:
                alldead[season] = [dead[season].sum()]
        alldead['Player'] = ['Dead Cap']
        alldead.reset_index(inplace=True)
        salary_df = pd.concat([salary_df, alldead])

    players = salary_df['Player'].unique()
    data_list = []

    for player in players:
        player_data = df[df['Player'] == player]
        row = {'Player': player}
        for season in seasons:
            if season in salary_df.columns:
                row[season] = 0
                season_data = player_data[player_data['Type'].str.contains(season, na=False)]
                if not season_data.empty:
                    if 'PLAYER' in season_data['Type'].values[0]:
                        row[season] = 'P'
                    elif 'CLUB' in season_data['Type'].values[0]:
                        row[season] = 'T'
                    elif 'GUARANTEED' in season_data['Type'].values[0]:
                        row[season] = 'NG'
                    elif 'EXTENSION' in season_data['Type'].values[0]:
                        row[season] = 'EE'
                    elif 'RFA' in season_data['Type'].values[0]:
                        row[season] = 'RFA'
                    elif 'UNREST' in season_data['Type'].values[0]:
                        row[season] = 'UFA'
                    else:
                        row[season] = season_data['Type'].values[0] + (' ' + season_data['Value'].values[0] if not pd.isna(season_data['Value'].values[0]) else '')
        data_list.append(row)

    new_df = pd.DataFrame(columns=['Player'] + seasons, data=data_list)
    new_df = new_df.drop_duplicates().reset_index(drop=True)
    salary_df = salary_df.drop_duplicates().reset_index(drop=True)

    for season in seasons:
        if season in salary_df.columns:
            salary_df[season] = salary_df[season].astype(float)

    salary_df['Team'] = team
    new_df['Team'] = team

    return salary_df, new_df

# Main execution
def main():
    """
    Main function to scrape all team data
    """
    teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 
             'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 
             'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
    
    # Initialize driver once for all teams to improve performance
    driver = setup_driver()
    
    try:
        salary = []
        options = []
        
        for team in teams:
            try:
                salary_df, option_df = team_books(team, driver)
                salary.append(salary_df)
                options.append(option_df)
                
                # Add small delay between requests to be respectful
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing team {team}: {e}")
                continue

        # Combine all data
        if salary:
            salary_df = pd.concat(salary, ignore_index=True)
        else:
            salary_df = pd.DataFrame()
            
        if options:
            option_df = pd.concat(options, ignore_index=True)
        else:
            option_df = pd.DataFrame()
        
        # Save to CSV
        salary_df.to_csv('salary.csv', index=False)
        option_df.to_csv('option.csv', index=False)
        
        print(f"Successfully processed {len(salary)} teams")
        return salary_df, option_df
        
    finally:
        driver.quit()

if __name__ == "__main__":
    salary_df, option_df = main()
    print("Scraping completed!")
    print(f"Salary data shape: {salary_df.shape}")
    print(f"Options data shape: {option_df.shape}")