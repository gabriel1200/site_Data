#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import unicodedata
import requests
import json
import math
import time
import sys
import os # Added os to check if file exists

def passing_data(year_to_process, ps=False, update=True):
    """
    Fetches and processes passing data for a single NBA season.
    
    Args:
        year_to_process (int): The end year of the season to process (e.g., 2025 for 2024-25).
        ps (bool): Whether to fetch Playoffs data (True) or Regular Season data (False).
        update (bool): Whether to read the existing CSV, remove the specified year, 
                       and append the new data.
    """
    url = 'https://api.pbpstats.com/get-totals/nba'
    stype = 'Regular Season'
    folder = 'tracking'
    output_file = 'passing.csv'
    
    if ps:
        stype = 'Playoffs'
        folder = 'tracking_ps'
        output_file = 'passing_ps.csv'

    frames = []
    
    if update:
        try:
            # Try to read the existing file
            if os.path.exists(output_file):
                print(f"Update mode: Reading existing data from {output_file}...")
                df_existing = pd.read_csv(output_file)
                # Keep all data *except* for the year we are about to process
                df_existing = df_existing[df_existing.year != year_to_process]
                if not df_existing.empty:
                    frames.append(df_existing)
            else:
                print(f"Update mode: {output_file} not found. Will create a new file.")
        except pd.errors.EmptyDataError:
            print(f"Update mode: {output_file} is empty. Will create a new file.")
        except FileNotFoundError:
            print(f"Update mode: {output_file} not found. Will create a new file.")

    # Use the single year provided
    year = year_to_process 
    time.sleep(1)
    
    # Prepare API call
    season = f"{year - 1}-{str(year)[-2:]}"
    print(f"Fetching {stype} data for {season}...")
    params = {
        "Season": season,
        "SeasonType": stype,
        "Type": "Player"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return pd.DataFrame() # Return empty dataframe on failure
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from response. Response text: {response.text}")
        return pd.DataFrame()

    if "multi_row_table_data" not in response_json or not response_json["multi_row_table_data"]:
        print(f"No 'multi_row_table_data' found in API response for {season}.")
        # If we had existing data, return that, otherwise an empty DF
        if frames:
            return pd.concat(frames)
        return pd.DataFrame()

    df = pd.DataFrame(response_json["multi_row_table_data"])
    df.rename(columns={'EntityId':'PLAYER_ID'},inplace=True)

    # Load the unified passing and touches data from the common files
    passing_file_path = f'{folder}/passing.csv'
    touches_file_path = f'{folder}/touches.csv'
    print(f"Reading tracking file: {passing_file_path}")
    print(f"Reading tracking file: {touches_file_path}")

    try:
        df2 = pd.read_csv(passing_file_path)
        df3 = pd.read_csv(touches_file_path)
    except FileNotFoundError as e:
        print(f"Error reading tracking files: {e}")
        print("Please ensure 'tracking/passing.csv', 'tracking/touches.csv', 'tracking_ps/passing.csv', and 'tracking_ps/touches.csv' exist.")
        return pd.DataFrame()

    df2.rename(columns={'PLAYER': 'Name'}, inplace=True)

    # Filter tracking data for the specific year
    df2 = df2[df2.year == year]
    df3 = df3[df3.year == year]

    if df2.empty or df3.empty:
        print(f"Warning: No tracking data found for year {year} in {folder}. Stats may be incomplete.")

    df['nba_id'] = df['PLAYER_ID'].astype(int)
    df2['nba_id'] = df2['PLAYER_ID'].astype(int)
    df3['nba_id'] = df3['PLAYER_ID'].astype(int)

    df.drop(columns=['PLAYER_ID'], inplace=True)
    df2.drop(columns=['PLAYER_ID', 'GP'], inplace=True, errors='ignore')
    df3.drop(columns=['PLAYER_ID'], inplace=True, errors='ignore')
    df3.rename(columns={'Player': 'Name'}, inplace=True)

    # Merging data
    merged = df.merge(df2, on='nba_id', how='left')
    merged = merged.merge(df3, on='nba_id', how='left')

    # Cleaning up column names and calculating additional fields
    merged = merged.fillna(0)
    merged['Points Unassisted'] = merged['PtsUnassisted2s'] + merged['PtsUnassisted3s']
    merged['UAFGM'] = (merged['PtsUnassisted2s'] / 2) + (merged['PtsUnassisted3s'] / 3)
    merged['UAPTS'] = merged['Points Unassisted']
    merged['on-ball-time'] = merged['TIME_OF_POSS']
    
    # Avoid division by zero
    merged['High Value Assist %'] = 100 * (merged['ThreePtAssists'] + merged['AtRimAssists']) / merged['Assists'].replace(0, pd.NA)
    merged['on-ball-time%'] = 100 * 2 * (merged['TIME_OF_POSS']) / (merged['Minutes']).replace(0, pd.NA)
    merged['TSA'] = (merged['Points'] / (merged['TsPct'] * 2).replace(0, pd.NA))
    
    merged['Potential Assists'] = merged['POTENTIAL_AST']
    merged['Passes'] = merged['PASSES_MADE']
    
    merged['PotAss/Passes'] = merged['POTENTIAL_AST'] / merged['Passes'].replace(0, pd.NA)
    merged['Assist PPP'] = (merged['AST_PTS_CREATED']) / merged['POTENTIAL_AST'].replace(0, pd.NA)
    merged['POT_AST_PER_MIN'] = merged['POTENTIAL_AST'] / (merged['on-ball-time']).replace(0, pd.NA)
    
    merged['year'] = year

    frames.append(merged)
    print(f'Season done {year}')
    
    if not frames:
        print("No data processed.")
        return pd.DataFrame()
        
    final_df = pd.concat(frames)
    
    # Handle potential duplicate columns from merges if Name_x, Name_y occurred
    final_df = final_df.loc[:, ~final_df.columns.duplicated()]
    
    return final_df


def main():
    """
    Main function to parse arguments and run the data processing.
    """
    if len(sys.argv) != 3:
        print("Usage: python passing.py <year> <season_type>")
        print("Example: python passing.py 2025 regular")
        print("Example: python passing.py 2025 playoffs")
        sys.exit(1)

    try:
        year_arg = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid year '{sys.argv[1]}'. Please provide an integer.")
        sys.exit(1)

    type_arg = sys.argv[2].lower()
    is_playoffs = type_arg in ['playoffs', 'ps', 'p']
    season_name = "Playoffs" if is_playoffs else "Regular Season"
    output_file = 'passing_ps.csv' if is_playoffs else 'passing.csv'

    print(f"Processing {season_name} data for year {year_arg}...")
    
    # Call the data processing function
    processed_data = passing_data(year_to_process=year_arg, ps=is_playoffs, update=True)

    if processed_data.empty:
        print("No data was processed or returned. Exiting.")
        return

    # Define columns to keep
    columns = ['nba_id','Name','Points','on-ball-time%','on-ball-time','UAPTS','TSA','OffPoss','Potential Assists','Travels','TsPct',
                'Turnovers','Passes','PASSES_RECEIVED','PotAss/Passes','UAFGM','High Value Assist %','Assist PPP','TOUCHES','AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH', 'PTS_PER_TOUCH',
                    'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED', 'AST_ADJ', 'AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ','Assists','POT_AST_PER_MIN','ThreePtAssists','AtRimAssists','BadPassTurnovers',
               'BadPassSteals','BadPassOutOfBoundsTurnovers',
                       'PtsUnassisted2s','PtsUnassisted3s','Fg3Pct','FG3A','FG3M','OffPoss','GP','Minutes','year']
    
    # Ensure all columns exist before trying to select them, fill missing ones with 0 or NaN
    for col in columns:
        if col not in processed_data.columns:
            print(f"Warning: Column '{col}' not found in processed data. Adding it as NaN.")
            processed_data[col] = pd.NA
            
    # Filter for the defined columns
    final_data = processed_data[columns]

    # Save the result
    try:
        final_data.to_csv(output_file, index=False)
        print(f"Successfully updated data to {output_file}")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")

# This block ensures the main() function is called only when the script is executed directly
if __name__ == "__main__":
    main()



avg = pd.read_html('https://www.basketball-reference.com/leagues/NBA_stats_per_poss.html')[0]
avg.columns = avg.columns.droplevel()
avg = avg.dropna(subset='Season')
avg = avg[avg.Season!='Season']

avg = avg.dropna()
avg['PTS'] = avg['PTS'].astype(float)
avg['FGA'] = avg['FGA'].astype(float)
avg['FTA'] = avg['FTA'].astype(float)

#avg.head(87)



avg['TS%'] = avg['PTS']/(2*(avg['FGA']+.44*avg['FTA']))
#avg


avg.to_csv('avg_shooting.csv',index = False)
avg = avg[['Season','ORtg']]
avg.to_csv('team_avg.csv',index = False)