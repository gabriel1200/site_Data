import pandas as pd
import requests

# Step 1: Read the URL
url_file = "download_url.txt2"
try:
    with open(url_file, "r") as file:
        url = file.readline().strip()
except FileNotFoundError:
    raise FileNotFoundError(f"{url_file} not found. Please create it and add the URL.")

# Step 2: Download the file
filename = "salary_link26.csv"
try:
    response = requests.get(url)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)

    print(f"Downloaded → {filename}")
except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Download failed: {e}")

# Step 3: Load + clean
df = pd.read_csv(filename)

# Select only needed columns and rename
df = df[['player_id', 'Year', 'salary']].copy()
df.columns = ['nba_id', 'year', 'salary']

# Optional: enforce types
df['nba_id'] = pd.to_numeric(df['nba_id'], errors='coerce')
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

# Step 4: Save
df.to_csv('year_salaries.csv', index=False)

print("Saved → year_salaries.csv")