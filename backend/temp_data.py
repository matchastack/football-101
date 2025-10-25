"""
Historical fixtures data fetching script.

This script fetches historical Premier League fixtures data from the RapidAPI
Football API for multiple seasons and saves it to a CSV file.
"""

import logging
import time
from pathlib import Path

import pandas as pd

from api_data import get_api_response, LEAGUE_IDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PREMIER_LEAGUE_ID = LEAGUE_IDS["Premier League"]
START_SEASON = 1992
END_SEASON = 2023
API_RATE_LIMIT_DELAY = 5  # seconds between API calls
OUTPUT_FILE = Path("../data/fixtures.csv")


def get_season_fixtures(league_id: int, season: int) -> pd.DataFrame:
    """
    Fetch fixtures data for a specific league and season.

    Args:
        league_id: League ID to fetch fixtures for
        season: Season year (e.g., 2022)

    Returns:
        DataFrame with fixtures data for the season
        Returns empty DataFrame if request fails
    """
    logger.info(f"Fetching fixtures for season {season}")

    params = {"league": league_id, "season": season}

    try:
        response = get_api_response("/fixtures", params=params)

        if response.status_code == 200:
            df = pd.json_normalize(response.json()["response"])
            logger.info(f"Successfully fetched {len(df)} fixtures for season {season}")
            return df
        else:
            logger.warning(f"Failed to fetch fixtures for season {season}: Status {response.status_code}")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"Error fetching fixtures for season {season}: {e}")
        return pd.DataFrame()


def fetch_historical_fixtures(
    league_id: int,
    start_season: int,
    end_season: int,
    delay: int = API_RATE_LIMIT_DELAY
) -> pd.DataFrame:
    """
    Fetch historical fixtures data across multiple seasons.

    Args:
        league_id: League ID to fetch fixtures for
        start_season: Starting season year (inclusive)
        end_season: Ending season year (exclusive)
        delay: Delay in seconds between API calls to respect rate limits

    Returns:
        DataFrame with all fixtures from specified seasons
    """
    logger.info(f"Starting fetch for seasons {start_season} to {end_season - 1}")

    all_fixtures = []
    total_seasons = end_season - start_season

    for i, season in enumerate(range(start_season, end_season), 1):
        logger.info(f"Progress: {i}/{total_seasons} seasons")

        # Fetch fixtures for this season
        season_df = get_season_fixtures(league_id, season)

        if not season_df.empty:
            all_fixtures.append(season_df)

        # Rate limiting - sleep between requests (except for last request)
        if i < total_seasons:
            logger.info(f"Waiting {delay} seconds before next request...")
            time.sleep(delay)

    # Combine all seasons
    if all_fixtures:
        combined_df = pd.concat(all_fixtures, ignore_index=True)
        logger.info(f"Total fixtures fetched: {len(combined_df)}")
        return combined_df
    else:
        logger.warning("No fixtures data fetched")
        return pd.DataFrame()


def main():
    """Main execution function."""
    logger.info("Starting historical fixtures data fetch")

    # Create output directory if it doesn't exist
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Fetch historical fixtures
    fixtures_df = fetch_historical_fixtures(
        league_id=PREMIER_LEAGUE_ID,
        start_season=START_SEASON,
        end_season=END_SEASON
    )

    # Save to CSV
    if not fixtures_df.empty:
        fixtures_df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"Fixtures data saved to {OUTPUT_FILE}")
        logger.info(f"Total rows: {len(fixtures_df)}")
    else:
        logger.error("No data to save")


if __name__ == "__main__":
    main()