import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
# 1. DATA PREPARATION (The "Plug-in" Logic)
def prepare_split_data(year=2026):
    old_url = 'https://raw.githubusercontent.com/gabriel1200/site_Data/2b9c9effa9686de6b1020dcd237f214d018680dc/teamplay.csv'
    now_url = 'https://raw.githubusercontent.com/gabriel1200/site_Data/refs/heads/master/teamplay.csv'
    
    df_old_raw = pd.read_csv(old_url)
    df_now_raw = pd.read_csv(now_url)

    # Filter for the correct year and ensure we only have relevant columns
    df_old = df_old_raw[df_old_raw.year == year].copy()
    df_now = df_now_raw[df_now_raw.year == year].copy()

    # --- PERIOD 1: PRE-NOV 15 (Entire League) ---
    # Group to ensure we have totals for frequency calculations
    team_totals_pre = df_old.groupby('Team')['POSS'].sum().reset_index().rename(columns={'POSS': 'team_total'})
    df_pre = df_old.merge(team_totals_pre, on='Team')
    df_pre['Freq%'] = (df_pre['POSS'] / df_pre['team_total']) * 100
    # PPP is already in the file, but we can recalculate to be safe
    df_pre['PPP'] = df_pre['Points'] / df_pre['POSS']
    # Normalize POSS by GP for the bubble size/scaling if needed
    df_pre['Poss_PG'] = df_pre['POSS'] / df_pre['GP']

    # --- PERIOD 2: POST-NOV 15 (Entire League Delta) ---
    merged = pd.merge(df_now, df_old, on=['Team', 'playtype', 'full_name'], suffixes=('_now', '_old'))
    
    df_post = pd.DataFrame()
    df_post['Team'] = merged['Team']
    df_post['full_name'] = merged['full_name']
    df_post['playtype'] = merged['playtype']
    df_post['POSS'] = merged['POSS_now'] - merged['POSS_old']
    df_post['Points'] = merged['Points_now'] - merged['Points_old']
    df_post['GP'] = merged['GP_now'] - merged['GP_old']
    
    # Calculate Frequency and PPP for the delta period specifically
    team_totals_post = df_post.groupby('Team')['POSS'].sum().reset_index().rename(columns={'POSS': 'team_total'})
    df_post = df_post.merge(team_totals_post, on='Team')
    df_post['Freq%'] = (df_post['POSS'] / df_post['team_total']) * 100
    df_post['PPP'] = np.where(df_post['POSS'] > 0, df_post['Points'] / df_post['POSS'], 0)
    df_post['Poss_PG'] = np.where(df_post['GP'] > 0, df_post['POSS'] / df_post['GP'], 0)

    return df_pre, df_post

# 2. UPDATED VISUALIZATION FUNCTION
def scatter_change_period(df_start, df_end, team, title_suffix=""):
    # Ensure column names are consistent
    df_start = df_start.rename(columns={"Poss_PG": "Poss"})
    df_end = df_end.rename(columns={"Poss_PG": "Poss"})

    data_names = {
        "pr_ball": "Handler", "iso": "Isolation", "tran": "Transition",
        "pr_roll": "Roll", "post": "Post", "hand_off": "Hand Off",
        "oreb": "Putback", "cut": "Cut", "off_screen": "Off Screen",
        "spot": "Spot Up", "misc": "misc"
    }

    # Map playtypes and filter out misc
    df_start["playtype_label"] = df_start["playtype"].map(data_names)
    df_end["playtype_label"] = df_end["playtype"].map(data_names)
    df_start = df_start[df_start.playtype != "misc"]
    df_end = df_end[df_end.playtype != "misc"]

    playtypes = [n for n in data_names.values() if n != "misc"]
    
    # Get the team's full name for the title
    name_dict = dict(zip(df_start.Team, df_start.full_name))
    fullname = name_dict.get(team.upper(), team)

    fig = make_subplots(
        rows=2, cols=5,
        subplot_titles=playtypes,
        shared_yaxes=True,
        x_title="Frequency (%)",
    )

    for i, play in enumerate(playtypes):
        row = i // 5 + 1
        col = i % 5 + 1

        # Period 1 (Pre-Nov 15) - DIAMONDS
        p1_sub = df_start[df_start.playtype_label == play].copy()
        p1_sub["perc"] = 100 * p1_sub["PPP"].rank(pct=True)
        # Apply logic on string elements works fine here
        p1_sub["opa"] = p1_sub["Team"].apply(lambda x: 1.0 if str(x).lower() == team.lower() else 0.1)

        fig.add_trace(go.Scatter(
            mode="markers", x=p1_sub["Freq%"], y=p1_sub["PPP"],
            marker=dict(size=12, line=dict(color="grey", width=1),
                        colorscale="plasma", color=p1_sub["perc"], opacity=p1_sub["opa"], symbol="diamond"),
            name="Pre Nov 15", showlegend=False
        ), row=row, col=col)

        # Period 2 (Post-Nov 15 Delta) - CIRCLES
        p2_sub = df_end[df_end.playtype_label == play].copy()
        p2_sub["perc"] = 100 * p2_sub["PPP"].rank(pct=True)
        p2_sub["opa"] = p2_sub["Team"].apply(lambda x: 1.0 if str(x).lower() == team.lower() else 0.1)

        fig.add_trace(go.Scatter(
            mode="markers", x=p2_sub["Freq%"], y=p2_sub["PPP"],
            marker=dict(size=12, line=dict(color="white", width=1),
                        colorscale="plasma", color=p2_sub["perc"], opacity=p2_sub["opa"], symbol="circle"),
            name="Post Nov 15", showlegend=False
        ), row=row, col=col)

        # FIX: Use .str.lower() for Series comparison
        t_start = p1_sub[p1_sub.Team.str.lower() == team.lower()]
        t_end = p2_sub[p2_sub.Team.str.lower() == team.lower()]

        if not t_start.empty and not t_end.empty:
            fig.add_trace(go.Scatter(
                x=[t_start["Freq%"].iloc[0], t_end["Freq%"].iloc[0]],
                y=[t_start["PPP"].iloc[0], t_end["PPP"].iloc[0]],
                mode="lines", line=dict(color="rgba(255,255,255,0.5)", width=2),
                showlegend=False
            ), row=row, col=col)

    # Layout styling
    fig.update_layout(
        height=800, width=1250, title_text=f"{fullname}: Early Season vs. Recent Stretch (Nov 15 Delta)",
        template="plotly_dark", paper_bgcolor="#211a1d", plot_bgcolor="#211a1d",
        title_x=0.5, font=dict(family="Malgun Gothic", size=12, color="#f6f7eb")
    )
    
    # Custom Legend markers
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                             marker=dict(symbol='diamond', color='white', size=10), name='Pre Nov 15'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', 
                             marker=dict(symbol='circle', color='white', size=10), name='Post Nov 15 (Delta)'))

    return fig

# 3. RUN IT
df_pre, df_post = prepare_split_data(year=2026)
fig = scatter_change_period(df_pre, df_post, team='NOP')

pio.write_image(fig, "spread.png")