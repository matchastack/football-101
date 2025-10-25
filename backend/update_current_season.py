"""
Script to update the current season in the database.
"""

from upload import get_db_cursor

def update_current_season(year: int = 2025):
    """Update the current season to the specified year."""

    with get_db_cursor() as cur:
        # First, set all Premier League seasons to not current
        cur.execute("""
            UPDATE seasons
            SET is_current = FALSE
            WHERE league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
        """)
        print(f"Set all Premier League seasons to is_current=False")

        # Then set the specified year as the current season
        cur.execute("""
            UPDATE seasons
            SET is_current = TRUE
            WHERE year = %s
            AND league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
        """, (year,))

        rows_updated = cur.rowcount
        if rows_updated > 0:
            print(f"Set {year} season to is_current=True")
        else:
            print(f"Warning: No season found for year {year}")

        # Verify the changes
        cur.execute("""
            SELECT id, year, is_current
            FROM seasons
            WHERE league_id = (SELECT id FROM leagues WHERE name = 'Premier League')
            ORDER BY year DESC
        """)
        seasons = cur.fetchall()
        print('\nCurrent seasons in database:')
        for s in seasons:
            current_marker = " ← CURRENT" if s[2] else ""
            print(f"  ID: {s[0]}, Year: {s[1]}, Current: {s[2]}{current_marker}")

if __name__ == "__main__":
    update_current_season(2025)
