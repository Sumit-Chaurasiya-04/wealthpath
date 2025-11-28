import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "wealthpath.db"

def init_db():
    """Initialize the SQLite database schema."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            is_predicted INTEGER DEFAULT 0
        )
    ''')
    
    # Categories reference (can be expanded)
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY
        )
    ''')
    
    # Seed categories if empty
    res = c.execute("SELECT count(*) FROM categories")
    if res.fetchone()[0] == 0:
        defaults = [('Food & Drink',), ('Groceries',), ('Transport',), 
                    ('Utilities',), ('Rent',), ('Income',), ('Shopping',), 
                    ('Entertainment',), ('Health',), ('Misc',)]
        c.executemany("INSERT INTO categories VALUES (?)", defaults)
        
    conn.commit()
    conn.close()

def save_transactions(df: pd.DataFrame):
    """Save a pandas DataFrame of transactions to the DB."""
    conn = sqlite3.connect(DB_NAME)
    # Ensure columns match
    df.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()

def get_transactions():
    """Retrieve all transactions as a DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT * FROM transactions", conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def get_categories():
    """Get list of categories."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT name FROM categories", conn)
    conn.close()
    return df['name'].tolist()

def clear_db():
    """Dangerous: clears all data."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()