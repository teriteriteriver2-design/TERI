import sqlite3
import os

DB_PATH = 'billing.sqlite'
INITIAL_CREDIT = 8100.0  # $6 * 1350 KRW

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance_krw REAL
        )
    ''')
    
    # Initialize test_user_01 if not exists
    c.execute('SELECT balance_krw FROM users WHERE user_id = ?', ('test_user_01',))
    row = c.fetchone()
    if not row:
        c.execute('INSERT INTO users (user_id, balance_krw) VALUES (?, ?)', ('test_user_01', INITIAL_CREDIT))
    
    conn.commit()
    conn.close()

def get_balance(user_id='test_user_01'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT balance_krw FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0

def deduct_balance(cost_krw, user_id='test_user_01'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET balance_krw = balance_krw - ? WHERE user_id = ?', (cost_krw, user_id))
    conn.commit()
    conn.close()

# Initialize DB when module is imported
init_db()
