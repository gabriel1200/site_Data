#!/usr/bin/env python
# coding: utf-8

# In[41]:


import plotly.graph_objects as go

import pandas as pd
import random
import numpy as np
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
        
    else:
        unit='O-LEBRON'
        prole = 'Offensive Archetype'
    
    pos = prole
    pos_type = prole

        
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

fig = player_trend('nic claxton',graphtype='d',role=True)
fig.show()


# In[59]:


df = pd.read_csv('lebron.csv')
df[df.Player.str.contains('holiday')]


# In[57]:


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


# In[60]:


df['Player'] = df['Player'].str.replace('ure holiday','jrue holiday')
df


# In[61]:


df[df.Player.str.contains('jrue')]


# In[65]:





# In[ ]:




