#!/usr/bin/env python
"""
Dump every '001'-prefixed game from the standard schedule feed, in full,
so we can eyeball whether these are actually preseason or secretly Summer League.
"""

import json
import requests

NBA_HEADERS = {
    'authority': 'cdn.nba.com',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'dnt': '1',
    'origin': 'https://www.nba.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.nba.com/',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
}

URL = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"


def main():
    resp = requests.get(URL, headers=NBA_HEADERS, timeout=10)
    data = resp.json()

    matches = []
    for gd in data["leagueSchedule"]["gameDates"]:
        for g in gd.get("games", []):
            if g["gameId"].startswith("001"):
                matches.append({
                    "gameId": g["gameId"],
                    "gameCode": g.get("gameCode"),
                    "gameDate": gd["gameDate"],
                    "gameLabel": g.get("gameLabel"),
                    "gameSubLabel": g.get("gameSubLabel"),
                    "seriesText": g.get("seriesText"),
                    "arenaName": g.get("arenaName"),
                    "arenaCity": g.get("arenaCity"),
                    "arenaState": g.get("arenaState"),
                    "homeTeam": f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}",
                    "awayTeam": f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}",
                })

    matches.sort(key=lambda x: x["gameDate"])

    print(f"Found {len(matches)} games with '001' prefix\n")
    print(json.dumps(matches, indent=2))

    with open("preseason_001_games.json", "w") as f:
        json.dump(matches, f, indent=2)
    print("\nSaved to preseason_001_games.json")


if __name__ == "__main__":
    main()