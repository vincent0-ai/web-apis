from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

app = Flask(__name__)



# Load environment variables from .env file
load_dotenv()
# CSRF Protection
csrf = CSRFProtect(app)


# Secret key for session management
app.config["SECRET_KEY"] = os.urandom(24)

# MongoDB Configuration
#app.config["MONGO_URI"] = "mongodb://localhost:27017"
#mongo = PyMongo(app)


# User collection
#users_collection = mongo.db.users

client = MongoClient('mongodb://localhost:27017/')
db = client['demo']
users_collection = db['data']

@app.route('/')
def index():
    """
    Home page. Shows user's name if logged in.
    """
    if 'user_id' in session:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', user=user)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return redirect(url_for('register'))

        # Hash the password and store the new user
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'username': username,
            'password': hashed_password
        })

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('login'))

        user = users_collection.find_one({'username': username})

        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Handles user logout.
    """
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)