import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

# This function establishes a connection to the PostgreSQL database using the psycopg library. 
# It retrieves the database connection parameters from environment variables and returns a connection object that can be used to interact with the database.
def get_connection():
    url = os.getenv('DATABASE_URL')
    if url:
        return psycopg.connect(url, connect_timeout=10, options='-c timezone=UTC')
    names = {'host': 'DB_HOST', 'port': 'DB_PORT', 'dbname': 'DB_NAME',
             'user': 'DB_USER', 'password': 'DB_PASSWORD'}
    settings = {key: os.getenv(env) for key, env in names.items()}
    settings['port'] = settings['port'] or '5432'
    if any(not settings[key] for key in ('host', 'dbname', 'user', 'password')):
        raise RuntimeError('Set DATABASE_URL or DB_HOST, DB_NAME, DB_USER and DB_PASSWORD')
    return psycopg.connect(**settings, connect_timeout=10, options='-c timezone=UTC')