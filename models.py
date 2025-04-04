import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from running_club import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

user_runs = db.Table('user_runs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('run_id', db.Integer, db.ForeignKey('run.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """
    Represents a user in the application.
    Inherits from db.Model for database interaction and UserMixin for Flask-Login.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='club-member')
    runs = db.relationship('Run', secondary=user_runs, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        """
        Hashes the provided password and stores it in the password_hash attribute.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored password hash.
        """
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

class UPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upi_id = db.Column(db.String(100), unique=True)