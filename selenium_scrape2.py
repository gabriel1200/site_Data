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
    'options': 'dataTable-active',
    'dead_money': 'dataTable-dead',
    'cap_holds': 'dataTable-cap-hold',
    'summary': 'dataTable-summary'
}

SEASONS = ['2025-26', '2026-27', '2027-28', '2028-29', '2029-30']
EXTRA_SEASONS = ['2030-31']

def setup_driver():
    """Set up Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_table_and_html_by_id(driver: webdriver.Chrome, table_id: str, timeout: int = 15) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Fetch a specific table by its ID using Selenium and return both DataFrame and raw HTML."""
    try:
        table_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, table_id))
        )
        table_html = table_element.get_attribute('outerHTML')
        df = pd.read_html(table_html, header=0)[0]
        return df, table_html
    except TimeoutException:
        print(f"Table with ID '{table_id}' not found within timeout")
        return None, None
    except Exception as e:
        print(f"Error fetching table with ID '{table_id}': {e}")
        return None, None

def get_team_data(driver: webdriver.Chrome, url: str, timeout: int = 15) -> Dict[str, Tuple[pd.DataFrame, str]]:
    """Fetch and parse tables from the team URL, returning a dictionary of table_type -> (DataFrame, HTML)."""
    try:
        driver.get(url)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        time.sleep(3)

        tables_data = {}
        for table_type, table_id in DATATABLE_CONTAINERS.items():
            df, html = get_table_and_html_by_id(driver, table_id, timeout=10)
            if df is not None:
                tables_data[table_type] = (df, html)
                print(f"Successfully fetched {table_type} table with {len(df)} rows")
            else:
                print(f"Table '{table_type}' (ID: {table_id}) not found")
        return tables_data
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

def clean_player_name(name: str) -> str:
    """Clean player name by removing duplicates, suffixes, and extra text."""
    if pd.isna(name):
        return ""
    name_str = str(name).strip()
    name_str = re.sub(r'\s*\(.*?\)', '', name_str)
    suffixes = ['Jr', 'Jr.', 'Sr', 'Sr.', 'II', 'III', 'IV', 'V']
    suffix_pattern = r'\b(?:' + '|'.join(re.escape(s) for s in suffixes) + r')\b'
    name_str = re.sub(r'\s*' + suffix_pattern, '', name_str, flags=re.IGNORECASE).strip()
    name_str = re.sub(r'\s+', ' ', name_str).strip()
    parts = name_str.split()
    unique_parts = list(dict.fromkeys(parts))
    if len(unique_parts) == 2:
        return f"{unique_parts[1]} {unique_parts[0]}"
    return " ".join(unique_parts)

def _parse_table_html_for_salaries(df: pd.DataFrame, html: str, value_cols: List[str]) -> pd.DataFrame:
    """Parses table HTML to extract salary data from 'data-sort' attributes."""
    if not html or df.empty:
        return df

    soup = BeautifulSoup(html, 'html.parser')
    header = soup.find('thead')
    if not header:
        print("Warning: HTML table header not found. Cannot perform precise salary extraction.")
        return df

    header_cells = [th.get_text(strip=True) for th in header.find_all('th')]
    col_indices = {col: header_cells.index(col) for col in value_cols if col in header_cells}

    body = soup.find('tbody')
    if not body:
        print("Warning: HTML table body not found.")
        return df

    html_rows = body.find_all('tr')
    if len(df) != len(html_rows):
        print(f"Warning: Mismatch between DataFrame rows ({len(df)}) and HTML rows ({len(html_rows)}).")

    min_rows = min(len(df), len(html_rows))
    for idx in range(min_rows):
        html_cells = html_rows[idx].find_all(['td', 'th'])
        for col_name, col_idx in col_indices.items():
            if col_idx < len(html_cells):
                cell = html_cells[col_idx]
                salary = 0.0
                if cell.has_attr('data-sort'):
                    try:
                        val = float(cell['data-sort'])
                        salary = val if val > 0 else 0.0
                    except (ValueError, TypeError):
                        pass
                df.loc[idx, col_name] = salary
    return df

def get_available_seasons(salary_df: pd.DataFrame) -> List[str]:
    """Get list of available seasons from salary data."""
    return [col for col in salary_df.columns if re.match(r'\d{4}-\d{2}', str(col))]

def process_salary_data(df_and_html: Tuple[pd.DataFrame, str], team: str) -> pd.DataFrame:
    """Process and clean salary data using 'data-sort' attributes from HTML."""
    if not df_and_html:
        return pd.DataFrame()
    df, html = df_and_html

    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(' '.join).str.replace(r' Unnamed: \d+_level_\d', '', regex=True).str.strip()
    if 'Player' in df.columns.get_level_values(0):
        df.columns = df.columns.droplevel(1)
    if 'Player' in df.columns[0] and 'Unnamed' in df.columns[1]:
        df[df.columns[0]] = df[df.columns[1]]
        df = df.drop(columns=df.columns[1])

    df.rename(columns={df.columns[0]: 'Player'}, inplace=True)
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)

    seasons = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
    df = _parse_table_html_for_salaries(df, html, seasons)
    df['Team'] = team
    return df

def extract_option_from_html_cell(soup_cell) -> str:
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
    """Process and clean options data by extracting option types from HTML classes."""
    if df_and_html is None:
        return pd.DataFrame(columns=['Player', 'Team'] + get_available_seasons(salary_df))
    df, html = df_and_html
    if df is None or df.empty:
        return pd.DataFrame(columns=['Player', 'Team'] + get_available_seasons(salary_df))

    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(' '.join).str.replace(r' Unnamed: \d+_level_\d', '', regex=True).str.strip()
    df.rename(columns={df.columns[0]: 'Player'}, inplace=True, errors='ignore')
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)
    else:
        return pd.DataFrame()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    if not table: return pd.DataFrame()

    seasons = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
    if not seasons: return pd.DataFrame()

    options_data = pd.DataFrame()
    options_data['Player'] = df['Player']
    rows = table.find_all('tr')[1:]
    header_row = table.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    season_indices = {season: headers.index(season) for season in seasons if season in headers}

    for row_idx, row in enumerate(rows):
        if row_idx >= len(df): break
        cells = row.find_all(['td', 'th'])
        for season in seasons:
            if season in season_indices:
                col_idx = season_indices[season]
                if col_idx < len(cells):
                    option_type = extract_option_from_html_cell(cells[col_idx])
                    if season not in options_data.columns:
                        options_data[season] = '0'
                    options_data.loc[row_idx, season] = option_type

    options_data['Team'] = team
    final_options_df = salary_df[['Player', 'Team']].drop_duplicates().merge(
        options_data, on=['Player', 'Team'], how='left'
    )
    all_seasons = get_available_seasons(salary_df)
    for season in all_seasons:
        if season not in final_options_df.columns:
            final_options_df[season] = '0'
        else:
            final_options_df[season] = final_options_df[season].fillna('0')

    final_options_df = final_options_df[['Player', 'Team'] + all_seasons].drop_duplicates(subset=['Player', 'Team']).reset_index(drop=True)
    return final_options_df

def process_cap_holds(df_and_html: Tuple[pd.DataFrame, str], team: str) -> pd.DataFrame:
    """Process cap holds table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    df.columns = ['Player' if 'player' in str(col).lower() else col for col in df.columns]
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)
        salary_cols = [col for col in df.columns if re.match(r'\d{4}-\d{2}', str(col))]
        df = _parse_table_html_for_salaries(df, html, salary_cols)
        df['Team'] = team
        non_salary_cols = ['Team', 'Player', 'Pos', 'Age']
        ordered_cols = [col for col in non_salary_cols if col in df.columns] + salary_cols
        return df[ordered_cols]
    return df

def process_dead_money(df_and_html: Tuple[pd.DataFrame, str], team: str) -> pd.DataFrame:
    """Process dead money table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    df.columns = ['Player' if 'player' in str(col).lower() else col for col in df.columns]
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(clean_player_name)
        value_cols = [col for col in df.columns if col not in ['Player', 'Team']]
        df = _parse_table_html_for_salaries(df, html, value_cols)
    df['Team'] = team
    return df

def process_summary(df_and_html: Tuple[pd.DataFrame, str], team: str) -> pd.DataFrame:
    """Process summary table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    value_cols = list(df.columns)
    df = _parse_table_html_for_salaries(df, html, value_cols)
    df['Team'] = team
    return df

def team_books(driver: webdriver.Chrome, team: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get salary, options, cap holds, dead money, and summary data for a given team."""
    print(f"\n{'='*50}\nProcessing {team}...\n{'='*50}")
    url = NBA_TEAM_URLS.get(team.upper())
    if not url: raise ValueError(f"Invalid team code: {team}")

    tables_data = get_team_data(driver, url)
    if not tables_data:
        print(f"No tables found for {team}")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    salary_data = tables_data.get('salary')
    if not salary_data or salary_data[0].empty:
        print(f"Required salary table not found for {team}")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    salary_df = process_salary_data(salary_data, team)
    options_df = process_options_data(tables_data.get('options'), salary_df, team)
    cap_holds_df = process_cap_holds(tables_data.get('cap_holds'), team)
    dead_money_df = process_dead_money(tables_data.get('dead_money'), team)
    summary_df = process_summary(tables_data.get('summary'), team)

    for df in [cap_holds_df, dead_money_df, summary_df]:
        if not df.empty and 'Team' not in df.columns:
            df['Team'] = team

    print(f"Completed {team}: Salary({len(salary_df)}), Options({len(options_df)}), Cap Holds({len(cap_holds_df)}), Dead Money({len(dead_money_df)}), Summary({len(summary_df)})")
    return salary_df, options_df, cap_holds_df, dead_money_df, summary_df

def scrape_all_teams(teams: List[str], delay: float = 3.0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Scrape data for all teams with rate limiting using Selenium."""
    all_dfs = {'salary': [], 'options': [], 'cap_holds': [], 'dead_money': [], 'summary': []}
    driver = setup_driver()
    try:
        for i, team in enumerate(teams):
            try:
                print(f"\n--- Processing team {i+1}/{len(teams)}: {team} ---")
                s_df, o_df, ch_df, dm_df, su_df = team_books(driver, team)
                if not s_df.empty: all_dfs['salary'].append(s_df)
                if not o_df.empty: all_dfs['options'].append(o_df)
                if not ch_df.empty: all_dfs['cap_holds'].append(ch_df)
                if not dm_df.empty: all_dfs['dead_money'].append(dm_df)
                if not su_df.empty: all_dfs['summary'].append(su_df)
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
        pd.concat(all_dfs['salary'], ignore_index=True) if all_dfs['salary'] else pd.DataFrame(),
        pd.concat(all_dfs['options'], ignore_index=True) if all_dfs['options'] else pd.DataFrame(),
        pd.concat(all_dfs['cap_holds'], ignore_index=True) if all_dfs['cap_holds'] else pd.DataFrame(),
        pd.concat(all_dfs['dead_money'], ignore_index=True) if all_dfs['dead_money'] else pd.DataFrame(),
        pd.concat(all_dfs['summary'], ignore_index=True) if all_dfs['summary'] else pd.DataFrame()
    )


if __name__ == "__main__":
    teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
             'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
             'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
  
    
    print("Starting NBA salary scraping...")
    salary_df, option_df, cap_holds_df, dead_money_df, summary_df = scrape_all_teams(teams)

    if not dead_money_df.empty:
        print("\nIntegrating dead cap data into salaries and options...")
        dead_options_df = dead_money_df.copy()
        season_cols = [col for col in dead_money_df.columns if re.match(r'\d{4}-\d{2}', str(col))]
        for season in season_cols:
            dead_options_df[season] = np.where(dead_money_df[season] > 0, 'D', '0')
        salary_df = pd.concat([salary_df, dead_money_df], ignore_index=True, sort=False)
        option_df = pd.concat([option_df, dead_options_df], ignore_index=True, sort=False)
        print(f"Successfully added {len(dead_money_df)} dead cap player entries.")

    if not salary_df.empty:
        print("\nPost-processing data...")
        salary_df.fillna(0, inplace=True)
        if not option_df.empty:
            option_df.fillna('0', inplace=True)
            seasons = ['2025-26', '2026-27', '2027-28', '2028-29', '2029-30']
            guarantee_multiplier = pd.DataFrame(index=option_df.index)
            for season in seasons:
                if season in option_df.columns:
                    guarantee_multiplier[season] = np.where(option_df[season] == 'T', 0, 1)
            guaranteed_total = pd.Series([0.0] * len(salary_df))
            for season in seasons:
                if season in salary_df.columns and season in guarantee_multiplier.columns:
                    guaranteed_total += salary_df[season] * guarantee_multiplier[season]
            salary_df['Guaranteed'] = guaranteed_total
        salary_df = salary_df.sort_values(by='Guaranteed', ascending=False).reset_index(drop=True)
        
        # Manual corrections
        salary_df.loc[salary_df['Player'].str.contains('Branden Carlson', na=False), '2024-25'] = 990895
        if not option_df.empty:
            option_df.loc[option_df['Player'].str.contains('Scottie Barnes', na=False), '2025-26'] = 0
            option_df.loc[option_df['Player'].str.contains('Bradley Beal', na=False), '2026-27'] = 'P'
            option_df.loc[option_df['Player'].str.contains('Jalen Brunson', na=False), '2025-26'] = 0
            option_df.loc[option_df['Player'].str.contains('Julius Randle', na=False), '2026-27'] = 'P'

    print("\nSaving results...")
    output_files = {
        'nba_salaries.csv': salary_df,
        'nba_options.csv': option_df,
        'nba_cap_holds.csv': cap_holds_df,
        'nba_dead_money.csv': dead_money_df,
        'nba_summary.csv': summary_df
    }
    for filename, df in output_files.items():
        df.to_csv(filename, index=False)
        print(f"Saved {filename} ({len(df)} rows)")

    # Also save to web_app directory if it exists
    for directory in ['../web_app/data', '../discord/data']:
        try:
            for filename, df in output_files.items():
                df.to_csv(f'{directory}/{filename}', index=False)
            print(f"Files also saved to {directory}")
        except Exception as e:
            print(f"Could not save to {directory} directory: {e}")

    print("\nScraping completed successfully!")