#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
nba_team_links = {
    "ATL": "https://www.sportsoddshistory.com/nba-team/?Team=Atlanta+Hawks&sa=nba",
    "BOS": "https://www.sportsoddshistory.com/nba-team/?Team=Boston+Celtics&sa=nba",
    "BKN": "https://www.sportsoddshistory.com/nba-team/?Team=Brooklyn+Nets&sa=nba",
    "CHA": "https://www.sportsoddshistory.com/nba-team/?Team=Charlotte+Hornets&sa=nba",
    "CHI": "https://www.sportsoddshistory.com/nba-team/?Team=Chicago+Bulls&sa=nba",
    "CLE": "https://www.sportsoddshistory.com/nba-team/?Team=Cleveland+Cavaliers&sa=nba",
    "DAL": "https://www.sportsoddshistory.com/nba-team/?Team=Dallas+Mavericks&sa=nba",
    "DEN": "https://www.sportsoddshistory.com/nba-team/?Team=Denver+Nuggets&sa=nba",
    "DET": "https://www.sportsoddshistory.com/nba-team/?Team=Detroit+Pistons&sa=nba",
    "GSW": "https://www.sportsoddshistory.com/nba-team/?Team=Golden+State+Warriors&sa=nba",
    "HOU": "https://www.sportsoddshistory.com/nba-team/?Team=Houston+Rockets&sa=nba",
    "IND": "https://www.sportsoddshistory.com/nba-team/?Team=Indiana+Pacers&sa=nba",
    "LAC": "https://www.sportsoddshistory.com/nba-team/?Team=Los+Angeles+Clippers&sa=nba",
    "LAL": "https://www.sportsoddshistory.com/nba-team/?Team=Los+Angeles+Lakers&sa=nba",
    "MEM": "https://www.sportsoddshistory.com/nba-team/?Team=Memphis+Grizzlies&sa=nba",
    "MIA": "https://www.sportsoddshistory.com/nba-team/?Team=Miami+Heat&sa=nba",
    "MIL": "https://www.sportsoddshistory.com/nba-team/?Team=Milwaukee+Bucks&sa=nba",
    "MIN": "https://www.sportsoddshistory.com/nba-team/?Team=Minnesota+Timberwolves&sa=nba",
    "NOP": "https://www.sportsoddshistory.com/nba-team/?Team=New+Orleans+Pelicans&sa=nba",
    "NYK": "https://www.sportsoddshistory.com/nba-team/?Team=New+York+Knicks&sa=nba",
    "OKC": "https://www.sportsoddshistory.com/nba-team/?Team=Oklahoma+City+Thunder&sa=nba",
    "ORL": "https://www.sportsoddshistory.com/nba-team/?Team=Orlando+Magic&sa=nba",
    "PHI": "https://www.sportsoddshistory.com/nba-team/?Team=Philadelphia+76ers&sa=nba",
    "PHX": "https://www.sportsoddshistory.com/nba-team/?Team=Phoenix+Suns&sa=nba",
    "POR": "https://www.sportsoddshistory.com/nba-team/?Team=Portland+Trail+Blazers&sa=nba",
    "SAC": "https://www.sportsoddshistory.com/nba-team/?Team=Sacramento+Kings&sa=nba",
    "SAS": "https://www.sportsoddshistory.com/nba-team/?Team=San+Antonio+Spurs&sa=nba",
    "TOR": "https://www.sportsoddshistory.com/nba-team/?Team=Toronto+Raptors&sa=nba",
    "UTA": "https://www.sportsoddshistory.com/nba-team/?Team=Utah+Jazz&sa=nba",
    "WAS": "https://www.sportsoddshistory.com/nba-team/?Team=Washington+Wizards&sa=nba"
}

all_futures=[]
for team in nba_team_links.keys():
    team_url = nba_team_links[team]
    frames = pd.read_html(team_url)
    
    df=frames[-2]
    
    df['team']=team
    print(df)
    all_futures.append(df)


# In[6]:


series_futures = pd.concat(all_futures)

series_futures


# In[7]:


series_futures.to_csv('series_futures.csv',index=False)


# In[ ]:




