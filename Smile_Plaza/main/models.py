from datetime import datetime
from time import time
import jwt
from flask import current_app
from main import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from time import time

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(30), nullable=False)
    MidName = db.Column(db.String(30), nullable=True)
    LName = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birthday = db.Column(db.String(8), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(30), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"User('{self.FName}', '{self.MidName}', '{self.LName}', '{self.birthday}', '{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    service = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    user_contact = db.Column(db.String(30), db.ForeignKey('user.contact'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('date', 'time', name='unique_date_time'),)
    
    def __repr__(self):
        return f"Appointment('{self.user_name}', '{self.user_email}', '{self.date}', '{self.time}"