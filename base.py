import sqlite3
from loguru import logger

logger.info('Import done')

def get_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_name):
    conn = get_db(db_name)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            description TEXT,
            amount REAL,
            date TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    
    # Predefined categories
    categories = ['grocery', 'fun', 'shopping', 'travel', 'salary', 'bills']
    cur.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', [(category,) for category in categories])

    conn.commit()
    logger.info('DB Created')
    conn.close()
