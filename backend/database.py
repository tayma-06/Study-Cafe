import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

# This function establishes a connection to the PostgreSQL database using the psycopg library. 
# It retrieves the database connection parameters from environment variables and returns a connection object that can be used to interact with the database.
def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )