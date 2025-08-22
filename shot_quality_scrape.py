#!/usr/bin/env python3
"""
NBA Shot Quality Analysis
Analyzes shot-making ability by comparing actual vs expected performance across different shot contexts.
Includes pace and era adjustments for cross-season comparisons.
This version is modified to update a CSV with data for a user-specified season.
"""

import os
import re
import time
import random
import argparse
from typing import List, Optional, Tuple, Dict, Union, Iterable
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# NBA API imports
from nba_api.stats.endpoints import (
    leaguedashplayerptshot,
    playerdashptshots,
    leaguedashteamstats,
)
from nba_api.stats.static import players as static_players
from nba_api.stats.library.parameters import PerModeSimple

# Configuration
CONFIG = {
    'seasons': [f"{y}-{str((y+1)%100).zfill(2)}" for y in range(2013, 2025)],
    'season_type': "Regular Season",
    'league_id': "00",
    'sleep_time': 0.1,
    'max_retries': 4,
    'base_delay': 0.2,
    'jitter': 0.1,
    'baseline_pace': 100.0,
    'baseline_ortg': 110.0,
    'force_refresh': False,
    'top_n_preview': 6
}

# Shot context bins
SHOT_TYPES = ["Catch and Shoot", "Pullups", "Less Than 10 ft"]
DEF_DISTANCES = [
    "0-2 Feet - Very Tight",
    "2-4 Feet - Tight",
    "4-6 Feet - Open",
    "6+ Feet - Wide Open"
]
TOUCH_TIMES = ["Touch < 2 Seconds", "Touch 2-6 Seconds", "Touch 6+ Seconds"]

# Output directories
DATA_DIR = Path("data")
PLAYERS_DIR = DATA_DIR / "players"
COMBINED_DIR = DATA_DIR / "combined"


class NBADataFetcher:
    """Handles NBA API data fetching with retry logic"""

    def __init__(self, config: dict):
        self.config = config
        self._ensure_directories()

    def _ensure_directories(self):
        """Create output directories if they don't exist"""
        PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
        COMBINED_DIR.mkdir(parents=True, exist_ok=True)

    def _retry_request(self, fn, *args, **kwargs):
        """Retry API requests with exponential backoff"""
        last_error = None
        for attempt in range(self.config['max_retries']):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                last_error = e
                delay = (self.config['base_delay'] * (2 ** attempt) +
                        random.random() * self.config['jitter'])
                time.sleep(delay)
        raise last_error

    def fetch_league_shot_data(self, season: str, shot_type: str,
                              def_distance: str, touch_time: str) -> pd.DataFrame:
        """Fetch league-wide shot data for a specific context bin"""
        def _api_call():
            return leaguedashplayerptshot.LeagueDashPlayerPtShot(
                season=season,
                season_type_all_star=self.config['season_type'],
                league_id=self.config['league_id'],
                per_mode_simple=PerModeSimple.totals,
                general_range_nullable=shot_type,
                close_def_dist_range_nullable=def_distance,
                touch_time_range_nullable=touch_time,
            )

        try:
            response = self._retry_request(_api_call)
            df = response.get_data_frames()[0] if response.get_data_frames() else pd.DataFrame()

            if not df.empty:
                df = df.assign(
                    BIN_SHOT_TYPE=shot_type,
                    BIN_DEF_DIST=def_distance,
                    BIN_TOUCH=touch_time,
                    DATA_SOURCE="league"
                )

            return df

        except Exception as e:
            print(f"Warning: Failed to fetch league data for {season}, {shot_type}: {e}")
            return pd.DataFrame()

    def fetch_league_environment(self, season: str) -> Dict[str, float]:
        """Fetch league pace and offensive rating for era adjustments"""
        def _api_call():
            return leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                season_type_all_star=self.config['season_type'],
                per_mode_detailed="PerGame",
                measure_type_detailed_defense="Advanced"
            )

        try:
            response = self._retry_request(_api_call)
            df = response.get_data_frames()[0]

            if df is not None and not df.empty and all(col in df.columns for col in ['PACE', 'OFF_RATING']):
                return {
                    'league_pace': float(df['PACE'].mean()),
                    'league_off_rating': float(df['OFF_RATING'].mean())
                }
        except Exception as e:
            print(f"Warning: Could not fetch league environment for {season}: {e}")

        return {
            'league_pace': self.config['baseline_pace'],
            'league_off_rating': self.config['baseline_ortg']
        }


class ShotAnalyzer:
    """Analyzes shot quality and calculates various metrics"""

    def __init__(self, config: dict):
        self.config = config
        self.required_columns = [
            'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION',
            'FGA', 'FGM', 'FG3A', 'FG3M', 'EFG_PCT'
        ]

    def _is_valid_shot_bin(self, shot_type: str, touch_time: str) -> bool:
        """Check if shot type and touch time combination is valid"""
        return not (shot_type == "Catch and Shoot" and
                   touch_time in {"Touch 2-6 Seconds", "Touch 6+ Seconds"})

    def get_valid_shot_bins(self) -> List[Tuple[str, str, str]]:
        """Generate all valid shot context combinations"""
        bins = []
        for shot_type in SHOT_TYPES:
            for def_dist in DEF_DISTANCES:
                for touch_time in TOUCH_TIMES:
                    if self._is_valid_shot_bin(shot_type, touch_time):
                        bins.append((shot_type, def_dist, touch_time))
        return bins

    def normalize_shot_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize and clean shot data"""
        if df.empty:
            return pd.DataFrame(columns=self.required_columns + ['FG2A', 'FG2M'])

        for col in self.required_columns:
            if col not in df.columns:
                df[col] = pd.NA

        name_alternatives = ['PLAYER', 'PLAYER_LAST_FIRST', 'PLAYER_NAME_LAST_FIRST']
        team_alternatives = ['TEAM_ABBREV', 'TEAM', 'TEAM_NAME']

        if df['PLAYER_NAME'].isna().all():
            for alt in name_alternatives:
                if alt in df.columns and df[alt].notna().any():
                    df['PLAYER_NAME'] = df[alt]
                    break

        if df['TEAM_ABBREVIATION'].isna().all():
            for alt in team_alternatives:
                if alt in df.columns and df[alt].notna().any():
                    df['TEAM_ABBREVIATION'] = df[alt]
                    break

        numeric_cols = ['FGA', 'FGM', 'FG3A', 'FG3M', 'EFG_PCT']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        df['FG2A'] = (df['FGA'] - df['FG3A']).clip(lower=0)
        df['FG2M'] = (df['FGM'] - df['FG3M']).clip(lower=0)

        if (df['EFG_PCT'] == 0).all() and (df['FGA'] > 0).any():
            df['EFG_PCT'] = (df['FGM'] + 0.5 * df['FG3M']) / df['FGA'].replace(0, pd.NA)
            df['EFG_PCT'] = df['EFG_PCT'].fillna(0.0)

        df['PLAYER_KEY'] = df['PLAYER_ID'].astype(str)
        if df['PLAYER_KEY'].isna().all() or (df['PLAYER_KEY'] == 'nan').all():
            df['PLAYER_KEY'] = df['PLAYER_NAME'].astype(str)

        return df

    def calculate_league_rates(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Calculate league-wide 2PT and 3PT shooting percentages"""
        if df.empty:
            return 0.0, 0.0

        total_2pt_attempts = df['FG2A'].sum()
        total_2pt_makes = df['FG2M'].sum()
        total_3pt_attempts = df['FG3A'].sum()
        total_3pt_makes = df['FG3M'].sum()

        fg2_pct = total_2pt_makes / total_2pt_attempts if total_2pt_attempts > 0 else 0.0
        fg3_pct = total_3pt_makes / total_3pt_attempts if total_3pt_attempts > 0 else 0.0

        return fg2_pct, fg3_pct

    def add_expected_points(self, df: pd.DataFrame, lg_fg2_pct: float, lg_fg3_pct: float) -> pd.DataFrame:
        """Add actual and expected points for each shot context"""
        df = df.copy()
        df['PTS_2PT'] = 2.0 * df['FG2M']
        df['PTS_3PT'] = 3.0 * df['FG3M']
        df['PTS_TOTAL'] = df['PTS_2PT'] + df['PTS_3PT']
        df['xPTS_2PT'] = 2.0 * df['FG2A'] * lg_fg2_pct
        df['xPTS_3PT'] = 3.0 * df['FG3A'] * lg_fg3_pct
        df['xPTS_TOTAL'] = df['xPTS_2PT'] + df['xPTS_3PT']
        return df

    def aggregate_player_stats(self, shot_data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate shot data by player"""
        if shot_data.empty:
            return pd.DataFrame()

        player_stats = shot_data.groupby('PLAYER_KEY', as_index=False).agg({
            'PLAYER_ID': 'first', 'PLAYER_NAME': 'first', 'TEAM_ABBREVIATION': 'first',
            'FG2A': 'sum', 'FG2M': 'sum', 'FG3A': 'sum', 'FG3M': 'sum', 'FGA': 'sum',
            'PTS_2PT': 'sum', 'xPTS_2PT': 'sum', 'PTS_3PT': 'sum', 'xPTS_3PT': 'sum',
            'PTS_TOTAL': 'sum', 'xPTS_TOTAL': 'sum'
        })

        player_stats['FG2_PCT'] = player_stats['FG2M'] / player_stats['FG2A'].replace(0, pd.NA)
        player_stats['FG3_PCT'] = player_stats['FG3M'] / player_stats['FG3A'].replace(0, pd.NA)
        player_stats['eFG_PCT'] = player_stats['PTS_TOTAL'] / (2.0 * player_stats['FGA']).replace(0, pd.NA)
        player_stats['xeFG_PCT'] = player_stats['xPTS_TOTAL'] / (2.0 * player_stats['FGA']).replace(0, pd.NA)
        player_stats['Shot_Making_2PT'] = (player_stats['PTS_2PT'] - player_stats['xPTS_2PT']) / player_stats['FG2A'].replace(0, pd.NA)
        player_stats['Points_Added_2PT'] = player_stats['PTS_2PT'] - player_stats['xPTS_2PT']
        player_stats['Shot_Making_3PT'] = (player_stats['PTS_3PT'] - player_stats['xPTS_3PT']) / player_stats['FG3A'].replace(0, pd.NA)
        player_stats['Points_Added_3PT'] = player_stats['PTS_3PT'] - player_stats['xPTS_3PT']
        player_stats['Shot_Making_Overall'] = (player_stats['PTS_TOTAL'] - player_stats['xPTS_TOTAL']) / player_stats['FGA'].replace(0, pd.NA)
        player_stats['Points_Added_Overall'] = player_stats['PTS_TOTAL'] - player_stats['xPTS_TOTAL']

        return player_stats

    def apply_era_pace_adjustments(self, df: pd.DataFrame, league_env: Dict[str, float]) -> pd.DataFrame:
        """Apply pace and era adjustments for cross-season comparisons"""
        df = df.copy()
        league_pace = league_env['league_pace']
        league_off_rating = league_env['league_off_rating']

        pace_factor = self.config['baseline_pace'] / league_pace if league_pace > 0 else 1.0
        era_factor = self.config['baseline_ortg'] / league_off_rating if league_off_rating > 0 else 1.0

        df['Points_Added_PaceAdj'] = df['Shot_Making_Overall'] * (df['FGA'] * pace_factor)
        df['Points_Added_EraAdj'] = df['Points_Added_Overall'] * era_factor
        df['Points_Added_EraPackeAdj'] = df['Points_Added_PaceAdj'] * era_factor
        df['League_Pace'] = league_pace
        df['League_OffRating'] = league_off_rating
        df['Pace_Factor'] = pace_factor
        df['Era_Factor'] = era_factor
        df['Combined_Factor'] = pace_factor * era_factor

        return df


class NBAAnalysisRunner:
    """Main class to orchestrate the NBA shot quality analysis"""

    def __init__(self, config: dict = None):
        self.config = config or CONFIG
        self.fetcher = NBADataFetcher(self.config)
        self.analyzer = ShotAnalyzer(self.config)

    def analyze_season(self, season: str) -> pd.DataFrame:
        """Analyze shot quality for a single season"""
        print(f"Analyzing season: {season}")

        shot_bins = self.analyzer.get_valid_shot_bins()
        all_shot_data = []

        for shot_type, def_dist, touch_time in tqdm(shot_bins, desc=f"Fetching {season} data", leave=False):
            bin_data = self.fetcher.fetch_league_shot_data(season, shot_type, def_dist, touch_time)

            if not bin_data.empty:
                normalized_data = self.analyzer.normalize_shot_data(bin_data)
                lg_fg2_pct, lg_fg3_pct = self.analyzer.calculate_league_rates(normalized_data)
                enriched_data = self.analyzer.add_expected_points(normalized_data, lg_fg2_pct, lg_fg3_pct)
                all_shot_data.append(enriched_data)

            time.sleep(self.config['sleep_time'])

        if not all_shot_data:
            print(f"Warning: No data collected for {season}")
            return pd.DataFrame()

        combined_shots = pd.concat(all_shot_data, ignore_index=True)
        player_stats = self.analyzer.aggregate_player_stats(combined_shots)
        league_env = self.fetcher.fetch_league_environment(season)
        player_stats = self.analyzer.apply_era_pace_adjustments(player_stats, league_env)

        player_stats['Season'] = season
        player_stats['Season_Type'] = self.config['season_type']

        numeric_columns = [col for col in player_stats.columns if player_stats[col].dtype in ['float64', 'int64']]
        player_stats[numeric_columns] = player_stats[numeric_columns].round(3)

        player_stats = player_stats.sort_values(
            ['Points_Added_EraPackeAdj', 'Points_Added_Overall', 'Shot_Making_Overall'],
            ascending=[False, False, False]
        ).reset_index(drop=True)

        return player_stats

    def run_full_analysis(self, seasons: List[str] = None) -> pd.DataFrame:
        """Run analysis for multiple seasons"""
        seasons = seasons or self.config['seasons']
        all_seasons = []

        for season in seasons:
            season_data = self.analyze_season(season)
            if not season_data.empty:
                all_seasons.append(season_data)

                preview_cols = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'Season', 'Points_Added_EraPackeAdj', 'Points_Added_Overall', 'Shot_Making_Overall']
                print(f"\n{season} Top {self.config['top_n_preview']}:")
                print(season_data[preview_cols].head(self.config['top_n_preview']).to_string(index=False))

        return pd.concat(all_seasons, ignore_index=True) if all_seasons else pd.DataFrame()


def main(target_season: str):
    """Run the NBA shot quality analysis for a specific season and update the master CSV."""

    output_csv = 'nbashotmaking.csv'

    print(f"Starting shot quality analysis update for season: {target_season}")

    # Initialize and run the analysis for the single target season
    runner = NBAAnalysisRunner()
    new_season_data = runner.run_full_analysis([target_season])

    if new_season_data.empty:
        print(f"No data was collected for {target_season}. The CSV file will not be updated.")
        return

    # --- Read, Update, and Save Logic ---
    final_data = pd.DataFrame()

    # Check if the master CSV file already exists
    if os.path.exists(output_csv):
        print(f"Reading existing data from {output_csv}")
        try:
            existing_data = pd.read_csv(output_csv)

            # Remove any previous entries for the target season to avoid duplication
            print(f"Removing existing entries for the {target_season} season...")
            updated_data = existing_data[existing_data['Season'] != target_season]

            # Combine the old data with the newly scraped season's data
            print("Appending new season data...")
            final_data = pd.concat([updated_data, new_season_data], ignore_index=True)

        except pd.errors.EmptyDataError:
            print(f"Warning: {output_csv} was found but is empty. It will be overwritten with new data.")
            final_data = new_season_data
    else:
        print(f"{output_csv} not found. A new file will be created with the scraped data.")
        final_data = new_season_data

    # Save the updated DataFrame back to the CSV file
    print(f"Saving updated data to {output_csv}...")
    final_data.to_csv(output_csv, index=False)
    print("Save complete.")

    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Total records in {output_csv}: {len(final_data)}")

    # Display the top performers from the newly added season
    top_performers_new_season = new_season_data.nlargest(15, 'Points_Added_EraPackeAdj')

    display_columns = [
        'PLAYER_NAME', 'Season', 'PTS_TOTAL', 'xPTS_TOTAL',
        'eFG_PCT', 'xeFG_PCT', 'Shot_Making_Overall',
        'Points_Added_Overall', 'Points_Added_EraPackeAdj'
    ]

    print(f"\nTop 15 Shot Makers for {target_season} (Era & Pace Adjusted):")
    print(top_performers_new_season[display_columns].to_string(index=False))


if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="NBA Shot Quality Analysis Scraper. Fetches data for a given season and updates the master CSV."
    )
    parser.add_argument(
        "season",
        type=str,
        help="The season to analyze in YYYY-YY format (e.g., '2025-26')."
    )

    args = parser.parse_args()

    # Validate the season format before running the main function
    if not re.match(r"^\d{4}-\d{2}$", args.season):
        print("Error: Invalid season format. Please use the YYYY-YY format (e.g., '2025-26').")
    else:
        main(args.season)