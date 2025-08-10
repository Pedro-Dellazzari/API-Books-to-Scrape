# database.py

import duckdb

def get_connection():
    con = duckdb.connect(database='books.db', read_only=True)
    return con
