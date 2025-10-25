"""
Football-101 Flask API Server.

This module provides REST API endpoints for serving Premier League football data
including standings and fixtures.
"""

import logging
import os
from pathlib import Path
from typing import Tuple

from flask import Flask, jsonify, Response
from flask_cors import CORS

from api_data import get_premier_league_standing, get_premier_league_fixtures
from utils import load_pkl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Application Configuration
class Config:
    """Flask application configuration."""

    DEBUG = True
    PORT = 9102
    DATA_DIR = Path("../data")
    STANDINGS_CACHE = DATA_DIR / "pl22.pkl"
    FIXTURES_CACHE = DATA_DIR / "fixtures.pkl"
    USE_CACHE = True  # Set to False to use live API


# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Load cached data at startup
def load_cached_data() -> Tuple:
    """
    Load cached data from pickle files.

    Returns:
        Tuple of (standings_df, fixtures_df)

    Raises:
        FileNotFoundError: If cache files don't exist
    """
    try:
        standings = load_pkl(str(Config.STANDINGS_CACHE))
        fixtures = load_pkl(str(Config.FIXTURES_CACHE))
        logger.info("Successfully loaded cached data")
        return standings, fixtures
    except FileNotFoundError as e:
        logger.error(f"Cache file not found: {e}")
        raise


# Load data if using cache
if Config.USE_CACHE:
    try:
        cached_standings, cached_fixtures = load_cached_data()
    except FileNotFoundError:
        logger.warning("Cache files not found. API will fail until cache is created.")
        cached_standings, cached_fixtures = None, None


# API Routes

@app.route("/")
def health_check() -> Response:
    """
    Health check endpoint.

    Returns:
        JSON response indicating API status
    """
    return jsonify({"message": "api is working", "status": "healthy"})


@app.route("/premier-league/table")
def get_premier_league_table() -> Response:
    """
    Get Premier League standings table.

    Returns:
        JSON response with team standings data

    Raises:
        500 Internal Server Error if data retrieval fails
    """
    try:
        if Config.USE_CACHE:
            if cached_standings is None:
                return jsonify({"error": "Cache not available"}), 500
            data = cached_standings
        else:
            # Fetch live data from API
            data = get_premier_league_standing(2022)

        return jsonify(data.to_json(orient='records', index=False))

    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        return jsonify({"error": "Failed to fetch standings"}), 500


@app.route("/premier-league/fixtures")
def get_premier_league_fixtures_endpoint() -> Response:
    """
    Get Premier League fixtures.

    Returns:
        JSON response with fixtures data

    Raises:
        500 Internal Server Error if data retrieval fails
    """
    try:
        if Config.USE_CACHE:
            if cached_fixtures is None:
                return jsonify({"error": "Cache not available"}), 500
            data = cached_fixtures
        else:
            # Fetch live data from API
            data = get_premier_league_fixtures()

        return jsonify(data.to_json(orient='records', index=False))

    except Exception as e:
        logger.error(f"Error fetching fixtures: {e}")
        return jsonify({"error": "Failed to fetch fixtures"}), 500


if __name__ == "__main__":
    logger.info(f"Starting Flask server on port {Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)
