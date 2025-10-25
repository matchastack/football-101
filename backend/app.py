"""
Football-101 Flask API Server.

This module provides REST API endpoints for serving Premier League football data
from the PostgreSQL database. All data is served from the database only - no external
API calls are made.
"""

import logging

from flask import Flask, jsonify, Response, request
from flask_cors import CORS

from upload import (
    get_db_cursor,
    get_standings_by_season,
    get_fixtures_by_season,
    get_all_teams,
    get_team_by_id,
    get_all_seasons
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Application Configuration
class Config:
    """Flask application configuration."""

    DEBUG = True
    PORT = 9102
    DEFAULT_LEAGUE = "Premier League"
    DEFAULT_SEASON = 2024


# Initialize Flask app
app = Flask(__name__)
CORS(app)


# API Routes

@app.route("/")
def health_check() -> Response:
    """
    Health check endpoint.

    Returns:
        JSON response indicating API status
    """
    return jsonify({
        "message": "Football-101 API",
        "status": "healthy",
        "version": "1.0.0",
        "data_source": "PostgreSQL Database"
    })


@app.route("/api/seasons")
def get_seasons() -> Response:
    """
    Get all available seasons.

    Query parameters:
        league: Filter by league name (optional)

    Returns:
        JSON array of seasons
    """
    try:
        league_name = request.args.get('league', Config.DEFAULT_LEAGUE)

        with get_db_cursor() as cur:
            seasons = get_all_seasons(cur, league_name)

        return jsonify({
            "success": True,
            "count": len(seasons),
            "data": seasons
        })

    except Exception as e:
        logger.error(f"Error fetching seasons: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch seasons"
        }), 500


@app.route("/api/standings")
def get_standings() -> Response:
    """
    Get league standings.

    Query parameters:
        league: League name (default: Premier League)
        season: Season year (default: 2024)

    Returns:
        JSON response with team standings data
    """
    try:
        league_name = request.args.get('league', Config.DEFAULT_LEAGUE)
        season_year = int(request.args.get('season', Config.DEFAULT_SEASON))

        with get_db_cursor() as cur:
            standings = get_standings_by_season(cur, league_name, season_year)

        if not standings:
            return jsonify({
                "success": False,
                "error": f"No standings found for {league_name} {season_year}"
            }), 404

        return jsonify({
            "success": True,
            "league": league_name,
            "season": season_year,
            "count": len(standings),
            "data": standings
        })

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid season parameter"
        }), 400
    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch standings"
        }), 500


@app.route("/api/fixtures")
def get_fixtures() -> Response:
    """
    Get fixtures.

    Query parameters:
        league: League name (default: Premier League)
        season: Season year (default: 2024)
        limit: Maximum number of fixtures to return (optional)

    Returns:
        JSON response with fixtures data
    """
    try:
        league_name = request.args.get('league', Config.DEFAULT_LEAGUE)
        season_year = int(request.args.get('season', Config.DEFAULT_SEASON))
        limit = request.args.get('limit', type=int)

        with get_db_cursor() as cur:
            fixtures = get_fixtures_by_season(cur, league_name, season_year, limit)

        if not fixtures:
            return jsonify({
                "success": False,
                "error": f"No fixtures found for {league_name} {season_year}"
            }), 404

        return jsonify({
            "success": True,
            "league": league_name,
            "season": season_year,
            "count": len(fixtures),
            "data": fixtures
        })

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid season or limit parameter"
        }), 400
    except Exception as e:
        logger.error(f"Error fetching fixtures: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch fixtures"
        }), 500


@app.route("/api/teams")
def get_teams() -> Response:
    """
    Get all teams.

    Query parameters:
        league: Filter by league name (optional)

    Returns:
        JSON array of teams
    """
    try:
        league_name = request.args.get('league')

        with get_db_cursor() as cur:
            teams = get_all_teams(cur, league_name)

        return jsonify({
            "success": True,
            "count": len(teams),
            "data": teams
        })

    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch teams"
        }), 500


@app.route("/api/teams/<int:team_id>")
def get_team(team_id: int) -> Response:
    """
    Get team details by ID.

    Args:
        team_id: Team ID

    Returns:
        JSON response with team data
    """
    try:
        with get_db_cursor() as cur:
            team = get_team_by_id(cur, team_id)

        if not team:
            return jsonify({
                "success": False,
                "error": f"Team with ID {team_id} not found"
            }), 404

        return jsonify({
            "success": True,
            "data": team
        })

    except Exception as e:
        logger.error(f"Error fetching team: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch team"
        }), 500


# Legacy endpoints for backward compatibility
@app.route("/premier-league/table")
def get_premier_league_table_legacy() -> Response:
    """
    Get Premier League standings table (legacy endpoint).

    Returns current season by default.
    Use /api/standings?league=Premier League&season=2024 instead.

    Returns:
        JSON response with team standings data
    """
    try:
        with get_db_cursor() as cur:
            standings = get_standings_by_season(cur, "Premier League", Config.DEFAULT_SEASON)

        if not standings:
            return jsonify({"error": "No standings found"}), 404

        # Return in original format for backward compatibility
        return jsonify(standings)

    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        return jsonify({"error": "Failed to fetch standings"}), 500


@app.route("/premier-league/fixtures")
def get_premier_league_fixtures_legacy() -> Response:
    """
    Get Premier League fixtures (legacy endpoint).

    Returns current season by default.
    Use /api/fixtures?league=Premier League&season=2024 instead.

    Returns:
        JSON response with fixtures data
    """
    try:
        with get_db_cursor() as cur:
            fixtures = get_fixtures_by_season(cur, "Premier League", Config.DEFAULT_SEASON, limit=50)

        if not fixtures:
            return jsonify({"error": "No fixtures found"}), 404

        # Return in original format for backward compatibility
        return jsonify(fixtures)

    except Exception as e:
        logger.error(f"Error fetching fixtures: {e}")
        return jsonify({"error": "Failed to fetch fixtures"}), 500


if __name__ == "__main__":
    logger.info(f"Starting Flask server on port {Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)
