from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'runclub.db')
app.config['SECRET_KEY'] = 'ecd3ab359dcce6b999c1c63981703a3d'
UPLOAD_FOLDER = os.path.join('static','profile_photos')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from running_club import routes, models, functions  