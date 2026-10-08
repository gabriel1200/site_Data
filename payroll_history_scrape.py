"""Historical team payrolls from Spotrac, one row per player per team-season.

    python payroll_history_scrape.py                 # every completed season not already cached (usually a no-op)
    python payroll_history_scrape.py --from 2013     # first season to cover (spot year = season start year)
    python payroll_history_scrape.py --force         # re-fetch even cached team-years

Spotrac's `payroll/_/year/YYYY` page shows the YYYY-(YY+1) season (year 2019 = 2019-20). Each page has
several tables; the heading above each one says what it is:

  active       "Active Roster Cap": real pay. Cap hit equals modern.csv's salary for 99% of players.
  dead_money   "Dead Money Cap": what the team still owes players it released. An obligation, not salary.
  exempt       "Exempt List Cap": players whose salary is exempt from the team's cap count (for example a long
               suspension). They are still paid, at their real salary, so the pipeline treats them like active.
  cap_hold     "Cap Hold Cap": placeholders for rights the team keeps. Not pay; kept only so it can be excluded.

A traded player is listed once, on his final team, at the full-season cap hit.

Outputs (also copied to ../web_app/data/):
  nba_payroll_history.csv   one row per player per section per team-year
  nba_payroll_pages.csv     which team-years loaded (the pipeline only calls a player absent from the league
                            when all 30 pages of that season loaded)

Fetches are cached per team-year in payroll_cache/ so an interrupted run resumes where it stopped.
"""
import argparse
import datetime as dt
import os
import random
import re
import shutil
import sys
import time

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}
SLUGS = {
    "ATL": "atlanta-hawks", "BOS": "boston-celtics", "BKN": "brooklyn-nets", "CHA": "charlotte-hornets",
    "CHI": "chicago-bulls", "CLE": "cleveland-cavaliers", "DAL": "dallas-mavericks", "DEN": "denver-nuggets",
    "DET": "detroit-pistons", "GSW": "golden-state-warriors", "HOU": "houston-rockets", "IND": "indiana-pacers",
    "LAC": "la-clippers", "LAL": "los-angeles-lakers", "MEM": "memphis-grizzlies", "MIA": "miami-heat",
    "MIL": "milwaukee-bucks", "MIN": "minnesota-timberwolves", "NOP": "new-orleans-pelicans", "NYK": "new-york-knicks",
    "OKC": "oklahoma-city-thunder", "ORL": "orlando-magic", "PHI": "philadelphia-76ers", "PHX": "phoenix-suns",
    "POR": "portland-trail-blazers", "SAC": "sacramento-kings", "SAS": "san-antonio-spurs", "TOR": "toronto-raptors",
    "UTA": "utah-jazz", "WAS": "washington-wizards",
}
SECTION_WORDS = (("Active Roster", "active"), ("Exempt List", "exempt"), ("Dead Money", "dead_money"), ("Cap Hold", "cap_hold"))
MIN_PAGE_BYTES = 200_000   # a real payroll page is ~1 MB; Cloudflare or error pages are far smaller
DELAY_SECONDS = 3.0        # between pages, plus up to 1s of jitter
BLOCK_WAITS = (20, 45, 90, 150)   # seconds to wait after an HTTP 403/429 before trying the same page again
SLOW_AFTER_BLOCK = 6.0     # seconds between pages for the next SLOW_PAGES pages after any block
SLOW_PAGES = 12
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "payroll_cache")
COLUMNS = ["season_end", "spot_year", "team", "section", "spotrac_id", "player", "pos", "age", "type", "cap_hit", "base_salary"]


def last_complete_spot_year(today=None):
    """Spot year of the most recent season that has finished (2025 for Oct 2026: the 2025-26 season)."""
    today = today or dt.date.today()
    current_season_end = today.year + 1 if today.month >= 7 else today.year
    return current_season_end - 2


def money(text):
    cleaned = re.sub(r"[^\d.\-]", "", str(text))
    return float(cleaned) if cleaned not in ("", "-", ".") else np.nan


def section_of(table):
    """Name the table from the heading above it."""
    for element in table.find_all_previous(limit=60):
        text = element.get_text(" ", strip=True) if hasattr(element, "get_text") else ""
        if text and len(text) < 140:
            for word, label in SECTION_WORDS:
                if word in text:
                    return label
    return "unknown"


def parse_payroll_page(html, team, spot_year):
    """Rows for every player table on a team-year page (empty frame if the page has no player tables)."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for table in soup.find_all("table"):
        heads = [th.get_text(" ", strip=True) for th in table.find_all("th")]
        if not heads or not heads[0].startswith("Player"):
            continue
        section = section_of(table)
        index = {head: i for i, head in enumerate(heads)}

        def column(prefix, exclude=None):
            for head, i in index.items():
                if head.startswith(prefix) and not (exclude and exclude in head):
                    return i
            return None

        cap_i, base_i = column("Cap Hit", exclude="Pct"), column("Base Salary")
        pos_i, age_i, type_i = column("Pos"), column("Age"), column("Type")
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            link = tr.find("a", href=re.compile(r"/nba/player/_/id/\d+"))
            if len(cells) < 3 or link is None or cap_i is None or cap_i >= len(cells):
                continue
            cell = lambda i: cells[i].get_text(" ", strip=True) if i is not None and i < len(cells) else None  # noqa: E731
            rows.append({
                "season_end": spot_year + 1, "spot_year": spot_year, "team": team, "section": section,
                "spotrac_id": re.search(r"/id/(\d+)", link["href"]).group(1), "player": link.get_text(" ", strip=True),
                "pos": cell(pos_i), "age": cell(age_i), "type": cell(type_i), "cap_hit": money(cell(cap_i)), "base_salary": money(cell(base_i)),
            })
    return pd.DataFrame(rows, columns=COLUMNS)


def page_is_valid(frame):
    """A real page has a full active roster; anything else (blocked, truncated, wrong season) is retried."""
    return (frame.section == "active").sum() >= 10


class Pacing:
    """Spotrac answers HTTP 403 in bursts when it sees a steady stream. After a block, wait longer before
    retrying the page and keep a slower pace for a while; a run of blocks never gives up quickly."""

    def __init__(self):
        self.slow_left = 0

    def delay(self):
        base = SLOW_AFTER_BLOCK if self.slow_left > 0 else DELAY_SECONDS
        self.slow_left = max(0, self.slow_left - 1)
        return base + random.random()

    def blocked(self):
        self.slow_left = SLOW_PAGES


def fetch_team_year(team, spot_year, session, pacing=None):
    pacing = pacing or Pacing()
    url = f"https://www.spotrac.com/nba/{SLUGS[team]}/payroll/_/year/{spot_year}"
    last_problem, blocks = "no attempt", 0
    while True:
        blocked = False
        try:
            response = session.get(url, headers=HEADERS, timeout=40)
            if response.status_code in (403, 429):
                blocked, last_problem = True, f"HTTP {response.status_code}, {len(response.text)} bytes"
            elif response.status_code == 404:
                return pd.DataFrame(columns=COLUMNS), "failed: HTTP 404 (no such page)"   # retrying cannot help
            elif response.status_code != 200 or len(response.text) < MIN_PAGE_BYTES:
                last_problem = f"HTTP {response.status_code}, {len(response.text)} bytes"
            else:
                frame = parse_payroll_page(response.text, team, spot_year)
                if page_is_valid(frame):
                    return frame, "ok"
                last_problem = "page parsed but has no full active roster"
        except requests.RequestException as error:
            last_problem = type(error).__name__
        if blocked:
            pacing.blocked()
            if blocks >= len(BLOCK_WAITS):
                return pd.DataFrame(columns=COLUMNS), f"failed: {last_problem}"
            print(f"    {team} {spot_year}: blocked ({last_problem}); waiting {BLOCK_WAITS[blocks]}s", flush=True)
            time.sleep(BLOCK_WAITS[blocks])
            blocks += 1
        else:
            time.sleep(5)
            if last_problem.startswith("page parsed") or blocks:
                return pd.DataFrame(columns=COLUMNS), f"failed: {last_problem}"
            blocks += 1   # one plain retry for transient non-block errors


def load_cache(team, spot_year):
    path = os.path.join(CACHE_DIR, f"{team}_{spot_year}.csv")
    return pd.read_csv(path, dtype={"spotrac_id": str}) if os.path.exists(path) else None


def assemble(first_year, last_year, failures=None):
    """Combine every cached team-year in the grid into the output files (a run limited to a few teams must not
    drop the rest). ``failures`` maps (team, year) to the reason a fetch just failed."""
    failures = failures or {}
    frames, manifest = [], []
    for year in range(first_year, last_year + 1):
        for team in SLUGS:
            cached = load_cache(team, year)
            status = "ok" if cached is not None else failures.get((team, year), "missing: not fetched yet")
            manifest.append({"season_end": year + 1, "spot_year": year, "team": team, "status": status,
                             "rows": 0 if cached is None else len(cached),
                             "active_rows": 0 if cached is None else int((cached.section == "active").sum())})
            if cached is not None:
                frames.append(cached)
    history = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)
    return history, pd.DataFrame(manifest)


def run(first_year, last_year, force=False, teams=None):
    os.makedirs(CACHE_DIR, exist_ok=True)
    session, pacing, failures, fetched = requests.Session(), Pacing(), {}, 0
    for year in range(first_year, last_year + 1):
        for team in (teams or SLUGS):
            if not force and load_cache(team, year) is not None:
                continue
            frame, status = fetch_team_year(team, year, session, pacing)
            fetched += 1
            if status == "ok":
                frame.to_csv(os.path.join(CACHE_DIR, f"{team}_{year}.csv"), index=False)
            else:
                failures[(team, year)] = status
            print(f"  {team} {year}-{str(year + 1)[-2:]}: {status} ({len(frame)} rows)", flush=True)
            time.sleep(pacing.delay())
    history, pages = assemble(min(first_year, 2013), max(last_year, last_complete_spot_year()), failures)
    history.to_csv(os.path.join(HERE, "nba_payroll_history.csv"), index=False)
    pages.to_csv(os.path.join(HERE, "nba_payroll_pages.csv"), index=False)
    web_data = os.path.join(HERE, "..", "web_app", "data")
    if os.path.isdir(web_data):
        for name in ("nba_payroll_history.csv", "nba_payroll_pages.csv"):
            shutil.copy(os.path.join(HERE, name), os.path.join(web_data, name))
    failed = pages[pages.status != "ok"]
    print(f"payroll history: {len(history)} rows from {int((pages.status == 'ok').sum())} of {len(pages)} team-years "
          f"({fetched} fetched this run); not loaded: {len(failed)}")
    return history, pages


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="first", type=int, default=2013, help="first spot year (2013 = the 2013-14 season)")
    parser.add_argument("--to", dest="last", type=int, default=None, help="last spot year (default: the last completed season)")
    parser.add_argument("--force", action="store_true", help="re-fetch cached team-years")
    parser.add_argument("--teams", nargs="*", help="limit to these team abbreviations (testing)")
    args = parser.parse_args()
    last = args.last if args.last is not None else last_complete_spot_year()
    _, pages = run(args.first, last, args.force, args.teams)
    if (pages.status != "ok").any():
        print("Some team-years failed; re-run to retry them (cached ones are skipped).", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
