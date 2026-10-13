import psycopg
from config import DB_CONFIG

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    return psycopg.connect(**DB_CONFIG)

