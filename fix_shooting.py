#!/usr/bin/env python
# coding: utf-8

"""
REGENERATE player_shooting.csv AND player_shooting_p.csv FROM SCRATCH

Refetches every season (2014 through SEASON_END_YEAR, per stat_scrape2.py's
config) from the NBA API for both regular season and playoffs, then rebuilds
the two master files from the freshly-written per-season folders.

Run this from the same directory as stat_scrape2.py (and the same directory
that contains your {year}/player_shooting/ folders).

WARNING: This refetches ~13 seasons x 4 shot-distance buckets x 2 (RS/PS)
= ~104 API calls with 0.5s sleeps between them. Expect this to take a while
and to hit stats.nba.com's rate limits occasionally -- the retry session in
stat_scrape2.py will handle transient 429/5xx errors, but if it stalls hard
on a specific season, just re-run; get_playershots will overwrite that
season's folder again.
"""

from stat_scrape2 import get_playershots, master_shooting, SEASON_END_YEAR

# Full season-start-year range. NBA API convention here: passing year=Y
# writes to folder {Y+1}/, i.e. the season that *ends* in calendar year Y+1.
# SEASON_END_YEAR comes from YEAR_TO_SCRAPE in stat_scrape2.py's config,
# so this will automatically include whatever the most recent season is.
START_YEAR = 2013  # writes to 2014/ folder onward, matching master_shooting's range(2014, ...)
END_YEAR = SEASON_END_YEAR - 1  # so END_YEAR + 1 == SEASON_END_YEAR

years = list(range(START_YEAR, END_YEAR + 1))

print(f"Regenerating player shooting data for seasons ending {START_YEAR + 1}-{END_YEAR + 1}")
print(f"({len(years)} seasons x 4 shot-distance buckets x 2 season types)\n")

# --- Regular season ---
print("=== REGULAR SEASON: refetching all years ===")
get_playershots(years, ps=False)

print("\n=== REGULAR SEASON: rebuilding master file ===")
master_rs = master_shooting(playoffs=False)
if not master_rs.empty:
    master_rs.to_csv('player_shooting.csv', index=False)
    print(f"Saved player_shooting.csv -- {len(master_rs)} rows")
    print(master_rs['year'].value_counts().sort_index())
else:
    print("WARNING: regular season master came back empty, nothing written.")

# --- Playoffs ---
print("\n=== PLAYOFFS: refetching all years ===")
get_playershots(years, ps=True)

print("\n=== PLAYOFFS: rebuilding master file ===")
master_ps = master_shooting(playoffs=True)
if not master_ps.empty:
    master_ps.to_csv('player_shooting_p.csv', index=False)
    print(f"Saved player_shooting_p.csv -- {len(master_ps)} rows")
    print(master_ps['year'].value_counts().sort_index())
else:
    print("WARNING: playoffs master came back empty, nothing written.")

print("\nDone.")