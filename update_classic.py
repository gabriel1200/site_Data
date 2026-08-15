import io
import os
import time
import pandas as pd
import requests


def fetch_table(url: str, season: int) -> pd.DataFrame:
    """Fetches a table from Basketball Reference with custom headers and cleans summary rows."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    dfs = pd.read_html(io.StringIO(response.text))
    df = dfs[0]

    # Drop repeating table headers & summary rows (e.g., 'League Average')
    if "Rk" in df.columns:
        df = df[pd.to_numeric(df["Rk"], errors="coerce").notnull()].copy()

    # Extract Bref ID and Player URL before renaming columns
    if "Player-additional" in df.columns:
        df["bref_id"] = df["Player-additional"]
        df["url"] = df["bref_id"].apply(
            lambda x: f"https://www.basketball-reference.com/players/{x[0]}/{x}.html"
            if isinstance(x, str) and len(x) > 0
            else None
        )

    # Standardize column naming to lowercase for core identifiers
    column_mapping = {
        "Player": "player",
        "Tm": "team",
    }
    df = df.rename(columns=column_mapping)
    df["year"] = season

    # Drop any duplicated column names within the single scraped frame
    df = df.loc[:, ~df.columns.duplicated()].copy()

    return df


def update_nba_stats(
    seasons_to_check=[2025, 2026], filename="tplayer_stats.csv"
):
    if os.path.exists(filename):
        print(f"Loading existing file '{filename}'...")
        existing_df = pd.read_csv(filename)

        # De-duplicate existing columns if the file was previously corrupted
        existing_df = existing_df.loc[:, ~existing_df.columns.duplicated()].copy()

        # Standardize year column naming
        if "year" not in existing_df.columns:
            if "Season" in existing_df.columns:
                existing_df["year"] = existing_df["Season"]
                existing_df = existing_df.drop(columns=["Season"])
            elif "Year" in existing_df.columns:
                existing_df["year"] = existing_df["Year"]
                existing_df = existing_df.drop(columns=["Year"])

        existing_df["year"] = pd.to_numeric(existing_df["year"], errors="coerce")
    else:
        print(f"File '{filename}' not found. Creating a new dataset...")
        existing_df = pd.DataFrame()

    new_data = []

    for season in seasons_to_check:
        is_current_season = season == 2026

        if (
            not existing_df.empty
            and "year" in existing_df.columns
            and season in existing_df["year"].values
            and not is_current_season
        ):
            print(f"Skipping {season} season (already saved in file)...")
            continue

        print(f"Fetching data for {season} season...")
        totals_url = (
            f"https://www.basketball-reference.com/leagues/NBA_{season}_totals.html"
        )
        adv_url = (
            f"https://www.basketball-reference.com/leagues/NBA_{season}_advanced.html"
        )

        df_totals = fetch_table(totals_url, season)
        time.sleep(3)

        df_adv = fetch_table(adv_url, season)
        time.sleep(3)

        # Keys used for merging Totals and Advanced tables
        merge_keys = [
            col
            for col in ["player", "Pos", "Age", "team", "G", "MP", "year"]
            if col in df_totals.columns and col in df_adv.columns
        ]

        # Merge Totals and Advanced tables
        df_merged = pd.merge(
            df_totals,
            df_adv.drop(
                columns=[
                    c
                    for c in df_adv.columns
                    if c in df_totals.columns and c not in merge_keys
                ]
            ),
            on=merge_keys,
            how="left",
        )

        # Ensure no duplicate columns post-merge
        df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()].copy()
        new_data.append(df_merged)

    if not new_data:
        print("No new data needed to be fetched.")
        existing_df.to_csv(filename, index=False)
        return

    scraped_df = pd.concat(new_data, ignore_index=True)

    if not existing_df.empty:
        # Re-align newly scraped data to match exact target schema columns
        target_columns = list(existing_df.columns)
        scraped_df = scraped_df.reindex(columns=target_columns)

        # Filter out existing data for the seasons being replaced
        seasons_scraped = scraped_df["year"].unique()
        existing_df = existing_df[~existing_df["year"].isin(seasons_scraped)]

        final_df = pd.concat([existing_df, scraped_df], ignore_index=True)
    else:
        final_df = scraped_df

    # Drop fully empty rows & save
    final_df = final_df.dropna(how="all")
    final_df.to_csv(filename, index=False)
    print(f"Successfully updated '{filename}'! Total rows: {len(final_df)}")


if __name__ == "__main__":
    update_nba_stats(seasons_to_check=[2025, 2026])