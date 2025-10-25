"""
Quick verification script to check database contents.
"""

import logging
from upload import get_db_cursor

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def verify_data():
    """Verify data was populated correctly."""

    with get_db_cursor() as cur:
        # Check record counts
        logger.info("=" * 60)
        logger.info("DATABASE VERIFICATION REPORT")
        logger.info("=" * 60)

        # Leagues
        cur.execute("SELECT COUNT(*) FROM leagues")
        league_count = cur.fetchone()[0]
        logger.info(f"\n📊 LEAGUES: {league_count}")

        cur.execute("SELECT id, name, country FROM leagues")
        for row in cur.fetchall():
            logger.info(f"  - ID {row[0]}: {row[1]} ({row[2]})")

        # Seasons
        cur.execute("SELECT COUNT(*) FROM seasons")
        season_count = cur.fetchone()[0]
        logger.info(f"\n📅 SEASONS: {season_count}")

        cur.execute("""
            SELECT s.year, l.name, s.is_current,
                   COUNT(st.id) as teams
            FROM seasons s
            JOIN leagues l ON s.league_id = l.id
            LEFT JOIN standings st ON s.id = st.season_id
            GROUP BY s.year, l.name, s.is_current
            ORDER BY s.year DESC
        """)
        for row in cur.fetchall():
            current = " (CURRENT)" if row[2] else ""
            logger.info(f"  - {row[0]} {row[1]}: {row[3]} teams{current}")

        # Teams
        cur.execute("SELECT COUNT(*) FROM teams")
        team_count = cur.fetchone()[0]
        logger.info(f"\n⚽ TEAMS: {team_count}")

        cur.execute("SELECT name FROM teams ORDER BY name LIMIT 10")
        logger.info("  Sample teams:")
        for row in cur.fetchall():
            logger.info(f"    • {row[0]}")
        if team_count > 10:
            logger.info(f"    ... and {team_count - 10} more")

        # Standings
        cur.execute("SELECT COUNT(*) FROM standings")
        standing_count = cur.fetchone()[0]
        logger.info(f"\n📈 STANDINGS: {standing_count}")

        # Show top 5 from each season
        cur.execute("""
            SELECT s.year, t.name, st.rank, st.points, st.played
            FROM standings st
            JOIN teams t ON st.team_id = t.id
            JOIN seasons s ON st.season_id = s.id
            WHERE st.rank <= 5
            ORDER BY s.year DESC, st.rank
        """)

        current_year = None
        for row in cur.fetchall():
            if current_year != row[0]:
                current_year = row[0]
                logger.info(f"\n  Top 5 - {row[0]} Season:")
            logger.info(f"    {row[2]:2d}. {row[1]:25s} - {row[3]:2d} pts ({row[4]} played)")

        # Fixtures
        cur.execute("SELECT COUNT(*) FROM fixtures")
        fixture_count = cur.fetchone()[0]
        logger.info(f"\n🎯 FIXTURES: {fixture_count}")

        cur.execute("""
            SELECT s.year, COUNT(*) as count
            FROM fixtures f
            JOIN seasons s ON f.season_id = s.id
            GROUP BY s.year
            ORDER BY s.year DESC
        """)
        for row in cur.fetchall():
            logger.info(f"  - {row[0]}: {row[1]} fixtures")

        # Sample upcoming fixtures
        cur.execute("""
            SELECT f.date, ht.name as home, at.name as away, f.venue
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            WHERE f.date > CURRENT_TIMESTAMP
            ORDER BY f.date
            LIMIT 5
        """)

        upcoming = cur.fetchall()
        if upcoming:
            logger.info(f"\n  Next 5 fixtures:")
            for row in upcoming:
                logger.info(f"    {row[0].strftime('%Y-%m-%d %H:%M')}: {row[1]} vs {row[2]} @ {row[3]}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ {league_count} league(s)")
        logger.info(f"✓ {season_count} season(s)")
        logger.info(f"✓ {team_count} team(s)")
        logger.info(f"✓ {standing_count} standing record(s)")
        logger.info(f"✓ {fixture_count} fixture(s)")
        logger.info("=" * 60)
        logger.info("✓ Database populated successfully!\n")

if __name__ == "__main__":
    verify_data()
