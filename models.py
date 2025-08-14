from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

users = {
    "marekm": User(id=1, username="marekm", password_hash=generate_password_hash("password123")),
}
    
