"""
Database initialization script.

This script initializes the PostgreSQL database by:
1. Creating a database user with appropriate privileges (if not exists)
2. Creating the database (if not exists)
3. Granting necessary privileges to the user
4. Executing the schema SQL file to create tables, indexes, views, and triggers

Usage:
    python init_db.py

Environment Variables Required:
    # PostgreSQL superuser credentials (for creating user/database)
    POSTGRES_SUPERUSER (default: postgres)
    POSTGRES_SUPERUSER_PASSWORD
    POSTGRES_HOST (default: localhost)
    POSTGRES_PORT (default: 5432)

    # Application user credentials (to be created)
    DB_USER
    DB_PASSWORD
    DB_NAME
"""

import logging
import os
import sys
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
SCHEMA_FILE = Path(__file__).parent / "db_schema.sql"

# Database configuration
SUPERUSER = os.getenv("POSTGRES_SUPERUSER", "postgres")
SUPERUSER_PASSWORD = os.getenv("POSTGRES_SUPERUSER_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Application database configuration
APP_USER = os.getenv("DB_USER")
APP_PASSWORD = os.getenv("DB_PASSWORD")
APP_DATABASE = os.getenv("DB_NAME")


def validate_config():
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If required variables are missing
    """
    missing_vars = []

    if not APP_USER:
        missing_vars.append("DB_USER")
    if not APP_PASSWORD:
        missing_vars.append("DB_PASSWORD")
    if not APP_DATABASE:
        missing_vars.append("DB_NAME")

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    logger.info("✓ Environment variables validated")


def get_superuser_connection():
    """
    Connect to PostgreSQL as superuser.

    Returns:
        Database connection object

    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",  # Connect to default database
            user=SUPERUSER,
            password=SUPERUSER_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"✓ Connected as superuser '{SUPERUSER}'")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect as superuser: {e}")
        raise


def create_user_if_not_exists(conn):
    """
    Create database user if it doesn't exist.

    Args:
        conn: Superuser database connection

    Returns:
        True if user was created, False if already exists
    """
    cur = conn.cursor()

    try:
        # Check if user exists
        cur.execute("""
            SELECT 1 FROM pg_roles WHERE rolname = %s
        """, (APP_USER,))

        if cur.fetchone():
            logger.info(f"User '{APP_USER}' already exists")
            return False

        # Create user
        logger.info(f"Creating user '{APP_USER}'...")
        cur.execute(f"""
            CREATE USER {APP_USER} WITH PASSWORD %s
        """, (APP_PASSWORD,))

        logger.info(f"✓ User '{APP_USER}' created successfully")
        return True

    except psycopg2.Error as e:
        logger.error(f"Failed to create user: {e}")
        raise
    finally:
        cur.close()


def create_database_if_not_exists(conn):
    """
    Create database if it doesn't exist.

    Args:
        conn: Superuser database connection

    Returns:
        True if database was created, False if already exists
    """
    cur = conn.cursor()

    try:
        # Check if database exists
        cur.execute("""
            SELECT 1 FROM pg_database WHERE datname = %s
        """, (APP_DATABASE,))

        if cur.fetchone():
            logger.info(f"Database '{APP_DATABASE}' already exists")
            return False

        # Create database
        logger.info(f"Creating database '{APP_DATABASE}'...")
        cur.execute(f"""
            CREATE DATABASE {APP_DATABASE}
            WITH OWNER = {APP_USER}
            ENCODING = 'UTF8'
            LC_COLLATE = 'en_US.UTF-8'
            LC_CTYPE = 'en_US.UTF-8'
        """)

        logger.info(f"✓ Database '{APP_DATABASE}' created successfully")
        return True

    except psycopg2.Error as e:
        logger.error(f"Failed to create database: {e}")
        raise
    finally:
        cur.close()


def grant_privileges(conn):
    """
    Grant necessary privileges to the application user.

    Args:
        conn: Superuser database connection
    """
    cur = conn.cursor()

    try:
        logger.info(f"Granting privileges to user '{APP_USER}'...")

        # Grant connect privilege
        cur.execute(f"""
            GRANT CONNECT ON DATABASE {APP_DATABASE} TO {APP_USER}
        """)

        # Grant usage on public schema
        cur.execute(f"""
            GRANT USAGE, CREATE ON SCHEMA public TO {APP_USER}
        """)

        # Grant all privileges on all tables in public schema
        cur.execute(f"""
            GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {APP_USER}
        """)

        # Grant all privileges on all sequences in public schema
        cur.execute(f"""
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {APP_USER}
        """)

        # Set default privileges for future tables
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
            GRANT ALL PRIVILEGES ON TABLES TO {APP_USER}
        """)

        # Set default privileges for future sequences
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
            GRANT ALL PRIVILEGES ON SEQUENCES TO {APP_USER}
        """)

        logger.info(f"✓ Privileges granted to '{APP_USER}'")

    except psycopg2.Error as e:
        logger.error(f"Failed to grant privileges: {e}")
        raise
    finally:
        cur.close()


def get_app_connection():
    """
    Connect to the application database as the application user.

    Returns:
        Database connection object
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=APP_DATABASE,
            user=APP_USER,
            password=APP_PASSWORD
        )
        logger.info(f"✓ Connected to '{APP_DATABASE}' as '{APP_USER}'")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to application database: {e}")
        raise


def create_schema(conn):
    """
    Create database schema by executing the SQL file.

    Args:
        conn: Application database connection

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    # Check if schema file exists
    if not SCHEMA_FILE.exists():
        logger.error(f"Schema file not found: {SCHEMA_FILE}")
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    logger.info(f"Reading schema from {SCHEMA_FILE}")

    # Read SQL schema file
    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()

    cur = conn.cursor()

    try:
        logger.info("Executing schema SQL...")
        cur.execute(schema_sql)
        conn.commit()

        logger.info("✓ Database schema created successfully!")

        # Verify tables were created
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        tables = cur.fetchall()
        logger.info(f"Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")

        # Verify views were created
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'VIEW'
            ORDER BY table_name
        """)

        views = cur.fetchall()
        logger.info(f"Created {len(views)} views:")
        for view in views:
            logger.info(f"  - {view[0]}")

    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()


def init_database():
    """
    Initialize the complete database setup.

    This function:
    1. Validates configuration
    2. Creates database user (if not exists)
    3. Creates database (if not exists)
    4. Grants appropriate privileges
    5. Creates schema (tables, indexes, views, triggers)

    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If schema file doesn't exist
        psycopg2.Error: If database operations fail
    """
    # Validate environment variables
    validate_config()

    superuser_conn = None
    app_conn = None

    try:
        # Step 1: Connect as superuser
        superuser_conn = get_superuser_connection()

        # Step 2: Create user if not exists
        create_user_if_not_exists(superuser_conn)

        # Step 3: Create database if not exists
        create_database_if_not_exists(superuser_conn)

        # Step 4: Grant privileges
        grant_privileges(superuser_conn)

        # Close superuser connection
        superuser_conn.close()
        logger.info("Superuser connection closed")

        # Step 5: Connect as application user
        app_conn = get_app_connection()

        # Step 6: Create schema
        create_schema(app_conn)

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    finally:
        if superuser_conn and not superuser_conn.closed:
            superuser_conn.close()
        if app_conn and not app_conn.closed:
            app_conn.close()
            logger.info("Application database connection closed")


def main():
    """Main execution function."""
    logger.info("Starting database initialization...")

    try:
        init_database()
        logger.info("Database initialization complete!")
        sys.exit(0)

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
