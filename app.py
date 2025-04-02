from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
import os
import re
from PIL import Image
from flask_login import current_user, LoginManager, UserMixin, login_required, login_user, logout_user
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'runclub.db')
db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.join('static','profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
ADMIN_UPI_ID='9620861165@pthdfc'
QR_CODE_FOLDER=os.path.join('static','qrcodes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'ecd3ab359dcce6b999c1c63981703a3d'

user_runs = db.Table('user_runs',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('run_id', db.Integer, db.ForeignKey('run.id'), primary_key=True)
)

login_manager = LoginManager()  # Create an instance of LoginManager
login_manager.init_app(app)  # Initialize it with your Flask app
login_manager.login_view = 'login'  # If the user is not logged in, redirect to login page.


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='club-member')
    runs = db.relationship('Run', secondary=user_runs, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    dob = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    bio = db.Column(db.Text)

class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    week = db.Column(db.Integer)
    theme = db.Column(db.String(100))
    time = db.Column(db.String(50))
    place = db.Column(db.String(100))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
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



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin-team':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))  # or another appropriate page
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_date(date_string):
    return re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$", date_string)


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

def register_user(username, password, role, name, dob, instagram):
    # ... (your register_user function code) ...
    if User.query.filter_by(username=username).first():
        return "Username already exists.", 400  # 400 Bad Request

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Create profile
    new_profile = Profile(id = new_user.id, name = name, dob = dob, instagram=instagram)
    db.session.add(new_profile)
    db.session.commit()

    return "User registered successfully.", 201  # 201 Created

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user) #flask-login login
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
        role = request.form['role']
        name = request.form['name']
        dob = request.form['dob']
        instagram = request.form['instagram']

        if dob and not is_valid_date(dob): #dob is optional, but if present, validate.
            flash('Invalid date of birth format. Please use dd/mm/yyyy.', 'error')
            return render_template('register.html')

        # Call the register_user function
        message, status_code = register_user(username, password, role, name, dob, instagram)

        if status_code == 201:  # Successful registration
            # Handle photo upload
            photo_path = None  # Initialize to None

            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    # Get the file extension
                    file_ext = os.path.splitext(file.filename)[1]

                    # Construct the filename
                    filename = f"{username}{file_ext}"

                    # Construct the filepath
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Save the file
                    file.save(filepath)

                    # Construct the relative path to store in the database
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Update the profile with the photo path
            user = User.query.filter_by(username=username).first()
            if user:
                profile = Profile.query.filter_by(id=user.id).first()
                if profile:
                    profile.photo = photo_path
                    db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:  # Registration error
            flash(message, 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    profile = Profile.query.filter_by(id=current_user.id).first()
    return render_template('home.html', profile=profile)


@app.route("/profile")
def profile_page():
    profile = Profile.query.filter_by(id=current_user.id).first()
    print(profile.photo) 
    if request.method == 'POST':
        db.session.commit()
        return redirect(url_for('profile_page'))
    return render_template('profile.html', profile=profile, username=current_user.username)
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

@app.route("/tracker")
@login_required
def tracker():
    runs = Run.query.all()
    user_runs_ids = [run.id for run in current_user.runs]
    return render_template('tracker.html', runs=runs, user_runs_ids=user_runs_ids)

@app.route('/save_selected_runs', methods=['POST'])
def save_selected_runs():
    data = request.get_json()
    selected_weeks = data['selectedWeeks']

    # Clear existing selections
    current_user.runs = []  # Clear existing runs
    db.session.commit()

    # Add new selections
    for week in selected_weeks:
        runs = Run.query.filter_by(week=week).all()
        for run in runs:
            current_user.runs.append(run)

    db.session.commit()
    return jsonify({'message': 'Selected runs saved successfully.'})

@app.route("/gallery")
def gallery_page():
    Runs = Gallery.query.filter_by(category="Runs").all()
    Events = Gallery.query.filter_by(category="Events").all()
    Sports = Gallery.query.filter_by(category="Sports").all()
    return render_template("gallery.html", Runs=Runs, Events=Events, Sports=Sports)


@app.route('/payments_qr/<int:event_id>')
def payments_qr(event_id):
    event = Event.query.get(event_id)
    qr_filename = f'upi_qr_{event_id}.png'
    qr_code_url = generate_upi_qrcode(ADMIN_UPI_ID, qr_filename)
    return render_template('payments_qr.html', event=event, qr_code_url=qr_code_url)

#ADMIN-ONLY
@app.route('/add_run', methods=['GET', 'POST'])
@login_required
@admin_required
def add_run():
    if request.method == 'POST':
        name = request.form.get('name')
        week = request.form.get('week')
        theme = request.form.get('theme')
        time = request.form.get('time')
        place = request.form.get('place')

        new_run = Run(name=name, week=week, theme=theme, time=time, place=place)
        db.session.add(new_run)
        db.session.commit()
        flash('Run added successfully!', 'success')
        return redirect(url_for('runs_page'))
    return render_template('add_run.html')

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        venue = request.form.get('venue')
        date = request.form.get('date')
        theme = request.form.get('theme')

        if not is_valid_date(date):
            flash('Invalid date format. Please use dd/mm/yyyy.', 'error')
            return render_template('add_event.html')

        new_event = Event(name=name, price=price, venue=venue, date=date, theme=theme)
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('events_page'))
    return render_template('add_event.html')

@app.route('/add_sport', methods=['GET', 'POST'])
@login_required
@admin_required
def add_sport():
    if request.method == 'POST':
        name = request.form.get('name')
        venue = request.form.get('venue')
        price = request.form.get('price')

        new_sport = Sport(name=name, venue=venue, price=price)
        db.session.add(new_sport)
        db.session.commit()
        flash('Sport added successfully!', 'success')
        return redirect(url_for('sports_page'))
    return render_template('add_sport.html')


@app.route('/add_gallery', methods=['GET', 'POST'])
@login_required
@admin_required
def add_gallery():
    if request.method == 'POST':
        category = request.form.get('category')
        files = request.files.getlist('images')  

        if not files:
            flash('No files selected', 'danger')
            return redirect(request.url)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'gallery', category, filename)
                file.save(filepath)

                # Create the database entry for each file
                image_path_db = f'gallery/{category}/{filename}'
                new_gallery = Gallery(category=category, image_path=image_path_db)
                db.session.add(new_gallery)

        db.session.commit()
        flash('Images uploaded successfully!', 'success')
        return redirect(url_for('gallery_page'))
    return render_template('add_gallery.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Populate Profile
        if not Profile.query.first():
            new_profile = Profile(name="Run Club Member", photo="placeholder.jpg", dob="YYYY-MM-DD", instagram="@runclub", bio="Join our running community!")
            db.session.add(new_profile)

        db.session.commit()
    app.run(debug=True)