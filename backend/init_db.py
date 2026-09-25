#!/usr/bin/env python3
"""
Database initialization script for Render deployment.
Runs all SQL files in the correct order to set up the database schema.
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def run_sql_file(conn, filepath):
    """Execute a SQL file."""
    with open(filepath, 'r') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Executed: {filepath}")

def main():
    url = os.getenv('DATABASE_URL')
    if not url:
        print("DATABASE_URL not set")
        return
    
    db_dir = os.path.join(os.path.dirname(__file__), "..", "database")
    sql_files = [
        "schema.sql",
        "functions.sql", 
        "triggers.sql",
        "procedures.sql",
        "views.sql",
        "seed.sql"
    ]
    
    try:
        with psycopg.connect(url, connect_timeout=30) as conn:
            for sql_file in sql_files:
                filepath = os.path.join(db_dir, sql_file)
                if os.path.exists(filepath):
                    run_sql_file(conn, filepath)
                else:
                    print(f"File not found: {filepath}")
        print("Database initialization complete!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()