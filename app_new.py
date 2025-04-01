from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
import os
from PIL import Image
from flask_login import current_user, LoginManager, UserMixin, login_required, login_user, logout_user
from functools import wraps

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'runclub.db')
db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.join('static', 'profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_UPI_ID = '9620861165@pthdfc'
QR_CODE_FOLDER = os.path.join('static', 'qrcodes')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'ecd3ab359dcce6b999c1c63981703a3d'

user_runs = db.Table('user_runs',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('run_id', db.Integer, db.ForeignKey('run.id'), primary_key=True)
)

login_manager = LoginManager()  # Create an instance of LoginManager
login_manager.init_app(app)  # Initialize it with your Flask app
login_manager.login_view = 'login'  # If the user is not logged in, redirect to login page.

print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")


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

def generate_upi_qrcode(upi_id, filename):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,)
    qr.add_data(f"upi://pay?pa={upi_id}")
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    filepath = os.path.join(QR_CODE_FOLDER, filename)
    img.save(filepath)
    return url_for('static', filename=f'qrcodes/{filename}')

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
            login_user(user)
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

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                photo_path = filepath
            else:
                photo_path = None
        else:
            photo_path = None

        new_profile = Profile(id=new_user.id, name=request.form['name'], photo=photo_path, dob=request.form['dob'], instagram=request.form['instagram'])
        db.session.add(new_profile)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

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
    if request.method == 'POST':
        db.session.commit()
        return redirect(url_for('profile_page'))
    return render_template('profile.html', profile=profile, username=current_user.username)

@app.route('/add_run', methods=['GET', 'POST'])
@login_required
@admin_required
def add_run():
    if request.method == 'POST':
        new_run = Run(name=request.form['name'], week=request.form['week'], theme=request.form['theme'], time=request.form['time'], place=request.form['place'])
        db.session.add(new_run)
        db.session.commit()
        return redirect(url_for('runs_page'))
    return render_template('add_run.html')

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    if request.method == 'POST':
        new_event = Event(name=request.form['name'], price=request.form['price'], venue=request.form['venue'], date=request.form['date'], theme=request.form['theme'])
        db.session.add(new_event)
        db.session.commit()

@app.route('/add_sport', methods=['GET', 'POST'])
@login_required
@admin_required
def add_sport():
    if request.method == 'POST':
        # ... (add sport logic)
        db.session.add(new_sport)
        db.session.commit()
        return redirect(url_for('sports_page'))
    return render_template('add_sport.html')

@app.route('/add_gallery', methods=['GET', 'POST'])
@login_required
@admin_required
def add_gallery():
    if request.method == 'POST':
        # ... (add gallery logic)
        db.session.add(new_gallery)
        db.session.commit()
        return redirect(url_for('gallery_page'))
    return render_template('add_gallery.html')

@app.route('/payments_qr/<int:event_id>')
def payments_qr(event_id):
    event = Event.query.get(event_id) #get the event object.
    qr_filename = f'upi_qr_{event_id}.png'
    qr_code_url = generate_upi_qrcode(ADMIN_UPI_ID, qr_filename)
    return render_template('payments_qr.html', event=event, qr_code_url=qr_code_url) #pass event object.


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        dob = request.form['dob']
        instagram = request.form['instagram']

        # Call the register_user function
        message, status_code = register_user(username, password, role, name, dob, instagram)

        if status_code == 201:  # Successful registration
            # Handle photo upload
            photo_path = None  # Initialize to None

            if 'photo' in request.files:
                file = request.files['photo']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
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





