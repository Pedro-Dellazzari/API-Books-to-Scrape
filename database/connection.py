# database.py

import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os
from contextlib import contextmanager

def get_connection():
    """Retorna uma conexão com PostgreSQL"""
    connection_params = {
        'host': os.getenv('POSTGRES_ENDPOINT'),
        'port': os.getenv('POSTGRES_PORT'),
        'database': os.getenv('POSTGRES_DATABASE'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
    conn = psycopg2.connect(**connection_params)
    return conn

@contextmanager
def get_connection_context():
    """Context manager para conexões PostgreSQL"""
    conn = None
    try:
        conn = get_connection()
        yield conn
    finally:
        if conn:
            conn.close()
