"""
Database population script.

This script fetches data from the RapidAPI Football API and populates
the PostgreSQL database with leagues, seasons, teams, standings, and fixtures.

Usage:
    python populate_db.py                    # Populate Premier League current season
    python populate_db.py --league all       # Populate all configured leagues
    python populate_db.py --season 2022      # Populate specific season
"""

import argparse
import logging
import sys
import time

import pandas as pd

from api_data import (
    get_leagues_data,
    get_league_standing,
    get_fixtures,
    LEAGUE_IDS,
    get_api_response
)
from upload import (
    get_db_cursor,
    insert_league,
    insert_season,
    insert_team,
    insert_standing,
    insert_fixture,
    get_season_id
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CURRENT_SEASON = 2024
API_RATE_LIMIT_DELAY = 1  # seconds between API calls


def populate_leagues():
    """
    Populate leagues table with data from API.

    Returns:
        Number of leagues inserted
    """
    logger.info("Fetching leagues data from API...")

    try:
        leagues_df = get_leagues_data()

        if leagues_df.empty:
            logger.warning("No leagues data fetched")
            return 0

        logger.info(f"Fetched {len(leagues_df)} leagues")

        with get_db_cursor() as cur:
            count = 0
            for _, row in leagues_df.iterrows():
                insert_league(
                    cur,
                    league_id=int(row['id']),
                    name=row['name'],
                    league_type=row['type'],
                    country=None,  # Not in current API response
                    logo_url=None  # Not in current API response
                )
                count += 1

            logger.info(f"✓ Inserted {count} leagues")
            return count

    except Exception as e:
        logger.error(f"Failed to populate leagues: {e}")
        raise


def populate_season(league_id: int, year: int, is_current: bool = False):
    """
    Populate season data for a specific league and year.

    Args:
        league_id: League ID
        year: Season year
        is_current: Whether this is the current season

    Returns:
        Season database ID
    """
    logger.info(f"Populating season {year} for league {league_id}...")

    # For simplicity, we'll create seasons based on year
    # In a real scenario, you'd fetch this from the API
    start_date = f"{year}-08-01"  # Typical season start
    end_date = f"{year + 1}-05-31"  # Typical season end

    try:
        with get_db_cursor() as cur:
            season_id = insert_season(
                cur,
                league_id=league_id,
                year=year,
                start_date=start_date,
                end_date=end_date,
                is_current=is_current
            )
            logger.info(f"✓ Created/updated season {year} (ID: {season_id})")
            return season_id

    except Exception as e:
        logger.error(f"Failed to populate season: {e}")
        raise


def populate_standings(league_id: int, season_year: int):
    """
    Populate standings for a specific league and season.

    Args:
        league_id: League ID
        season_year: Season year

    Returns:
        Number of standings inserted
    """
    logger.info(f"Fetching standings for league {league_id}, season {season_year}...")

    try:
        standings_df = get_league_standing(season_year, league_id)

        if standings_df.empty:
            logger.warning("No standings data fetched")
            return 0

        logger.info(f"Fetched standings for {len(standings_df)} teams")

        with get_db_cursor() as cur:
            # Get or create season
            season_id = get_season_id(cur, league_id, season_year)
            if season_id is None:
                season_id = populate_season(league_id, season_year, is_current=(season_year == CURRENT_SEASON))

            count = 0
            for _, row in standings_df.iterrows():
                # Insert team first
                insert_team(
                    cur,
                    team_id=int(row['id']),
                    name=row['team'],
                    logo_url=None  # Could construct from API-Sports CDN
                )

                # Prepare home stats
                home_stats = {
                    'played': int(row['home.played']),
                    'wins': int(row['home.win']),
                    'draws': int(row['home.draw']),
                    'losses': int(row['home.lose']),
                    'goals_for': int(row['home.goals.for']),
                    'goals_against': int(row['home.goals.against'])
                }

                # Prepare away stats
                away_stats = {
                    'played': int(row['away.played']),
                    'wins': int(row['away.win']),
                    'draws': int(row['away.draw']),
                    'losses': int(row['away.lose']),
                    'goals_for': int(row['away.goals.for']),
                    'goals_against': int(row['away.goals.against'])
                }

                # Insert standing
                insert_standing(
                    cur,
                    season_id=season_id,
                    team_id=int(row['id']),
                    rank=int(row['rank']),
                    points=int(row['points']),
                    played=int(row['all.played']),
                    wins=int(row['all.win']),
                    draws=int(row['all.draw']),
                    losses=int(row['all.lose']),
                    goals_for=int(row['all.goals.for']),
                    goals_against=int(row['all.goals.against']),
                    goal_difference=int(row['goalsDiff']),
                    home_stats=home_stats,
                    away_stats=away_stats,
                    form=row['form'] if 'form' in row else None,
                    description=row['description'] if 'description' in row else None
                )
                count += 1

            logger.info(f"✓ Inserted {count} standings")
            return count

    except Exception as e:
        logger.error(f"Failed to populate standings: {e}")
        raise


def populate_fixtures(league_id: int, season_year: int, num_fixtures: int = 50):
    """
    Populate fixtures for a specific league.

    Args:
        league_id: League ID
        season_year: Season year
        num_fixtures: Number of upcoming fixtures to fetch

    Returns:
        Number of fixtures inserted
    """
    logger.info(f"Fetching {num_fixtures} fixtures for league {league_id}...")

    try:
        fixtures_df = get_fixtures(league_id, num_fixtures)

        if fixtures_df.empty:
            logger.warning("No fixtures data fetched")
            return 0

        logger.info(f"Fetched {len(fixtures_df)} fixtures")

        with get_db_cursor() as cur:
            # Get or create season
            season_id = get_season_id(cur, league_id, season_year)
            if season_id is None:
                season_id = populate_season(league_id, season_year, is_current=(season_year == CURRENT_SEASON))

            count = 0
            for _, row in fixtures_df.iterrows():
                # Insert teams first
                insert_team(
                    cur,
                    team_id=int(row['home.id']),
                    name=row['home.name']
                )
                insert_team(
                    cur,
                    team_id=int(row['away.id']),
                    name=row['away.name']
                )

                # Insert fixture
                insert_fixture(
                    cur,
                    fixture_id=int(row['id']),
                    season_id=season_id,
                    round_name=row['round'],
                    date=row['date'].isoformat(),
                    home_team_id=int(row['home.id']),
                    away_team_id=int(row['away.id']),
                    venue=row['venue'],
                    city=row['city'],
                    status='NS'  # Not Started - default for upcoming fixtures
                )
                count += 1

            logger.info(f"✓ Inserted {count} fixtures")
            return count

    except Exception as e:
        logger.error(f"Failed to populate fixtures: {e}")
        raise


def ensure_league_exists(league_id: int, league_name: str):
    """
    Ensure league exists in the database before populating data.

    Args:
        league_id: League ID
        league_name: League name
    """
    logger.info(f"Ensuring league '{league_name}' (ID: {league_id}) exists...")

    try:
        with get_db_cursor() as cur:
            insert_league(
                cur,
                league_id=league_id,
                name=league_name,
                league_type="League",
                country="England" if league_name == "Premier League" else "Spain"
            )
            logger.info(f"✓ League '{league_name}' ready")

    except Exception as e:
        logger.error(f"Failed to ensure league exists: {e}")
        raise


def populate_premier_league(season_year: int = CURRENT_SEASON, include_fixtures: bool = True):
    """
    Populate all Premier League data for a specific season.

    Args:
        season_year: Season year
        include_fixtures: Whether to include fixtures

    Returns:
        Dict with counts of inserted records
    """
    logger.info(f"Populating Premier League data for season {season_year}...")

    league_id = LEAGUE_IDS["Premier League"]
    results = {}

    try:
        # Ensure league exists first
        ensure_league_exists(league_id, "Premier League")

        # Populate standings (this will also populate teams)
        standings_count = populate_standings(league_id, season_year)
        results['standings'] = standings_count

        # Small delay to respect API rate limits
        time.sleep(API_RATE_LIMIT_DELAY)

        # Populate fixtures
        if include_fixtures:
            fixtures_count = populate_fixtures(league_id, season_year)
            results['fixtures'] = fixtures_count

        logger.info(f"✓ Premier League population complete: {results}")
        return results

    except Exception as e:
        logger.error(f"Failed to populate Premier League: {e}")
        raise


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Populate football database with API data")
    parser.add_argument(
        '--season',
        type=int,
        default=CURRENT_SEASON,
        help=f'Season year to populate (default: {CURRENT_SEASON})'
    )
    parser.add_argument(
        '--league',
        type=str,
        default='premier',
        choices=['premier', 'laliga', 'all'],
        help='League to populate (default: premier)'
    )
    parser.add_argument(
        '--no-fixtures',
        action='store_true',
        help='Skip populating fixtures'
    )

    args = parser.parse_args()

    logger.info("Starting database population...")
    logger.info(f"Season: {args.season}, League: {args.league}")

    try:
        # Populate Premier League
        if args.league in ['premier', 'all']:
            populate_premier_league(
                season_year=args.season,
                include_fixtures=not args.no_fixtures
            )

        # Populate La Liga
        if args.league in ['laliga', 'all']:
            logger.info("La Liga population not yet implemented")
            # TODO: Implement La Liga population

        logger.info("✓ Database population complete!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Population failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
