#!/usr/bin/env python3
"""
Script to create test users in New York for PingGov application
"""

from app import app, db, User, ForumPost
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

def create_test_users():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # New York coordinates (Manhattan area)
        ny_locations = [
            {"lat": 40.7589, "lng": -73.9851, "area": "Times Square"},
            {"lat": 40.7505, "lng": -73.9934, "area": "Hell's Kitchen"},
            {"lat": 40.7614, "lng": -73.9776, "area": "Central Park South"},
            {"lat": 40.7831, "lng": -73.9712, "area": "Upper West Side"},
            {"lat": 40.7282, "lng": -73.9942, "area": "Greenwich Village"},
            {"lat": 40.7180, "lng": -74.0134, "area": "Tribeca"},
            {"lat": 40.7061, "lng": -74.0087, "area": "Financial District"},
            {"lat": 40.7505, "lng": -73.9934, "area": "Midtown West"},
            {"lat": 40.7549, "lng": -73.9840, "area": "Theater District"},
            {"lat": 40.7411, "lng": -73.9897, "area": "Chelsea"},
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
            # Add some random variation to coordinates (within ~100 meters)
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
            created_users.append((user, location["area"]))
        
        # Create business accounts
        for i, business in enumerate(test_businesses):
            location = ny_locations[i % len(ny_locations)]
            # Add some random variation to coordinates
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
            created_users.append((user, location["area"]))
        
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
            user = created_users[post_data["user_idx"]][0]
            post = ForumPost(
                user_id=user.id,
                content=post_data["content"],
                latitude=user.latitude,
                longitude=user.longitude,
                timestamp=datetime.utcnow()
            )
            db.session.add(post)
        
        db.session.commit()
        
        print("✅ Test users created successfully!")
        print("\n👥 PEOPLE ACCOUNTS:")
        for user, area in created_users[:len(test_people)]:
            print(f"  • {user.username} ({user.email}) - {area}")
            print(f"    Password: password123")
            print(f"    Location: {user.latitude:.4f}, {user.longitude:.4f}")
            print(f"    Bio: {user.bio}\n")
        
        print("🏪 BUSINESS ACCOUNTS:")
        for user, area in created_users[len(test_people):]:
            print(f"  • {user.business_name} (@{user.username}) - {area}")
            print(f"    Email: {user.email}")
            print(f"    Password: business123")
            print(f"    Category: {user.business_category}")
            print(f"    Location: {user.latitude:.4f}, {user.longitude:.4f}")
            print(f"    Bio: {user.bio}\n")
        
        print("💬 FORUM POSTS:")
        posts = ForumPost.query.all()
        for post in posts:
            print(f"  • {post.user.username}: {post.content}")
        
        print(f"\n🎉 Created {len(created_users)} users and {len(posts)} forum posts!")
        print("You can now login with any of the accounts above.")

if __name__ == "__main__":
    create_test_users()
