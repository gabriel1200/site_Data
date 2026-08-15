"""
Spotrac NBA contract scraper — requests edition (no Selenium / Chrome).

Drop-in replacement for selenium_scrape2.py. The Selenium version only ever
used the browser to (a) GET the team page and (b) wait for a <table> to exist,
then read element.outerHTML. But Spotrac renders the salary tables server-side:
the real data lives in `data-sort` attributes and `pill-*` CSS classes that are
present in the raw HTML. So a plain HTTP GET returns the same markup the parser
needs — no headless browser required.

All parsing/processing logic (option pills, data-sort salaries, cap holds,
dead money, summary, post-processing) is preserved verbatim from the original.
Only the fetch layer changed.

If Spotrac starts returning 403 / a Cloudflare challenge (the page won't contain
'dataTable-active'), flip USE_CLOUDSCRAPER = True below, or swap in curl_cffi
(impersonate='chrome120') the same way you do for the WNBA feed. The parser is
agnostic to which client delivered the HTML.
"""
import pandas as pd
import numpy as np
import time
import re
import sys
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
import requests

# ---------------------------------------------------------------------------
# Fetch-layer configuration
# ---------------------------------------------------------------------------
USE_CLOUDSCRAPER = False   # set True if you hit Cloudflare; needs `pip install cloudscraper`

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def make_session() -> requests.Session:
    """Build a requests Session (or cloudscraper) with browser-like headers."""
    if USE_CLOUDSCRAPER:
        import cloudscraper
        sess = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    else:
        sess = requests.Session()
    sess.headers.update(DEFAULT_HEADERS)
    return sess


def fetch_html(session: requests.Session, url: str, timeout: int = 20,
               retries: int = 3, backoff: float = 2.0) -> Optional[str]:
    """GET a URL with retries. Returns HTML text, or None on persistent failure."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout)
            if resp.status_code == 200:
                # sanity-check that we got the real page, not a challenge/placeholder
                if "dataTable-" in resp.text or "<table" in resp.text:
                    return resp.text
                print(f"  [warn] 200 but no tables in body (len={len(resp.text)}); "
                      f"possible JS-gate/Cloudflare. Consider USE_CLOUDSCRAPER=True.")
                return resp.text  # still return; parser will no-op if truly empty
            print(f"  [warn] {url} -> HTTP {resp.status_code} (attempt {attempt}/{retries})")
        except requests.RequestException as e:
            print(f"  [warn] {url} -> {type(e).__name__}: {e} (attempt {attempt}/{retries})")
        if attempt < retries:
            time.sleep(backoff * attempt)
    print(f"  [error] giving up on {url}")
    return None


# ---------------------------------------------------------------------------
# Constants (unchanged)
# ---------------------------------------------------------------------------
NBA_TEAM_URLS = {
    "ATL": "https://www.spotrac.com/nba/atlanta-hawks/yearly",
    "BOS": "https://www.spotrac.com/nba/boston-celtics/yearly",
    "BKN": "https://www.spotrac.com/nba/brooklyn-nets/yearly",
    "CHA": "https://www.spotrac.com/nba/charlotte-hornets/yearly",
    "CHI": "https://www.spotrac.com/nba/chicago-bulls/yearly",
    "CLE": "https://www.spotrac.com/nba/cleveland-cavaliers/yearly",
    "DAL": "https://www.spotrac.com/nba/dallas-mavericks/yearly",
    "DEN": "https://www.spotrac.com/nba/denver-nuggets/yearly",
    "DET": "https://www.spotrac.com/nba/detroit-pistons/yearly",
    "GSW": "https://www.spotrac.com/nba/golden-state-warriors/yearly",
    "HOU": "https://www.spotrac.com/nba/houston-rockets/yearly",
    "IND": "https://www.spotrac.com/nba/indiana-pacers/yearly",
    "LAC": "https://www.spotrac.com/nba/la-clippers/yearly",
    "LAL": "https://www.spotrac.com/nba/los-angeles-lakers/yearly",
    "MEM": "https://www.spotrac.com/nba/memphis-grizzlies/yearly",
    "MIA": "https://www.spotrac.com/nba/miami-heat/yearly",
    "MIL": "https://www.spotrac.com/nba/milwaukee-bucks/yearly",
    "MIN": "https://www.spotrac.com/nba/minnesota-timberwolves/yearly",
    "NOP": "https://www.spotrac.com/nba/new-orleans-pelicans/yearly",
    "NYK": "https://www.spotrac.com/nba/new-york-knicks/yearly",
    "OKC": "https://www.spotrac.com/nba/oklahoma-city-thunder/yearly",
    "ORL": "https://www.spotrac.com/nba/orlando-magic/yearly",
    "PHI": "https://www.spotrac.com/nba/philadelphia-76ers/yearly",
    "PHX": "https://www.spotrac.com/nba/phoenix-suns/yearly",
    "POR": "https://www.spotrac.com/nba/portland-trail-blazers/yearly",
    "SAC": "https://www.spotrac.com/nba/sacramento-kings/yearly",
    "SAS": "https://www.spotrac.com/nba/san-antonio-spurs/yearly",
    "TOR": "https://www.spotrac.com/nba/toronto-raptors/yearly",
    "UTA": "https://www.spotrac.com/nba/utah-jazz/yearly",
    "WAS": "https://www.spotrac.com/nba/washington-wizards/yearly",
}

DATATABLE_CONTAINERS = {
    "salary": "dataTable-active",
    "options": "dataTable-active",
    "dead_money": "dataTable-dead",
    "cap_holds": "dataTable-cap-hold",
    "summary": "dataTable-summary",
}

SEASONS = ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30"]
EXTRA_SEASONS = ["2030-31"]


# ---------------------------------------------------------------------------
# NEW fetch/parse layer: pull tables out of static HTML instead of the DOM
# ---------------------------------------------------------------------------
def get_table_and_html_by_id(page_html: str, table_id: str
                             ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Find a table by id in already-fetched HTML; return (DataFrame, outerHTML).

    Mirrors the Selenium function's contract exactly, so all downstream
    processing functions work without modification.
    """
    if not page_html:
        return None, None
    soup = BeautifulSoup(page_html, "lxml")
    el = soup.find(id=table_id)
    if el is None:
        return None, None

    # Spotrac renders a hidden <span class="d-none">Porter Jr.</span> next to the
    # visible anchor inside the fixed player cell. read_html concatenates both,
    # producing a doubled name ("Porter Jr. Michael Porter Jr.") that then gets
    # mangled by clean_player_name. Remove those hidden spans from a COPY of the
    # element so the parsed name is clean. The original page HTML (used to build
    # the id map) is untouched.
    from copy import copy as _shallow  # noqa
    el_clean = BeautifulSoup(str(el), "lxml").find(id=table_id) or \
        BeautifulSoup(str(el), "lxml")
    for hidden in el_clean.select("span.d-none"):
        hidden.decompose()

    table_html = str(el_clean)
    try:
        from io import StringIO
        df = pd.read_html(StringIO(table_html), header=0)[0]
    except (ValueError, IndexError):
        # the element exists but isn't itself a <table> (e.g. a wrapping div);
        # try the first descendant table
        inner = el_clean.find("table") if hasattr(el_clean, "find") else None
        if inner is None:
            return None, table_html
        table_html = str(inner)
        try:
            from io import StringIO
            df = pd.read_html(StringIO(table_html), header=0)[0]
        except (ValueError, IndexError):
            return None, table_html
    return df, table_html


def get_team_data(session: requests.Session, url: str
                  ) -> Dict[str, Tuple[pd.DataFrame, str]]:
    """Fetch a team page once, then extract every table id from that one HTML."""
    page_html = fetch_html(session, url)
    if not page_html:
        return {}

    # page-level name->spotrac_id map, built once, robust to per-table quirks
    id_map = _build_id_map_from_page(page_html)
    print(f"  built id map: {len(id_map)} name keys")

    tables_data: Dict[str, Tuple[pd.DataFrame, str]] = {}
    for table_type, table_id in DATATABLE_CONTAINERS.items():
        df, html = get_table_and_html_by_id(page_html, table_id)
        if df is not None:
            tables_data[table_type] = (df, html)
            print(f"  fetched {table_type} table ({len(df)} rows)")
        else:
            print(f"  table '{table_type}' (id={table_id}) not found")
    tables_data["_id_map"] = id_map  # threaded through to processors
    return tables_data


# ---------------------------------------------------------------------------
# Everything below is UNCHANGED from selenium_scrape2.py
# (clean_player_name, _parse_table_html_for_salaries, get_available_seasons,
#  process_salary_data, extract_option_from_html_cell, process_options_data,
#  process_cap_holds, process_dead_money, process_summary)
# ---------------------------------------------------------------------------
def clean_player_name(name: str) -> str:
    """Clean player name by removing duplicates, suffixes, and extra text."""
    if pd.isna(name):
        return ""
    name_str = str(name).strip()
    name_str = re.sub(r"\s*\(.*?\)", "", name_str)
    suffixes = ["Jr", "Jr.", "Sr", "Sr.", "II", "III", "IV", "V"]
    suffix_pattern = r"\b(?:" + "|".join(re.escape(s) for s in suffixes) + r")\b"
    name_str = re.sub(r"\s*" + suffix_pattern, "", name_str, flags=re.IGNORECASE).strip()
    # a stripped 'Jr.' can leave a dangling '.'; remove trailing punctuation
    name_str = re.sub(r"[.\s]+$", "", name_str).strip()
    name_str = re.sub(r"\s+", " ", name_str).strip()
    parts = name_str.split()
    unique_parts = list(dict.fromkeys(parts))
    # NOTE: previously this swapped two-token names (return "{1} {0}") to correct
    # for read_html doubling the name via the hidden <span class="d-none"> that
    # rendered surname-first. Now that get_table_and_html_by_id strips those
    # d-none spans before parsing, the input already reads "First Last" in the
    # correct order, so the swap would reverse a correct name. Keep natural order.
    return " ".join(unique_parts)


def _build_id_map_from_page(page_html: str) -> Dict[str, str]:
    """Scan the WHOLE page once and map player-name -> spotrac_id.

    Spotrac player cells carry both a `data-export="Michael Porter Jr."` attr and
    an anchor `/nba/player/_/id/26980/...`. We pair them wherever they co-occur in a
    cell (or its row). Scanning the full page (not a single tbody) makes this
    robust to DataTables FixedColumns cloning and to read_html row-count
    mismatches, since we later look ids up by name rather than by row position.
    Keys are stored both raw and cleaned for flexible lookup.
    """
    id_map: Dict[str, str] = {}
    if not page_html:
        return id_map
    soup = BeautifulSoup(page_html, "lxml")
    for a in soup.find_all("a", href=True):
        m = re.search(r"/player/_/?id/(\d+)", a["href"])
        if not m:
            continue
        sid = m.group(1)
        # name candidates: the cell's data-export, then the anchor text
        cell = a.find_parent(["td", "th"])
        raw_names = []
        if cell and cell.has_attr("data-export"):
            raw_names.append(cell["data-export"])
        anchor_text = a.get_text(strip=True)
        if anchor_text:
            raw_names.append(anchor_text)
        for nm in raw_names:
            id_map.setdefault(nm, sid)
            id_map.setdefault(clean_player_name(nm), sid)
    return id_map


def _extract_spotrac_ids(html: str, n_rows: int) -> List[Optional[str]]:
    """Pull the Spotrac player id from each body row, in table order.

    Each player cell contains an anchor like
    '/nba/player/_/id/26980/michael-porter-jr'; we grab the digits after 'id/'.
    Returns a list aligned to the DataFrame's rows (None where no link exists,
    e.g. 'Incomplete Roster Charge' rows). Falls back gracefully if the table
    has no tbody.
    """
    ids, _ = _extract_spotrac_ids_and_names(html, n_rows)
    return ids


def _extract_spotrac_ids_and_names(html: str, n_rows: int
                                   ) -> Tuple[List[Optional[str]], List[Optional[str]]]:
    """Extract (id, clean_anchor_name) per body row, in table order.

    The anchor text (e.g. 'Michael Porter Jr.') is the clean canonical name,
    free of the hidden <span class="d-none"> duplicate text that otherwise
    corrupts pd.read_html's cell value. Returns None entries for rows without
    a player link (e.g. roster-charge rows).
    """
    ids: List[Optional[str]] = []
    names: List[Optional[str]] = []
    if not html:
        return [None] * n_rows, [None] * n_rows
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("tbody")
    rows = body.find_all("tr") if body else []
    id_re = re.compile(r"/player/_/?id/(\d+)")
    for row in rows:
        found_id, found_name = None, None
        for a in row.find_all("a", href=True):
            m = id_re.search(a["href"])
            if m:
                found_id = m.group(1)
                found_name = a.get_text(strip=True) or None
                break
        ids.append(found_id)
        names.append(found_name)
    pad = lambda lst: (lst + [None] * (n_rows - len(lst)))[:n_rows]
    return pad(ids), pad(names)


def _attach_spotrac_id(df: pd.DataFrame, html: str,
                       use_anchor_name: bool = False,
                       id_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Insert 'spotrac_id' after 'Player', aligned by row order.

    Two matching strategies, in order of reliability:
      1. id_map (name -> id, built from the whole page): looked up by the row's
         Player value. Immune to row-count mismatches and column cloning.
      2. positional tbody scan (fallback) when no id_map is supplied.

    When use_anchor_name is True, also replaces the Player value with the clean
    anchor text where a link was present. Defaults False so the id column is
    purely additive.
    """
    if df.empty:
        return df

    if id_map:
        ids = []
        for nm in df["Player"] if "Player" in df.columns else [None] * len(df):
            sid = None
            if isinstance(nm, str):
                sid = id_map.get(nm) or id_map.get(clean_player_name(nm))
            ids.append(sid)
    else:
        ids, names = _extract_spotrac_ids_and_names(html, len(df))
        if use_anchor_name and "Player" in df.columns:
            cleaned = [clean_player_name(nm) if nm else None for nm in names]
            df = df.reset_index(drop=True)
            for i, nm in enumerate(cleaned):
                if nm:
                    df.at[i, "Player"] = nm

    if "spotrac_id" in df.columns:
        df = df.drop(columns=["spotrac_id"])
    insert_at = df.columns.get_loc("Player") + 1 if "Player" in df.columns else len(df.columns)
    df.insert(insert_at, "spotrac_id", ids)
    return df


def _parse_table_html_for_salaries(df: pd.DataFrame, html: str,
                                   value_cols: List[str]) -> pd.DataFrame:
    """Parses table HTML to extract salary data from 'data-sort' attributes."""
    if not html or df.empty:
        return df

    soup = BeautifulSoup(html, "html.parser")
    header = soup.find("thead")
    if not header:
        print("Warning: HTML table header not found. Cannot perform precise salary extraction.")
        return df

    header_cells = [th.get_text(strip=True) for th in header.find_all("th")]
    col_indices = {col: header_cells.index(col) for col in value_cols if col in header_cells}

    body = soup.find("tbody")
    if not body:
        print("Warning: HTML table body not found.")
        return df

    html_rows = body.find_all("tr")
    if len(df) != len(html_rows):
        print(f"Warning: Mismatch between DataFrame rows ({len(df)}) and HTML rows ({len(html_rows)}).")

    min_rows = min(len(df), len(html_rows))
    # newer pandas infers string dtype from the rendered cell text and then
    # rejects float assignment; coerce the columns we're about to fill.
    for col_name in col_indices:
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(object)
    for idx in range(min_rows):
        html_cells = html_rows[idx].find_all(["td", "th"])
        for col_name, col_idx in col_indices.items():
            if col_idx < len(html_cells):
                cell = html_cells[col_idx]
                salary = 0.0
                if _is_free_agent_cell(cell):
                    # Pending-free-agent cells ("UFA / $65.7M", "RFA / $17.0M")
                    # have no real contracted salary. Spotrac still stamps a
                    # data-sort attribute on them (small integers like 4/5,
                    # presumably a sort-priority code for the table's JS sort,
                    # NOT a dollar value) — trusting it produces phantom
                    # salaries of $4 / $5. Treat these as 0 unconditionally.
                    salary = 0.0
                elif cell.has_attr("data-sort"):
                    try:
                        val = float(cell["data-sort"])
                        salary = val if val > 0 else 0.0
                    except (ValueError, TypeError):
                        pass
                df.loc[idx, col_name] = salary
    return df


def _is_free_agent_cell(cell) -> bool:
    """True if a salary-table cell is a UFA/RFA placeholder, not a real dollar cell.

    Mirrors the pill-class detection already used for the options table in
    extract_option_from_html_cell, plus a plain-text fallback in case the
    markup for this table doesn't use the same pill-* classes.
    """
    pill_elements = cell.find_all(class_=lambda x: x and ("pill-" in x))
    for pill in pill_elements:
        class_str = " ".join(pill.get("class", []))
        if "pill-ufa" in class_str or "pill-rfa" in class_str:
            return True
    text_content = cell.get_text(strip=True).upper()
    return "UFA" in text_content or "RFA" in text_content


def get_available_seasons(salary_df: pd.DataFrame) -> List[str]:
    """Get list of available seasons from salary data."""
    return [col for col in salary_df.columns if re.match(r"\d{4}-\d{2}", str(col))]


def process_salary_data(df_and_html: Tuple[pd.DataFrame, str], team: str,
                        id_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Process and clean salary data using 'data-sort' attributes from HTML."""
    if not df_and_html:
        return pd.DataFrame()
    df, html = df_and_html
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(" ".join).str.replace(r" Unnamed: \d+_level_\d", "", regex=True).str.strip()
        # these two fix-ups only make sense for the 2-row Spotrac header;
        # guarded so a flat single-row header doesn't raise.
        if "Player" in df.columns.get_level_values(0):
            df.columns = df.columns.droplevel(1)
        if len(df.columns) > 1 and "Player" in str(df.columns[0]) and "Unnamed" in str(df.columns[1]):
            df[df.columns[0]] = df[df.columns[1]]
            df = df.drop(columns=df.columns[1])

    df.rename(columns={df.columns[0]: "Player"}, inplace=True)
    if "Player" in df.columns:
        df["Player"] = df["Player"].apply(clean_player_name)

    df = _attach_spotrac_id(df, html, id_map=id_map)
    seasons = [col for col in df.columns if re.match(r"\d{4}-\d{2}", str(col))]
    df = _parse_table_html_for_salaries(df, html, seasons)
    df["Team"] = team
    return df


def extract_option_from_html_cell(soup_cell) -> str:
    pill_elements = soup_cell.find_all(class_=lambda x: x and ("pill-" in x))

    for pill in pill_elements:
        classes = pill.get("class", [])
        class_str = " ".join(classes)
        if "pill-club" in class_str:
            return "T"
        elif "pill-player" in class_str:
            return "P"
        elif "pill-early" in class_str:
            return "ETO"
        elif "pill-rfa" in class_str:
            return "RFA"
        elif "pill-ufa" in class_str:
            return "UFA"
        elif "pill-extension" in class_str or "pill-eligible" in class_str:
            return "EE"
        elif "pill-guaranteed" in class_str:
            return "G"
        elif "pill-non-guaranteed" in class_str:
            return "NG"

    text_content = soup_cell.get_text(strip=True).upper()
    if "PLAYER" in text_content: return "P"
    if "CLUB" in text_content or "TEAM" in text_content: return "T"
    if "EARLY" in text_content and "TERM" in text_content: return "ETO"
    if "RFA" in text_content: return "RFA"
    if "UFA" in text_content: return "UFA"
    if "GUARANTEED" in text_content: return "G"
    if "NON-GUARANTEED" in text_content: return "NG"
    return "0"


def process_options_data(df_and_html: Tuple[pd.DataFrame, str],
                         salary_df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Process and clean options data by extracting option types from HTML classes."""
    if df_and_html is None:
        return pd.DataFrame(columns=["Player", "Team"] + get_available_seasons(salary_df))
    df, html = df_and_html
    if df is None or df.empty:
        return pd.DataFrame(columns=["Player", "Team"] + get_available_seasons(salary_df))

    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(" ".join).str.replace(r" Unnamed: \d+_level_\d", "", regex=True).str.strip()
    df.rename(columns={df.columns[0]: "Player"}, inplace=True, errors="ignore")
    if "Player" in df.columns:
        df["Player"] = df["Player"].apply(clean_player_name)
    else:
        return pd.DataFrame()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return pd.DataFrame()

    seasons = [col for col in df.columns if re.match(r"\d{4}-\d{2}", str(col))]
    if not seasons:
        return pd.DataFrame()

    options_data = pd.DataFrame()
    options_data["Player"] = df["Player"]
    rows = table.find_all("tr")[1:]
    header_row = table.find("tr")
    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    season_indices = {season: headers.index(season) for season in seasons if season in headers}

    for row_idx, row in enumerate(rows):
        if row_idx >= len(df): break
        cells = row.find_all(["td", "th"])
        for season in seasons:
            if season in season_indices:
                col_idx = season_indices[season]
                if col_idx < len(cells):
                    option_type = extract_option_from_html_cell(cells[col_idx])
                    if season not in options_data.columns:
                        options_data[season] = "0"
                    options_data.loc[row_idx, season] = option_type

    options_data["Team"] = team
    # carry spotrac_id from salary_df (same dataTable-active source table)
    id_cols = ["Player", "Team"] + (["spotrac_id"] if "spotrac_id" in salary_df.columns else [])
    final_options_df = salary_df[id_cols].drop_duplicates().merge(
        options_data, on=["Player", "Team"], how="left"
    )
    all_seasons = get_available_seasons(salary_df)
    for season in all_seasons:
        if season not in final_options_df.columns:
            final_options_df[season] = "0"
        else:
            final_options_df[season] = final_options_df[season].fillna("0")

    keep = ["Player"] + (["spotrac_id"] if "spotrac_id" in final_options_df.columns else []) + ["Team"] + all_seasons
    final_options_df = final_options_df[keep].drop_duplicates(
        subset=["Player", "Team"]).reset_index(drop=True)
    return final_options_df


def process_cap_holds(df_and_html: Tuple[pd.DataFrame, str], team: str,
                      id_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Process cap holds table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    df.columns = ["Player" if "player" in str(col).lower() else col for col in df.columns]
    if "Player" in df.columns:
        df["Player"] = df["Player"].apply(clean_player_name)
        df = _attach_spotrac_id(df, html, id_map=id_map)
        value_cols = [col for col in df.columns if col not in ["Player", "Team", "spotrac_id"]]
        df = _parse_table_html_for_salaries(df, html, value_cols)
    df["Team"] = team
    return df


def process_dead_money(df_and_html: Tuple[pd.DataFrame, str], team: str,
                       id_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Process dead money table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    df.columns = ["Player" if "player" in str(col).lower() else col for col in df.columns]
    if "Player" in df.columns:
        df["Player"] = df["Player"].apply(clean_player_name)
        df = _attach_spotrac_id(df, html, id_map=id_map)
        value_cols = [col for col in df.columns if col not in ["Player", "Team", "spotrac_id"]]
        df = _parse_table_html_for_salaries(df, html, value_cols)
    df["Team"] = team
    return df


def process_summary(df_and_html: Tuple[pd.DataFrame, str], team: str) -> pd.DataFrame:
    """Process summary table."""
    if not df_and_html: return pd.DataFrame()
    df, html = df_and_html
    if df.empty: return pd.DataFrame()
    df = df.copy()
    value_cols = list(df.columns)
    df = _parse_table_html_for_salaries(df, html, value_cols)
    df["Team"] = team
    return df


# ---------------------------------------------------------------------------
# Orchestration (session replaces driver; everything else unchanged)
# ---------------------------------------------------------------------------
def team_books(session: requests.Session, team: str
               ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get salary, options, cap holds, dead money, and summary data for a team."""
    print(f"\n{'='*50}\nProcessing {team}...\n{'='*50}")
    url = NBA_TEAM_URLS.get(team.upper())
    if not url:
        raise ValueError(f"Invalid team code: {team}")

    tables_data = get_team_data(session, url)
    if not tables_data:
        print(f"No tables found for {team}")
        return (pd.DataFrame(),) * 5

    salary_data = tables_data.get("salary")
    if not salary_data or salary_data[0].empty:
        print(f"Required salary table not found for {team}")
        return (pd.DataFrame(),) * 5

    id_map = tables_data.get("_id_map") or {}
    salary_df = process_salary_data(salary_data, team, id_map=id_map)
    options_df = process_options_data(tables_data.get("options"), salary_df, team)
    cap_holds_df = process_cap_holds(tables_data.get("cap_holds"), team, id_map=id_map)
    dead_money_df = process_dead_money(tables_data.get("dead_money"), team, id_map=id_map)
    summary_df = process_summary(tables_data.get("summary"), team)

    for df in [cap_holds_df, dead_money_df, summary_df]:
        if not df.empty and "Team" not in df.columns:
            df["Team"] = team

    print(f"Completed {team}: Salary({len(salary_df)}), Options({len(options_df)}), "
          f"Cap Holds({len(cap_holds_df)}), Dead Money({len(dead_money_df)}), Summary({len(summary_df)})")
    return salary_df, options_df, cap_holds_df, dead_money_df, summary_df


def scrape_all_teams(teams: List[str], delay: float = 3.0
                     ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Scrape data for all teams with rate limiting, using a requests Session."""
    all_dfs = {"salary": [], "options": [], "cap_holds": [], "dead_money": [], "summary": []}
    session = make_session()
    try:
        for i, team in enumerate(teams):
            try:
                print(f"\n--- Processing team {i+1}/{len(teams)}: {team} ---")
                s_df, o_df, ch_df, dm_df, su_df = team_books(session, team)
                if not s_df.empty: all_dfs["salary"].append(s_df)
                if not o_df.empty: all_dfs["options"].append(o_df)
                if not ch_df.empty: all_dfs["cap_holds"].append(ch_df)
                if not dm_df.empty: all_dfs["dead_money"].append(dm_df)
                if not su_df.empty: all_dfs["summary"].append(su_df)
            except Exception as e:
                print(f"Error processing {team}: {e}")
                import traceback
                traceback.print_exc()
            if i < len(teams) - 1:
                print(f"Waiting {delay} seconds before next team...")
                time.sleep(delay)
    finally:
        session.close()

    return (
        pd.concat(all_dfs["salary"], ignore_index=True) if all_dfs["salary"] else pd.DataFrame(),
        pd.concat(all_dfs["options"], ignore_index=True) if all_dfs["options"] else pd.DataFrame(),
        pd.concat(all_dfs["cap_holds"], ignore_index=True) if all_dfs["cap_holds"] else pd.DataFrame(),
        pd.concat(all_dfs["dead_money"], ignore_index=True) if all_dfs["dead_money"] else pd.DataFrame(),
        pd.concat(all_dfs["summary"], ignore_index=True) if all_dfs["summary"] else pd.DataFrame(),
    )


def enrich_with_crosswalk(output_files: Dict[str, pd.DataFrame],
                          crosswalk_path: str = "sal_crosswalk.csv"
                          ) -> Dict[str, pd.DataFrame]:
    """Left-merge nba_id/bref_id onto every output frame that has spotrac_id.

    Keeps every scraped row (left join); rows whose spotrac_id isn't in the
    crosswalk (e.g. rookies not yet mapped) simply get null ids. Summary is
    team-level and has no spotrac_id, so it passes through untouched. If the
    crosswalk file is missing, warns and returns the frames unchanged so the
    scrape still produces normal output.
    """
    import os
    if not os.path.exists(crosswalk_path):
        print(f"  [crosswalk] {crosswalk_path} not found — skipping id enrichment. "
              f"Run build_crosswalk.py to generate it.")
        return output_files

    cross = pd.read_csv(crosswalk_path, dtype={"spotrac_id": str})
    id_cols = [c for c in ("spotrac_id", "nba_id", "bref_id") if c in cross.columns]
    cross = cross[id_cols].drop_duplicates(subset=["spotrac_id"])
    print(f"  [crosswalk] loaded {len(cross)} id mappings from {crosswalk_path}")

    enriched = {}
    for fname, df in output_files.items():
        if df.empty or "spotrac_id" not in df.columns:
            enriched[fname] = df
            continue
        df = df.copy()
        df["spotrac_id"] = df["spotrac_id"].astype(str).str.replace(r"\.0$", "", regex=True)
        # drop any pre-existing id cols so reruns don't create nba_id_x/_y
        df = df.drop(columns=[c for c in ("nba_id", "bref_id") if c in df.columns])
        merged = df.merge(cross, on="spotrac_id", how="left")
        # place nba_id/bref_id right after spotrac_id for readability
        cols = list(merged.columns)
        for idc in ("bref_id", "nba_id"):  # insert in reverse so nba_id ends up first
            if idc in cols:
                cols.remove(idc)
                cols.insert(cols.index("spotrac_id") + 1, idc)
        merged = merged[cols]
        # keep nba_id as a clean integer string (avoid '1628369.0' from float promotion)
        if "nba_id" in merged.columns:
            merged["nba_id"] = pd.to_numeric(merged["nba_id"], errors="coerce").astype("Int64")
        matched = merged["nba_id"].notna().sum() if "nba_id" in merged else 0
        print(f"  [crosswalk] {fname}: {matched}/{len(merged)} rows got an nba_id")
        enriched[fname] = merged
    return enriched


if __name__ == "__main__":
    teams = ["ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
             "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
             "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

    print("Starting NBA salary scraping (requests edition)...")
    salary_df, option_df, cap_holds_df, dead_money_df, summary_df = scrape_all_teams(teams)

    if not dead_money_df.empty:
        print("\nIntegrating dead cap data into salaries and options...")
        dead_options_df = dead_money_df.copy()
        season_cols = [col for col in dead_money_df.columns if re.match(r"\d{4}-\d{2}", str(col))]
        for season in season_cols:
            dead_options_df[season] = np.where(dead_money_df[season] > 0, "D", "0")
        salary_df = pd.concat([salary_df, dead_money_df], ignore_index=True, sort=False)
        option_df = pd.concat([option_df, dead_options_df], ignore_index=True, sort=False)
        print(f"Successfully added {len(dead_money_df)} dead cap player entries.")

    if not salary_df.empty:
        print("\nPost-processing data...")
        # fill numeric/season columns but preserve spotrac_id nulls (don't turn
        # a missing id into 0, which is indistinguishable from a real value).
        _sid = salary_df["spotrac_id"] if "spotrac_id" in salary_df.columns else None
        salary_df.fillna(0, inplace=True)
        if _sid is not None:
            salary_df["spotrac_id"] = _sid
        if not option_df.empty:
            _osid = option_df["spotrac_id"] if "spotrac_id" in option_df.columns else None
            option_df.fillna("0", inplace=True)
            if _osid is not None:
                option_df["spotrac_id"] = _osid
            seasons = ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30"]
            guarantee_multiplier = pd.DataFrame(index=option_df.index)
            for season in seasons:
                if season in option_df.columns:
                    guarantee_multiplier[season] = np.where(option_df[season] == "T", 0, 1)
            guaranteed_total = pd.Series([0.0] * len(salary_df))
            for season in seasons:
                if season in salary_df.columns and season in guarantee_multiplier.columns:
                    guaranteed_total += salary_df[season] * guarantee_multiplier[season]
            salary_df["Guaranteed"] = guaranteed_total
        salary_df = salary_df.sort_values(by="Guaranteed", ascending=False).reset_index(drop=True)

        # Manual corrections
        salary_df.loc[salary_df["Player"].str.contains("Branden Carlson", na=False), "2024-25"] = 990895
        if not option_df.empty:
            option_df.loc[option_df["Player"].str.contains("Scottie Barnes", na=False), "2025-26"] = 0
            option_df.loc[option_df["Player"].str.contains("Bradley Beal", na=False), "2026-27"] = "P"
            option_df.loc[option_df["Player"].str.contains("Jalen Brunson", na=False), "2025-26"] = 0
            option_df.loc[option_df["Player"].str.contains("Julius Randle", na=False), "2026-27"] = "P"

    print("\nSaving results...")
    output_files = {
        "nba_salaries.csv": salary_df,
        "nba_options.csv": option_df,
        "nba_cap_holds.csv": cap_holds_df,
        "nba_dead_money.csv": dead_money_df,
        "nba_summary.csv": summary_df,
    }

    # Second pass: fold nba_id/bref_id in from the crosswalk (left join on
    # spotrac_id). Every scraped row is kept; unmapped rows get null ids.
    print("Enriching with crosswalk ids...")
    output_files = enrich_with_crosswalk(output_files)

    for filename, df in output_files.items():
        df.to_csv(filename, index=False)
        print(f"Saved {filename} ({len(df)} rows)")

    for directory in ["../web_app/data", "../discord/data"]:
        try:
            for filename, df in output_files.items():
                df.to_csv(f"{directory}/{filename}", index=False)
            print(f"Files also saved to {directory}")
        except Exception as e:
            print(f"Could not save to {directory} directory: {e}")

    print("\nScraping completed successfully!")