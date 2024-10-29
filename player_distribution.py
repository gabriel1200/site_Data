#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objects as go

import pandas as pd
import random
import numpy as np
import json
def full_name(team):
    team_dict = {'ATL': 'Atlanta Hawks',
     'BOS': 'Boston Celtics',
     'CLE': 'Cleveland Cavaliers',
     'NOP': 'New Orleans Pelicans',
     'CHI': 'Chicago Bulls',
     'DAL': 'Dallas Mavericks',
     'DEN': 'Denver Nuggets',
     'GSW': 'Golden State Warriors',
     'HOU': 'Houston Rockets',
     'LAC': 'Los Angeles Clippers',
     'LAL': 'Los Angeles Lakers',
     'MIA': 'Miami Heat',
     'MIL': 'Milwaukee Bucks',
     'MIN': 'Minnesota Timberwolves',
     'BRK': 'Brooklyn Nets',
     'NYK': 'New York Knicks',
     'ORL': 'Orlando Magic',
     'IND': 'Indiana Pacers',
     'PHI': 'Philadelphia 76ers',

     'PHO': 'Phoenix Suns',
     'POR': 'Portland Trail Blazers',
     'SAC': 'Sacramento Kings',
     'SAS': 'San Antonio Spurs',
     'OKC': 'Oklahoma City Thunder',
     'TOR': 'Toronto Raptors',
     'UTA': 'Utah Jazz',
     'MEM': 'Memphis Grizzlies',
     'WAS': 'Washington Wizards',
     'DET': 'Detroit Pistons',
     'CHA': 'Charlotte Hornets'}
    return team_dict[team.upper()]
def player_trend(player,graphtype='d', role = True):

    df = pd.read_csv('lebron.csv')
    
    
    old =df[df.year<2014].reset_index(drop=True)
    new= df[df.year>2013].reset_index(drop=True)
    old['Defensive Role'] = old['Pos']

    df = pd.concat([old,new]).reset_index(drop=True)

    # Create the scatter plot
    fig = go.Figure()
    
    df['year'] =df['year'].astype(int)
    
    pdf = df[df.Player.str.lower().str.contains(player.lower())].reset_index(drop=True)

    start_year = pdf['year'].min()
 
    end_year=pdf['year'].max()
    if graphtype =='d':
        unit = 'D-LEBRON'
        prole = 'Defensive Role'
    elif graphtype =='t':
        unit = 'LEBRON'
        prole = 'Pos'
        
    elif graphtype =='o':
        unit='O-LEBRON'
        prole = 'Offensive Archetype'
    
    pos = prole
    pos_type = prole
    if  graphtype=='t':
        df[pos]=''
        pdf[pos]=''
        pos_type='All Players'
            
    pdf['pos_year']= pdf[pos]+pdf['year'].astype(str)
    to_comp =pdf['pos_year'].tolist()
    

    df['pos_year'] =  df[pos]+df['year'].astype(str)


    df =df[df.pos_year.isin(to_comp)]


    # Add scatter points and lines connecting the points
    
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df[unit],
        mode='markers',
        name='Other Players',
        line=dict(shape='linear'),
        marker_color = '#3e8989',
        marker_size=10,
        
    ))
    fig.add_trace(go.Scatter(
        x=pdf['year'],
        y=pdf[unit],
        mode='lines+markers+text',
         textposition = 'top center',
        text =pdf[pos],
        textfont =dict(color='white',family='Malgun Gothic',size=20),
        name=player.title(),
        line=dict(shape='linear'),
        marker_color='#ffdb58',
        marker_size=20,
    ))
    
    # Customize layout
    fig.update_layout(
        width=1800,
        height=1200,
        title=player.title() + '<br>'+unit+' vs '+pos_type,
        paper_bgcolor='#0d0106',
        plot_bgcolor='#0d0106',
                      
                   
                   
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
        title_x=.5,
        xaxis_title='Year',
        yaxis_title=unit,
        showlegend=True,
         legend={'traceorder':'reversed','font':dict(color='#FFFFFF', size=22,family="Malgun Gothic") },
    )
    
# Show the plot
    fig.update_yaxes(
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
    
    tickfont=dict(color='#e5e5e5', size=25,family="Malgun Gothic",) ,
        showgrid=False,zeroline=False
    )
    fig.update_xaxes(
        showgrid=False,
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
        tickvals=[i for i in range(start_year,end_year+1)],
    
    tickfont=dict(color='#e5e5e5', size=25,family="Malgun Gothic",) 
    )
    return fig

fig = player_trend('nikola jokic',graphtype='o',role=True)
fig.show()


# In[2]:


df = pd.read_csv('lebron.csv')
df[df.Player.str.contains('holiday')]


# In[3]:


def weighted_average(dataframe, value, weight):
    val = dataframe[value]
    wt = dataframe[weight]
    return (val * wt).sum() / wt.sum()
 
 


name_dict = dict(zip(df['bref_id'],df['Player']))
# Weighted average of value  grouped by item name
career_average = df.groupby('bref_id').apply(weighted_average, 
                                     'O-LEBRON', 'Minutes').reset_index()
career_average.columns = ['bref_id','O-LEBRON']

career_average['name'] = career_average['bref_id'].map(name_dict)
career_average.sort_values(by='O-LEBRON')


# In[4]:


df['Player'] = df['Player'].str.replace('ure holiday','jrue holiday')
df


# In[8]:


def get_colors():
    path = 'colors.json'
    f = open(path)

    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    team_colors = {}
    for team in data:
        obj = data[team]
        color = obj['mainColor']
        color_hex = obj['colors'][color]['hex']
        team_colors[team]=color_hex
    team_colors['PHX']= '#e56020',
    second_colors = {}
    for team in data:
        obj = data[team]
        color = obj['secondaryColor']
        color_hex = obj['colors'][color]['hex']
        second_colors[team]=color_hex
    second_colors['PHX']= '#1d1160',

    temp = team_colors['BKN']

    team_colors['BKN'] = second_colors['BKN']
    second_colors['BKN'] = temp
    return team_colors,second_colors
def teambron_trend(team,graphtype='d', role = True):

    df = pd.read_csv('lebron.csv')
    jitter_strength = 0.02
    
    df['year_jitter'] = df['year'] + np.random.uniform(-jitter_strength, jitter_strength, len(df))
    
    old =df[df.year<2014].reset_index(drop=True)
    new= df[df.year>2013].reset_index(drop=True)
    old['Defensive Role'] = old['Pos']

    df = pd.concat([old,new]).reset_index(drop=True)
    team_colors,second_colors = get_colors()
    df['color'] = df['team'].map(team_colors)
    df['second_color'] = df['team'].map(second_colors)

    # Create the scatter plot
    fig = go.Figure()
    
    df['year'] =df['year'].astype(int)
    
    tdf = df[df.team.str.lower()==team].reset_index(drop=True)
    

    start_year = tdf['year'].min()
 
    end_year=tdf['year'].max()
    if graphtype =='d':
        unit = 'D-LEBRON'
        prole = 'Defensive Role'
    elif graphtype =='t':
        unit = 'LEBRON'
        prole = 'Pos'
        
    elif graphtype =='o':
        unit='O-LEBRON'
        prole = 'Offensive Archetype'
    
    df['color']='grey'
    df['second_color']='grey'

    # Add scatter points and lines connecting the points
    
    
    fig.add_trace(go.Scatter(
        x=df['year_jitter'],
        y=df[unit],
        mode='markers',
        name='All Players',
        line=dict(shape='linear'),
        marker_color = df['color'],
        marker_size=12,
        marker_opacity=.2,
        marker_line_color=df['second_color'],
        #marker_line_width=3
        
    ))
    fig.add_trace(go.Scatter(
        x=tdf['year_jitter'],
        y=tdf[unit],
        mode='markers',
         textposition = 'top center',
        text =tdf['Player'].str.title(),
        textfont =dict(color='white',family='Malgun Gothic',size=20),
        name=full_name(team).split(' ')[-1]+ ' Players',
        line=dict(shape='linear'),
        marker_color=tdf['color'],
        marker_line_color=tdf['second_color'],
        marker_size=15,
         marker_line_width=3,
    ))
    
    # Customize layout
    fig.update_layout(
        width=1800,
        height=1200,
        title=full_name(team) + '<br>'+unit,
        paper_bgcolor='#0d0106',
        plot_bgcolor='#0d0106',
                      
                   
                   
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
        title_x=.5,
        xaxis_title='Year',
        yaxis_title=unit,
        showlegend=True,
         legend={'traceorder':'reversed','font':dict(color='#FFFFFF', size=22,family="Malgun Gothic") },
    )
    
# Show the plot
    fig.update_yaxes(
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
    
    tickfont=dict(color='#e5e5e5', size=25,family="Malgun Gothic",) ,
        showgrid=False,zeroline=False
    )
    fig.update_xaxes(
        showgrid=False,
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
        tickvals=[i for i in range(start_year,end_year+1)],
    
    tickfont=dict(color='#e5e5e5', size=25,family="Malgun Gothic",) 
    )
    return fig

fig = teambron_trend('det',graphtype='t',role=True)
fig.show()


# In[ ]:




