"""
Build a Summer League (Vegas) schedule CSV from core-api.nba.com's
gamecardfeed, matching the column schema of schedule.csv / wschedule.csv so
it drops straight into the same schedule_df pattern used elsewhere.

No proxy -- this runs once to generate a CSV, not as a live per-request
fetch, so there's nothing to hide behind a proxy for.

Columns: game_id, game_date, home_team, away_team, home_team_id, away_team_id
"""

import time
import requests
import pandas as pd

HEADERS = {
    "authority": "core-api.nba.com",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1",
    "ocp-apim-subscription-key": "747fa6900c6c4e89a58b81b72f36eb96",
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
    "x-postal-code": "89119",
}

URL = "https://core-api.nba.com/cp/api/v1.9/feeds/gamecardfeed"

# 2026 Vegas Summer League: July 9-19 (confirmed via NBA.com)
DATES = pd.date_range("2026-07-09", "2026-07-19", freq="D")


def fetch_date(date_obj):
    """Returns list of row-dicts for one date, or [] on failure/empty."""
    date_str = date_obj.strftime("%m/%d/%Y")
    params = {"gamedate": date_str, "platform": "web"}
    try:
        resp = requests.get(URL, headers=HEADERS, params=params, timeout=10)
    except Exception as e:
        print(f"{date_str}: EXCEPTION {e}")
        return []

    if resp.status_code != 200:
        print(f"{date_str}: status {resp.status_code}, skipping")
        return []

    try:
        data = resp.json()
    except Exception:
        print(f"{date_str}: non-JSON response, skipping")
        return []

    rows = []
    modules = data.get("modules", [])
    for module in modules:
        for card in module.get("cards", []):
            cd = card.get("cardData", {})
            if cd.get("leagueId") != "15":
                continue  # defensive filter -- only Summer League (Vegas)
            game_id = cd.get("gameId")
            if not game_id:
                continue  # nothing to key off of -- skip placeholder cards
            # homeTeam/awayTeam can be null for not-yet-determined games
            # (semifinals/championship before earlier games finish) -- treat
            # as TBD rather than crashing.
            home = cd.get("homeTeam") or {}
            away = cd.get("awayTeam") or {}
            rows.append({
                "game_id": game_id,
                "game_date": date_obj.strftime("%Y-%m-%d"),
                "home_team": home.get("teamTricode"),  # None/TBD if not yet set
                "away_team": away.get("teamTricode"),
                "home_team_id": home.get("teamId"),
                "away_team_id": away.get("teamId"),
                "game_status_text": cd.get("gameStatusText"),  # extra, drop if unneeded
            })
    print(f"{date_str}: {len(rows)} Summer League games")
    return rows


def main():
    all_rows = []
    for date_obj in DATES:
        all_rows.extend(fetch_date(date_obj))
        time.sleep(0.5)  # be polite, this is 11 sequential requests

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("\nNo games found -- check header combo against probe_gamecardfeed.py output")
        return

    df = df.drop_duplicates(subset="game_id")
    df.to_csv("summer_league_schedule.csv", index=False)
    print(f"\nSaved {len(df)} games to summer_league_schedule.csv")
    print(df.head(10))


if __name__ == "__main__":
    main()