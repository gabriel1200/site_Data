#!/usr/bin/env python
"""
It's mid-July -- no regular NBA games are being played. If
todaysScoreboard_00.json has ANY games in it right now, they're almost
certainly Summer League games riding under the regular NBA suffix.
Dump it raw so we can see gameId format, league labeling, everything.
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

URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"


def main():
    resp = requests.get(URL, headers=NBA_HEADERS, timeout=10)
    print(f"status: {resp.status_code}")
    data = resp.json()

    games = data.get("scoreboard", {}).get("games", [])
    print(f"games today: {len(games)}")
    print(f"scoreboard.gameDate: {data.get('scoreboard', {}).get('gameDate')}")
    print(f"scoreboard.leagueId: {data.get('scoreboard', {}).get('leagueId')}")

    for g in games:
        print("-" * 60)
        print(f"gameId: {g.get('gameId')}")
        print(f"gameCode: {g.get('gameCode')}")
        print(f"gameStatusText: {g.get('gameStatusText')}")
        print(f"arenaName: {g.get('arenaName')}, arenaCity: {g.get('arenaCity')}")
        print(f"home: {g['homeTeam']['teamCity']} {g['homeTeam']['teamName']} ({g['homeTeam']['teamTricode']})")
        print(f"away: {g['awayTeam']['teamCity']} {g['awayTeam']['teamName']} ({g['awayTeam']['teamTricode']})")

    # Full raw dump too, in case there's a top-level leagueId/label field we're not printing above
    with open("todays_scoreboard_00_raw.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nFull raw JSON saved to todays_scoreboard_00_raw.json")


if __name__ == "__main__":
    main()