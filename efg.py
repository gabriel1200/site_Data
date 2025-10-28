import requests
import pandas as pd
from typing import Optional, Literal

class NBAStatsScraper:
    """Scraper for NBA Stats API endpoints"""
    
    BASE_URL = "https://stats.nba.com/stats"
    
    HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/"
    }
    
    def get_shot_quality_leaders(
        self,
        season: str = "2025-26",
        season_type: Literal["Regular Season", "Playoffs", "Pre Season"] = "Regular Season",
        league_id: str = "00",
        team_id: int = 0
    ) -> pd.DataFrame:
        """
        Fetch shot quality leaders data from NBA Stats API.
        
        Parameters:
        -----------
        season : str
            Season in format "YYYY-YY" (e.g., "2025-26")
        season_type : str
            Type of season: "Regular Season", "Playoffs", or "Pre Season"
        league_id : str
            League ID (00 for NBA)
        team_id : int
            Team ID (0 for all teams)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing shot quality leaders data
        """
        
        url = f"{self.BASE_URL}/shotqualityleaders"
        
        params = {
            "LeagueID": league_id,
            "Season": season,
            "SeasonType": season_type,
            "TeamID": team_id
        }
        
        try:
            response = requests.get(url, headers=self.HEADERS, params=params, timeout=30)
            response.raise_for_status()
            
            json_data = response.json()
            
            shots = json_data.get("shots", [])

            if not shots:
                raise ValueError("No 'shots' data found in API response")

            # Convert list of dicts into DataFrame
            df = pd.DataFrame(shots)
            print(df)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            raise
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {e}")
            raise


# Example usage
if __name__ == "__main__":
    scraper = NBAStatsScraper()
    
    # Get shot quality leaders for 2025-26 regular season
    df = scraper.get_shot_quality_leaders(
        season="2025-26",
        season_type="Regular Season"
    )
    
    print(f"Retrieved {len(df)} rows")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Optional: Save to CSV
    df.to_csv("efg.csv", index=False)