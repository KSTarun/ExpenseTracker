from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    expenses = conn.execute('SELECT e.id, e.amount, e.date, c.name as category FROM expenses e LEFT JOIN categories c ON e.category_id = c.id').fetchall()
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
    
    conn.close()
    return render_template('index.html', categories=categories, expenses=expenses, budgets=budgets)

@app.route('/add_expense', methods=('GET', 'POST'))
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (amount, category_id, date) VALUES (?, ?, ?)', (amount, category_id, date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
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
            conn.execute('INSERT INTO budgets (category_id, amount) VALUES (?, ?)', (category_id, amount))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
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

@app.route('/delete_expenses', methods=['POST'])
def delete_expenses():
    expense_ids = request.form.getlist('expense_ids')
    if expense_ids:
        conn = get_db_connection()
        conn.executemany('DELETE FROM expenses WHERE id = ?', [(expense_id,) for expense_id in expense_ids])
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
