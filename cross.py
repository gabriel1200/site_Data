"""
Build a Spotrac <-> index_master crosswalk.

Produces one row per player linking:
    spotrac_id  <->  nba_id  <->  bref_id  <->  canonical name

The join is by name (layered normalized matcher), because spotrac_id is the NEW
key and index_master doesn't carry it yet. Once this crosswalk exists you join
future scrapes on spotrac_id directly and never name-match again.

Inputs:
    nba_salaries.csv  (or any scraper output with Player + spotrac_id columns)
    index_master.csv  (player, bref_id, nba_id, year, ...)

Outputs (to /mnt/user-data/outputs):
    spotrac_crosswalk.csv        matched rows: spotrac_id, name, nba_id, bref_id, ...
    crosswalk_unmatched.csv      spotrac players with no index_master match
    crosswalk_ambiguous.csv      names mapping to >1 index_master id (needs review)

Usage:
    python build_crosswalk.py [scraper_csv] [index_master_csv]
"""
import sys
import re
import unicodedata
import pandas as pd

OUT_DIR = "figures"


def norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[.'\u2019]", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", s).strip()
    return s


def clean_spotrac(name: str) -> str:
    name = re.sub(r"\s+WAIVED\s*$", "", str(name), flags=re.I).strip()
    return name.rstrip(".").strip()


# Spotrac uses a different name form than index_master for some established
# players (nicknames, spelling, legal names). Map Spotrac's name -> the name as
# it appears in index_master. These are applied as the highest-priority match
# candidate, so the player still resolves to their REAL index_master nba_id/
# bref_id — this table only fixes the name lookup, it never invents ids.
# Add a line here whenever a known veteran lands in crosswalk_unmatched.csv.
NAME_ALIASES = {
    "herb jones": "Herbert Jones",
    "nicolas claxton": "Nic Claxton",
    "sviatoslav mykhailiuk": "Svi Mykhailiuk",
    "nah'shon hyland": "Bones Hyland",
    "cameron christie": "Cam Christie",
}


def candidates(name: str):
    """Normalized name variants to try, in priority order.

    Order matters — first hit wins:
      1. explicit alias (nickname/spelling fixes for known players)
      2. name as-is
      3. first/last swap ('Porter Michael' -> 'Michael Porter')
      4. multi-word surname rotation ('Da Silva Tristan' -> 'Tristan Da Silva')
    """
    base = clean_spotrac(name)
    alias = NAME_ALIASES.get(norm(base)) or NAME_ALIASES.get(base.lower().strip())
    if alias:
        yield norm(alias)
    yield norm(base)
    toks = base.split()
    if len(toks) >= 2:
        yield norm(" ".join(toks[1:] + toks[:1]))   # first token to back
        yield norm(" ".join(toks[-1:] + toks[:-1]))  # last token to front


NON_PLAYER = re.compile(
    r"incomplete roster|roster charge|cap hold|trade exception|"
    r"dead money|draft pick|empty|total|charge", re.I
)


def build_index_lookup(idx: pd.DataFrame):
    """Collapse season-level index_master to one row per normalized name."""
    idx = idx.copy()
    idx["key"] = idx["player"].map(norm)
    idx = idx.sort_values("year")
    grp = idx.groupby("key")
    lookup = grp.agg(
        canonical_name=("player", "last"),
        nba_id=("nba_id", "last"),
        bref_id=("bref_id", "last"),
        latest_year=("year", "last"),
        n_distinct_nba_id=("nba_id", "nunique"),
    ).reset_index()
    return lookup.set_index("key")


def main():
    scraper_csv = sys.argv[1] if len(sys.argv) > 1 else "nba_salaries.csv"
    index_csv = sys.argv[2] if len(sys.argv) > 2 else "index_master.csv"

    sal = pd.read_csv(scraper_csv)
    idx = pd.read_csv(index_csv)

    # sanity check on the spotrac_id column
    if "spotrac_id" not in sal.columns:
        print("ERROR: scraper file has no 'spotrac_id' column. Re-run the scraper first.")
        sys.exit(1)
    sal["spotrac_id"] = sal["spotrac_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    real_ids = ~sal["spotrac_id"].isin(["0", "nan", "", "None"])
    print(f"Scraper rows: {len(sal)}, with real spotrac_id: {real_ids.sum()}")
    if real_ids.sum() == 0:
        print("WARNING: every spotrac_id is 0/blank. The crosswalk will have no "
              "usable ids. Re-run the fixed scraper before building the real crosswalk.")

    lookup = build_index_lookup(idx)
    lookup_keys = set(lookup.index)

    # Optional manual overrides: real ids you sourced yourself (e.g. from NBA.com)
    # for players not yet in index_master — incoming rookies, UDFAs, etc.
    # Format (manual_ids.csv, header required):
    #     spotrac_id,nba_id,bref_id,canonical_name
    #     107917,,dybanaj01,AJ Dybantsa      <- bref only is fine; blank nba_id ok
    # Applied by spotrac_id, so it's stable across name changes and reruns.
    overrides = {}
    manual_path = f"{OUT_DIR}/manual_ids.csv"
    import os
    if os.path.exists(manual_path):
        mo = pd.read_csv(manual_path, dtype=str).fillna("")
        for _, mr in mo.iterrows():
            sid = str(mr.get("spotrac_id", "")).strip().replace(".0", "")
            if sid:
                overrides[sid] = {
                    "nba_id": mr.get("nba_id", "").strip(),
                    "bref_id": mr.get("bref_id", "").strip(),
                    "canonical_name": mr.get("canonical_name", "").strip(),
                }
        print(f"Loaded {len(overrides)} manual id override(s) from manual_ids.csv")

    # one crosswalk row per unique (spotrac_id, player); drop non-player charge rows
    players = sal[sal["Player"].notna()].copy()
    players = players[~players["Player"].str.contains(NON_PLAYER, na=False)]
    players = players.drop_duplicates(subset=["spotrac_id", "Player"])

    rows, unmatched, ambiguous = [], [], []
    for _, r in players.iterrows():
        name = r["Player"]
        sid = str(r["spotrac_id"])
        team = r.get("Team", "")

        hit_key = next((c for c in candidates(name) if c in lookup_keys), None)
        if hit_key is None:
            # try manual override before giving up
            ov = overrides.get(sid)
            if ov and (ov["nba_id"] or ov["bref_id"]):
                rows.append({
                    "spotrac_id": sid,
                    "spotrac_name": name,
                    "canonical_name": ov["canonical_name"] or name,
                    "nba_id": ov["nba_id"] or pd.NA,
                    "bref_id": ov["bref_id"] or pd.NA,
                    "team": team,
                    "latest_year": pd.NA,
                    "match_key": "manual_override",
                    "ambiguous": False,
                })
                continue
            unmatched.append({"spotrac_id": sid, "spotrac_name": name, "team": team})
            continue
        m = lookup.loc[hit_key]
        rec = {
            "spotrac_id": sid,
            "spotrac_name": name,
            "canonical_name": m["canonical_name"],
            "nba_id": m["nba_id"],
            "bref_id": m["bref_id"],
            "team": team,
            "latest_year": int(m["latest_year"]),
            "match_key": hit_key,
            "ambiguous": bool(m["n_distinct_nba_id"] > 1),
        }
        rows.append(rec)
        if rec["ambiguous"]:
            ambiguous.append(rec)

    cross = pd.DataFrame(rows)
    # normalize id dtypes for clean output
    for col in ["nba_id"]:
        if col in cross.columns:
            cross[col] = cross[col].astype("Int64", errors="ignore")

    cross.to_csv(f"sal_crosswalk.csv", index=False)
    pd.DataFrame(unmatched).to_csv(f"{OUT_DIR}/crosswalk_unmatched.csv", index=False)
    pd.DataFrame(ambiguous).to_csv(f"{OUT_DIR}/crosswalk_ambiguous.csv", index=False)

    n_override = sum(1 for r in rows if r.get("match_key") == "manual_override")
    print(f"\nCrosswalk rows:        {len(cross)}")
    print(f"  from index_master:   {len(cross) - n_override}")
    print(f"  from manual_ids.csv: {n_override}")
    print(f"  with real nba_id:    {cross['nba_id'].notna().sum() if len(cross) else 0}")
    print(f"  ambiguous (review):  {len(ambiguous)}")
    print(f"Unmatched (no id yet): {len(unmatched)}")

    # Emit a ready-to-fill template for the still-unmatched players, so you can
    # paste in ids from NBA.com / Basketball Reference and rerun. Merges with any
    # existing manual_ids.csv so you never lose ids you've already entered.
    if unmatched:
        tmpl = pd.DataFrame(unmatched)
        tmpl["nba_id"] = ""
        tmpl["bref_id"] = ""
        tmpl["canonical_name"] = tmpl["spotrac_name"]
        tmpl = tmpl[["spotrac_id", "nba_id", "bref_id", "canonical_name", "spotrac_name", "team"]]
        tmpl_path = f"{OUT_DIR}/manual_ids_template.csv"
        tmpl.to_csv(tmpl_path, index=False)
        print(f"\n-> Wrote {tmpl_path} ({len(tmpl)} rows). Fill nba_id/bref_id, "
              f"rename to manual_ids.csv, and rerun to fold them in.")

    if len(cross):
        print("\nsample:")
        print(cross[["spotrac_id", "spotrac_name", "canonical_name", "nba_id", "bref_id"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()