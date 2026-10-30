"""Add one season to pay_table.csv, the salary-comps history behind the web app's /salarycomp.

price.py built it from HoopsHype salaries, but HoopsHype has answered 402 since mid-2025, so the table stopped at
2024-25. This builds a season from the Spotrac data already collected here, in price.py's layout and formulas:

- Salary: the player's Spotrac cap hits for the season, active roster plus dead money, so a waived player counts what
  he was paid (HoopsHype's figure) rather than only his new minimum (nba_payroll_history.csv, from
  payroll_history_scrape.py). Matched to NBA ids through sal_crosswalk.csv, else by name within the season; players
  still missing fall back to ../web_app/data/modern.csv's salary (also the Spotrac cap hit).
- Ratings and roles: lebron.csv rows for the year, the same source as the rest of pay_table.
- Win_Cost: the league's Spotrac payroll (active + dead money) / 1230 games, price.py's cost of a win; for 2023-24 and
  2024-25 that total is ~1.7% below the HoopsHype totals price.py used. WAC = WAR - Salary / Win_Cost.

    python pay_table_season.py 2026              # replace or add 2025-26 in ../web_app/data/pay_table.csv
    python pay_table_season.py 2026 --dry-run    # report only
    python pay_table_season.py 2025 --compare    # rebuild a season that has HoopsHype rows and compare to them
"""
import argparse
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PAY_TABLE = os.path.join(HERE, '..', 'web_app', 'data', 'pay_table.csv')
MODERN = os.path.join(HERE, '..', 'web_app', 'data', 'modern.csv')
GAMES = 1230  # price.py's games_per_year G: wins in a season, so Win_Cost is payroll per win


def name_key(name):
    """Lowercase ASCII letters only: 'Luka Dončić' and 'Luka Doncic' meet; suffixes kept."""
    name = unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z]', '', name.lower())


def price_key(name):
    """price.py's Player column: first three letters of the first name + the second word, letters only."""
    words = str(name).lower().replace("'", '').split(' ')
    return re.sub(r'\W', '', words[0][:3] + (words[1] if len(words) > 1 else ''))


def season_salaries(year, lebron):
    """{NBA ID: salary} for the season, plus the league payroll used for Win_Cost."""
    ph = pd.read_csv(os.path.join(HERE, 'nba_payroll_history.csv'))
    season = ph[(ph.season_end == year) & ph.section.isin(['active', 'dead_money'])]
    if season.empty:
        sys.exit(f'No Spotrac payroll rows for season_end {year}: run payroll_history_scrape.py first.')
    league_payroll = season.cap_hit.sum()

    per_player = season.groupby(['spotrac_id', 'player'], as_index=False).cap_hit.sum()
    cw = pd.read_csv(os.path.join(HERE, 'sal_crosswalk.csv'))
    cw = cw[~cw.ambiguous.astype(str).str.lower().eq('true')].dropna(subset=['nba_id']).drop_duplicates('spotrac_id')
    per_player = per_player.merge(cw[['spotrac_id', 'nba_id']], on='spotrac_id', how='left')

    by_name = dict(zip(lebron['Player'].map(name_key), lebron['NBA ID']))
    missing = per_player.nba_id.isna()
    per_player.loc[missing, 'nba_id'] = per_player.loc[missing, 'player'].map(name_key).map(by_name)
    salaries = per_player.dropna(subset=['nba_id']).groupby('nba_id').cap_hit.sum()
    salaries.index = salaries.index.astype(int)

    modern = pd.read_csv(MODERN, usecols=['PLAYER_ID', 'year', 'salary'], low_memory=False)
    modern = modern[(modern.year == year) & (modern.salary > 0)].drop_duplicates('PLAYER_ID').set_index('PLAYER_ID').salary
    fallback = modern[~modern.index.isin(salaries.index)]
    return pd.concat([salaries, fallback]), league_payroll, len(fallback)


def build_season(year):
    lebron = pd.read_csv(os.path.join(HERE, 'lebron.csv'))
    lebron = lebron[lebron.year == year].dropna(subset=['NBA ID']).drop_duplicates('NBA ID').copy()
    lebron['NBA ID'] = lebron['NBA ID'].astype(int)
    salaries, league_payroll, n_fallback = season_salaries(year, lebron)
    win_cost = league_payroll / GAMES

    rows = lebron[lebron['NBA ID'].isin(salaries.index)].copy()
    rows['Salary'] = rows['NBA ID'].map(salaries).astype(float)
    rows = rows[rows.Salary > 0]
    rows['WAR'] = rows['WAR'].fillna(0)
    rows = rows.assign(
        G=GAMES, Inflation_Salary=rows.Salary.round().astype('int64').astype(str), Year=float(year),
        Name=rows['Player'], Win_Cost=win_cost, Season=f'{year - 1}-{str(year)[-2:]}',
        all_teams=rows['team'], team=rows['team'].astype(str).str.split('/').str[-1],
        WAC=rows['WAR'] - rows['Salary'] / win_cost, year=float(year))
    rows['Player'] = rows['Name'].map(price_key)
    return rows, league_payroll, n_fallback


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('year', type=int, help='season end year, e.g. 2026 for 2025-26')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--compare', action='store_true', help='compare with the existing rows for that year; write nothing')
    args = ap.parse_args()

    table = pd.read_csv(PAY_TABLE)
    rows, league_payroll, n_fallback = build_season(args.year)
    rows = rows[table.columns]
    print(f'{args.year}: {len(rows)} player-seasons, {int(rows.LEBRON.notna().sum())} with LEBRON, '
          f'{n_fallback} salaries from modern.csv, league payroll ${league_payroll / 1e9:.3f}B, '
          f'Win_Cost ${rows.Win_Cost.iloc[0]:,.0f}')

    if args.compare:
        old = table[table.Year == args.year]
        both = old.merge(rows, on='NBA ID', suffixes=('_old', '_new'))
        diff = (both.Salary_old - both.Salary_new).abs()
        print(f'vs existing {len(old)} rows: {len(both)} in both; salary exact {int((diff < 1).sum())}, '
              f'within 2% {int((diff <= 0.02 * both.Salary_old).sum())}; Win_Cost old ${old.Win_Cost.iloc[0]:,.0f}; '
              f'WAC correlation {both[["WAC_old", "WAC_new"]].dropna().corr().iloc[0, 1]:.3f}')
        return
    if args.dry_run:
        return
    table = pd.concat([table[table.Year != args.year], rows], ignore_index=True)
    table.to_csv(PAY_TABLE, index=False)
    print(f'wrote {PAY_TABLE} ({len(table)} rows, years {int(table.Year.min())}-{int(table.Year.max())})')


if __name__ == '__main__':
    main()
