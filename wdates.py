import requests
import pandas as pd
import os

# WNBA Schedule Endpoint
URL = "https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/WNBA/staticData/scheduleLeagueV2.json"

# Team ids and codes come from the feed itself (homeTeam/awayTeam teamId, teamTricode).
# A hand-typed name -> id table used to live here and had six ids wrong (PHX, CON, LAS, LVA,
# MIN, WAS: logos and previews showed the wrong team or none); fixed 2026-11-10.
# Codes are the feed's, e.g. WAS and PDX, the same as the live game pages and the playoff rows.

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
            home, away = game["homeTeam"], game["awayTeam"]
            # 0 / blank until a matchup is set (e.g. All-Star rosters, later playoff rounds)
            home_id, away_id = home.get("teamId") or None, away.get("teamId") or None
            home_abbr = home.get("teamTricode") or home.get("teamName") or None
            away_abbr = away.get("teamTricode") or away.get("teamName") or None
            
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