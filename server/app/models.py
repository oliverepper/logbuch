import base64
import os
from datetime import datetime, timedelta
from enum import Enum
from textwrap import shorten
from time import time

import jwt
from flask import current_app, render_template
from flask_babel import _
from flask_login import UserMixin
from marshmallow_enum import EnumField
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login, ma
from app.email import send_email


class MembershipType(Enum):
    READ = 1
    WRITE = 2

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return not self.__gt__(other)


class Membership(db.Model):
    __tablename__ = "memberships"
    log_id = db.Column(db.Integer, db.ForeignKey("logs.id"), primary_key=True)
    log = db.relationship("Log")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship("User")
    type = db.Column(db.Enum(MembershipType), default=MembershipType.READ)

    @classmethod
    def from_invitation_token(cls, token):
        try:
            membership_data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except Exception as e:
            raise Exception("Your invitation token is invalid")

        try:
            membership = Membership.query.filter_by(
                log_id=membership_data["log"], user_id=membership_data["user"]
            ).one()
        except Exception as e:
            membership = Membership()
        return MembershipSchema().load(
            membership_data, instance=membership, session=db.session
        )


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

    memberships = db.relationship("Membership", back_populates="user")
    foreign_logs = association_proxy("memberships", "log")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        if self.username:
            return self.username
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

    def has_write_permission(self, log: "Log") -> bool:
        if log in self.my_logs:
            return True
        try:
            ms = Membership.query.filter_by(log=log, user=self).one()
        except Exception as e:
            return False
        return ms.type == MembershipType.WRITE


class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    ctime = db.Column(db.DateTime, default=datetime.utcnow)
    mtime = db.Column(db.DateTime, onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="my_logs")

    entries = db.relationship(
        "Entry", back_populates="log", cascade="all, delete, delete-orphan"
    )

    memberships = db.relationship("Membership", back_populates="log")
    members = association_proxy("memberships", "user")

    def __repr__(self):
        return f"<Log {self.id}>"

    def invite_as_write_member(self, user: User):
        self._send_membership_invitation(
            Membership(user=user, log=self, type=MembershipType.WRITE)
        )

    invite_as_coach = invite_as_write_member

    def invite_as_read_member(self, user: User):
        self._send_membership_invitation(
            Membership(user=user, log=self, type=MembershipType.READ)
        )

    invite_as_fan = invite_as_read_member

    def _send_membership_invitation(self, membership: Membership):
        membership_data = MembershipSchema().dump(membership)
        token = jwt.encode(
            membership_data, current_app.config["SECRET_KEY"], algorithm="HS256"
        ).decode("utf-8")
        with current_app.app_context(), current_app.test_request_context():
            send_email(
                _("[Logbuch] membership invitation"),
                sender=current_app.config["SENDER_EMAIL"][0],
                recipients=[membership.user.email],
                text_body=render_template(
                    "models/email/membership_invite.txt", token=token
                ),
                html_body=render_template(
                    "models/email/membership_invite.html", token=token
                )
            )


class Entry(db.Model):
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.UnicodeText)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    creator = db.relationship("User")
    ctime = db.Column(db.DateTime, default=datetime.utcnow)
    mtime = db.Column(db.DateTime, onupdate=datetime.utcnow)

    log_id = db.Column(db.Integer, db.ForeignKey("logs.id"), nullable=False)
    log = db.relationship("Log", back_populates="entries")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)


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


class LogSchema(ma.ModelSchema):
    class Meta:
        model = Log
        dump_only = ("id", "mtime", "ctime", "entries", "memberships")

    # entries = ma.Nested(EntrySchema, many=True)

    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("api.get_log", id="<id>"),
    #         "collection": ma.URLFor("api.get_logs"),
    #     }
    # )


class EntrySchema(ma.ModelSchema):
    class Meta:
        model = Entry
        dump_only = ("id", "mtime", "ctime", "creator")

    # log = ma.Nested(LogSchema)

    # _links = ma.Hyperlinks(
    #     {
    #         "self": ma.URLFor("api.get_entry", id="<id>"),
    #         "collection": ma.URLFor("api.get_log", id="<log.id>"),
    #     }
    # )


class MembershipSchema(ma.ModelSchema):
    type = EnumField(MembershipType, by_value=True)

    class Meta:
        model = Membership


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
