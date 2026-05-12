import requests
import pandas as pd
import os

# WNBA Schedule Endpoint
URL = "https://cdn.wnba.com/static/json/staticData/scheduleLeagueV2.json"

# WNBA Team Mapping: Name -> (ID, Acronym)
# Includes 2026 expansion teams: GSV, POR, TOR
WNBA_MAPPING = {
    'Dream': (1611661330, 'ATL'),
    'Sky': (1611661329, 'CHI'),
    'Sun': (1611661317, 'CON'),
    'Wings': (1611661321, 'DAL'),
    'Fever': (1611661325, 'IND'),
    'Aces': (1611661324, 'LVA'),
    'Sparks': (1611661319, 'LAS'),
    'Lynx': (1611661322, 'MIN'),
    'Liberty': (1611661313, 'NYL'),
    'Mercury': (1611661315, 'PHX'),
    'Storm': (1611661328, 'SEA'),
    'Mystics': (1611661320, 'WSH'),
    'Valkyries': (1611661331, 'GSV'),
    'Fire': (1611661327, 'POR'),
    'Tempo': (1611661332, 'TOR')
}

def update_wschedule():
    # 1. Fetch live data
    response = requests.get(URL)
    data = response.json()
    
    games_list = []
    
    # 2. Iterate through schedule structure
    for game_date_obj in data["leagueSchedule"]["gameDates"]:
        # Extract date string (YYYY-MM-DD)
        raw_date = game_date_obj["gameDate"].split("T")[0]
        
        for game in game_date_obj["games"]:
            home_name = game["homeTeam"]["teamName"]
            away_name = game["awayTeam"]["teamName"]
            
            # Map IDs and Acronyms
            home_id, home_abbr = WNBA_MAPPING.get(home_name, (None, home_name))
            away_id, away_abbr = WNBA_MAPPING.get(away_name, (None, away_name))
            
            # Build row matching schedule.csv columns
            if game["gameLabel"]!= "Preseason":
                games_list.append({
                    "game_id": game["gameId"],
                    "game_date": raw_date,
                    "home_team": home_abbr,
                    "away_team": away_abbr,
                    "home_team_id": float(home_id) if home_id else None,
                    "away_team_id": float(away_id) if away_id else None
                })
            
    # 3. Create DataFrame
    df = pd.DataFrame(games_list)
    
    # 4. Save to local and web_app directory
    output_filename = "wschedule.csv"
    web_app_dir = os.path.join("..", "web_app", "data")
    
    # Save locally
    df.to_csv(output_filename) # Index remains as the first unnamed column
    
    # Save to web_app path
    if not os.path.exists(web_app_dir):
        os.makedirs(web_app_dir, exist_ok=True)
    
    web_app_path = os.path.join(web_app_dir, output_filename)
    df.to_csv(web_app_path)
    
    print(f"Successfully updated {output_filename} and {web_app_path}")

if __name__ == "__main__":
    update_wschedule()