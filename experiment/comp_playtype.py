import pandas as pd
import numpy as np

# 1. DATA SOURCES
# Note: I have corrected the variable names to match chronological order
URL_NOV_15 = 'https://raw.githubusercontent.com/gabriel1200/site_Data/2b9c9effa9686de6b1020dcd237f214d018680dc/teamplay.csv'
URL_CURRENT = 'https://raw.githubusercontent.com/gabriel1200/site_Data/refs/heads/master/teamplay.csv'

def get_performance_shift(team='NOP', year=2026):
    # Load data
    try:
        df_old = pd.read_csv(URL_NOV_15)
        df_now = pd.read_csv(URL_CURRENT)
    except Exception as e:
        return f"Error fetching data: {e}"

    # Filter for the specific team and year
    df_old = df_old[(df_old.Team == team) & (df_old.year == year)].copy()
    df_now = df_now[(df_now.Team == team) & (df_now.year == year)].copy()

    # --- PERIOD 1: PRE-NOV 15 (SNAPSHOT) ---
    p1 = df_old[['playtype', 'POSS', 'Points']].copy()
    total_poss_p1 = p1['POSS'].sum()
    p1['Freq_Pre'] = (p1['POSS'] / total_poss_p1) * 100
    p1['PPP_Pre'] = p1['Points'] / p1['POSS']

    # --- PERIOD 2: POST-NOV 15 (NEW PRODUCTION ONLY) ---
    # Merge to align rows and subtract old totals from current totals
    merged = pd.merge(df_now, df_old, on='playtype', suffixes=('_now', '_old'))
    
    p2 = pd.DataFrame()
    p2['playtype'] = merged['playtype']
    p2['POSS_New'] = merged['POSS_now'] - merged['POSS_old']
    p2['Points_New'] = merged['Points_now'] - merged['Points_old']
    
    # Calculate Frequency and PPP for the isolated "After" period
    total_poss_p2 = p2['POSS_New'].sum()
    p2['Freq_Post'] = (p2['POSS_New'] / total_poss_p2) * 100
    p2['PPP_Post'] = np.where(p2['POSS_New'] > 0, p2['Points_New'] / p2['POSS_New'], 0)

    # --- COMPARISON TABLE ---
    comp = pd.merge(
        p1[['playtype', 'Freq_Pre', 'PPP_Pre']],
        p2[['playtype', 'Freq_Post', 'PPP_Post']],
        on='playtype'
    )

    # Calculate Shifts
    comp['Freq_Shift'] = comp['Freq_Post'] - comp['Freq_Pre']
    comp['PPP_Shift'] = comp['PPP_Post'] - comp['PPP_Pre']

    # Formatting and Sorting
    comp = comp.sort_values('Freq_Shift', ascending=False).reset_index(drop=True)
    
    # Rounding for clean display
    display_cols = ['playtype', 'Freq_Pre', 'Freq_Post', 'Freq_Shift', 'PPP_Pre', 'PPP_Post', 'PPP_Shift']
    return comp[display_cols].round(3)

# Execute
results = get_performance_shift('NOP', 2026)

print("\n=== NOP PLAYTYPE ANALYSIS: PRE VS. POST NOV 15TH ===")
print(results.to_string(index=False))

# Optional: Save to CSV
# results.to_csv('nop_playstyle_shift.csv', index=False)