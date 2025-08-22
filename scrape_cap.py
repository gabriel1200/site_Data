import pandas as pd
import requests

# Fetch the page with requests
url = 'https://basketball.realgm.com/nba/info/salary_cap'
response = requests.get(url)
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
