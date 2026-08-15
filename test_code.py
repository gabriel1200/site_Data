import requests, re
url = "https://www.spotrac.com/nba/brooklyn-nets/yearly"
html = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9",
}, timeout=25).text

# show the actual /player/ link format
print("--- first 5 /player/ hrefs ---")
for m in re.findall(r'href="([^"]*?/player/[^"]*)"', html)[:5]:
    print(m)

print("\n--- a full data-export name cell as served ---")
m = re.search(r'<td[^>]*data-export="[^"]*"[^>]*>.*?</td>', html, re.S)
print(m.group(0)[:900] if m else "no data-export cell matched")