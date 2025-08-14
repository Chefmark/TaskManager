from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.String(10), nullable=True)  # Format: YYYY-MM-DD
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10))
    tags=db.Column(db.Text)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

users = {
    "marekm": User(id=1, username="marekm", password_hash=generate_password_hash("password123")),
}
    
