#!/usr/bin/env python
# coding: utf-8

# In[44]:


import plotly.graph_objects as go

import pandas as pd
import random
import numpy as np
def player_trend(player):
    df = pd.read_csv('lebron.csv')
    
    
    
    # Create the scatter plot
    fig = go.Figure()
    df['year'] =df['year'].astype(int)
    
    pdf = df[df.Player.str.lower()==player.lower()].reset_index(drop=True)

    start_year = pdf['year'].min()
    end_year=pdf['year'].max()
    pos = 'Pos'
    pdf['pos_year']= pdf[pos]+pdf['year'].astype(str)
    to_comp =pdf['pos_year'].tolist()
    

    df['pos_year'] =  df[pos]+df['year'].astype(str)


    df =df[df.pos_year.isin(to_comp)]

    # Add scatter points and lines connecting the points
    
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['D-LEBRON'],
        mode='markers',
        name='Other Players',
        line=dict(shape='linear'),
        marker_color = '#3e8989',
        marker_size=10,
        
    ))
    fig.add_trace(go.Scatter(
        x=pdf['year'],
        y=pdf['D-LEBRON'],
        mode='lines+markers',
        name=player.title(),
        line=dict(shape='linear'),
        marker_color='#ffdb58',
        marker_size=20,
    ))
    
    # Customize layout
    fig.update_layout(
        width=1620,
        height=1260,
        title=player.title() + '<br>D-Lebron vs Position',
        paper_bgcolor='#0d0106',
        plot_bgcolor='#0d0106',
                      
                   
                   
        title_font = dict(color='white', size=50,family="Malgun Gothic",) ,
        title_x=.5,
        xaxis_title='Year',
        yaxis_title='D-Lebron',
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
    
    tickfont=dict(color='#e5e5e5', size=24,family="Malgun Gothic",) 
    )
    return fig

fig = player_trend('alex caruso')
fig.show()


# In[ ]:




