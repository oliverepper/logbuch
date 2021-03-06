from time import time

import jwt
from flask import current_app, render_template

from app.email import send_email

SUBJECT_REGISTER: str = "[Logbuch] Create your account"
SUBJECT_RESET: str = "[Logbuch] Reset your password"


def get_registration_token(email, expires_in=600):
    token = jwt.encode(
        {"email": email, "exp": time() + expires_in},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    ).decode("utf-8")
    return token


def send_registration_email(email, expires_in=600):
    token = get_registration_token(email)
    send_email(
        SUBJECT_REGISTER,
        sender=current_app.config["SENDER_EMAIL"][0],
        recipients=[email],
        text_body=render_template("console/email/registration.txt", token=token),
        html_body=render_template("console/email/registration.html", token=token),
    )


def verify_registration_token(token):
    try:
        email = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])[
            "email"
        ]
    except:
        return
    return email


def send_password_reset_email(user):
    token = user.get_password_reset_token()
    send_email(
        SUBJECT_RESET,
        sender=current_app.config["SENDER_EMAIL"][0],
        recipients=[user.email],
        text_body=render_template("console/email/reset_password.txt", token=token),
        html_body=render_template("console/email/reset_password.html", token=token),
    )
