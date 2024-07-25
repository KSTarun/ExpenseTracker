from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def initialize_db():
    with app.app_context():
        init_db('expenses.db')

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')

    # Predefined categories
    categories = ['grocery', 'fun', 'shopping', 'travel', 'salary', 'bills', 'food']
    for category in categories:
        conn.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT name FROM categories ORDER BY name').fetchall()
    expenses = conn.execute('SELECT e.id, e.description, e.amount, e.date, c.name as category FROM expenses e LEFT JOIN categories c ON e.category_id = c.id').fetchall()
    budgets = conn.execute('SELECT b.id, b.amount, c.name as category FROM budgets b LEFT JOIN categories c ON b.category_id = c.id').fetchall()

    # Calculate total expenses per category
    total_expenses = conn.execute('''
        SELECT c.name as category, SUM(e.amount) as total_expense
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        GROUP BY c.name
    ''').fetchall()

    # Convert budgets and total_expenses to lists of dictionaries for mutability
    budgets = [dict(budget) for budget in budgets]
    total_expenses = [dict(expense) for expense in total_expenses]

    # Merge budget and total expenses
    expense_dict = {expense['category']: expense['total_expense'] for expense in total_expenses}
    for budget in budgets:
        budget['total_expense'] = expense_dict.get(budget['category'], 0)
        budget['Percentage_Spent'] = round((budget['total_expense'] / budget['amount']) * 100, 1) if budget['amount'] > 0 else 0

    conn.close()

    # Calculate total budget and total expenses
    total_budget = sum(budget['amount'] for budget in budgets)
    total_expense = sum(expense['total_expense'] for expense in total_expenses)

    return render_template('index.html', categories=categories, expenses=expenses, budgets=budgets, total_budget=total_budget, total_expense=total_expense)

@app.route('/add_expense', methods=('GET', 'POST'))
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        category_id = request.form['category']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (description, amount, category_id, date) VALUES (?, ?, ?, ?)', (description, amount, category_id, date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return render_template('add_expense.html', categories=categories)

@app.route('/set_budget', methods=('GET', 'POST'))
def set_budget():
    if request.method == 'POST':
        category_id = request.form['category']
        amount = request.form['amount']
        conn = get_db_connection()
        
        # Check if budget for this category already exists
        existing_budget = conn.execute('SELECT * FROM budgets WHERE category_id = ?', (category_id,)).fetchone()
        
        if existing_budget:
            # Update the existing budget
            conn.execute('UPDATE budgets SET amount = ? WHERE category_id = ?', (amount, category_id))
        else:
            # Insert a new budget
            conn.execute('INSERT INTO budgets (category_id, amount) VALUES (?, ?,)', (category_id, amount))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return render_template('set_budget.html', categories=categories)

@app.route('/delete_budgets', methods=['POST'])
def delete_budgets():
    budget_ids = request.form.getlist('budget_ids')
    if budget_ids:
        conn = get_db_connection()
        conn.executemany('DELETE FROM budgets WHERE id = ?', [(budget_id,) for budget_id in budget_ids])
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    expense_id = request.form['expense_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    category_totals = conn.execute('''
        SELECT c.name as category, SUM(e.amount) as total_expense
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        GROUP BY c.name
    ''').fetchall()
    conn.close()
    # Convert to a list of dictionaries
    category_totals = [dict(row) for row in category_totals]
    return render_template('analytics.html', category_totals=category_totals)


if __name__ == '__main__':
    app.run(debug=True)
