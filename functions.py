
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from running_club import db, app
from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user
from running_club.models import User, Profile
from werkzeug.security import generate_password_hash
import re
import os
import qrcode

UPLOAD_FOLDER = os.path.join('static','profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
QR_CODE_FOLDER = os.path.join('static','qrcodes')

def admin_required(f):
    """
    Decorator to require admin-team role for accessing a route.

    Redirects non-admin users to the home page with a flash message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin-team':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """
    Checks if the given filename has an allowed file extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_date(date_string):
    """
    Validates if the given string matches the format dd/mm/yyyy.

    Args:
        date_string (str): The string to validate.

    Returns:
        bool: True if the format is correct, False otherwise.
    """
    return re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$", date_string)

def generate_upi_qrcode():
    """
    Generates a UPI QR code based on the UPI ID stored in the database.

    Returns:
        str or None: The URL of the generated QR code image, or None if no UPI ID is found.
    """
    from running_club.models import UPI
    upi_record = UPI.query.first()
    if not upi_record:
        return None
    upi_id = upi_record.upi_id
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(f"upi://pay?pa={upi_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    filename = 'upi_qr.png'
    filepath = os.path.join(QR_CODE_FOLDER, filename)
    img.save(filepath)
    return url_for('static', filename=f'qrcodes/{filename}')

def register_user(username, password, role, name, dob, instagram):
    """
    Registers a new user in the application.

    Args:
        username (str): The desired username.
        password (str): The user's password.
        role (str): The user's role (e.g., 'club-member', 'admin-team').
        name (str): The user's name.
        dob (str, optional): The user's date of birth (dd/mm/yyyy). Defaults to None.
        instagram (str, optional): The user's Instagram handle. Defaults to None.

    Returns:
        tuple: A tuple containing a message (str) and a status code (int).
               - Success: ("User registered successfully.", 201)
               - Error (Username exists): ("Username already exists.", 400)
    """
    
    if User.query.filter_by(username=username).first():
        return "Username already exists.", 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    new_profile = Profile(id=new_user.id, name=name, dob=dob, instagram=instagram)
    db.session.add(new_profile)
    db.session.commit()
    return "User registered successfully.", 201