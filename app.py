import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from models import db, User, Trip
from utils.ai import recommend_states, recommend_places, get_place_details, answer_place_question
from utils.image_api import get_place_images

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    if not os.path.exists('instance/database.db'):
        db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.')
            return redirect(url_for('signup'))
        
        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.id.desc()).all()
    # Calculate some basic stats
    total_trips = len(trips)
    planned_trips = len([t for t in trips if not t.selected_place])
    completed_trips = total_trips - planned_trips # Simplified logic
    
    return render_template('dashboard.html', 
                           user=current_user, 
                           trips=trips,
                           stats={
                               'total': total_trips,
                               'planned': planned_trips,
                               'completed': completed_trips
                           })

@app.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():
    if request.method == 'POST':
        budget = request.form.get('budget-range', '25000')
        travelers = request.form.get('traveler-count', '2')
        age_group = request.form.get('age-group', 'adult')
        travel_type = request.form.get('travel-type', 'nature')
        duration = request.form.get('duration', '7')
        
        try:
            # Clean budget string if it has symbols
            budget_val = str(budget).replace('₹', '').replace(',', '').strip()
            budget_int = int(float(budget_val)) if budget_val else 25000
            
            new_trip = Trip(
                user_id=current_user.id,
                budget=budget_int,
                travelers=int(travelers),
                age_group=age_group,
                travel_type=travel_type,
                duration=int(duration)
            )
            db.session.add(new_trip)
            db.session.commit()
            
            session['last_trip_id'] = new_trip.id
            return redirect(url_for('recommend'))
        except Exception as e:
            app.logger.error(f"Error saving trip: {e}")
            flash(f"Error saving trip: {e}")
            return redirect(url_for('plan'))
    
    return render_template('travel_input.html')

@app.route('/recommend')
@login_required
def recommend():
    trip_id = session.get('last_trip_id')
    if not trip_id:
        return redirect(url_for('plan'))
    
    trip = Trip.query.get(trip_id)
    states = recommend_states(trip.budget, trip.travelers, trip.travel_type, trip.duration)

    # Attach one Unsplash image per state card.
    for state_item in states:
        name = state_item.get("name")
        images = get_place_images(name) if name else []
        state_item["image"] = images[0] if images else None

    return render_template('recommendations.html', states=states)

@app.route('/places/<state_name>')
@login_required
def places(state_name):
    trip_id = session.get('last_trip_id')
    if not trip_id:
        return redirect(url_for('plan'))
    
    trip = Trip.query.get(trip_id)
    trip.selected_state = state_name
    db.session.commit()
    
    places_list = recommend_places(
        state_name,
        trip.travel_type,
        budget=trip.budget,
        members=trip.travelers,
        age_group=trip.age_group,
        duration=trip.duration,
    )

    # Attach one specific Unsplash image per place card
    for place_item in places_list:
        place_name = place_item.get('name', '')
        imgs = get_place_images(place_name)
        place_item['image'] = imgs[0] if imgs else None

    return render_template('recommendations.html', places=places_list, state=state_name)

@app.route('/place/<place_name>')
@login_required
def place_details_view(place_name):
    trip_id = session.get('last_trip_id')
    if not trip_id:
        return redirect(url_for('plan'))
    
    trip = Trip.query.get(trip_id)
    trip.selected_place = place_name

    # Fetch images first so we can reuse the hero image
    images = get_place_images(place_name)
    hero_image = images[0] if images else None

    # Pass trip duration so the AI generates the right number of itinerary days
    details = get_place_details(place_name, duration=trip.duration)
    
    trip.itinerary = str(details.get('itinerary', []))
    db.session.commit()
    
    return render_template('place.html', 
                          place_name=place_name,
                          state_name=trip.selected_state or '',
                          trip=trip,
                          description=details.get('description'),
                          cost=details.get('estimated_cost'),
                          itinerary=details.get('itinerary', []),
                          images=images,
                          hero_image=hero_image)

from flask import jsonify

@app.route('/api/chat/<place_name>', methods=['POST'])
@login_required
def chat_about_place(place_name):
    data = request.get_json()
    question = (data or {}).get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    trip_id = session.get('last_trip_id')
    state_name = ''
    if trip_id:
        trip = Trip.query.get(trip_id)
        if trip:
            state_name = trip.selected_state or ''

    answer = answer_place_question(place_name, state_name, question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
