"""
Script to create the PostgreSQL database.

Run this before initializing migrations.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_USER = 'postgres'
DB_PASSWORD = 'Y9*jj%0#r@6655'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'smart_maintenance'

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database='postgres'  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()

        if not exists:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
            )
            print(f"[SUCCESS] Database '{DB_NAME}' created successfully!")
        else:
            print(f"[INFO] Database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"[ERROR] Error creating database: {e}")
        return False

    return True

if __name__ == '__main__':
    print("Creating PostgreSQL database...")
    if create_database():
        print("\nNext steps:")
        print("1. Run: flask db init")
        print("2. Run: flask db migrate -m 'Initial migration'")
        print("3. Run: flask db upgrade")
    else:
        print("\nPlease ensure PostgreSQL is running and credentials are correct.")
