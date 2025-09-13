import json
import os
from datetime import datetime
from key import flashkey as fkey, admin_key as akey
import uuid
import logging
from flask import Blueprint,Flask,flash, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from models import User, Task
from werkzeug.security import check_password_hash
from extensions import db
from utils import log_error, is_valid_date, is_overdue
from routes.main import main_bp
from routes.auth import auth_bp 
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = fkey
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

logging.basicConfig(
    filename='error.log',
    level =logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

def create_admin_user():
    admin_username = "admin"
    admin_password = akey

    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        admin_user = User(username=admin_username, is_admin=True)
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user created with username: {admin_username} and password.")
    else:
        print("Admin user already exists.")    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        create_admin_user()
    app.run(debug=True)