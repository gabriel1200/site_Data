import pandas as pd

# Load data
df = pd.read_csv('nbashotmaking.csv')
index_frame = pd.read_csv('index_master.csv')

# Rename nba_id → PLAYER_ID
index_frame = index_frame.rename(columns={'nba_id': 'PLAYER_ID'})

# Create Season column in format "YYYY-YY"
index_frame['Season'] = (index_frame['year'] - 1).astype(str) + "-" + (index_frame['year'] % 100).astype(str).str.zfill(2)

# Remove '2TM' rows
index_frame = index_frame[index_frame['team'] != "2TM"]

# Keep only most recent row per PLAYER_ID + Season (assuming larger 'year' = more recent)
index_frame = index_frame.sort_values('year').drop_duplicates(subset=['PLAYER_ID', 'Season'], keep='last')

# Drop TEAM_ABBREVIATION from df before merging
if 'TEAM_ABBREVIATION' in df.columns:
    df = df.drop(columns=['TEAM_ABBREVIATION'])

# Merge on PLAYER_ID + Season
merged = df.merge(index_frame[['PLAYER_ID', 'Season', 'team']], 
                  on=['PLAYER_ID', 'Season'], how='left')

# Rename Team → TEAM_ABBREVIATION
merged = merged.rename(columns={'team': 'TEAM_ABBREVIATION'})
merged.to_csv('nbashotmaking.csv')
player_id_test = 1629029

test_rows = merged[merged['PLAYER_ID'] == player_id_test]

print(test_rows[['PLAYER_ID', 'Season', 'TEAM_ABBREVIATION']].drop_duplicates())
