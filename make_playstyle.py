import pandas as pd

PLAYTYPE_MAP = {
    'pr_ball':     'on_ball',
    'iso':         'on_ball',
    'post':        'on_ball',
    'pr_roll':     'play_finish',
    'oreb':        'play_finish',
    'cut':         'play_finish',
    'spot':        'play_finish',
    'hand_off':    'motion',
    'off_screen':  'motion',
    'tran':        'tran',
    # 'misc' intentionally excluded
}

COUNT_COLS  = ['Poss', 'FGM', 'FGA', 'Points']
RATE_COLS   = ['aFG%', '%FT', '%TO', '%SF', '%Score']   # weighted avg by Poss
GROUP_COLS  = ['Player', 'Team', 'GP', 'PLAYER_ID', 'playtype', 'year']


def build_playstyle_df(playtype_df: pd.DataFrame) -> pd.DataFrame:
    df = playtype_df.copy()

    # Apply the many-to-one playtype mapping; drop unmapped rows (misc, etc.)
    df['playtype'] = df['playtype'].map(PLAYTYPE_MAP)
    df = df.dropna(subset=['playtype'])

    # Only group by columns that are actually present
    group_cols = [c for c in GROUP_COLS if c in df.columns]

    # Sum the counting stats
    count_agg = (
        df.groupby(group_cols)[COUNT_COLS]
        .sum()
        .reset_index()
    )

    # Weighted average for rate stats (weight = Poss)
    rate_cols_present = [c for c in RATE_COLS if c in df.columns]
    if rate_cols_present:
        def wavg(g, cols):
            w = g['Poss']
            total = w.sum()
            if total == 0:
                return pd.Series({c: 0.0 for c in cols})
            return pd.Series({c: (g[c] * w).sum() / total for c in cols})

        rate_agg = (
            df.groupby(group_cols)
            .apply(wavg, cols=rate_cols_present, include_groups=False)
            .reset_index()
        )
        result = count_agg.merge(rate_agg, on=group_cols, how='left')
    else:
        result = count_agg

    # Derive calculated columns
    result['PPP']  = (result['Points'] / result['Poss']).fillna(0)
    result['FG%']  = (result['FGM']    / result['FGA']).fillna(0) * 100
    result['% Time'] = (
        df.groupby(group_cols)['% Time'].sum().reset_index()['% Time']
        if '% Time' in df.columns
        else 0
    )

    # Match the column order of the original playstyle.csv
    col_order = [
        'Player', 'Team', 'year', '% Time', 'PPP', 'Points',
        'FGM', 'FGA', 'FG%', 'aFG%', '%FT', '%TO', '%SF', '%Score',
        'Poss', 'GP', 'playtype', 'PLAYER_ID',
    ]
    col_order = [c for c in col_order if c in result.columns]
    result = result[col_order]

    result.sort_values(by='year', inplace=True)
    return result.reset_index(drop=True)


if __name__ == '__main__':
    PLAYTYPE_FILE  = 'playtype.csv'
    PLAYSTYLE_FILE = 'playstyle.csv'

    PLAYTYPE_FILE_PS  = 'playtype_p.csv'
    PLAYSTYLE_FILE_PS = 'playstyle_p.csv'

    for src, dst in [
        (PLAYTYPE_FILE, PLAYSTYLE_FILE),
        (PLAYTYPE_FILE_PS, PLAYSTYLE_FILE_PS),
    ]:
        print(f'Reading {src}...')
        raw = pd.read_csv(src, low_memory=False)
        out = build_playstyle_df(raw)
        out.to_csv(dst, index=False)
        print(f'Wrote {len(out)} rows to {dst}.')