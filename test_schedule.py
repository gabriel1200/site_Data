import requests

headers = {
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

# Example of how to use it:
url = 'https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_1.json'
response = requests.get(url, headers=headers)

print(response.json())