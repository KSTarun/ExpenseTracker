from flask import Flask, render_template, request, redirect, url_for
from base import get_db, init_db
import os

app = Flask(__name__)

DATABASE = 'expenses.db'

@app.route('/')
def index():
    db = get_db(DATABASE)
    cur = db.execute('SELECT id, description, amount, date, category FROM expenses ORDER BY date DESC')
    expenses = cur.fetchall()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        date = request.form['date']
        category = request.form['category']
        
        db = get_db(DATABASE)
        db.execute('INSERT INTO expenses (description, amount, date, category) VALUES (?, ?, ?, ?)', 
                   [description, amount, date, category])
        db.commit()
        return redirect(url_for('index'))
    
    db = get_db(DATABASE)
    cur = db.execute('SELECT name FROM categories')
    categories = cur.fetchall()
    return render_template('add_expense.html', categories=categories)

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        budget = float(request.form['budget'])
        category = request.form['category']
        
        db = get_db(DATABASE)
        db.execute('INSERT OR REPLACE INTO budget (id, amount, category) VALUES (?, ?, ?)', [1, budget, category])
        db.commit()
        return redirect(url_for('index'))
    
    db = get_db(DATABASE)
    cur = db.execute('SELECT name FROM categories')
    categories = cur.fetchall()
    return render_template('set_budget.html', categories=categories)

if __name__ == '__main__':
    init_db(DATABASE)
    app.run(debug=True)
