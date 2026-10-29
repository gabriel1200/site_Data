import requests
import pandas as pd

def fetch_and_parse_nba_schedule():
    url = "https://nba-prod-us-east-1-mediaops-stats.s3.amazonaws.com/NBA/staticData/scheduleLeagueV2_1.json"
    
    # Reusing your app's headers to bypass CDN blocking
    headers = {
        "authority": "cdn.nba.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "dnt": "1",
        "origin": "https://www.nba.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.nba.com/",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"),
    }

    print(f"Fetching schedule data from {url}...")
    response = requests.get(url, headers=headers, timeout=60)  # ~7.4 MB uncompressed on the feed
    response.raise_for_status()
    
    data = response.json()
    
    # The JSON structure groups games by date: leagueSchedule -> gameDates -> games
    game_dates = data.get("leagueSchedule", {}).get("gameDates", [])
    
    flat_games = []
    
    for date_node in game_dates:
        # e.g., "10/04/2024 00:00:00" -> "2024-10-04"
        raw_date = date_node.get("gameDate", "")
        clean_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if raw_date else None
        
        for game in date_node.get("games", []):
            game_id = str(game.get("gameId", ""))
            
            # --- FILTER PRESEASON ---
            # NBA game IDs starting with '001' are preseason.
            if game_id.startswith("001"):
                continue
            
            home_team = game.get("homeTeam", {})
            away_team = game.get("awayTeam", {})
            
            # Flatten the dictionary for Pandas
            flat_games.append({
                "game_id": game_id,
                "game_date": clean_date,
                "game_status": game.get("gameStatusText"),
                "arena": game.get("arenaName"),
                "home_team": home_team.get("teamTricode"),
                "home_team_id": home_team.get("teamId"),
                "home_wins": home_team.get("wins"),
                "home_losses": home_team.get("losses"),
                "away_team": away_team.get("teamTricode"),
                "away_team_id": away_team.get("teamId"),
                "away_wins": away_team.get("wins"),
                "away_losses": away_team.get("losses"),
            })

    # Convert to DataFrame for easy analytical breakdown
    df = pd.DataFrame(flat_games)
    
    return df

if __name__ == "__main__":
    schedule_df = fetch_and_parse_nba_schedule()
    schedule_df.to_csv('upcoming_schedule.csv')
    print("\n--- Raw DataFrame Info ---")
    print(schedule_df.info())
    
    print("\n--- Sample Data ---")
    print(schedule_df[['game_date', 'away_team', 'home_team', 'game_status']].head())