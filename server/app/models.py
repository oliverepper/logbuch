import base64
import os
from datetime import datetime, timedelta
from textwrap import shorten
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login, ma


class ApiToken(db.Model):
    __tablename__ = "api_tokens"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64), index=True)
    expiration_date = db.Column(db.DateTime, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="api_token")

    @property
    def is_valid(self) -> bool:
        now = datetime.utcnow()
        return now < self.expiration_date


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    cellphone = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(256))
    allow_password_reset = db.Column(db.Boolean, default=False)

    api_token = db.relationship("ApiToken", uselist=False, back_populates="owner")

    my_logs = db.relationship("Log", back_populates="owner")

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

    def update_api_token(self, expires_in=3600):
        if self.api_token:
            db.session.delete(self.api_token)
        now = datetime.utcnow()
        self.api_token = ApiToken(
            value=base64.b64encode(os.urandom(32)).decode("utf-8"),
            expiration_date=now + timedelta(seconds=expires_in),
        )
        db.session.add(self.api_token)


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.UnicodeText)
    ctime = db.Column(db.DateTime, default=datetime.utcnow)
    mtime = db.Column(db.DateTime, onupdate=datetime.utcnow)

    log_id = db.Column(db.Integer, db.ForeignKey("logs.id"), nullable=False)
    log = db.relationship("Log", back_populates="entries")


class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ctime = db.Column(db.DateTime, default=datetime.utcnow)
    mtime = db.Column(db.DateTime, onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="my_logs")

    entries = db.relationship("Entry", back_populates="log", cascade="all, delete, delete-orphan")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)


class LogSchema(ma.ModelSchema):
    class Meta:
        model = Log
        dump_only = ('id', 'mtime', 'ctime')

    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("api.get_log", id="<id>"),
    #         "collection": ma.URLFor("api.get_logs"),
    #     }
    # )


class EntrySchema(ma.ModelSchema):
    class Meta:
        model = Entry
        dump_only = ('id', 'mtime', 'ctime')

    # log = ma.Nested(LogSchema)

    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("api.get_entry", id="<id>"),
    #         "collection": ma.URLFor("api.get_log", id="<log.id>"),
    #     }
    # )


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
