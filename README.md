# PingGov - Local Social Discovery Platform

A geo-location based social and business discovery platform built with Flask. Connect with nearby users, discover local businesses, and join location-based discussions.

## 🌟 Features

- **🗺️ Interactive Map**: See nearby users and businesses on an interactive map with clickable pins
- **💬 Local Forum**: Join discussions that are only visible to people in your area
- **🏪 Business Discovery**: Find local businesses with ratings and reviews (Google Maps-like experience)
- **👥 User Profiles**: Create customizable profiles (Rappi-style for users, business profiles for companies)
- **📍 Real-time Location**: Automatic location tracking and proximity-based content
- **🔐 Authentication**: Secure user registration and login system

## 🚀 Live Demo

Visit the live application: [PingGov on Vercel](https://your-app-url.vercel.app)

## 🧪 Test Accounts

### Personal Accounts
- **Email**: `john@example.com` | **Password**: `password123`
- **Email**: `sarah@example.com` | **Password**: `password123`
- **Email**: `mike@example.com` | **Password**: `password123`

### Business Accounts
- **Email**: `info@joescoffee.com` | **Password**: `business123`
- **Email**: `mario@mariospizza.com` | **Password**: `business123`

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript, Leaflet Maps
- **Database**: SQLite (development), PostgreSQL (production)
- **Deployment**: Vercel
- **Styling**: Custom CSS with yellow/white/black theme

## 🏃‍♂️ Running Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pinggov.git
   cd pinggov
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create test data**
   ```bash
   python create_test_users.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 🌐 Deployment

This app is configured for easy deployment on Vercel:

1. Push to GitHub
2. Connect your GitHub repo to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy!

## 📁 Project Structure

```
pinggov/
├── app.py                 # Main Flask application
├── create_test_users.py   # Script to populate test data
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── map.html
│   ├── forum.html
│   └── profile.html
└── static/              # Static assets
    ├── css/
    ├── js/
    └── images/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with Flask and Leaflet Maps
- Inspired by modern social platforms and local discovery apps
- Test data includes fictional NYC locations and businesses
