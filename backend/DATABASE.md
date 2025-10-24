# Database Documentation

PostgreSQL database setup and usage for the Football-101 application.

## Table of Contents

- [Database Schema](#database-schema)
- [Setup](#setup)
- [Population](#population)
- [Queries](#queries)
- [Maintenance](#maintenance)

## Database Schema

The database consists of 5 main tables and 3 views:

### Tables

1. **leagues** - Football leagues information
   - Primary key: `id`
   - Fields: name, type, country, logo_url

2. **seasons** - Season information for each league
   - Primary key: `id` (auto-increment)
   - Foreign key: `league_id` → leagues(id)
   - Unique constraint: (league_id, year)
   - Fields: year, start_date, end_date, is_current

3. **teams** - Team information
   - Primary key: `id`
   - Fields: name, code, country, founded, logo_url, venue_name, venue_city

4. **standings** - League standings/table data
   - Primary key: `id` (auto-increment)
   - Foreign keys: `season_id` → seasons(id), `team_id` → teams(id)
   - Unique constraint: (season_id, team_id)
   - Fields: rank, points, played, wins, draws, losses, goals (for/against/difference)
   - Separate stats for: overall, home, away
   - Additional: form, description

5. **fixtures** - Match fixtures (past and future)
   - Primary key: `id` (from API)
   - Foreign keys: `season_id` → seasons(id), `home_team_id` → teams(id), `away_team_id` → teams(id)
   - Fields: round, date, venue, city, referee, scores, status

### Views

1. **current_standings** - Current season standings with team names
2. **upcoming_fixtures** - Future fixtures with team names
3. **recent_results** - Past results with scores

### Indexes

- All foreign keys are indexed
- Additional indexes on: league names, team names, fixture dates, standings rank

## Setup

### Prerequisites

- PostgreSQL 15+ running (locally or via Docker)
- PostgreSQL superuser credentials (e.g., `postgres` user)
- Python virtual environment activated
- Environment variables configured in `.env`

### Environment Variables

Create a `backend/.env` file (copy from `.env.example`):

```env
# RapidAPI Football API Configuration
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
RAPIDAPI_KEY=your_rapidapi_key_here

# PostgreSQL Superuser (for database initialization)
# Only needed when running init_db.py
POSTGRES_SUPERUSER=postgres
POSTGRES_SUPERUSER_PASSWORD=your_superuser_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application Database Configuration
# The init_db.py script will create this user and database
DB_USER=football_user
DB_PASSWORD=your_secure_password_here
DB_NAME=football_db
```

### Initialize Database

The `init_db.py` script handles everything automatically:
- Creates the database user with appropriate privileges
- Creates the database (if it doesn't exist)
- Creates all tables, indexes, views, and triggers

**Step-by-step:**

1. **Start PostgreSQL** (locally or via Docker):

```bash
# Option 1: Using Docker
cd docker
docker compose up -d db

# Option 2: Using local PostgreSQL (if already installed)
# Make sure PostgreSQL is running
pg_ctl status
```

2. **Configure environment variables**:

```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
```

3. **Run initialization script**:

```bash
# Activate virtual environment
source bin/activate

# Run init script
python init_db.py
```

The script will:
1. ✓ Validate environment variables
2. ✓ Connect as PostgreSQL superuser
3. ✓ Create application user (with minimal required privileges)
4. ✓ Create database (owned by application user)
5. ✓ Grant appropriate privileges
6. ✓ Create all tables, indexes, views, and triggers

**Expected output:**

```
2024-10-24 20:00:00 - INFO - Starting database initialization...
2024-10-24 20:00:00 - INFO - ✓ Environment variables validated
2024-10-24 20:00:00 - INFO - ✓ Connected as superuser 'postgres'
2024-10-24 20:00:00 - INFO - Creating user 'football_user'...
2024-10-24 20:00:00 - INFO - ✓ User 'football_user' created successfully
2024-10-24 20:00:00 - INFO - Creating database 'football_db'...
2024-10-24 20:00:00 - INFO - ✓ Database 'football_db' created successfully
2024-10-24 20:00:00 - INFO - Granting privileges to user 'football_user'...
2024-10-24 20:00:00 - INFO - ✓ Privileges granted to 'football_user'
2024-10-24 20:00:00 - INFO - Superuser connection closed
2024-10-24 20:00:00 - INFO - ✓ Connected to 'football_db' as 'football_user'
2024-10-24 20:00:00 - INFO - Reading schema from /path/to/db_schema.sql
2024-10-24 20:00:00 - INFO - Executing schema SQL...
2024-10-24 20:00:01 - INFO - ✓ Database schema created successfully!
2024-10-24 20:00:01 - INFO - Created 5 tables:
2024-10-24 20:00:01 - INFO -   - fixtures
2024-10-24 20:00:01 - INFO -   - leagues
2024-10-24 20:00:01 - INFO -   - seasons
2024-10-24 20:00:01 - INFO -   - standings
2024-10-24 20:00:01 - INFO -   - teams
2024-10-24 20:00:01 - INFO - Created 3 views:
2024-10-24 20:00:01 - INFO -   - current_standings
2024-10-24 20:00:01 - INFO -   - recent_results
2024-10-24 20:00:01 - INFO -   - upcoming_fixtures
2024-10-24 20:00:01 - INFO - Database initialization complete!
```

**Re-running the script:**

If you run `init_db.py` again, it will:
- Skip creating the user if it already exists
- Skip creating the database if it already exists
- Recreate all tables, views, and triggers (using DROP IF EXISTS)

This makes it safe to re-run for schema updates.

## Population

### Populate from API

Use the `populate_db.py` script to fetch data from RapidAPI and populate the database:

```bash
# Populate current season Premier League
python populate_db.py

# Populate specific season
python populate_db.py --season 2023

# Populate without fixtures (standings only)
python populate_db.py --no-fixtures

# View all options
python populate_db.py --help
```

The script will:
1. Fetch standings data from API
2. Insert leagues, seasons, and teams
3. Insert standings for all teams
4. Fetch and insert upcoming fixtures

### Manual Population

You can also manually insert data using the `upload.py` functions:

```python
from upload import get_db_cursor, insert_league, insert_team, insert_season

with get_db_cursor() as cur:
    # Insert a league
    insert_league(cur, league_id=39, name="Premier League", league_type="League")

    # Insert a team
    insert_team(cur, team_id=33, name="Manchester United")

    # Insert a season
    season_id = insert_season(cur, league_id=39, year=2024,
                              start_date="2024-08-01", end_date="2025-05-31",
                              is_current=True)
```

## Queries

### Using Views

The database provides convenient views for common queries:

```sql
-- Get current Premier League standings
SELECT * FROM current_standings
WHERE league_name = 'Premier League'
ORDER BY rank;

-- Get upcoming Premier League fixtures
SELECT * FROM upcoming_fixtures
WHERE league_name = 'Premier League'
LIMIT 10;

-- Get recent results
SELECT * FROM recent_results
WHERE league_name = 'Premier League'
ORDER BY date DESC
LIMIT 10;
```

### Using Python Functions

```python
from upload import get_db_cursor, get_current_standings, get_upcoming_fixtures

with get_db_cursor() as cur:
    # Get current standings
    standings = get_current_standings(cur, "Premier League")

    # Get upcoming fixtures
    fixtures = get_upcoming_fixtures(cur, "Premier League", limit=20)
```

### Custom Queries

```sql
-- Get team head-to-head record
SELECT
    COUNT(*) as matches,
    SUM(CASE WHEN home_score > away_score AND home_team_id = 33 THEN 1
             WHEN away_score > home_score AND away_team_id = 33 THEN 1
             ELSE 0 END) as team_wins,
    SUM(CASE WHEN home_score = away_score THEN 1 ELSE 0 END) as draws
FROM fixtures
WHERE (home_team_id = 33 OR away_team_id = 33)
  AND (home_team_id = 50 OR away_team_id = 50)
  AND status = 'FT';

-- Get top scorers (would need additional stats table)
-- Get team form over last 5 games
SELECT
    t.name,
    st.form,
    st.points,
    st.rank
FROM standings st
JOIN teams t ON st.team_id = t.id
JOIN seasons s ON st.season_id = s.id
WHERE s.is_current = TRUE
ORDER BY st.rank;
```

## Maintenance

### Update Data

To refresh data with latest from API:

```bash
# Re-run population script (uses ON CONFLICT DO UPDATE)
python populate_db.py
```

The INSERT statements use `ON CONFLICT DO UPDATE` to automatically update existing records.

### Backup Database

```bash
# Backup to file
docker exec -t football-db-1 pg_dump -U your_username football_db > backup.sql

# Restore from file
docker exec -i football-db-1 psql -U your_username football_db < backup.sql
```

### Reset Database

To completely reset the database:

```bash
# Drop and recreate database
docker exec -it football-db-1 psql -U your_username -d postgres -c "DROP DATABASE IF EXISTS football_db;"
docker exec -it football-db-1 psql -U your_username -d postgres -c "CREATE DATABASE football_db;"

# Re-initialize schema
python init_db.py

# Re-populate data
python populate_db.py
```

### Monitor Database

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check record counts
SELECT 'leagues' as table_name, COUNT(*) as count FROM leagues
UNION ALL
SELECT 'seasons', COUNT(*) FROM seasons
UNION ALL
SELECT 'teams', COUNT(*) FROM teams
UNION ALL
SELECT 'standings', COUNT(*) FROM standings
UNION ALL
SELECT 'fixtures', COUNT(*) FROM fixtures;

-- Check for missing data
SELECT s.year, s.league_id, COUNT(st.id) as teams_count
FROM seasons s
LEFT JOIN standings st ON s.id = st.season_id
WHERE s.is_current = TRUE
GROUP BY s.year, s.league_id;
```

## Troubleshooting

### Connection Issues

```bash
# Test database connection
python -c "from upload import get_db_connection; conn = get_db_connection(); print('Connected!'); conn.close()"
```

### Missing Tables

If tables are missing, re-run `init_db.py`:

```bash
python init_db.py
```

### Data Not Showing

1. Check if season is marked as current:
```sql
UPDATE seasons SET is_current = TRUE WHERE league_id = 39 AND year = 2024;
```

2. Verify data exists:
```sql
SELECT COUNT(*) FROM standings;
SELECT COUNT(*) FROM fixtures;
```

### API Rate Limits

If you hit API rate limits:
- Increase `API_RATE_LIMIT_DELAY` in `populate_db.py`
- Use cached pickle files instead of live API calls
- Check your RapidAPI subscription limits

## Schema Migration

When updating the schema:

1. Create a migration SQL file
2. Test on development database
3. Backup production database
4. Apply migration
5. Verify data integrity

Example migration:

```sql
-- Add new column
ALTER TABLE teams ADD COLUMN twitter_handle VARCHAR(50);

-- Create index
CREATE INDEX idx_teams_twitter ON teams(twitter_handle);

-- Update view
CREATE OR REPLACE VIEW current_standings AS
-- updated view definition
...
```
