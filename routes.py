import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from running_club import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user
from running_club.models import User, Profile, Run, Event, Sport, Gallery, UPI
from running_club.functions import admin_required, allowed_file, is_valid_date, generate_upi_qrcode, register_user
from werkzeug.utils import secure_filename

import os

QR_CODE_FOLDER=os.path.join('static','qrcodes')

@login_manager.user_loader
def load_user(user_id):
    """
    Callback function required by Flask-Login to load a user from the database.
    It retrieves a User object based on the provided user ID.
    """
    return User.query.get(int(user_id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Route for the user login page.
    Handles both displaying the login form (GET request) and processing login attempts (POST request).
    """
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
    """
    Route for the user registration page.
    Handles both displaying the registration form (GET request) and processing new user registrations (POST request).
    """
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
    """
    Route to log the current user out of the application.
    """
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    """
    Route for the application's home page.
    Requires the user to be logged in to access.
    Fetches the user's profile information to display.
    """
    profile = Profile.query.filter_by(id=current_user.id).first()
    return render_template('home.html', profile=profile)


@app.route("/profile")
def profile_page():
    """
    Route for displaying the user's profile page.
    Fetches the user's profile information.
    Currently, it only handles GET requests to display the profile.
    """
    profile = Profile.query.filter_by(id=current_user.id).first()
    print(profile.photo) 
    if request.method == 'POST':
        db.session.commit()
        return redirect(url_for('profile_page'))
    return render_template('profile.html', profile=profile, username=current_user.username)

@app.route("/runs")
def runs_page():
    """
    Route to display the page listing available runs.
    Fetches all run events from the database.
    """
    with app.app_context():
        runs=Run.query.all()
    return render_template("runs.html",runs=runs)


@app.route("/events")
def events_page():
    """
    Route to display the page listing upcoming events.
    Fetches all event records from the database.
    """
    with app.app_context():
        upcoming_events = Event.query.all()
    return render_template("events.html", upcoming_events=upcoming_events)

@app.route("/sports")
def sports_page():
    """
    Route to display the page listing available sports activities.
    Fetches all sport records from the database.
    """
    with app.app_context():
        sports = Sport.query.all()
    return render_template("sports.html", sports=sports)

@app.route("/tracker")
@login_required
def tracker():
    """
    Route for the user's run tracker page.
    Requires the user to be logged in.
    Fetches all available runs and the IDs of the runs the current user has selected.
    """
    runs = Run.query.all()
    user_runs_ids = [run.id for run in current_user.runs]
    return render_template('tracker.html', runs=runs, user_runs_ids=user_runs_ids)

@app.route('/save_selected_runs', methods=['POST'])
def save_selected_runs():
    """
    Route to handle saving the user's selected runs.
    Accepts a POST request with JSON data containing the selected run weeks.
    Updates the user's associated runs in the database.
    """
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
    """
    Route to display the image gallery, categorized by Runs, Events, and Sports.
    Fetches images from the database based on their category.
    """
    Runs = Gallery.query.filter_by(category="Runs").all()
    Events = Gallery.query.filter_by(category="Events").all()
    Sports = Gallery.query.filter_by(category="Sports").all()
    return render_template("gallery.html", Runs=Runs, Events=Events, Sports=Sports)


@app.route('/payments_qr/<int:event_id>')
def payments_qr(event_id):
    """
    Route to display the payment QR code for a specific event.
    Fetches the event details and generates the UPI QR code URL.
    """
    event = Event.query.get(event_id)
    qr_code_url = generate_upi_qrcode()
    return render_template('payments_qr.html', event=event, qr_code_url=qr_code_url)

@app.route('/update_upi', methods=['GET', 'POST'])
@login_required
@admin_required
def update_upi():
    """
    Route for administrators to update the stored UPI ID.
    Handles both displaying the update form (GET request) and processing the update (POST request).
    Requires the user to be logged in as an admin.
    """
    upi_record = UPI.query.first()
    if request.method == 'POST':
        new_upi_id = request.form.get('upi_id')
        if upi_record:
            upi_record.upi_id = new_upi_id
        else:
            new_upi = UPI(upi_id=new_upi_id)
            db.session.add(new_upi)
        db.session.commit()
        flash('UPI ID updated successfully!', 'success')
        # delete the previous QR code.
        filename = os.listdir(QR_CODE_FOLDER)[0] if os.listdir(QR_CODE_FOLDER) else None
        if filename:
          os.remove(os.path.join(QR_CODE_FOLDER, filename))
        return redirect(url_for('update_upi'))
    return render_template('update_upi.html', upi_record=upi_record)

#admin access only routes
@app.route('/add_run', methods=['GET', 'POST'])
@login_required
@admin_required
def add_run():
    """
    Route for administrators to add a new run event.
    Handles both displaying the add run form (GET request) and processing the submission (POST request).
    Requires the user to be logged in as an admin.
    """
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
    """
    Route for administrators to add a new event.
    Handles both displaying the add event form (GET request) and processing the submission (POST request).
    Requires the user to be logged in as an admin.
    """
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
    """
    Route for administrators to add a new sport activity.
    Handles both displaying the add sport form (GET request) and processing the submission (POST request).
    Requires the user to be logged in as an admin.
    """
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
    """
    Route for administrators to add new images to the gallery.
    Handles both displaying the add gallery form (GET request) and processing the image uploads (POST request).
    Requires the user to be logged in as an admin.
    """
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

