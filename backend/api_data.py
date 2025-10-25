"""
RapidAPI Football API integration module.

This module provides functions to fetch football data from the RapidAPI Football API,
including leagues, standings, and fixtures data.
"""

import os
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
HEADERS = {
    "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY")
}

# League IDs
LEAGUE_IDS = {
    "Premier League": 39,
    "La-Liga": 140
}

# Constants
DEFAULT_FIXTURES_COUNT = 20


# Helper Functions

def _make_url(endpoint: str) -> str:
    """
    Construct full API URL from endpoint.

    Args:
        endpoint: API endpoint path (e.g., "/leagues")

    Returns:
        Complete API URL
    """
    return f"{API_BASE_URL}{endpoint}"


def get_api_response(
    endpoint: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    method: str = "GET"
) -> requests.Response:
    """
    Make a request to the Football API.

    Args:
        endpoint: API endpoint path
        params: Query parameters for the request
        headers: Request headers (defaults to configured headers)
        method: HTTP method (default: "GET")

    Returns:
        Response object from the API

    Raises:
        requests.RequestException: If the request fails
    """
    if params is None:
        params = {}
    if headers is None:
        headers = HEADERS

    url = _make_url(endpoint)
    response = requests.request(method, url, headers=headers, params=params)
    response.raise_for_status()
    return response


# API Endpoint Functions


def get_leagues_data() -> pd.DataFrame:
    """
    Fetch all available leagues data from the API.

    Returns:
        DataFrame with columns: id, name, type, start, end
        Returns empty DataFrame if request fails

    Raises:
        requests.RequestException: If API request fails
    """
    response = get_api_response("/leagues")

    if response.status_code != 200:
        return pd.DataFrame()

    # Unnest top layer JSON response
    df = pd.json_normalize(response.json()["response"])

    # Explode seasons column (list of dicts)
    df = df.explode("seasons").reset_index(drop=True)

    # Unnest seasons column (dict)
    df = df.join(pd.json_normalize(df["seasons"])).drop(columns=["seasons"])

    # Select and rename columns
    df = df[["league.id", "league.name", "league.type", "start", "end"]]
    df.columns = ["id", "name", "type", "start", "end"]

    # Convert date columns to datetime
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    return df


def get_league_standing(
    season: int,
    league_id: Optional[int] = None,
    team_id: Optional[int] = None
) -> pd.DataFrame:
    """
    Fetch league standings for a specific season.

    Args:
        season: Season year (e.g., 2022)
        league_id: Optional league ID to filter by specific league
        team_id: Optional team ID to filter by specific team

    Returns:
        DataFrame with team standings including rank, points, and statistics
        Returns empty DataFrame if request fails

    Raises:
        requests.RequestException: If API request fails
    """
    # Build query parameters
    params = {"season": season}

    if league_id is not None:
        params["league"] = league_id

    if team_id is not None:
        params["team"] = team_id

    # Get standings data from API
    response = get_api_response("/standings", params=params)

    if response.status_code != 200:
        return pd.DataFrame()

    # Extract standings data from nested response
    response_data = response.json()["response"]
    standings_list = pd.json_normalize(response_data)["league.standings"][0][0]
    df = pd.DataFrame(standings_list)

    # Drop unnecessary columns
    df = df.drop(columns=["group", "status", "description", "update"])

    # Extract team name and ID from team column
    df["id"] = df["team"].apply(lambda x: x["id"])
    df["team"] = df["team"].apply(lambda x: x["name"])

    # Expand nested statistic columns (all, home, away)
    def _expand_column(col: pd.Series) -> pd.DataFrame:
        """Expand a column containing nested data."""
        return pd.json_normalize(col).add_prefix(f"{col.name}.")

    df = df.join(_expand_column(df["all"])).drop(columns=["all"])
    df = df.join(_expand_column(df["home"])).drop(columns=["home"])
    df = df.join(_expand_column(df["away"])).drop(columns=["away"])

    return df


def get_premier_league_standing(season: int) -> pd.DataFrame:
    """
    Fetch Premier League standings for a specific season.

    Args:
        season: Season year (e.g., 2022)

    Returns:
        DataFrame with Premier League standings
    """
    return get_league_standing(season, LEAGUE_IDS["Premier League"])


def get_laliga_standing(season: int) -> pd.DataFrame:
    """
    Fetch La Liga standings for a specific season.

    Args:
        season: Season year (e.g., 2022)

    Returns:
        DataFrame with La Liga standings
    """
    return get_league_standing(season, LEAGUE_IDS["La-Liga"])



def get_fixtures(league_id: int, num_fixtures: int = DEFAULT_FIXTURES_COUNT) -> pd.DataFrame:
    """
    Fetch upcoming fixtures for a specific league.

    Args:
        league_id: League ID to fetch fixtures for
        num_fixtures: Number of upcoming fixtures to fetch (default: 20)

    Returns:
        DataFrame with fixture details including teams, venue, and date
        Returns empty DataFrame if request fails

    Raises:
        requests.RequestException: If API request fails
    """
    # Build query parameters
    params = {"league": league_id, "next": num_fixtures}

    # Get fixtures data from API
    response = get_api_response("/fixtures", params=params)

    if response.status_code != 200:
        return pd.DataFrame()

    # Unnest JSON response
    df = pd.json_normalize(response.json()["response"])

    # Select relevant columns
    df = df[[
        'fixture.id', 'fixture.timezone', 'fixture.date',
        'fixture.venue.name', 'fixture.venue.city',
        'league.season', 'league.round',
        'teams.home.id', 'teams.home.name',
        'teams.away.id', 'teams.away.name'
    ]]

    # Convert date column to datetime (UTC)
    df["fixture.date"] = pd.to_datetime(df["fixture.date"], utc=True)
    # TODO: Convert to local time using fixture.timezone
    df = df.drop(columns=["fixture.timezone"])

    # Rename columns for cleaner interface
    df.columns = [
        'id', 'date', 'venue', 'city', 'season', 'round',
        'home.id', 'home.name', 'away.id', 'away.name'
    ]

    return df


def get_premier_league_fixtures() -> pd.DataFrame:
    """
    Fetch upcoming Premier League fixtures.

    Returns:
        DataFrame with Premier League fixtures
    """
    return get_fixtures(LEAGUE_IDS["Premier League"])
