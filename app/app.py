from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from contextlib import contextmanager
import re

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Change this to a secure random key in production

# Database connection context manager
@contextmanager
def get_db_connection():
    conn = psycopg2.connect("dbname=voice_to_text user=postgres password=123456789")
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

# --------------------------------
#  Home Route (Index Page)
# --------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# --------------------------------
#  Home Page (After Login)
# ---------------------------@app.route('/home', methods=['GET', 'POST'])
@app.route('/home')
def home():
    return render_template('home.html')
# --------------------------------
#  Signup Route
# --------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if any required field is missing
        if not username or not email or not password or not confirm_password:
            flash("All fields are required!", "danger")
            return redirect(url_for('signup'))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        # Ensure the email is a Gmail address
        if not email.endswith("@gmail.com"):
            flash("Only Gmail addresses are allowed!", "danger")
            return redirect(url_for('signup'))

        # Ensure password meets complexity requirements
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            flash("Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and symbols.", "danger")
            return redirect(url_for('signup'))

        # Check if username already exists
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()
        
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user
        try:
            with get_db_cursor() as cur:
                cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                            (username, email, hashed_password, 'User'))
                cur.connection.commit()
        except Exception as e:
            # Handle database errors
            flash(f"An error occurred while creating your account: {str(e)}", "danger")
            return redirect(url_for('signup'))

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))  # Redirect to login page after signup

    # For GET requests, render the signup template
    return render_template('signup.html')
# --------------------------------
#  Login Route
# --------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'user_id' in session:
        flash("You are already logged in.", "info")
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required!", "danger")
            return redirect(url_for('login'))

        with get_db_cursor() as cur:
            cur.execute("SELECT id, password, role FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['role'] = user[2]

            flash("Login successful!", "success")

            # Redirect to appropriate page based on user role
            if user[2] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))  # Redirect to home page for regular users
        else:
            flash("Invalid username or password", "danger")

    # For GET requests or failed login, render the login template
    return render_template('login.html')
# --------------------------------
#  User Dashboard
# --------------------------------
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'User':
        flash("Please log in first", "warning")
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

# --------------------------------
#  Admin Dashboard
# --------------------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# --------------------------------
#  Logout Route
# --------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

# --------------------------------
#  Run Flask App
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)