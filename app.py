# Import necessary libraries
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from geopy.distance import geodesic
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
# Fix for PostgreSQL URL format (Heroku/Vercel compatibility)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'person' or 'business'
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    profile_photo = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    bio = db.Column(db.Text)
    business_name = db.Column(db.String(100))  # For business accounts
    business_category = db.Column(db.String(50))  # For business accounts
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='posts')

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
# Routes
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

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type=user_type,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # Store user location in session for easy access
            session['latitude'] = user.latitude
            session['longitude'] = user.longitude
            session['user_type'] = user.user_type

            # Redirect to next page or map
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('map_view'))
        else:
            flash('Invalid email or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/map')
@login_required
def map_view():
    # Pass current user's location to the template
    user_lat = current_user.latitude or 40.7589  # Default to Times Square
    user_lng = current_user.longitude or -73.9851
    return render_template('map.html', user_lat=user_lat, user_lng=user_lng, current_user=current_user)

@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    if request.method == 'POST':
        content = request.form['content']
        user_lat = session.get('latitude')
        user_lng = session.get('longitude')

        # Create new forum post
        new_post = ForumPost(
            user_id=current_user.id,
            content=content,
            latitude=user_lat,
            longitude=user_lng,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_post)
        db.session.commit()

        flash('Post shared with your local community!')
        return redirect(url_for('forum'))

    # Get nearby posts (within 5km for demo)
    user_lat = session.get('latitude')
    user_lng = session.get('longitude')

    if user_lat and user_lng:
        # For demo, get all posts (in production, filter by distance)
        nearby_posts = ForumPost.query.order_by(ForumPost.timestamp.desc()).limit(10).all()
    else:
        nearby_posts = []

    return render_template('forum.html', posts=nearby_posts)

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

@app.route('/api/nearby-users')
@login_required
def get_nearby_users():
    # Get all users of type 'person' (excluding current user)
    users = User.query.filter(
        User.user_type == 'person',
        User.id != current_user.id,
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    ).all()

    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'latitude': user.latitude,
            'longitude': user.longitude,
            'bio': user.bio or 'No bio available',
            'rating': user.rating or 0
        })

    return jsonify(user_data)

@app.route('/api/nearby-businesses')
@login_required
def get_nearby_businesses():
    # Get all users of type 'business'
    businesses = User.query.filter(
        User.user_type == 'business',
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    ).all()

    business_data = []
    for business in businesses:
        business_data.append({
            'id': business.id,
            'username': business.username,
            'business_name': business.business_name or business.username,
            'business_category': business.business_category or 'Business',
            'latitude': business.latitude,
            'longitude': business.longitude,
            'bio': business.bio or 'No description available',
            'rating': business.rating or 0
        })

    return jsonify(business_data)

@app.route('/test-api')
@login_required
def test_api():
    users = User.query.filter(User.user_type == 'person').all()
    businesses = User.query.filter(User.user_type == 'business').all()

    return f"""
    <h1>API Test</h1>
    <h2>Users ({len(users)}):</h2>
    <ul>
    {''.join([f'<li>{u.username} - {u.latitude}, {u.longitude}</li>' for u in users])}
    </ul>

    <h2>Businesses ({len(businesses)}):</h2>
    <ul>
    {''.join([f'<li>{b.business_name or b.username} - {b.latitude}, {b.longitude}</li>' for b in businesses])}
    </ul>

    <h2>API Endpoints:</h2>
    <p><a href="/api/nearby-users" target="_blank">Test Users API</a></p>
    <p><a href="/api/nearby-businesses" target="_blank">Test Businesses API</a></p>
    """

@app.route('/init-database')
def init_database():
    """Initialize database with test users - for production deployment"""
    try:
        # Create tables
        db.create_all()

        # Check if users already exist
        existing_users = User.query.count()
        if existing_users > 0:
            return f"""
            <h1>Database Already Initialized</h1>
            <p>Found {existing_users} existing users in database.</p>
            <p><a href="/">Go to Home Page</a></p>
            """

        # Import the test user creation logic
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

        # Create people accounts
        for i, person in enumerate(test_people):
            location = ny_locations[i % len(ny_locations)]
            lat_variation = random.uniform(-0.001, 0.001)
            lng_variation = random.uniform(-0.001, 0.001)

            user = User(
                username=person["username"],
                email=person["email"],
                password=generate_password_hash("password123"),
                user_type="person",
                latitude=location["lat"] + lat_variation,
                longitude=location["lng"] + lng_variation,
                bio=person["bio"],
                rating=random.uniform(4.0, 5.0)
            )
            db.session.add(user)
            created_users.append(user)

        # Create business accounts
        for i, business in enumerate(test_businesses):
            location = ny_locations[i % len(ny_locations)]
            lat_variation = random.uniform(-0.0005, 0.0005)
            lng_variation = random.uniform(-0.0005, 0.0005)

            user = User(
                username=business["username"],
                email=business["email"],
                password=generate_password_hash("business123"),
                user_type="business",
                latitude=location["lat"] + lat_variation,
                longitude=location["lng"] + lng_variation,
                bio=business["bio"],
                business_name=business["business_name"],
                business_category=business["business_category"],
                rating=random.uniform(3.5, 5.0)
            )
            db.session.add(user)
            created_users.append(user)

        db.session.commit()

        # Create some forum posts
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
            post = ForumPost(
                user_id=user.id,
                content=post_data["content"],
                latitude=user.latitude,
                longitude=user.longitude,
                timestamp=datetime.utcnow()
            )
            db.session.add(post)

        db.session.commit()

        return f"""
        <h1>✅ Database Initialized Successfully!</h1>
        <p>Created {len(created_users)} users and {len(forum_posts)} forum posts.</p>

        <h2>👥 Test Accounts Created:</h2>
        <h3>Personal Accounts (Password: password123):</h3>
        <ul>
        {''.join([f'<li><strong>{u.username}</strong> - {u.email}</li>' for u in created_users if u.user_type == 'person'])}
        </ul>

        <h3>Business Accounts (Password: business123):</h3>
        <ul>
        {''.join([f'<li><strong>{u.business_name}</strong> (@{u.username}) - {u.email}</li>' for u in created_users if u.user_type == 'business'])}
        </ul>

        <p><strong>🎉 Your PingGov app is ready!</strong></p>
        <p><a href="/" style="background: #ffcc00; padding: 10px 20px; text-decoration: none; border-radius: 5px; color: black; font-weight: bold;">Go to Home Page</a></p>
        """

    except Exception as e:
        return f"""
        <h1>❌ Database Initialization Failed</h1>
        <p>Error: {str(e)}</p>
        <p><a href="/">Go to Home Page</a></p>
        """

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)