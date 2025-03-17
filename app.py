from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os   

app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'runclub.db')
db = SQLAlchemy(app)

class Profile(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    dob = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    bio = db.Column(db.Text)

class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer)
    theme = db.Column(db.String(100))
    time = db.Column(db.String(50))
    place = db.Column(db.String(100))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    venue = db.Column(db.String(100))
    date = db.Column(db.String(20))
    theme = db.Column(db.String(100))

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    price = db.Column(db.Integer)

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    image_path = db.Column(db.String(200))

# Dummy Data (Replace with Database Later)
# profile = {
#     "name": "Run Club Member",
#     "photo": "placeholder.jpg",
#     "dob": "YYYY-MM-DD",
#     "instagram": "@runclub",
#     "bio": "Join our running community!"
# }

# runs = [
#     {"week": 1, "theme": "Neon", "time": "7:00 AM", "place": "City Park"},
#     {"week": 2, "theme": "Retro", "time": "7:30 AM", "place": "Beachfront"},
#     {"week": 3, "theme": "Superhero", "time": "8:00 AM", "place": "Mountain Trail"}
# ]

# upcoming_events = [
#     {"price": 20, "venue": "Stadium", "date": "2024-12-15", "theme": "Winter Run"},
#     {"price": 15, "venue": "Community Hall", "date": "2025-01-10", "theme": "New Year Run"}
# ]

# sports = [
#     {"name": "Basketball", "venue": "Indoor Court", "price": 10},
#     {"name": "Volleyball", "venue": "Beach Court", "price": 8}
# ]

# gallery = {
#     "weekly_runs": ["run1.jpg", "run2.jpg", "run3.jpg"],
#     "events": ["event1.jpg", "event2.jpg"],
#     "sports": ["sport1.jpg", "sport2.jpg", "sport3.jpg"]
# }



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/profile")
def profile_page():
    with app.app_context():
        profile = Profile.query.all()
    return render_template("profile.html", profile=profile)

@app.route("/runs")
def runs_page():
    with app.app_context():
        runs=Run.query.all()
    return render_template("runs.html",runs=runs)

@app.route("/events")
def events_page():
    with app.app_context():
        events = Event.query.all()
    return render_template("events.html", events=events)

@app.route("/sports")
def sports_page():
    with app.app_context():
        sports = Sport.query.all()
    return render_template("sports.html", sports=sports)

@app.route("/gallery")
def gallery_page():
    weekly_runs=Gallery.query.filter_by(category="weekly_runs").all()
    events=Gallery.query.filter_by(category="events").all()
    sports=Gallery.query.filter_by(category="sports").all()
    return render_template("gallery.html", weekly_runs=weekly_runs,events=events,sports=sports)


if __name__=='__main__':
    with app.app_context():
        # db.create_all()
        # Populate Profile
        if not Profile.query.first():  # Check if profile exists
            new_profile = Profile(name="Run Club Member", photo="placeholder.jpg", dob="YYYY-MM-DD", instagram="@runclub", bio="Join our running community!")
            db.session.add(new_profile)

        # Populate Runs
        if not Run.query.first():
            for run_data in runs:
                new_run = Run(week=run_data["week"], theme=run_data["theme"], time=run_data["time"], place=run_data["place"])
                db.session.add(new_run)

        # Populate Events
        if not Event.query.first():
            for event_data in upcoming_events:
                new_event = Event(price=event_data["price"], venue=event_data["venue"], date=event_data["date"], theme=event_data["theme"])
                db.session.add(new_event)

        # Populate Sports
        if not Sport.query.first():
            for sport_data in sports:
                new_sport = Sport(name=sport_data["name"], venue=sport_data["venue"], price=sport_data["price"])
                db.session.add(new_sport)

        # Populate Gallery
        # Clear existing gallery entries
        Gallery.query.delete()

        # Populate Gallery (Dynamic)
        gallery_base_folder = os.path.join(basedir, 'static', 'gallery')

        categories = {
            'weekly_runs': 'runs',
            'events': 'events',
            'sports': 'sports'
        }

        for category_db, category_folder in categories.items():
            category_path = os.path.join(gallery_base_folder, category_folder)
            if os.path.exists(category_path):
                image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
                image_files = [f for f in os.listdir(category_path) if f.lower().endswith(image_extensions)]

                for image in image_files:
                    image_path_db = os.path.join('static','gallery', category_folder, image)
                    new_gallery = Gallery(category=category_db, image_path=image_path_db)
                    db.session.add(new_gallery)

        db.session.commit()
    app.run(debug=True)