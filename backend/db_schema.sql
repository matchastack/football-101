-- Football-101 Database Schema
-- PostgreSQL database schema for storing football data from RapidAPI

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS standings CASCADE;
DROP TABLE IF EXISTS fixtures CASCADE;
DROP TABLE IF EXISTS seasons CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS leagues CASCADE;

-- ============================================================================
-- LEAGUES TABLE
-- Stores information about football leagues
-- ============================================================================
CREATE TABLE leagues (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'League', 'Cup', etc.
    country VARCHAR(100),
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leagues_name ON leagues(name);
CREATE INDEX idx_leagues_country ON leagues(country);

-- ============================================================================
-- SEASONS TABLE
-- Stores season information for each league
-- ============================================================================
CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,  -- e.g., 2022 for 2022-23 season
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(league_id, year)
);

CREATE INDEX idx_seasons_league ON seasons(league_id);
CREATE INDEX idx_seasons_year ON seasons(year);
CREATE INDEX idx_seasons_current ON seasons(is_current);

-- ============================================================================
-- TEAMS TABLE
-- Stores team information
-- ============================================================================
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),  -- 3-letter code (e.g., 'ARS', 'MCI')
    country VARCHAR(100),
    founded INTEGER,
    logo_url VARCHAR(500),
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_country ON teams(country);

-- ============================================================================
-- STANDINGS TABLE
-- Stores league standings/table data
-- ============================================================================
CREATE TABLE standings (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    points INTEGER NOT NULL,

    -- Overall statistics
    played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    draws INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    goals_for INTEGER NOT NULL,
    goals_against INTEGER NOT NULL,
    goal_difference INTEGER NOT NULL,

    -- Home statistics
    home_played INTEGER,
    home_wins INTEGER,
    home_draws INTEGER,
    home_losses INTEGER,
    home_goals_for INTEGER,
    home_goals_against INTEGER,

    -- Away statistics
    away_played INTEGER,
    away_wins INTEGER,
    away_draws INTEGER,
    away_losses INTEGER,
    away_goals_for INTEGER,
    away_goals_against INTEGER,

    -- Additional info
    form VARCHAR(20),  -- Last 5 games: e.g., 'WWDLW'
    description TEXT,  -- e.g., 'Promotion - Champions League'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(season_id, team_id)
);

CREATE INDEX idx_standings_season ON standings(season_id);
CREATE INDEX idx_standings_team ON standings(team_id);
CREATE INDEX idx_standings_rank ON standings(rank);

-- ============================================================================
-- FIXTURES TABLE
-- Stores match fixtures (past and future)
-- ============================================================================
CREATE TABLE fixtures (
    id INTEGER PRIMARY KEY,  -- API fixture ID
    season_id INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    round VARCHAR(100) NOT NULL,  -- e.g., 'Regular Season - 15'

    -- Match details
    date TIMESTAMP NOT NULL,
    timezone VARCHAR(50),
    venue VARCHAR(255),
    city VARCHAR(255),
    referee VARCHAR(255),

    -- Teams
    home_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,

    -- Scores (NULL for future fixtures)
    home_score INTEGER,
    away_score INTEGER,
    home_halftime_score INTEGER,
    away_halftime_score INTEGER,
    home_fulltime_score INTEGER,
    away_fulltime_score INTEGER,

    -- Status
    status VARCHAR(50) NOT NULL,  -- 'TBD', 'NS', 'LIVE', 'HT', 'FT', 'PST', 'CANC'
    status_long VARCHAR(100),
    elapsed INTEGER,  -- Minutes elapsed

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fixtures_season ON fixtures(season_id);
CREATE INDEX idx_fixtures_date ON fixtures(date);
CREATE INDEX idx_fixtures_home_team ON fixtures(home_team_id);
CREATE INDEX idx_fixtures_away_team ON fixtures(away_team_id);
CREATE INDEX idx_fixtures_status ON fixtures(status);
CREATE INDEX idx_fixtures_round ON fixtures(round);

-- ============================================================================
-- VIEWS
-- Convenient views for common queries
-- ============================================================================

-- Current season standings with team names
CREATE OR REPLACE VIEW current_standings AS
SELECT
    l.name AS league_name,
    s.year AS season,
    st.rank,
    t.name AS team_name,
    t.logo_url AS team_logo,
    st.points,
    st.played,
    st.wins,
    st.draws,
    st.losses,
    st.goals_for,
    st.goals_against,
    st.goal_difference,
    st.form
FROM standings st
JOIN seasons s ON st.season_id = s.id
JOIN teams t ON st.team_id = t.id
JOIN leagues l ON s.league_id = l.id
WHERE s.is_current = TRUE
ORDER BY l.id, st.rank;

-- Upcoming fixtures with team names
CREATE OR REPLACE VIEW upcoming_fixtures AS
SELECT
    f.id,
    l.name AS league_name,
    s.year AS season,
    f.round,
    f.date,
    f.venue,
    f.city,
    ht.name AS home_team,
    ht.logo_url AS home_logo,
    at.name AS away_team,
    at.logo_url AS away_logo,
    f.status
FROM fixtures f
JOIN seasons s ON f.season_id = s.id
JOIN leagues l ON s.league_id = l.id
JOIN teams ht ON f.home_team_id = ht.id
JOIN teams at ON f.away_team_id = at.id
WHERE f.date > CURRENT_TIMESTAMP
ORDER BY f.date;

-- Recent results with team names and scores
CREATE OR REPLACE VIEW recent_results AS
SELECT
    f.id,
    l.name AS league_name,
    s.year AS season,
    f.round,
    f.date,
    f.venue,
    ht.name AS home_team,
    f.home_score,
    at.name AS away_team,
    f.away_score,
    f.status
FROM fixtures f
JOIN seasons s ON f.season_id = s.id
JOIN leagues l ON s.league_id = l.id
JOIN teams ht ON f.home_team_id = ht.id
JOIN teams at ON f.away_team_id = at.id
WHERE f.status = 'FT'
ORDER BY f.date DESC;

-- ============================================================================
-- TRIGGERS
-- Automatic timestamp updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_leagues_updated_at BEFORE UPDATE ON leagues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_seasons_updated_at BEFORE UPDATE ON seasons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_standings_updated_at BEFORE UPDATE ON standings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fixtures_updated_at BEFORE UPDATE ON fixtures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get Premier League current season standings
-- SELECT * FROM current_standings WHERE league_name = 'Premier League';

-- Get upcoming Premier League fixtures
-- SELECT * FROM upcoming_fixtures WHERE league_name = 'Premier League' LIMIT 10;

-- Get recent results
-- SELECT * FROM recent_results WHERE league_name = 'Premier League' LIMIT 10;

-- Get team head-to-head record
-- SELECT
--     COUNT(*) as matches,
--     SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as home_wins,
--     SUM(CASE WHEN home_score < away_score THEN 1 ELSE 0 END) as away_wins,
--     SUM(CASE WHEN home_score = away_score THEN 1 ELSE 0 END) as draws
-- FROM fixtures
-- WHERE (home_team_id = 33 AND away_team_id = 50)
--    OR (home_team_id = 50 AND away_team_id = 33)
--    AND status = 'FT';
