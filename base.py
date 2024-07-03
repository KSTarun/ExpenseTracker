import sqlite3
from loguru import logger

logger.info('Import complete')

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            category_id INTEGER,
            amount REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    # Insert predefined categories if they don't exist
    categories = ['Grocery', 'Fun', 'Shopping', 'Travel', 'Salary', 'Bills', 'Food']
    for category in categories:
        c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
    
    conn.commit()
    logger.info('DB Setup')
    conn.close()

if __name__ == '__main__':
    init_db()
