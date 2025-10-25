# Football-101 API Documentation

REST API for accessing Premier League football data from PostgreSQL database.

## Base URL

```
http://localhost:9102
```

## Data Source

All data is served directly from the PostgreSQL database. **No external API calls are made** during request handling.

## Response Format

All endpoints return JSON responses with the following structure:

**Success Response:**
```json
{
  "success": true,
  "count": 10,
  "data": [...]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Endpoints

### Health Check

Check API status and version.

```
GET /
```

**Response:**
```json
{
  "message": "Football-101 API",
  "status": "healthy",
  "version": "1.0.0",
  "data_source": "PostgreSQL Database"
}
```

---

### Get Seasons

Get all available seasons.

```
GET /api/seasons
```

**Query Parameters:**
- `league` (optional): League name (default: "Premier League")

**Example:**
```bash
curl "http://localhost:9102/api/seasons?league=Premier%20League"
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 3,
      "year": 2024,
      "start_date": "2024-08-01",
      "end_date": "2025-05-31",
      "is_current": true,
      "league_name": "Premier League"
    },
    ...
  ]
}
```

---

### Get Standings

Get league standings for a specific season.

```
GET /api/standings
```

**Query Parameters:**
- `league` (optional): League name (default: "Premier League")
- `season` (optional): Season year (default: 2024)

**Example:**
```bash
curl "http://localhost:9102/api/standings?league=Premier%20League&season=2024"
```

**Response:**
```json
{
  "success": true,
  "league": "Premier League",
  "season": 2024,
  "count": 20,
  "data": [
    {
      "rank": 1,
      "id": 40,
      "team": "Liverpool",
      "logo_url": null,
      "points": 84,
      "played": 38,
      "wins": 25,
      "draws": 9,
      "losses": 4,
      "goals_for": 86,
      "goals_against": 41,
      "goal_difference": 45,
      "form": "DLDLW",
      "home_played": 19,
      "home_wins": 14,
      "home_draws": 4,
      "home_losses": 1,
      "home_goals_for": 42,
      "home_goals_against": 16,
      "away_played": 19,
      "away_wins": 11,
      "away_draws": 5,
      "away_losses": 3,
      "away_goals_for": 44,
      "away_goals_against": 25
    },
    ...
  ]
}
```

**Standing Fields:**
- `rank`: Position in table
- `id`: Team ID
- `team`: Team name
- `points`: Total points
- `played`: Games played
- `wins`, `draws`, `losses`: Match results
- `goals_for`, `goals_against`: Goals scored/conceded
- `goal_difference`: Goal difference
- `form`: Recent form (e.g., "WWDLW")
- `home_*`: Home statistics
- `away_*`: Away statistics

---

### Get Fixtures

Get fixtures for a specific season.

```
GET /api/fixtures
```

**Query Parameters:**
- `league` (optional): League name (default: "Premier League")
- `season` (optional): Season year (default: 2024)
- `limit` (optional): Maximum number of fixtures to return

**Example:**
```bash
curl "http://localhost:9102/api/fixtures?season=2022&limit=5"
```

**Response:**
```json
{
  "success": true,
  "league": "Premier League",
  "season": 2022,
  "count": 5,
  "data": [
    {
      "id": 1379057,
      "date": "2025-10-25T14:00:00",
      "round": "Regular Season - 9",
      "venue": "St. James' Park",
      "city": "Newcastle",
      "home_id": 34,
      "home_name": "Newcastle",
      "away_id": 36,
      "away_name": "Fulham",
      "home_score": null,
      "away_score": null,
      "status": "NS"
    },
    ...
  ]
}
```

**Fixture Fields:**
- `id`: Fixture ID
- `date`: Match date/time (ISO 8601)
- `round`: Round name
- `venue`, `city`: Match location
- `home_id`, `home_name`: Home team
- `away_id`, `away_name`: Away team
- `home_score`, `away_score`: Scores (null if not played)
- `status`: Match status (NS=Not Started, FT=Full Time, etc.)

---

### Get Teams

Get all teams, optionally filtered by league.

```
GET /api/teams
```

**Query Parameters:**
- `league` (optional): Filter by league name

**Example:**
```bash
curl "http://localhost:9102/api/teams?league=Premier%20League"
```

**Response:**
```json
{
  "success": true,
  "count": 24,
  "data": [
    {
      "id": 42,
      "name": "Arsenal",
      "code": null,
      "country": null,
      "founded": null,
      "logo_url": null,
      "venue_name": null,
      "venue_city": null
    },
    ...
  ]
}
```

---

### Get Team by ID

Get detailed information for a specific team.

```
GET /api/teams/<team_id>
```

**Path Parameters:**
- `team_id`: Team ID (integer)

**Example:**
```bash
curl "http://localhost:9102/api/teams/42"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "name": "Arsenal",
    "code": null,
    "country": null,
    "founded": null,
    "logo_url": null,
    "venue_name": null,
    "venue_city": null
  }
}
```

**Error (404):**
```json
{
  "success": false,
  "error": "Team with ID 999 not found"
}
```

---

## Legacy Endpoints

For backward compatibility, these endpoints are maintained:

### Legacy: Get Premier League Table

```
GET /premier-league/table
```

Returns current season (2024) standings in array format.

**Response:**
```json
[
  {
    "rank": 1,
    "id": 40,
    "team": "Liverpool",
    "points": 84,
    ...
  },
  ...
]
```

**Note:** Use `/api/standings` for new implementations.

---

### Legacy: Get Premier League Fixtures

```
GET /premier-league/fixtures
```

Returns current season (2024) fixtures (limit 50) in array format.

**Response:**
```json
[
  {
    "id": 1379057,
    "date": "2025-10-25T14:00:00",
    "home_id": 34,
    "home_name": "Newcastle",
    ...
  },
  ...
]
```

**Note:** Use `/api/fixtures` for new implementations.

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Internal Server Error (database or server error) |

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Get current standings
fetch('http://localhost:9102/api/standings?season=2024')
  .then(response => response.json())
  .then(data => {
    console.log('Standings:', data.data);
  })
  .catch(error => console.error('Error:', error));

// Get fixtures with limit
fetch('http://localhost:9102/api/fixtures?season=2022&limit=10')
  .then(response => response.json())
  .then(data => {
    console.log('Fixtures:', data.data);
  });

// Get team details
fetch('http://localhost:9102/api/teams/42')
  .then(response => response.json())
  .then(data => {
    console.log('Team:', data.data);
  });
```

### Python (requests)

```python
import requests

# Get standings
response = requests.get('http://localhost:9102/api/standings', params={
    'league': 'Premier League',
    'season': 2024
})
standings = response.json()
print(f"Found {standings['count']} teams")

# Get fixtures
response = requests.get('http://localhost:9102/api/fixtures', params={
    'season': 2022,
    'limit': 5
})
fixtures = response.json()
for fixture in fixtures['data']:
    print(f"{fixture['home_name']} vs {fixture['away_name']}")

# Get team
response = requests.get('http://localhost:9102/api/teams/42')
team = response.json()
print(f"Team: {team['data']['name']}")
```

### cURL

```bash
# Get all seasons
curl "http://localhost:9102/api/seasons"

# Get standings for 2023 season
curl "http://localhost:9102/api/standings?season=2023"

# Get first 3 fixtures from 2022 season
curl "http://localhost:9102/api/fixtures?season=2022&limit=3"

# Get all teams in Premier League
curl "http://localhost:9102/api/teams?league=Premier%20League"

# Get team by ID
curl "http://localhost:9102/api/teams/42"

# Health check
curl "http://localhost:9102/"
```

## Rate Limiting

Currently, no rate limiting is enforced. All data is served from the local database.

## CORS

CORS is enabled for all origins. For production, configure specific origins in `app.py`.

## Database Schema

The API queries the following database tables:
- `leagues` - League information
- `seasons` - Season data per league
- `teams` - Team information
- `standings` - League table data
- `fixtures` - Match fixtures

See `DATABASE.md` for detailed schema documentation.

## Development

### Running the API

```bash
cd backend
source bin/activate
python app.py
```

Server runs on `http://localhost:9102` with debug mode enabled.

### Adding New Endpoints

1. Add query function to `upload.py`
2. Add route to `app.py`
3. Update this documentation
4. Test endpoint

### Testing

```bash
# Test all endpoints
curl http://localhost:9102/
curl "http://localhost:9102/api/seasons"
curl "http://localhost:9102/api/standings?season=2024"
curl "http://localhost:9102/api/fixtures?season=2022&limit=5"
curl "http://localhost:9102/api/teams"
curl "http://localhost:9102/api/teams/42"
```

## Notes

- All timestamps are in ISO 8601 format
- Dates are in YYYY-MM-DD format
- Team logos URLs are currently null (can be added later)
- Fixture scores are null for unplayed matches
- Form strings show last 5 games (W=Win, D=Draw, L=Loss)
