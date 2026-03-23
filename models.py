from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    trips = db.relationship('Trip', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    travelers = db.Column(db.Integer, nullable=False)
    age_group = db.Column(db.String(50), nullable=False)
    travel_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    selected_state = db.Column(db.String(100))
    selected_place = db.Column(db.String(100))
    itinerary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
