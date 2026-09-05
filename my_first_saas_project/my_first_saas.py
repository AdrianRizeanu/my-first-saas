from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'

def init_db():
    conn = sqlite3.connect('saas_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('customer1', 'password123', 'user'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin1', 'adminpass', 'admin'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

# --- USER ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('saas_users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "That username is already taken. Please go back and pick another one."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('saas_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = 'user'", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Customer Credentials. Please go back and try again."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('saas_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = 'admin'", (username, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid Admin Credentials. Please go back and try again."
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # 1. Connect to database
    conn = sqlite3.connect('saas_users.db')
    cursor = conn.cursor()
    # 2. Grab all registered users
    cursor.execute("SELECT id, username, role FROM users")
    all_users = cursor.fetchall()
    conn.close()
    
    # 3. Send that user list over to the HTML template
    return render_template('admin.html', users=all_users)

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
