#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd

# Fetch the JSON data
url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
response = requests.get(url)
data = response.json()
print(data.keys())
# Extract games data
games_data = []
for game_date in data["leagueSchedule"]["gameDates"]:
    game_date_str = game_date["gameDate"]
    for game in game_date["games"]:
        game_info = {
            "gameId": game["gameId"],
            "gameCode": game["gameCode"],
            "gameStatus": game["gameStatus"],
            "gameStatusText": game["gameStatusText"],
            "gameDate": game_date_str,
            "arenaName": game["arenaName"],
            "arenaCity": game["arenaCity"],
            "homeTeam": game["homeTeam"]["teamName"],
            "homeTeamCity": game["homeTeam"]["teamCity"],
            "homeTeamScore": game["homeTeam"]["score"],
            "awayTeam": game["awayTeam"]["teamName"],
            "awayTeamCity": game["awayTeam"]["teamCity"],
            "awayTeamScore": game["awayTeam"]["score"],
            "pointsLeaderName": f"{game['pointsLeaders'][0]['firstName']} {game['pointsLeaders'][0]['lastName']}" if game["pointsLeaders"] else None,
            "pointsLeaderPoints": game["pointsLeaders"][0]["points"] if game["pointsLeaders"] else None
        }
        games_data.append(game_info)

# Convert to DataFrame
df = pd.DataFrame(games_data)

# Display the DataFrame
print(df.columns)


df.to_csv('schedule.csv')

print(df[df.gameId=='0032400001'])
df['gameDate'] = pd.to_datetime(df['gameDate']).dt.strftime('%Y-%m-%d')

df=df[df['gameDate']>='10222024']

team_acronyms = {
    'Celtics': 'BOS',
    'Lakers': 'LAL',
    'Pistons': 'DET',
    'Hawks': 'ATL',
    'Heat': 'MIA',
    '76ers': 'PHI',
    'Raptors': 'TOR',
    'Rockets': 'HOU',
    'Pelicans': 'NOP',
    'Jazz': 'UTA',
    'Clippers': 'LAC',
    'Trail Blazers': 'POR',
    'Wizards': 'WAS',
    'Mavericks': 'DAL',
    'Nuggets': 'DEN',
    'Kings': 'SAC',
    'Magic': 'ORL',
    'Cavaliers': 'CLE',
    'Knicks': 'NYK',
    'Bucks': 'MIL',
    'Hornets': 'CHA',
    'Bulls': 'CHI',
    'Grizzlies': 'MEM',
    'Timberwolves': 'MIN',
    'Spurs': 'SAS',
    'Suns': 'PHX',
    'Pacers': 'IND',
    'Nets': 'BKN',
    'Thunder': 'OKC',
    'Warriors': 'GSW'
}
df['homeTeam']=df['homeTeam'].map(team_acronyms)

df['awayTeam']=df['awayTeam'].map(team_acronyms)

df =df[['gameId','gameDate','homeTeam','awayTeam']]

df.rename(columns={'gameId':'game_id','gameDate':'game_date','homeTeam':'home_team','awayTeam':'away_team'},inplace=True)
old_dates=pd.read_csv('../web_app/data/game_dates.csv')


old_map=dict(zip(old_dates.team,old_dates.TEAM_ID))

df['home_team_id']=df['home_team'].map(old_map)

df['away_team_id']=df['away_team'].map(old_map)
df.dropna(subset= 'home_team_id',inplace=True)
df.to_csv('schedule.csv')
df.to_csv('../web_app/data/schedule.csv')
df['home_team_id'].unique()


# In[2]:


df[df['home_team_id'].isna()]


# In[ ]:




