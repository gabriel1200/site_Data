import pandas as pd
import requests

# RealGM 403s the default python-requests UA; a browser-like header set
# (same approach as salary_scrape.py's DEFAULT_HEADERS) gets past it.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://basketball.realgm.com/",
}

# Fetch the page with requests
url = 'https://basketball.realgm.com/nba/info/salary_cap'
session = requests.Session()
session.headers.update(HEADERS)
response = session.get(url)
response.raise_for_status()  # raise an error if request failed

# Parse the tables from the HTML content
dfs = pd.read_html(response.text)
cap = dfs[0]

# Drop the multi-level column
print(cap.columns)

# Clean up columns
columns = ['Salary Cap', 'Luxury Tax', '1st Apron', '2nd Apron', 'BAE',
       'Non-Taxpayer MLE', 'Taxpayer MLE', 'Team Room MLE']

for col in columns:
    cap[col] = cap[col].str.replace(r'\D', '', regex=True).astype(float)
# For seasons like "2023-24", the second part is '24', so we prepend '20' if necessary
cap['year'] = cap['Season'].str.split('-').str[1]

cap.to_csv('cap.csv', index=False)