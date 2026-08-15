import pandas as pd
import urllib.request
import urllib.parse
import re
import time

def get_nba_id(player_name):
    """
    Searches for the player's NBA.com profile and extracts their ID.
    """
    # Construct the search query targeting NBA.com player profiles
    query = f"{player_name} nba player profile site:nba.com/player"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    # Use a standard User-Agent to prevent the request from being blocked
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Use regex to find the numeric ID immediately following /player/
            match = re.search(r'nba\.com/player/(\d+)', html)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
    
    return None

def main():
    # Read the file verbatim as requested
    file_name = "crosswalk_unmatched.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"Error: {file_name} not found in the current directory.")
        return

    print("Starting ID search. This may take a few minutes to avoid rate limits...\n")
    
    nba_ids = []
    for index, row in df.iterrows():
        name = row['spotrac_name']
        print(f"Searching for {name}...")
        
        nba_id = get_nba_id(name)
        nba_ids.append(nba_id)
        
        # Sleep for 2 seconds between requests to avoid getting blocked by the search engine
        time.sleep(2)
        
    # Append the newly found IDs as a new column
    df['nba_id'] = nba_ids
    
    # Save the populated dataframe to a new file
    output_filename = "crosswalk_matched.csv"
    df.to_csv(output_filename, index=False)
    print(f"\nFinished! The updated data has been saved to {output_filename}")

if __name__ == "__main__":
    main()