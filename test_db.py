
import sqlite3
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Database file
DB_NAME = BASE_DIR / "conversations.db"

try:
    # Connect to database
    connection = sqlite3.connect(DB_NAME)

    print("SUCCESS: Database connection established!")

    cursor = connection.cursor()

    # Check SQLite version
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()

    print("SQLite Version:", version[0])

    # Check database tables
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tables = cursor.fetchall()

    print("\nAvailable Tables:")

    if tables:
        for table in tables:
            print("-", table[0])
    else:
        print("No tables found.")

    connection.close()

    print("\nDatabase connection closed successfully!")

except sqlite3.Error as error:
    print("Database connection failed!")
    print("Error:", error)