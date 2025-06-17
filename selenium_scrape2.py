import pandas as pd
import math
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple, Optional
import time
import re
import sys
from bs4 import BeautifulSoup
# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Constants
NBA_TEAM_URLS = {
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

DATATABLE_CONTAINERS = {
    'salary': 'dataTable-active',
    'options': 'dataTable-active', # Corrected ID for options table
    'dead_money': 'dataTable-dead',
    'cap_holds': 'dataTable-cap-hold',
    'summary': 'dataTable-summary'
}

SEASONS = [ '2025-26', '2026-27', '2027-28', '2028-29','2029-30']
EXTRA_SEASONS = [ '2030-31']
FREE_AGENT_TYPES = ['UFA', 'RFA']

def setup_driver():
    """
    Set up Chrome WebDriver with appropriate options.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_table_by_id(driver: webdriver.Chrome, table_id: str, timeout: int = 15) -> Optional[pd.DataFrame]:
    """
    Fetch a specific table by its ID using Selenium.
    Returns DataFrame or None if not found.
    """
    try:
        table_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, table_id))
        )
        table_html = table_element.get_attribute('outerHTML')
        df = pd.read_html(table_html, header=0)[0] # Set header to the first row
        return df

    except TimeoutException:
        print(f"Table with ID '{table_id}' not found within timeout")
        return None
    except Exception as e:
        print(f"Error fetching table with ID '{table_id}': {e}")
        return None

def get_table_with_classes_by_id(driver: webdriver.Chrome, table_id: str, timeout: int = 15) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Fetch a specific table by its ID using Selenium and return both DataFrame and raw HTML.
    Returns (DataFrame, HTML) or (None, None) if not found.
    """
    try:
        table_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, table_id))
        )
        table_html = table_element.get_attribute('outerHTML')
        df = pd.read_html(table_html, header=0)[0] # Set header to the first row
        return df, table_html

    except TimeoutException:
        print(f"Table with ID '{table_id}' not found within timeout")
        return None, None
    except Exception as e:
        print(f"Error fetching table with ID '{table_id}': {e}")
        return None, None

def get_team_data(driver: webdriver.Chrome, url: str, timeout: int = 15) -> Dict[str, pd.DataFrame]:
    """
    Fetch and parse specific tables from the team URL using their IDs.
    Returns dictionary of table_type -> DataFrame (or tuple for options table)
    """
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(3)

        tables_data = {}
        for table_type, table_id in DATATABLE_CONTAINERS.items():
            if table_type == 'options':
                # For options table, we need both DataFrame and HTML
                df, html = get_table_with_classes_by_id(driver, table_id, timeout=10)
                if df is not None:
                    tables_data[table_type] = (df, html)
                    print(f"Successfully fetched {table_type} table with {len(df)} rows")
                else:
                    print(f"Table '{table_type}' (ID: {table_id}) not found")
            else:
                df = get_table_by_id(driver, table_id, timeout=10)
                if df is not None:
                    tables_data[table_type] = df
                    print(f"Successfully fetched {table_type} table with {len(df)} rows")
                else:
                    print(f"Table '{table_type}' (ID: {table_id}) not found")
        return tables_data

    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

def clean_player_name(name: str) -> str:
    """
    Clean player name by removing duplicates, suffixes, and extra text.
    Handles suffixes like Jr., Sr., II, III, IV, etc.
    Also attempts to fix reversed names like 'Young Trae' -> 'Trae Young'.
    """
    if pd.isna(name):
        return ""
    
    name_str = str(name).strip()
    
    # Remove any text in parentheses
    name_str = re.sub(r'\s*\(.*?\)', '', name_str)

    # Define common suffixes to remove
    suffixes = ['Jr', 'Jr.', 'Sr', 'Sr.', 'II', 'III', 'IV', 'V']
    suffix_pattern = r'\b(?:' + '|'.join(re.escape(s) for s in suffixes) + r')\b'
    name_str = re.sub(r'\s*' + suffix_pattern + r'\s*', ' ', name_str, flags=re.IGNORECASE)
    
    # Normalize whitespace
    name_str = re.sub(r'\s+', ' ', name_str).strip()
    
    # Remove duplicate parts
    parts = name_str.split()
    unique_parts = list(dict.fromkeys(parts))

    # Heuristic for flipped names
    if len(unique_parts) == 2:
        return f"{unique_parts[1]} {unique_parts[0]}"

    return " ".join(unique_parts)

def process_salary_value2(value: str) -> float:
    """
    Process salary value from string format - more lenient version.
    """
    if pd.isna(value):
        return None

    value_str = str(value).strip()
    million_match = re.search(r'\$?([\d.]+)M', value_str, flags=re.IGNORECASE)
    if million_match:
        try:
            return float(million_match.group(1)) * 1_000_000
        except ValueError:
            pass
    
    dollar_match = re.search(r'\$?([\d,]+)', value_str)
    if dollar_match:
        try:
            return float(dollar_match.group(1).replace(',', ''))
        except ValueError:
            pass
    
    return None

# Establish a baseline salary cap for the 2025-26 season and project forward.
try:
    cap_df = pd.read_csv('cap.csv')
    cap_df['Salary Cap'] = cap_df['Salary Cap'].replace({r'[\$,]': ''}, regex=True).astype(float)
    SALARY_CAPS = cap_df['Salary Cap'].tolist()
    print("Successfully loaded and processed cap.csv. Salary caps are ready.")
except FileNotFoundError:
    print("Error: cap.csv not found. Using fallback projected salary caps.")
    BASE_SALARY_CAP = 155_000_000
    SALARY_CAPS = [BASE_SALARY_CAP * (1.10**i) for i in range(10)]

MAX_CAP_PERCENTAGE = 50.0

def process_salary_value(value: str) -> float:
    """
    Convert complex salary strings to float values.
    """
    if pd.isna(value):
        return 0.0

    value_str = str(value).strip()

    if any(fa_type in value_str for fa_type in FREE_AGENT_TYPES):
        return 0.0

    # Handle million format (e.g., "$38.6M")
    million_match = re.search(r'\$?([\d\.]+)M', value_str, re.IGNORECASE)
    if million_match:
        return float(million_match.group(1)) * 1_000_000

    # Handle simple dollar amounts without percentages
    if '%' not in value_str:
        dollar_match = re.search(r'\$([\d,]+)', value_str)
        if dollar_match:
            return float(dollar_match.group(1).replace(',', ''))
        return 0.0

    # Extract all digits from the string
    full_numeric_part = re.sub(r'[\D]', '', value_str)
    
    # NBA minimum salary is over $1M, so we know the salary portion should be at least 7 digits
    MIN_SALARY = 1_157_153
    scenarios = []

    # Try different splits for percentage (1-2 decimal places)
    for percent_digits in [1, 2, 3]:  # Handle X.X% or XX.X% formats
        if len(full_numeric_part) <= percent_digits:
            continue
            
        # Extract potential percentage portion
        percent_part = full_numeric_part[-percent_digits:]
        salary_part = full_numeric_part[:-percent_digits]
        
        if not salary_part:
            continue
            
        # Try to construct a reasonable percentage
        if percent_digits == 1:
            # Single digit like "6" -> could be 6.0%
            percent_val = float(percent_part)
        elif percent_digits == 2:
            # Two digits like "36" -> could be 3.6% or 36%
            percent_val_option1 = float(f"{percent_part[0]}.{percent_part[1]}")
            percent_val_option2 = float(percent_part)
            
            # Test both options
            for pct in [percent_val_option1, percent_val_option2]:
                if 0 < pct < MAX_CAP_PERCENTAGE:
                    salary_val = float(salary_part)
                    if salary_val >= MIN_SALARY:
                        scenarios.append({'salary': salary_val, 'percent': pct})
            continue
        else:  # percent_digits == 3
            # Three digits like "250" -> could be 25.0%
            if len(percent_part) >= 2:
                percent_val = float(f"{percent_part[:-1]}.{percent_part[-1]}")
            else:
                continue
        
        # For 1 and 3 digit cases
        if percent_digits != 2 and 0 < percent_val < MAX_CAP_PERCENTAGE:
            salary_val = float(salary_part)
            if salary_val >= MIN_SALARY:
                scenarios.append({'salary': salary_val, 'percent': percent_val})

    if not scenarios:
        return 0.0

    # Find the scenario that best matches expected salary based on cap percentage
    best_fit = {'min_diff': float('inf'), 'best_salary': 0.0}
    
    for cap in SALARY_CAPS:
        for scen in scenarios:
            # Calculate what the salary should be based on the percentage
            expected_salary = cap * (scen['percent'] / 100.0)
            # Check how close our extracted salary is to the expected salary
            difference = abs(scen['salary'] - expected_salary)
            
            if difference < best_fit['min_diff']:
                best_fit['min_diff'] = difference
                best_fit['best_salary'] = scen['salary']

    return best_fit['best_salary']

def get_available_seasons(salary_df: pd.DataFrame) -> List[str]:
    """
    Get list of available seasons from salary data.
    """
    print(salary_df.columns)
    available_seasons = []
    for season in SEASONS + EXTRA_SEASONS:
        if season in salary_df.columns:
            available_seasons.append(season)
    return available_seasons

def process_salary_data(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process and clean salary data.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(' '.join).str.replace(r' Unnamed: \d+_level_\d', '', regex=True).str.strip()

    if 'Player' in df.columns.get_level_values(0): # Check if 'Player' exists in the top level
      df.columns = df.columns.droplevel(1)

    if 'Player' in df.columns[0] and 'Unnamed' in df.columns[1]:
        df[df.columns[0]] = df[df.columns[1]]
        df = df.drop(columns=df.columns[1])
    
    df.rename(columns={df.columns[0]: 'Player'}, inplace=True)
    
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)

    seasons = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
    for season in seasons:
        if season in df.columns:
            df[season] = df[season].apply(process_salary_value)

    df['Team'] = team
    return df

def extract_option_from_html_cell(soup_cell, season_index: int) -> str:
    """
    Extract option type from HTML cell by checking CSS classes.
    """
    if soup_cell is None:
        return '0'
    
    # Look for elements with pill classes
    pill_elements = soup_cell.find_all(class_=lambda x: x and ('pill-' in x))
    
    for pill in pill_elements:
        classes = pill.get('class', [])
        class_str = ' '.join(classes)
        
        # Check for specific pill types based on CSS classes
        if 'pill-club' in class_str:
            return 'T'  # Team option
        elif 'pill-player' in class_str:
            return 'P'  # Player option
        elif 'pill-early' in class_str:
            return 'ETO'  # Early termination option
        elif 'pill-rfa' in class_str:
            return 'RFA'  # Restricted free agent
        elif 'pill-ufa' in class_str:
            return 'UFA'  # Unrestricted free agent
        elif 'pill-extension' in class_str or 'pill-eligible' in class_str:
            return 'EE'  # Extension eligible
        elif 'pill-guaranteed' in class_str:
            return 'G'  # Guaranteed
        elif 'pill-non-guaranteed' in class_str:
            return 'NG'  # Non-guaranteed
    
    # If no pill classes found, check text content as fallback
    text_content = soup_cell.get_text(strip=True).upper()
    if 'PLAYER' in text_content: return 'P'
    if 'CLUB' in text_content or 'TEAM' in text_content: return 'T'
    if 'EARLY' in text_content and 'TERM' in text_content: return 'ETO'
    if 'RFA' in text_content: return 'RFA'
    if 'UFA' in text_content: return 'UFA'
    if 'GUARANTEED' in text_content: return 'G'
    if 'NON-GUARANTEED' in text_content: return 'NG'
    
    return '0'

def process_options_data(df_and_html: Tuple[pd.DataFrame, str], salary_df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process and clean options data by extracting option types from HTML classes.
    """
    if df_and_html is None:
        return pd.DataFrame(columns=['Player', 'Team'] + get_available_seasons(salary_df))
    
    df, html = df_and_html
    if df is None or df.empty:
        return pd.DataFrame(columns=['Player', 'Team'] + get_available_seasons(salary_df))

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(' '.join).str.replace(r' Unnamed: \d+_level_\d', '', regex=True).str.strip()
    print(df.columns)
    df.rename(columns={df.columns[0]: 'Player'}, inplace=True, errors='ignore')
    
    if 'Player' in df.columns:
         df['Player'] = df['Player'].apply(clean_player_name)
    else:
        return pd.DataFrame()

    # Parse HTML to extract class information
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    
    if not table:
        return pd.DataFrame()

    # Find season columns
    seasons = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
 
    if not seasons:
        return pd.DataFrame()

    options_data = pd.DataFrame()
    options_data['Player'] = df['Player']

    # Get table rows (skip header)
    rows = table.find_all('tr')[1:]  # Skip header row
    
    # Find the column indices for seasons
    header_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    season_indices = {}
    for season in seasons:
        try:
            season_indices[season] = headers.index(season)
        except ValueError:
            continue

    # Process each row
    for row_idx, row in enumerate(rows):
        if row_idx >= len(df):
            break
            
        cells = row.find_all(['td', 'th'])
        
        for season in seasons:
            if season in season_indices:
                col_idx = season_indices[season]
                if col_idx < len(cells):
                    option_type = extract_option_from_html_cell(cells[col_idx], col_idx)
                    # Create season column if it doesn't exist
                    if season not in options_data.columns:
                        options_data[season] = '0'
                    options_data.loc[row_idx, season] = option_type

    options_data['Team'] = team

    # Use a left merge to keep all players from salary_df and add option info
    final_options_df = salary_df[['Player', 'Team']].drop_duplicates().merge(
        options_data, on=['Player', 'Team'], how='left'
    )
    
    all_seasons = get_available_seasons(salary_df)
    for season in all_seasons:
        if season not in final_options_df.columns:
            final_options_df[season] = '0'
        else:
            final_options_df[season] = final_options_df[season].fillna('0')

    final_options_df = final_options_df[['Player', 'Team'] + all_seasons]
    final_options_df = final_options_df.drop_duplicates(subset=['Player', 'Team']).reset_index(drop=True)

 

    return final_options_df

def process_cap_holds(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process cap holds table.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = ['Player' if 'player' in str(col).lower() else col for col in df.columns]
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)
        salary_cols = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
        for col in salary_cols:
            df[col] = df[col].apply(process_salary_value2)
        df['Team'] = team
        non_salary_cols = ['Team', 'Player', 'Pos', 'Age']
        ordered_cols = [col for col in non_salary_cols if col in df.columns] + salary_cols
        return df[ordered_cols]
    return df

def process_dead_money(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process dead money table.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = ['Player' if 'player' in str(col).lower() else col for col in df.columns]
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)
        value_cols = [col for col in df.columns if col != 'Player']
        for col in value_cols:
            df[col] = df[col].apply(process_salary_value)
    df['Team'] = team
    return df

def process_summary(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    Process summary table.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    value_cols = df.columns
    for col in value_cols:
        df[col] = df[col].apply(process_salary_value)
    df['Team'] = team
    return df

def team_books(driver: webdriver.Chrome, team: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Get salary, options, cap holds, dead money, and summary data for a given team.
    """
    print(f"\n{'='*50}")
    print(f"Processing {team}...")
    print(f"{'='*50}")

    url = NBA_TEAM_URLS.get(team.upper())
    if not url:
        raise ValueError(f"Invalid team code: {team}")

    tables_data = get_team_data(driver, url)
    if not tables_data:
        print(f"No tables found for {team}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    salary_df = tables_data.get('salary')
    options_df_raw = tables_data.get('options')  # This is now a tuple (df, html)
    cap_holds_df_raw = tables_data.get('cap_holds')
    dead_money_df_raw = tables_data.get('dead_money')
    summary_df_raw = tables_data.get('summary')

    if salary_df is None or salary_df.empty:
        print(f"Required salary table not found for {team}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
   
    salary_df = process_salary_data(salary_df, team)

    print(salary_df['2025-26'].sum())
    
    # For debugging - remove sys.exit() and the debug print
    options_df = process_options_data(options_df_raw, salary_df, team)
    cap_holds_df = process_cap_holds(cap_holds_df_raw, team)
    dead_money_df = process_dead_money(dead_money_df_raw, team)
    summary_df = process_summary(summary_df_raw, team)

    for df in [cap_holds_df, dead_money_df, summary_df]:
        if not df.empty and 'Team' not in df.columns:
            df['Team'] = team

    print(f"Completed {team}: Salary({len(salary_df)}), Options({len(options_df)}), Cap Holds({len(cap_holds_df)}), Dead Money({len(dead_money_df)}), Summary({len(summary_df)})")
    
    return salary_df, options_df, cap_holds_df, dead_money_df, summary_df

def scrape_all_teams(teams: List[str], delay: float = 3.0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Scrape data for all teams with rate limiting using Selenium.
    """
    salary_dfs, options_dfs, cap_holds_dfs, dead_money_dfs, summary_dfs = [], [], [], [], []

    driver = setup_driver()
    try:
        for i, team in enumerate(teams):
            try:
                print(f"\n--- Processing team {i+1}/{len(teams)}: {team} ---")
                s_df, o_df, ch_df, dm_df, su_df = team_books(driver, team)

                if not s_df.empty: salary_dfs.append(s_df)
                if not o_df.empty: options_dfs.append(o_df)
                if not ch_df.empty: cap_holds_dfs.append(ch_df)
                if not dm_df.empty: dead_money_dfs.append(dm_df)
                if not su_df.empty: summary_dfs.append(su_df)

            except Exception as e:
                print(f"Error processing {team}: {e}")
                import traceback
                traceback.print_exc()

            if i < len(teams) - 1:
                print(f"Waiting {delay} seconds before next team...")
                time.sleep(delay)
    finally:
        driver.quit()

    return (
        pd.concat(salary_dfs, ignore_index=True) if salary_dfs else pd.DataFrame(),
        pd.concat(options_dfs, ignore_index=True) if options_dfs else pd.DataFrame(),
        pd.concat(cap_holds_dfs, ignore_index=True) if cap_holds_dfs else pd.DataFrame(),
        pd.concat(dead_money_dfs, ignore_index=True) if dead_money_dfs else pd.DataFrame(),
        pd.concat(summary_dfs, ignore_index=True) if summary_dfs else pd.DataFrame()
    )

# Main execution
if __name__ == "__main__":
    teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 
             'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 
             'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
    # For testing, you can use a smaller subset:
    
    print("Starting NBA salary scraping...")
    print(f"Teams to process: {teams}")
    
    salary_df, option_df, cap_holds_df, dead_money_df, summary_df = scrape_all_teams(teams)

    # Post-processing (same as original but with better error handling)
    if not salary_df.empty:
        print("\nPost-processing data...")
        
        if not option_df.empty:
            temp_df = pd.DataFrame()
            temp_df['Player'] = option_df['Player']
            seasons = ['2025-26', '2026-27', '2027-28', '2028-29','2029-30']
            
            for season in seasons:
                if season in option_df.columns:
                    # Convert non-team options to 1 (guaranteed), team options to 0
                    temp_df[season] = np.where(option_df[season] != 'T', 1, 0)

            # Calculate guaranteed money
            guar = pd.DataFrame()
            guar['Player'] = salary_df['Player']
            guar['Guaranteed'] = 0
            
            for season in seasons:
                if season in salary_df.columns and season in temp_df.columns:
                    # Merge temp_df with salary_df to get the guarantee multiplier
                    season_guar = salary_df[['Player', season]].merge(
                        temp_df[['Player', season]], on='Player', how='left', suffixes=('_salary', '_guar')
                    )
                    # Add to guaranteed total
                    guar['Guaranteed'] += (season_guar[f'{season}_salary'].fillna(0) * season_guar[f'{season}_guar'].fillna(0))
                    
            salary_df = salary_df.merge(guar[['Player', 'Guaranteed']], on='Player', how='left')
            salary_df['Guaranteed'] = salary_df['Guaranteed'].fillna(0)
            salary_df = salary_df.sort_values(by='Guaranteed', ascending=False).reset_index(drop=True)
            
        # Remove duplicates
        salary_df = salary_df.drop_duplicates(subset=['Player', 'Team'])
        if not option_df.empty:
            option_df = option_df.drop_duplicates(subset=['Player', 'Team'])

        # Manual corrections (same as original)
        salary_df.loc[salary_df['Player'].str.contains('Branden Carlson', na=False), '2024-25'] = 990895
        if not option_df.empty:
            option_df.loc[option_df['Player'].str.contains('Scottie Barnes', na=False), '2025-26'] = 0
            option_df.loc[option_df['Player'].str.contains('Bradley Beal', na=False), '2026-27'] = 'P'
            option_df.loc[option_df['Player'].str.contains('Jalen Brunson', na=False), '2025-26'] = 0
            option_df.loc[option_df['Player'].str.contains('Julius Randle', na=False), '2026-27'] = 'P'

    # Save results
    print("\nSaving results...")
    salary_df.to_csv('nba_salaries.csv', index=False)
    option_df.to_csv('nba_options.csv', index=False)
    cap_holds_df.to_csv('nba_cap_holds.csv', index=False)
    dead_money_df.to_csv('nba_dead_money.csv', index=False)
    summary_df.to_csv('nba_summary.csv', index=False)

    # Also save to web_app directory if it exists
    try:
        salary_df.to_csv('../web_app/data/nba_salaries.csv', index=False)
        option_df.to_csv('../web_app/data/nba_options.csv', index=False)
        cap_holds_df.to_csv('../web_app/data/nba_cap_holds.csv', index=False)
        dead_money_df.to_csv('../web_app/data/nba_dead_money.csv', index=False)
        summary_df.to_csv('../web_app/data/nba_summary.csv', index=False)
        print("Files also saved to ../web_app/data/ directory")
    except Exception as e:
        print(f"Could not save to web_app directory: {e}")

    print("\nScraping completed successfully!")
    print(f"Salary data: {len(salary_df)} rows")
    print(f"Options data: {len(option_df)} rows")
    print(f"Cap holds data: {len(cap_holds_df)} rows")
    print(f"Dead money data: {len(dead_money_df)} rows")