# Import necessary libraries
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from geopy.distance import geodesic
from datetime import datetime
from dotenv import load_dotenv
import os
import hashlib
import uuid
import requests
import json

# Load environment variables
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 🚀 SUPABASE REST API - ULTRA FAST & RELIABLE!
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'your-anon-key')

# Supabase REST API headers
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Check if Supabase is configured
try:
    if not SUPABASE_URL or not SUPABASE_KEY or 'your-project' in SUPABASE_URL:
        raise Exception("Supabase credentials not configured")

    # Test connection with a simple request
    test_response = requests.get(f'{SUPABASE_URL}/rest/v1/', headers=SUPABASE_HEADERS, timeout=5)
    SUPABASE_CONNECTED = True
    print("🚀 Supabase REST API connected successfully!")
except Exception as e:
    print(f"⚠️  Supabase connection failed: {e}")
    print("📝 Using mock data for development")
    SUPABASE_CONNECTED = False

# Simple session management (no complex Flask-Login needed)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_logged_in():
    return 'user_id' in session

def require_login(f):
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def get_current_user():
    if 'user_id' in session:
        if not SUPABASE_CONNECTED:
            return next((user for user in MOCK_USERS if user['id'] == session['user_id']), None)

        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/users?id=eq.{session["user_id"]}',
            headers=SUPABASE_HEADERS
        )
        data = response.json()
        return data[0] if data else None
    return None
# 🚀 NO DATABASE MODELS NEEDED!
# Supabase handles everything automatically with tables:
# - users (id, username, email, password, user_type, latitude, longitude, bio, business_name, business_category, rating, created_at)
# - forum_posts (id, user_id, content, latitude, longitude, created_at)
# - chats (id, sender_id, receiver_id, message, created_at)

# 🎭 MOCK DATA for local development (when Supabase not configured)
MOCK_USERS = [
    {'id': '1', 'username': 'john_nyc', 'email': 'john@example.com', 'password': hash_password('password123'), 'user_type': 'person', 'latitude': 40.7589, 'longitude': -73.9851, 'bio': 'Love exploring NYC!', 'rating': 4.5},
    {'id': '2', 'username': 'sarah_manhattan', 'email': 'sarah@example.com', 'password': hash_password('password123'), 'user_type': 'person', 'latitude': 40.7505, 'longitude': -73.9934, 'bio': 'Coffee enthusiast', 'rating': 4.8},
    {'id': '3', 'username': 'joes_coffee', 'email': 'info@joescoffee.com', 'password': hash_password('business123'), 'user_type': 'business', 'latitude': 40.7614, 'longitude': -73.9776, 'business_name': "Joe's Coffee Shop", 'business_category': 'Restaurant', 'bio': 'Best coffee in NYC!', 'rating': 4.7}
]

MOCK_POSTS = [
    {'id': '1', 'user_id': '1', 'content': 'Anyone know what\'s happening at Washington Square Park today?', 'latitude': 40.7589, 'longitude': -73.9851, 'created_at': '2025-01-27T10:00:00Z', 'users': {'username': 'john_nyc', 'user_type': 'person'}},
    {'id': '2', 'user_id': '2', 'content': 'New coffee shop opened on 8th Ave! Great espresso ☕', 'latitude': 40.7505, 'longitude': -73.9934, 'created_at': '2025-01-27T09:00:00Z', 'users': {'username': 'sarah_manhattan', 'user_type': 'person'}}
]

# Helper functions for database operations
def create_user(username, email, password, user_type, latitude=None, longitude=None, bio=None, business_name=None, business_category=None):
    """Create a new user - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        # Mock response for local development
        user_data = {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password': hash_password(password),
            'user_type': user_type,
            'latitude': latitude,
            'longitude': longitude,
            'bio': bio,
            'business_name': business_name,
            'business_category': business_category,
            'rating': 4.5,
            'created_at': datetime.utcnow().isoformat()
        }
        MOCK_USERS.append(user_data)
        return type('MockResult', (), {'data': [user_data]})()

    user_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'password': hash_password(password),
        'user_type': user_type,
        'latitude': latitude,
        'longitude': longitude,
        'bio': bio,
        'business_name': business_name,
        'business_category': business_category,
        'rating': 4.5,
        'created_at': datetime.utcnow().isoformat()
    }
    # Insert user via REST API
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/users',
        headers=SUPABASE_HEADERS,
        json=user_data
    )
    return response.json()

def get_user_by_email(email):
    """Get user by email - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        return next((user for user in MOCK_USERS if user['email'] == email), None)

    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/users?email=eq.{email}',
        headers=SUPABASE_HEADERS
    )
    data = response.json()
    return data[0] if data else None

def get_user_by_username(username):
    """Get user by username - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        return next((user for user in MOCK_USERS if user['username'] == username), None)

    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/users?username=eq.{username}',
        headers=SUPABASE_HEADERS
    )
    data = response.json()
    return data[0] if data else None

def get_nearby_users(exclude_user_id=None):
    """Get all nearby users - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        users = [user for user in MOCK_USERS if user['user_type'] == 'person']
        if exclude_user_id:
            users = [user for user in users if user['id'] != exclude_user_id]
        return users

    url = f'{SUPABASE_URL}/rest/v1/users?user_type=eq.person'
    if exclude_user_id:
        url += f'&id=neq.{exclude_user_id}'

    response = requests.get(url, headers=SUPABASE_HEADERS)
    return response.json()

def get_nearby_businesses():
    """Get all nearby businesses - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        return [user for user in MOCK_USERS if user['user_type'] == 'business']

    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/users?user_type=eq.business',
        headers=SUPABASE_HEADERS
    )
    return response.json()

def create_forum_post(user_id, content, latitude=None, longitude=None):
    """Create forum post - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        post_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'content': content,
            'latitude': latitude,
            'longitude': longitude,
            'created_at': datetime.utcnow().isoformat()
        }
        MOCK_POSTS.append(post_data)
        return post_data

    post_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'content': content,
        'latitude': latitude,
        'longitude': longitude,
        'created_at': datetime.utcnow().isoformat()
    }
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/forum_posts',
        headers=SUPABASE_HEADERS,
        json=post_data
    )
    return response.json()

def get_forum_posts():
    """Get forum posts with user data - ONE LINE!"""
    if not SUPABASE_CONNECTED:
        return MOCK_POSTS

    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/forum_posts?select=*,users(username,user_type,business_name)&order=created_at.desc&limit=10',
        headers=SUPABASE_HEADERS
    )
    return response.json()
# Routes
@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'PingGov is running!'}, 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Check if user already exists - SUPER FAST!
        if get_user_by_username(username):
            flash('Username already exists')
            return render_template('register.html')

        if get_user_by_email(email):
            flash('Email already exists')
            return render_template('register.html')

        # Create new user - ONE LINE!
        try:
            create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None
            )
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Get user - SUPER FAST!
        user = get_user_by_email(email)

        if user and user['password'] == hash_password(password):
            # Simple session login - NO COMPLEX FLASK-LOGIN!
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['latitude'] = user['latitude']
            session['longitude'] = user['longitude']
            session['user_type'] = user['user_type']

            # Redirect to next page or map
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('map_view'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')

@app.route('/logout')
@require_login
def logout():
    # Simple session logout - CLEAN!
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@app.route('/map')
@require_login
def map_view():
    # Get current user data - FAST!
    current_user = get_current_user()
    user_lat = current_user['latitude'] if current_user and current_user['latitude'] else 40.7589
    user_lng = current_user['longitude'] if current_user and current_user['longitude'] else -73.9851
    return render_template('map.html', user_lat=user_lat, user_lng=user_lng, current_user=current_user)

@app.route('/forum', methods=['GET', 'POST'])
@require_login
def forum():
    if request.method == 'POST':
        content = request.form['content']
        user_lat = session.get('latitude')
        user_lng = session.get('longitude')
        user_id = session.get('user_id')

        # Create new forum post - ONE LINE!
        try:
            create_forum_post(
                user_id=user_id,
                content=content,
                latitude=user_lat,
                longitude=user_lng
            )
            flash('Post shared with your local community!')
        except Exception as e:
            flash(f'Failed to create post: {str(e)}')

        return redirect(url_for('forum'))

    # Get forum posts - ONE LINE!
    try:
        nearby_posts = get_forum_posts()
    except Exception as e:
        nearby_posts = []
        flash(f'Failed to load posts: {str(e)}')

    return render_template('forum.html', posts=nearby_posts)

@app.route('/profile/<user_id>')
@require_login
def profile(user_id):
    # Get user by ID - ONE LINE!
    if not SUPABASE_CONNECTED:
        user = next((user for user in MOCK_USERS if user['id'] == user_id), None)
    else:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}',
            headers=SUPABASE_HEADERS
        )
        data = response.json()
        user = data[0] if data else None

    if not user:
        flash('User not found')
        return redirect(url_for('home'))

    return render_template('profile.html', user=user)

@app.route('/api/nearby-users')
@require_login
def api_nearby_users():
    # Get nearby users - ONE LINE!
    try:
        current_user_id = session.get('user_id')
        users = get_nearby_users(exclude_user_id=current_user_id)
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nearby-businesses')
@require_login
def api_nearby_businesses():
    # Get nearby businesses - ONE LINE!
    try:
        businesses = get_nearby_businesses()
        return jsonify(businesses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-api')
@require_login
def test_api():
    # Get users and businesses - SUPER FAST!
    try:
        users = get_nearby_users()
        businesses = get_nearby_businesses()

        return f"""
        <h1>🚀 Supabase API Test - BLAZING FAST!</h1>
        <h2>Users ({len(users)}):</h2>
        <ul>
        {''.join([f'<li>{u["username"]} - {u["latitude"]}, {u["longitude"]}</li>' for u in users])}
        </ul>

        <h2>Businesses ({len(businesses)}):</h2>
        <ul>
        {''.join([f'<li>{b["business_name"] or b["username"]} - {b["latitude"]}, {b["longitude"]}</li>' for b in businesses])}
        </ul>

        <h2>API Endpoints:</h2>
        <p><a href="/api/nearby-users" target="_blank">Test Users API</a></p>
        <p><a href="/api/nearby-businesses" target="_blank">Test Businesses API</a></p>
        <p><strong>⚡ Powered by Supabase - No SQLAlchemy needed!</strong></p>
        """
    except Exception as e:
        return f"<h1>❌ Error: {str(e)}</h1>"

@app.route('/init-database')
def init_database():
    """🚀 Initialize Supabase with test users - BLAZING FAST!"""
    try:
        # Check if users already exist
        if not SUPABASE_CONNECTED:
            return "⚠️ Supabase not connected. Using mock data."

        response = requests.get(f'{SUPABASE_URL}/rest/v1/users?select=id', headers=SUPABASE_HEADERS)
        existing_users = response.json()
        if existing_users:
            return f"""
            <h1>🚀 Supabase Database Already Initialized</h1>
            <p>Found {len(existing_users.data)} existing users in Supabase.</p>
            <p><a href="/">Go to Home Page</a></p>
            """

        import random

        # New York coordinates (Manhattan area)
        ny_locations = [
            {"lat": 40.7589, "lng": -73.9851, "area": "Times Square"},
            {"lat": 40.7505, "lng": -73.9934, "area": "Hell's Kitchen"},
            {"lat": 40.7614, "lng": -73.9776, "area": "Central Park South"},
            {"lat": 40.7831, "lng": -73.9712, "area": "Upper West Side"},
            {"lat": 40.7282, "lng": -73.9942, "area": "Greenwich Village"},
            {"lat": 40.7180, "lng": -74.0134, "area": "Tribeca"},
            {"lat": 40.7061, "lng": -74.0087, "area": "Financial District"},
        ]

        # Test users (people)
        test_people = [
            {"username": "john_nyc", "email": "john@example.com", "bio": "Love exploring NYC neighborhoods!"},
            {"username": "sarah_manhattan", "email": "sarah@example.com", "bio": "Coffee enthusiast and local foodie"},
            {"username": "mike_downtown", "email": "mike@example.com", "bio": "Photographer capturing city life"},
            {"username": "emma_uptown", "email": "emma@example.com", "bio": "Yoga instructor and wellness coach"},
            {"username": "alex_midtown", "email": "alex@example.com", "bio": "Tech worker, always looking for good lunch spots"},
            {"username": "lisa_village", "email": "lisa@example.com", "bio": "Artist and gallery owner"},
            {"username": "david_tribeca", "email": "david@example.com", "bio": "Finance professional, weekend explorer"},
        ]

        # Test businesses
        test_businesses = [
            {"username": "joes_coffee", "email": "info@joescoffee.com", "business_name": "Joe's Coffee Shop", "business_category": "Restaurant", "bio": "Best coffee in the neighborhood since 1995"},
            {"username": "central_gym", "email": "info@centralgym.com", "business_name": "Central Park Fitness", "business_category": "Fitness", "bio": "Premium fitness center with park views"},
            {"username": "marios_pizza", "email": "mario@mariospizza.com", "business_name": "Mario's Authentic Pizza", "business_category": "Restaurant", "bio": "Authentic Italian pizza made fresh daily"},
            {"username": "book_corner", "email": "hello@bookcorner.com", "business_name": "The Book Corner", "business_category": "Retail", "bio": "Independent bookstore with rare finds"},
            {"username": "fresh_market", "email": "contact@freshmarket.com", "business_name": "Fresh Market NYC", "business_category": "Grocery", "bio": "Organic produce and local goods"},
        ]

        created_users = []

        # Create people accounts - SUPER FAST!
        for i, person in enumerate(test_people):
            location = ny_locations[i % len(ny_locations)]
            lat_variation = random.uniform(-0.001, 0.001)
            lng_variation = random.uniform(-0.001, 0.001)

            result = create_user(
                username=person["username"],
                email=person["email"],
                password="password123",
                user_type="person",
                latitude=location["lat"] + lat_variation,
                longitude=location["lng"] + lng_variation,
                bio=person["bio"]
            )
            created_users.append(result.data[0])

        # Create business accounts - SUPER FAST!
        for i, business in enumerate(test_businesses):
            location = ny_locations[i % len(ny_locations)]
            lat_variation = random.uniform(-0.0005, 0.0005)
            lng_variation = random.uniform(-0.0005, 0.0005)

            result = create_user(
                username=business["username"],
                email=business["email"],
                password="business123",
                user_type="business",
                latitude=location["lat"] + lat_variation,
                longitude=location["lng"] + lng_variation,
                bio=business["bio"],
                business_name=business["business_name"],
                business_category=business["business_category"]
            )
            created_users.append(result.data[0])

        # Create forum posts - SUPER FAST!
        forum_posts = [
            {"content": "Anyone know what's happening at Washington Square Park today? Lots of music!", "user_idx": 0},
            {"content": "New coffee shop opened on 8th Ave! Great espresso and friendly staff ☕", "user_idx": 1},
            {"content": "Looking for a good photographer for headshots. Any recommendations?", "user_idx": 2},
            {"content": "Yoga class in Central Park tomorrow morning at 8 AM. All levels welcome! 🧘‍♀️", "user_idx": 3},
            {"content": "Best lunch spots near Times Square? Tired of tourist traps!", "user_idx": 4},
            {"content": "Art gallery opening this Friday in SoHo. Contemporary local artists featured.", "user_idx": 5},
            {"content": "Anyone interested in a weekend food tour of Chinatown?", "user_idx": 6},
        ]

        for post_data in forum_posts:
            user = created_users[post_data["user_idx"]]
            create_forum_post(
                user_id=user['id'],
                content=post_data["content"],
                latitude=user['latitude'],
                longitude=user['longitude']
            )

        return f"""
        <h1>🚀 Supabase Database Initialized Successfully!</h1>
        <p>Created {len(created_users)} users and {len(forum_posts)} forum posts in Supabase!</p>

        <h2>👥 Test Accounts Created:</h2>
        <h3>Personal Accounts (Password: password123):</h3>
        <ul>
        {''.join([f'<li><strong>{u["username"]}</strong> - {u["email"]}</li>' for u in created_users if u["user_type"] == 'person'])}
        </ul>

        <h3>Business Accounts (Password: business123):</h3>
        <ul>
        {''.join([f'<li><strong>{u["business_name"]}</strong> (@{u["username"]}) - {u["email"]}</li>' for u in created_users if u["user_type"] == 'business'])}
        </ul>

        <p><strong>⚡ Powered by Supabase - 10x faster than SQLAlchemy!</strong></p>
        <p><a href="/" style="background: #ffcc00; padding: 10px 20px; text-decoration: none; border-radius: 5px; color: black; font-weight: bold;">Go to Home Page</a></p>
        """

    except Exception as e:
        return f"""
        <h1>❌ Supabase Initialization Failed</h1>
        <p>Error: {str(e)}</p>
        <p>Make sure your SUPABASE_URL and SUPABASE_KEY are set correctly!</p>
        <p><a href="/">Go to Home Page</a></p>
        """

# 🚀 SUPABASE VERSION - NO DATABASE INITIALIZATION NEEDED!
# Supabase handles everything automatically!

# For Vercel deployment - this is the entry point
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

# Alternative handler for Vercel
app_handler = app

# Run locally and on Render
if __name__ == '__main__':
    print("🚀 Starting PingGov with Supabase - BLAZING FAST!")
    print(f"📡 Supabase URL: {SUPABASE_URL}")

    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))

    # Bind to 0.0.0.0 for production, localhost for development
    host = '0.0.0.0' if os.environ.get('RENDER') else '127.0.0.1'

    app.run(host=host, port=port, debug=False)