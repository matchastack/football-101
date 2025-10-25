"""
Database utilities for PostgreSQL operations.

This module provides utilities for connecting to PostgreSQL database
and managing table operations.
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection() -> connection:
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        Database connection object

    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", os.getenv("HOST", "localhost")),
            port=os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        logger.info("Database connection established")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


@contextmanager
def get_db_cursor() -> Generator[cursor, None, None]:
    """
    Context manager for database cursor with automatic cleanup.

    Yields:
        Database cursor object

    Example:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM table")
            results = cur.fetchall()
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        yield cur
        conn.commit()
        logger.info("Transaction committed successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction failed, rolling back: {e}")
        raise
    finally:
        cur.close()
        conn.close()
        logger.info("Database connection closed")


def create_leagues_table(cur: cursor) -> None:
    """
    Create the leagues table if it doesn't exist.

    Args:
        cur: Database cursor object

    Raises:
        psycopg2.Error: If table creation fails
    """
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(255) NOT NULL,
                start TIMESTAMP NOT NULL,
                end TIMESTAMP NOT NULL
            )
        """)
        logger.info("Leagues table created successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to create leagues table: {e}")
        raise


def create_test_table(cur: cursor) -> None:
    """
    Create a test table for development purposes.

    Args:
        cur: Database cursor object

    Raises:
        psycopg2.Error: If table creation fails
    """
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test (
                column1 INTEGER PRIMARY KEY,
                column2 VARCHAR(255) NOT NULL
            )
        """)
        logger.info("Test table created successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to create test table: {e}")
        raise


# ============================================================================
# INSERT FUNCTIONS
# ============================================================================

def insert_league(cur: cursor, league_id: int, name: str, league_type: str,
                  country: str = None, logo_url: str = None) -> None:
    """
    Insert or update a league record.

    Args:
        cur: Database cursor
        league_id: League ID from API
        name: League name
        league_type: Type of league (e.g., 'League', 'Cup')
        country: Country name
        logo_url: URL to league logo

    Raises:
        psycopg2.Error: If insert fails
    """
    try:
        cur.execute("""
            INSERT INTO leagues (id, name, type, country, logo_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                type = EXCLUDED.type,
                country = EXCLUDED.country,
                logo_url = EXCLUDED.logo_url,
                updated_at = CURRENT_TIMESTAMP
        """, (league_id, name, league_type, country, logo_url))
        logger.debug(f"Inserted/updated league: {name}")
    except psycopg2.Error as e:
        logger.error(f"Failed to insert league {name}: {e}")
        raise


def insert_season(cur: cursor, league_id: int, year: int,
                  start_date: str, end_date: str, is_current: bool = False) -> int:
    """
    Insert or update a season record.

    Args:
        cur: Database cursor
        league_id: League ID
        year: Season year
        start_date: Season start date (YYYY-MM-DD)
        end_date: Season end date (YYYY-MM-DD)
        is_current: Whether this is the current season

    Returns:
        Season ID (database ID, not API ID)

    Raises:
        psycopg2.Error: If insert fails
    """
    try:
        cur.execute("""
            INSERT INTO seasons (league_id, year, start_date, end_date, is_current)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (league_id, year) DO UPDATE SET
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                is_current = EXCLUDED.is_current,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """, (league_id, year, start_date, end_date, is_current))
        season_id = cur.fetchone()[0]
        logger.debug(f"Inserted/updated season {year} for league {league_id}")
        return season_id
    except psycopg2.Error as e:
        logger.error(f"Failed to insert season {year}: {e}")
        raise


def insert_team(cur: cursor, team_id: int, name: str, code: str = None,
                country: str = None, founded: int = None, logo_url: str = None,
                venue_name: str = None, venue_city: str = None) -> None:
    """
    Insert or update a team record.

    Args:
        cur: Database cursor
        team_id: Team ID from API
        name: Team name
        code: Team code (3-letter)
        country: Country name
        founded: Year founded
        logo_url: URL to team logo
        venue_name: Home venue name
        venue_city: Venue city

    Raises:
        psycopg2.Error: If insert fails
    """
    try:
        cur.execute("""
            INSERT INTO teams (id, name, code, country, founded, logo_url, venue_name, venue_city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                code = EXCLUDED.code,
                country = EXCLUDED.country,
                founded = EXCLUDED.founded,
                logo_url = EXCLUDED.logo_url,
                venue_name = EXCLUDED.venue_name,
                venue_city = EXCLUDED.venue_city,
                updated_at = CURRENT_TIMESTAMP
        """, (team_id, name, code, country, founded, logo_url, venue_name, venue_city))
        logger.debug(f"Inserted/updated team: {name}")
    except psycopg2.Error as e:
        logger.error(f"Failed to insert team {name}: {e}")
        raise


def insert_standing(cur: cursor, season_id: int, team_id: int, rank: int,
                    points: int, played: int, wins: int, draws: int, losses: int,
                    goals_for: int, goals_against: int, goal_difference: int,
                    home_stats: dict = None, away_stats: dict = None,
                    form: str = None, description: str = None) -> None:
    """
    Insert or update a standing record.

    Args:
        cur: Database cursor
        season_id: Season ID from database
        team_id: Team ID
        rank: Team rank/position
        points: Total points
        played: Games played
        wins: Games won
        draws: Games drawn
        losses: Games lost
        goals_for: Goals scored
        goals_against: Goals conceded
        goal_difference: Goal difference
        home_stats: Dict with home statistics
        away_stats: Dict with away statistics
        form: Recent form string (e.g., 'WWDLW')
        description: Description (e.g., 'Promotion')

    Raises:
        psycopg2.Error: If insert fails
    """
    try:
        # Extract home stats
        home_played = home_stats.get('played') if home_stats else None
        home_wins = home_stats.get('wins') if home_stats else None
        home_draws = home_stats.get('draws') if home_stats else None
        home_losses = home_stats.get('losses') if home_stats else None
        home_goals_for = home_stats.get('goals_for') if home_stats else None
        home_goals_against = home_stats.get('goals_against') if home_stats else None

        # Extract away stats
        away_played = away_stats.get('played') if away_stats else None
        away_wins = away_stats.get('wins') if away_stats else None
        away_draws = away_stats.get('draws') if away_stats else None
        away_losses = away_stats.get('losses') if away_stats else None
        away_goals_for = away_stats.get('goals_for') if away_stats else None
        away_goals_against = away_stats.get('goals_against') if away_stats else None

        cur.execute("""
            INSERT INTO standings (
                season_id, team_id, rank, points, played, wins, draws, losses,
                goals_for, goals_against, goal_difference,
                home_played, home_wins, home_draws, home_losses, home_goals_for, home_goals_against,
                away_played, away_wins, away_draws, away_losses, away_goals_for, away_goals_against,
                form, description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (season_id, team_id) DO UPDATE SET
                rank = EXCLUDED.rank,
                points = EXCLUDED.points,
                played = EXCLUDED.played,
                wins = EXCLUDED.wins,
                draws = EXCLUDED.draws,
                losses = EXCLUDED.losses,
                goals_for = EXCLUDED.goals_for,
                goals_against = EXCLUDED.goals_against,
                goal_difference = EXCLUDED.goal_difference,
                home_played = EXCLUDED.home_played,
                home_wins = EXCLUDED.home_wins,
                home_draws = EXCLUDED.home_draws,
                home_losses = EXCLUDED.home_losses,
                home_goals_for = EXCLUDED.home_goals_for,
                home_goals_against = EXCLUDED.home_goals_against,
                away_played = EXCLUDED.away_played,
                away_wins = EXCLUDED.away_wins,
                away_draws = EXCLUDED.away_draws,
                away_losses = EXCLUDED.away_losses,
                away_goals_for = EXCLUDED.away_goals_for,
                away_goals_against = EXCLUDED.away_goals_against,
                form = EXCLUDED.form,
                description = EXCLUDED.description,
                updated_at = CURRENT_TIMESTAMP
        """, (season_id, team_id, rank, points, played, wins, draws, losses,
              goals_for, goals_against, goal_difference,
              home_played, home_wins, home_draws, home_losses, home_goals_for, home_goals_against,
              away_played, away_wins, away_draws, away_losses, away_goals_for, away_goals_against,
              form, description))
        logger.debug(f"Inserted/updated standing for team {team_id} in season {season_id}")
    except psycopg2.Error as e:
        logger.error(f"Failed to insert standing: {e}")
        raise


def insert_fixture(cur: cursor, fixture_id: int, season_id: int, round_name: str,
                   date: str, home_team_id: int, away_team_id: int,
                   venue: str = None, city: str = None, timezone: str = None,
                   referee: str = None, status: str = 'TBD', status_long: str = None,
                   elapsed: int = None, home_score: int = None, away_score: int = None,
                   home_ht_score: int = None, away_ht_score: int = None,
                   home_ft_score: int = None, away_ft_score: int = None) -> None:
    """
    Insert or update a fixture record.

    Args:
        cur: Database cursor
        fixture_id: Fixture ID from API
        season_id: Season ID from database
        round_name: Round name (e.g., 'Regular Season - 15')
        date: Match date and time (ISO format)
        home_team_id: Home team ID
        away_team_id: Away team ID
        venue: Venue name
        city: City name
        timezone: Timezone
        referee: Referee name
        status: Match status code
        status_long: Match status description
        elapsed: Minutes elapsed
        home_score: Home team score
        away_score: Away team score
        home_ht_score: Home halftime score
        away_ht_score: Away halftime score
        home_ft_score: Home fulltime score
        away_ft_score: Away fulltime score

    Raises:
        psycopg2.Error: If insert fails
    """
    try:
        cur.execute("""
            INSERT INTO fixtures (
                id, season_id, round, date, timezone, venue, city, referee,
                home_team_id, away_team_id, home_score, away_score,
                home_halftime_score, away_halftime_score,
                home_fulltime_score, away_fulltime_score,
                status, status_long, elapsed
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                season_id = EXCLUDED.season_id,
                round = EXCLUDED.round,
                date = EXCLUDED.date,
                timezone = EXCLUDED.timezone,
                venue = EXCLUDED.venue,
                city = EXCLUDED.city,
                referee = EXCLUDED.referee,
                home_team_id = EXCLUDED.home_team_id,
                away_team_id = EXCLUDED.away_team_id,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score,
                home_halftime_score = EXCLUDED.home_halftime_score,
                away_halftime_score = EXCLUDED.away_halftime_score,
                home_fulltime_score = EXCLUDED.home_fulltime_score,
                away_fulltime_score = EXCLUDED.away_fulltime_score,
                status = EXCLUDED.status,
                status_long = EXCLUDED.status_long,
                elapsed = EXCLUDED.elapsed,
                updated_at = CURRENT_TIMESTAMP
        """, (fixture_id, season_id, round_name, date, timezone, venue, city, referee,
              home_team_id, away_team_id, home_score, away_score,
              home_ht_score, away_ht_score, home_ft_score, away_ft_score,
              status, status_long, elapsed))
        logger.debug(f"Inserted/updated fixture {fixture_id}")
    except psycopg2.Error as e:
        logger.error(f"Failed to insert fixture {fixture_id}: {e}")
        raise


# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_season_id(cur: cursor, league_id: int, year: int) -> Optional[int]:
    """
    Get season ID for a specific league and year.

    Args:
        cur: Database cursor
        league_id: League ID
        year: Season year

    Returns:
        Season ID or None if not found
    """
    try:
        cur.execute("""
            SELECT id FROM seasons
            WHERE league_id = %s AND year = %s
        """, (league_id, year))
        result = cur.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        logger.error(f"Failed to get season ID: {e}")
        raise


def get_current_standings(cur: cursor, league_name: str = "Premier League") -> list:
    """
    Get current standings for a league.

    Args:
        cur: Database cursor
        league_name: League name

    Returns:
        List of standings rows
    """
    try:
        cur.execute("""
            SELECT * FROM current_standings
            WHERE league_name = %s
            ORDER BY rank
        """, (league_name,))
        return cur.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Failed to get current standings: {e}")
        raise


def get_upcoming_fixtures(cur: cursor, league_name: str = "Premier League", limit: int = 20) -> list:
    """
    Get upcoming fixtures for a league.

    Args:
        cur: Database cursor
        league_name: League name
        limit: Maximum number of fixtures to return

    Returns:
        List of fixture rows
    """
    try:
        cur.execute("""
            SELECT * FROM upcoming_fixtures
            WHERE league_name = %s
            ORDER BY date
            LIMIT %s
        """, (league_name, limit))
        return cur.fetchall()
    except psycopg2.Error as e:
        logger.error(f"Failed to get upcoming fixtures: {e}")
        raise


def get_standings_by_season(cur: cursor, league_name: str, season_year: int) -> list:
    """
    Get standings for a specific season.

    Args:
        cur: Database cursor
        league_name: League name
        season_year: Season year

    Returns:
        List of dictionaries with standing data
    """
    try:
        cur.execute("""
            SELECT
                st.rank,
                t.id as team_id,
                t.name as team,
                t.logo_url,
                st.points,
                st.played,
                st.wins,
                st.draws,
                st.losses,
                st.goals_for,
                st.goals_against,
                st.goal_difference,
                st.form,
                st.home_played,
                st.home_wins,
                st.home_draws,
                st.home_losses,
                st.home_goals_for,
                st.home_goals_against,
                st.away_played,
                st.away_wins,
                st.away_draws,
                st.away_losses,
                st.away_goals_for,
                st.away_goals_against
            FROM standings st
            JOIN teams t ON st.team_id = t.id
            JOIN seasons s ON st.season_id = s.id
            JOIN leagues l ON s.league_id = l.id
            WHERE l.name = %s AND s.year = %s
            ORDER BY st.rank
        """, (league_name, season_year))

        columns = [
            'rank', 'id', 'team', 'logo_url', 'points', 'played', 'wins', 'draws', 'losses',
            'goals_for', 'goals_against', 'goal_difference', 'form',
            'home_played', 'home_wins', 'home_draws', 'home_losses', 'home_goals_for', 'home_goals_against',
            'away_played', 'away_wins', 'away_draws', 'away_losses', 'away_goals_for', 'away_goals_against'
        ]

        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except psycopg2.Error as e:
        logger.error(f"Failed to get standings by season: {e}")
        raise


def get_fixtures_by_season(cur: cursor, league_name: str, season_year: int, limit: int = None) -> list:
    """
    Get fixtures for a specific season.

    Args:
        cur: Database cursor
        league_name: League name
        season_year: Season year
        limit: Optional limit on number of fixtures

    Returns:
        List of dictionaries with fixture data
    """
    try:
        query = """
            SELECT
                f.id,
                f.date,
                f.round,
                f.venue,
                f.city,
                ht.id as home_id,
                ht.name as home_name,
                at.id as away_id,
                at.name as away_name,
                f.home_score,
                f.away_score,
                f.status
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            JOIN seasons s ON f.season_id = s.id
            JOIN leagues l ON s.league_id = l.id
            WHERE l.name = %s AND s.year = %s
            ORDER BY f.date
        """

        params = [league_name, season_year]
        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cur.execute(query, params)

        columns = [
            'id', 'date', 'round', 'venue', 'city',
            'home_id', 'home_name', 'away_id', 'away_name',
            'home_score', 'away_score', 'status'
        ]

        results = []
        for row in cur.fetchall():
            result = dict(zip(columns, row))
            # Convert datetime to ISO string
            if result['date']:
                result['date'] = result['date'].isoformat()
            results.append(result)

        return results
    except psycopg2.Error as e:
        logger.error(f"Failed to get fixtures by season: {e}")
        raise


def get_all_teams(cur: cursor, league_name: str = None) -> list:
    """
    Get all teams, optionally filtered by league.

    Args:
        cur: Database cursor
        league_name: Optional league name to filter by

    Returns:
        List of dictionaries with team data
    """
    try:
        if league_name:
            # Get teams that have played in this league
            cur.execute("""
                SELECT DISTINCT
                    t.id,
                    t.name,
                    t.code,
                    t.country,
                    t.founded,
                    t.logo_url,
                    t.venue_name,
                    t.venue_city
                FROM teams t
                JOIN standings st ON t.id = st.team_id
                JOIN seasons s ON st.season_id = s.id
                JOIN leagues l ON s.league_id = l.id
                WHERE l.name = %s
                ORDER BY t.name
            """, (league_name,))
        else:
            cur.execute("""
                SELECT
                    id,
                    name,
                    code,
                    country,
                    founded,
                    logo_url,
                    venue_name,
                    venue_city
                FROM teams
                ORDER BY name
            """)

        columns = ['id', 'name', 'code', 'country', 'founded', 'logo_url', 'venue_name', 'venue_city']

        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    except psycopg2.Error as e:
        logger.error(f"Failed to get teams: {e}")
        raise


def get_team_by_id(cur: cursor, team_id: int) -> Optional[dict]:
    """
    Get team details by ID.

    Args:
        cur: Database cursor
        team_id: Team ID

    Returns:
        Dictionary with team data or None if not found
    """
    try:
        cur.execute("""
            SELECT
                id,
                name,
                code,
                country,
                founded,
                logo_url,
                venue_name,
                venue_city
            FROM teams
            WHERE id = %s
        """, (team_id,))

        row = cur.fetchone()
        if not row:
            return None

        columns = ['id', 'name', 'code', 'country', 'founded', 'logo_url', 'venue_name', 'venue_city']
        return dict(zip(columns, row))
    except psycopg2.Error as e:
        logger.error(f"Failed to get team by ID: {e}")
        raise


def get_all_seasons(cur: cursor, league_name: str = None) -> list:
    """
    Get all seasons, optionally filtered by league.

    Args:
        cur: Database cursor
        league_name: Optional league name to filter by

    Returns:
        List of dictionaries with season data
    """
    try:
        if league_name:
            cur.execute("""
                SELECT
                    s.id,
                    s.year,
                    s.start_date,
                    s.end_date,
                    s.is_current,
                    l.name as league_name
                FROM seasons s
                JOIN leagues l ON s.league_id = l.id
                WHERE l.name = %s
                ORDER BY s.year DESC
            """, (league_name,))
        else:
            cur.execute("""
                SELECT
                    s.id,
                    s.year,
                    s.start_date,
                    s.end_date,
                    s.is_current,
                    l.name as league_name
                FROM seasons s
                JOIN leagues l ON s.league_id = l.id
                ORDER BY s.year DESC
            """)

        columns = ['id', 'year', 'start_date', 'end_date', 'is_current', 'league_name']

        results = []
        for row in cur.fetchall():
            result = dict(zip(columns, row))
            # Convert dates to ISO strings
            if result['start_date']:
                result['start_date'] = result['start_date'].isoformat()
            if result['end_date']:
                result['end_date'] = result['end_date'].isoformat()
            results.append(result)

        return results
    except psycopg2.Error as e:
        logger.error(f"Failed to get seasons: {e}")
        raise