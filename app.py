from flask import Flask, render_template, request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
import os   
from PIL import Image

app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'runclub.db')
db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.join('static','profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
ADMIN_UPI_ID='9620861165@pthdfc'
QR_CODE_FOLDER=os.path.join('static','qrcodes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_upi_qrcode(upi_id,filename):
    qr=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,)
    
    qr.add_data(f"upi://pay?pa={upi_id}")
    qr.make(fit=True)

    img=qr.make_image(fill_color='black',back_color='white')
    filepath=os.path.join(QR_CODE_FOLDER,filename)
    img.save(filepath)
    return url_for('static',filename=f'qrcodes/{filename}')



app.config['SECRET_KEY']='ecd3ab359dcce6b999c1c63981703a3d'

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password_hash=db.Column(db.String(120),nullable=False)
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('home')) 
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Handle photo upload
        if 'photo' in request.files:
            print("photo in request files")
            file = request.files['photo']
            if file and allowed_file(file.filename):
                print("allowed")
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'])
                file.save(filepath)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #Path to store in the database.
            else:
                print("not allowed")
                photo_path = None 
        else:
            print("photo not in request files")
            photo_path = None 

        # Create Profile for the new user
        new_profile = Profile(id=new_user.id, name=request.form['name'], photo=photo_path, dob=request.form['dob'], instagram=request.form['instagram'])
        db.session.add(new_profile)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/")
def home(): 
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            profile = Profile.query.filter_by(id=user.id).first()
            return render_template('home.html', profile=profile)
        else:
            return render_template('home.html', profile=None)
    else:
        return redirect(url_for('login'))

@app.route("/profile")
def profile_page():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            profile = Profile.query.filter_by(id=user.id).first()
            if request.method == 'POST': #add this section to update or create a profile.
                name = request.form.get('name')
                dob = request.form.get('dob')
                instagram = request.form.get('instagram')
                bio = request.form.get('bio')
                #Handle photo upload here.

                if profile:
                    profile.name = name
                    profile.dob = dob
                    profile.instagram = instagram
                    profile.bio = bio
                else:
                    profile = Profile(id=user.id,name=name, dob=dob, instagram=instagram, bio=bio)
                    db.session.add(profile)
                db.session.commit()
                return redirect(url_for('profile_page'))

            return render_template('profile.html', profile=profile,username=username)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route("/runs")
def runs_page():
    with app.app_context():
        runs=Run.query.all()
    return render_template("runs.html",runs=runs)

@app.route("/events")
def events_page():
    with app.app_context():
        upcoming_events = Event.query.all()
    return render_template("events.html", upcoming_events=upcoming_events)

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

@app.route('/payments_qr/<int:event_id>')
def payments_qr(event_id):
    event = Event.query.get(event_id) #get the event object.
    qr_filename = f'upi_qr_{event_id}.png'
    qr_code_url = generate_upi_qrcode(ADMIN_UPI_ID, qr_filename)
    return render_template('payments_qr.html', event=event, qr_code_url=qr_code_url) #pass event object.



if __name__=='__main__':
    with app.app_context():
        db.create_all()
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
                    image_path_db = f'gallery/{category_folder}/{image}'
                    new_gallery = Gallery(category=category_db, image_path=image_path_db)
                    db.session.add(new_gallery)

        db.session.commit()
    app.run(debug=True)





