from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    cellphone = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(256))
    allow_password_reset = db.Column(db.Boolean, default=False)

    logs = db.relationship("Log", back_populates="owner")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<" + self.email + ">"

    def get_password_reset_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_password_reset_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)


class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship("User", back_populates="logs")


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
