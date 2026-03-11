import sqlite3
import base64
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
description TEXT,
type TEXT,
image_data TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
dob TEXT
)
""")

conn.commit()
conn.close()

@app.route('/')
def index():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user_name=session['user_name'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        
        if name and dob:
            session['user_name'] = name
            session['user_dob'] = dob
            
            conn = get_db_connection()
            conn.execute('INSERT INTO users (name, dob) VALUES (?, ?)', (name, dob))
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/report_lost', methods=['GET', 'POST'])
def report_lost():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        image_data = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Read and encode image as base64
                image_bytes = file.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO items (name, description, type, image_data) VALUES (?, ?, ?, ?)',
                     (name, description, 'lost', image_data))
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_items'))
    
    return render_template('report_lost.html')

@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location', '')
        
        image_data = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Read and encode image as base64
                image_bytes = file.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
        
        full_description = f"{description} | Location: {location}"
        
        conn = get_db_connection()
        conn.execute('INSERT INTO items (name, description, type, image_data) VALUES (?, ?, ?, ?)',
                     (name, full_description, 'found', image_data))
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_items'))
    
    return render_template('report_found.html')

@app.route('/view_items')
def view_items():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('view_items.html', items=items)

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_items'))

if __name__ == '__main__':
    app.run(debug=True)
