"""Current-season LEBRON from the public LEBRON Ratings table on bball-index.com/nba.

Why: BBall Index moved to a new site (Nov 2026). Its NBA numbers come from the new site's own backend; R2
(r2-bbi.fanspo.com, read by update_lebron2.py) stopped at 2025-26. So this renders the public table in a
headless browser, like a visitor, and reads what it shows. No login, no API calls, one page load a day.

Writes, only if every check passes:
  bbi_lebron/lebron_<year>.csv  every column the table shows (ranks, percentiles, roles, BBI's player code)
  lebron.csv                    replaces this season's rows, same 16 columns as before (script.sh copies it on)

Run from site_data:  python bbi_lebron_scrape.py [--season 2026-27] [--dry-run]
Season defaults to NBA_SEASON from ~/basketball/season.sh (exported by all_scrapes.sh).
"""
import argparse
import asyncio
import datetime as dt
import os
import re
import sys
import unicodedata

import pandas as pd
from playwright.async_api import async_playwright

URL = "https://www.bball-index.com/nba"
HISTORY = "lebron.csv"
INDEX = "index_master.csv"     # name/team -> nba_id, bref_id (has the current season)
# nba_id -> Pos (BRef positions, this season's rows), best first: site_data's own (bio.py, written minutes
# before this in script.sh), then player_sheets' copy (yesterday's run).
POS_SOURCES = ["modern_index.csv", "../player_sheets/gen_totals/modern_index.csv"]
# Last resort for a player the indexes miss (check basketball-reference.com by hand): nba_id -> (bref_id, Pos).
# Empty since index_gen.py matches names without accents/suffixes (2026-11-20; Marković was the case).
MANUAL = {}
TOTALS = "../player_sheets/year_totals/{year}.csv"  # NBA names + PLAYER_ID, the main ID match
OUT_DIR = "bbi_lebron"
MIN_SHARE = 0.8   # BBI lists ~every player who has played (473 of 473 on 2026-11-20); accept 80% of the NBA's count
MIN_ROWS = 100    # floor when the NBA totals aren't available
MAX_UNMATCHED = 10
SEASON_RE = r"^\d{4}-\d{2}$"
TARGET_COLUMNS = ['Season', 'Player', 'team', 'Minutes', 'Pos', 'Offensive Archetype', 'WAR', 'LEBRON',
                  'O-LEBRON', 'D-LEBRON', 'year', 'Defensive Role', 'NBA ID', 'bref_id', 'Games', 'Age']

ROWS_JS = """() => {
  const ths = [...document.querySelectorAll('thead tr:last-child th')].map(th => th.innerText.replace(/[▲▼]/g,'').trim());
  const rows = [...document.querySelectorAll('tbody tr')].map(tr => {
    const a = tr.querySelector('a[href*="/nba/player/"]'); const img = tr.querySelector('img');
    return {href: a && a.getAttribute('href'), team: img && img.alt, cells: [...tr.querySelectorAll('td')].map(td => td.innerText.trim())};
  });
  return {ths, rows};
}"""
SCROLLER_JS = """() => { let e = document.querySelector('table');
  while (e && !(e.scrollHeight > e.clientHeight + 5 && /auto|scroll/.test(getComputedStyle(e).overflowY))) e = e.parentElement;
  return e || document.scrollingElement; }"""


def default_season():
    s = os.environ.get("NBA_SEASON")
    if s:
        return s
    today = dt.date.today()
    end = today.year + 1 if today.month >= 10 else today.year
    return f"{end - 1}-{str(end)[-2:]}"


async def scrape(season):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 1200})
        await page.goto(URL, wait_until="networkidle", timeout=90000)
        await page.wait_for_selector("tbody tr", timeout=60000)

        # The season menu is the <select> whose options look like "2026-27".
        selects = page.locator("select")
        picker = None
        for i in range(await selects.count()):
            opts = await selects.nth(i).evaluate("s => [...s.options].map(o => o.value)")
            if opts and all(re.match(SEASON_RE, o) for o in opts):
                picker, seasons = selects.nth(i), opts
                break
        if picker is None:
            raise SystemExit("No season menu found on the page (layout changed?); nothing written.")
        if season not in seasons:
            raise SystemExit(f"BBI doesn't list {season} yet (newest: {seasons[0]}); nothing written.")
        shown = await picker.input_value()
        if shown != season:
            await picker.select_option(season)
            await page.wait_for_timeout(2500)
            shown = await picker.input_value()
        if shown != season:
            raise SystemExit(f"Page shows season {shown!r}, wanted {season!r}; nothing written.")

        # The page opens filtered to four rotation roles; clear it so every rated player is listed.
        clear = page.locator('button[aria-label="Clear Rotation Role"]')
        if await clear.count():
            await clear.first.click()
            await page.wait_for_timeout(1500)

        # The table only keeps ~50 rows in the page, so scroll through it and collect by player link.
        scroller = await page.evaluate_handle(SCROLLER_JS)
        seen, headers = {}, None
        for _ in range(1000):
            got = await page.evaluate(ROWS_JS)
            headers = headers or got["ths"]
            for r in got["rows"]:
                if r["href"]:
                    seen[r["href"]] = r
            at_end = await scroller.evaluate(
                "e => { const b = e.scrollTop; e.scrollTop += e.clientHeight * 0.7; return e.scrollTop === b; }")
            await page.wait_for_timeout(150)
            if at_end:
                break
        got = await page.evaluate(ROWS_JS)
        for r in got["rows"]:
            if r["href"]:
                seen[r["href"]] = r
        await browser.close()
        return headers, list(seen.values())


def num(s):
    s = (s or "").replace("+", "").replace("−", "-").replace("%", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def split_metric(cell):
    """'+9.19\\n#1 · 100%' -> (9.19, 1, 100); '483\\n94%' -> (483, None, 94)."""
    lines = [x.strip() for x in cell.split("\n") if x.strip()]
    value = num(lines[0]) if lines else None
    rank = pct = None
    if len(lines) > 1:
        m = re.match(r"#(\d+)\s*·\s*([\d.]+)%", lines[1])
        if m:
            rank, pct = int(m.group(1)), float(m.group(2))
        else:
            pct = num(lines[1])
    return value, rank, pct


def parse(headers, rows, season):
    out = []
    for r in rows:
        cells = r["cells"]
        h = headers[-len(cells):]  # last header row lines up with the cells
        c = dict(zip(h, cells))
        who = [x.strip() for x in c.get("PLAYER", "").split("\n") if x.strip()]
        roles = who[2].split("•") if len(who) > 2 else []
        rec = {
            "Season": season, "bbi_id": r["href"].rsplit("/", 1)[-1], "Player": who[0] if who else None,
            "team": r["team"], "adv_position": who[1] if len(who) > 1 else None,
            "offensive_role": roles[0].strip() if roles else None,
            "defensive_role": roles[1].strip() if len(roles) > 1 else None,
            "age": num(c.get("AGE")), "exp": num(c.get("EXP")), "rotation": c.get("ROTATION"),
            "gp": num(c.get("GP")),
        }
        for col, key in [("MIN", "min"), ("MPG", "mpg")]:
            rec[key], _, rec[f"{key}_pct"] = split_metric(c.get(col, ""))
        for col, key in [("LEBRON", "lebron"), ("O-LEBRON", "o_lebron"), ("D-LEBRON", "d_lebron"), ("WAR", "war")]:
            rec[key], rec[f"{key}_rank"], rec[f"{key}_pct"] = split_metric(c.get(col, ""))
        out.append(rec)
    return pd.DataFrame(out)


def norm(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = s.replace(".", "")
    s = re.sub(r"['’,-]", " ", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", " ", s)
    return " ".join(s.split())


def id_sources(year):
    """(name key, team, nba_id) tables, best first: the NBA's own names (player_sheets season totals,
    which BBI's spellings follow), then index_master (BRef names) for anyone the totals don't have yet."""
    out = []
    if os.path.exists(TOTALS.format(year=year)):
        t = pd.read_csv(TOTALS.format(year=year), usecols=["PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION"])
        out.append(pd.DataFrame({"key": t["PLAYER_NAME"].map(norm), "team": t["TEAM_ABBREVIATION"], "nba_id": t["PLAYER_ID"]}))
    i = pd.read_csv(INDEX)
    i = i[i["year"] == year]
    out.append(pd.DataFrame({"key": i["player"].map(norm), "team": i["team"], "nba_id": i["nba_id"]}))
    return out


def add_ids(df, year):
    df["key"] = df["Player"].map(norm)
    df["nba_id"] = None
    for src in id_sources(year):
        by_team = src.drop_duplicates(["key", "team"]).set_index(["key", "team"])["nba_id"]
        names = src.drop_duplicates(["key", "nba_id"])
        by_name = names[~names["key"].duplicated(keep=False)].set_index("key")["nba_id"]  # unambiguous names only
        todo = df["nba_id"].isna()
        pairs = list(zip(df.loc[todo, "key"], df.loc[todo, "team"]))
        df.loc[todo, "nba_id"] = [by_team.get(p, by_name.get(p[0])) for p in pairs]
    df["nba_id"] = pd.to_numeric(df["nba_id"]).astype("Int64")
    bref = pd.read_csv(INDEX).dropna(subset=["nba_id"]).drop_duplicates("nba_id", keep="last")
    df["bref_id"] = df["nba_id"].map(dict(zip(bref["nba_id"].astype(int), bref["bref_id"])))
    df["bref_id"] = df["bref_id"].fillna(df["nba_id"].map({k: v[0] for k, v in MANUAL.items()}))

    pos = {k: v[1] for k, v in MANUAL.items()}
    for path in reversed(POS_SOURCES):  # earlier sources overwrite later ones
        if os.path.exists(path):
            m = pd.read_csv(path).dropna(subset=["nba_id", "Pos"])
            m = m[m["year"] == year]
            pos.update(zip(m["nba_id"].astype(int), m["Pos"]))
    df["Pos"] = df["nba_id"].map(pos)
    return df.drop(columns="key")


def to_history(df, season, year):
    h = pd.DataFrame({
        "Season": season, "Player": df["Player"].str.lower(), "team": df["team"], "Minutes": df["min"],
        "Pos": df["Pos"],"Offensive Archetype": df["offensive_role"], "WAR": df["war"],
        "LEBRON": df["lebron"], "O-LEBRON": df["o_lebron"], "D-LEBRON": df["d_lebron"], "year": year,
        "Defensive Role": df["defensive_role"], "NBA ID": df["nba_id"], "bref_id": df["bref_id"],
        "Games": df["gp"], "Age": df["age"],
    })
    return h[TARGET_COLUMNS]


def check(df, season):
    problems = []
    # Expect about as many players as the NBA's season totals list (early season is small, so no fixed number).
    need = MIN_ROWS
    totals = TOTALS.format(year=int(season[:4]) + 1)
    if os.path.exists(totals):
        need = max(MIN_ROWS, int(MIN_SHARE * len(pd.read_csv(totals, usecols=["PLAYER_ID"]))))
    if len(df) < need:
        problems.append(f"only {len(df)} players (expected at least {need})")
    if df["lebron"].isna().any() or (df["lebron"].abs() < 1e-9).all():
        problems.append("LEBRON missing or all zero")
    if df["bbi_id"].duplicated().any():
        problems.append("duplicate players")
    unmatched = df[df["nba_id"].isna()]
    if len(unmatched) > MAX_UNMATCHED:
        problems.append(f"{len(unmatched)} players without an NBA ID (max {MAX_UNMATCHED})")
    if df["nba_id"].dropna().duplicated().any():
        problems.append("two players matched the same NBA ID")
    if os.path.exists(HISTORY):
        old = pd.read_csv(HISTORY)
        n_old = (old["Season"] == season).sum()
        if n_old and len(df) < n_old * 0.95:
            problems.append(f"{len(df)} players, fewer than the {n_old} already saved for {season}")
    return problems, unmatched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default=default_season(), help="e.g. 2026-27")
    ap.add_argument("--dry-run", action="store_true", help="scrape and check, write nothing")
    a = ap.parse_args()
    season = a.season
    year = int(season[:4]) + 1

    headers, rows = asyncio.run(scrape(season))
    df = add_ids(parse(headers, rows, season), year)
    problems, unmatched = check(df, season)
    print(f"{season}: {len(df)} players scraped, {df['nba_id'].notna().sum()} with NBA IDs")
    if len(unmatched):
        print("No NBA ID (left blank):", "; ".join(f"{p} ({t})" for p, t in zip(unmatched["Player"], unmatched["team"])))
    if problems:
        print("NOT WRITTEN:", "; ".join(problems))
        sys.exit(1)
    if a.dry_run:
        print(df.sort_values("lebron", ascending=False).head(5).to_string(index=False))
        return

    df.insert(0, "scraped_at", dt.datetime.now().isoformat(timespec="seconds"))
    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(f"{OUT_DIR}/lebron_{year}.csv", index=False)

    hist = to_history(df, season, year)
    if os.path.exists(HISTORY):
        old = pd.read_csv(HISTORY)
        replaced = (old["Season"] == season).sum()
        hist = pd.concat([old[old["Season"] != season], hist], ignore_index=True)
        print(f"{HISTORY}: replaced {replaced} rows for {season} with {len(df)}")
    hist.to_csv(HISTORY, index=False)


if __name__ == "__main__":
    main()
