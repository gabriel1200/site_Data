"""
NBA salary cap table generator.

Every column in RealGM's "NBA Salary Cap History" table (Luxury Tax, 1st
Apron, 2nd Apron, BAE, Non-Taxpayer MLE, Taxpayer MLE, Team Room MLE) is a
fixed CBA-defined multiple of the Salary Cap for that season. Confirmed
against the known-actual 2024-25 and 2025-26 rows (not projections) to
4+ decimal places of agreement, and cross-checked against RealGM's own
2026-27..2034-35 projected rows.

CAP_RATIOS below are the empirically-derived multiples. Once you have a
season's Salary Cap number, every other column is `round(cap * ratio, -3)`
(rounded to the nearest $1,000, matching how these figures are always
reported).

Cap growth itself is NOT a fixed ratio of anything — it's a projection
assumption. RealGM's own projected rows show a flat 5% year-over-year cap
increase starting in 2027-28 (174.0M -> 182.7M -> 191.835M -> ... each is
exactly prior * 1.05, rounded to the nearest $1,000). 2026-27 is a
near-term estimate off the actual 2025-26 cap (+6.67%) rather than the
long-run 5% assumption, since it's close enough to be based on real BRI
data rather than a flat long-run guess.

Adjust GROWTH_RATE below if the league signals a different trajectory
(e.g. new media rights deals coming online), or override per-season via
the `overrides` dict in generate_projected().
"""
import pandas as pd
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# CBA-defined ratios (column value = Salary Cap * ratio, rounded to nearest $1k)
# ---------------------------------------------------------------------------
CAP_RATIOS = {
    "Luxury Tax":        1.21500,
    "1st Apron":         1.26705,
    "2nd Apron":         1.34386,
    "BAE":               0.03320,
    "Non-Taxpayer MLE":  0.09120,
    "Taxpayer MLE":      0.03676,
    "Team Room MLE":     0.05678,
}

# ---------------------------------------------------------------------------
# Known-actual seasons — hardcoded, not derived. The NBA doesn't compute tax/
# apron thresholds as (current cap * fixed ratio) each year; each threshold
# carries forward from the PRIOR season's dollar figure scaled by the cap's
# growth rate, so a flat ratio applied fresh to the current cap can be off by
# a few hundred to a couple thousand dollars vs. the officially announced
# number (confirmed: no single ratio reproduces all of 2024-25/2025-26/
# 2026-27's real figures exactly — the windows are parts-per-million apart
# but don't overlap). Once a season is officially announced, just enter the
# real numbers here instead of trusting the ratio to reproduce them.
KNOWN_ACTUALS = {
    "2024-2025": {"Salary Cap": 140_588_000, "Luxury Tax": 170_814_000,
                  "1st Apron": 178_132_000, "2nd Apron": 188_931_000},
    "2025-2026": {"Salary Cap": 154_647_000, "Luxury Tax": 187_895_000,
                  "1st Apron": 195_945_000, "2nd Apron": 207_824_000},
    "2026-2027": {"Salary Cap": 164_961_000, "Luxury Tax": 200_428_000,
                  "1st Apron": 209_015_000, "2nd Apron": 221_686_000},
}

# Last known-actual season and its real cap figure (update this each summer
# once the league officially sets the new cap).
BASE_SEASON = "2025-2026"
BASE_CAP = 154_647_000

# Near-term estimate for the season immediately after BASE_SEASON. This is
# usually available well before the flat long-run assumption applies (the
# league gives an early estimate based on actual BRI, ~midseason of the
# prior year). Set to None to just apply GROWTH_RATE to every year instead.
NEXT_SEASON = "2026-2027"
NEXT_SEASON_CAP = 164_961_000

# Flat long-run year-over-year growth assumption applied from the season
# after NEXT_SEASON onward. RealGM's own table implies exactly 5%.
GROWTH_RATE = 0.05


def round_to_thousand(x: float) -> int:
    return int(round(x, -3))


def derive_row(cap: int, season: Optional[str] = None) -> Dict[str, int]:
    """Given a Salary Cap figure, derive every other CBA-linked column.

    If `season` matches a KNOWN_ACTUALS entry, those real announced dollar
    figures are used directly for Tax/1st Apron/2nd Apron instead of the
    ratio (see KNOWN_ACTUALS comment above for why — the ratio is accurate
    to ~5 decimal places but the league's actual compounding formula can
    land a few hundred to a couple thousand dollars off from a fresh
    cap*ratio calculation). BAE/MLE columns aren't independently announced
    the same way, so those still derive from the ratio even in known-actual
    seasons.
    """
    row = {"Salary Cap": cap}
    actual = KNOWN_ACTUALS.get(season, {}) if season else {}
    for col, ratio in CAP_RATIOS.items():
        row[col] = actual.get(col, round_to_thousand(cap * ratio))
    return row


def season_str(start_year: int) -> str:
    return f"{start_year}-{start_year + 1}"


def generate_projected(num_years: int = 9,
                        growth_rate: float = GROWTH_RATE,
                        overrides: Optional[Dict[str, int]] = None
                        ) -> pd.DataFrame:
    """Generate BASE_SEASON + NEXT_SEASON + `num_years` more projected seasons.

    overrides: optional {season_str: cap_value} to hard-set specific future
    seasons (e.g. a new CBA-negotiated fixed number) instead of applying
    the flat growth_rate for that year.
    """
    overrides = overrides or {}
    rows = []

    base_start = int(BASE_SEASON.split("-")[0])
    rows.append({"Season": BASE_SEASON, **derive_row(BASE_CAP, season=BASE_SEASON)})

    next_start = int(NEXT_SEASON.split("-")[0])
    cap = NEXT_SEASON_CAP
    rows.append({"Season": NEXT_SEASON, **derive_row(cap, season=NEXT_SEASON)})

    for i in range(1, num_years + 1):
        start_year = next_start + i
        season = season_str(start_year)
        if season in overrides:
            cap = overrides[season]
        else:
            cap = round_to_thousand(cap * (1 + growth_rate))
        # season won't be in KNOWN_ACTUALS for genuinely future years, so
        # this naturally falls back to ratio-derivation for those — only
        # matters if you extend KNOWN_ACTUALS with a newly-announced season
        # that also happens to fall in this projected range.
        rows.append({"Season": season, **derive_row(cap, season=season)})

    df = pd.DataFrame(rows)
    df["year"] = df["Season"].str.split("-").str[1].astype(int)
    # write season as "YYYY-YYYY" to match the existing cap.csv convention
    df["Season"] = df["Season"]
    return df.sort_values("year", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    import os

    # Path to the historical cap.csv this script keeps up to date. Point
    # this at wherever your real file lives (e.g. the scrape_cap.py output
    # path) — defaults to a file alongside this script.
    CAP_CSV_PATH = os.environ.get("CAP_CSV_PATH", "cap.csv")

    # 2027-28 is itself a round, hand-set number ($174.0M) rather than a
    # straight 5%-of-2026-27 calc (174.0M / 164.961M = ~5.48% growth, not
    # 5%) — it's the anchor the flat 5% assumption starts FROM, not the
    # first output of it. Pin it via override; every year after derives at
    # a clean 5% off the previous year automatically.
    projected = generate_projected(
        num_years=8,  # 2027-28 .. 2034-35
        overrides={"2027-2028": 174_000_000},
    )
    print(projected.to_string(index=False))

    if os.path.exists(CAP_CSV_PATH):
        existing = pd.read_csv(CAP_CSV_PATH)
        existing["Season"] = existing["Season"].astype(str)
        projected_seasons = set(projected["Season"])
        # drop any rows for seasons this run just (re)computed, then splice
        # the fresh ones back in — everything else (real historical actuals)
        # passes through untouched.
        kept = existing[~existing["Season"].isin(projected_seasons)].copy()
        combined = pd.concat([projected, kept], ignore_index=True)
        combined = combined.sort_values("year", ascending=False).reset_index(drop=True)
    else:
        print(f"\n[note] {CAP_CSV_PATH} not found — writing projected rows only.")
        combined = projected

    combined.to_csv(CAP_CSV_PATH, index=False)
    print(f"\nUpdated {CAP_CSV_PATH} ({len(combined)} rows, "
          f"{len(projected)} projected seasons refreshed).")