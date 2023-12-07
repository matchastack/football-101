import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Establish a connection to the PostgreSQL database
def connect_to_db():
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    # Create a cursor object to interact with the database
    cur = conn.cursor()
    return cur, conn

def create_table(cur):
    # Execute a CREATE TABLE statement
    cur.execute("""
        CREATE TABLE IF NOT EXISTS test (
            column1 INTEGER PRIMARY KEY,
            column2 VARCHAR(255) NOT NULL
        )
    """)
    print("Table created successfully")
    return True

# Close the cursor and connection
def execute(cur, conn):
    # Commit the changes to the database
    conn.commit()
    cur.close()
    conn.close()
    return True