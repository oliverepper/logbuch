from time import time

import jwt
from flask import current_app, render_template

from app.email import send_email


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
        "[Logbuch] Registrierung",
        sender=current_app.config["SENDER_EMAIL"][0],
        recipients=[email],
        text_body=render_template("user/email/registration.txt", token=token),
        html_body=render_template("user/email/registration.html", token=token),
    )


def verify_registration_token(token):
    try:
        email = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["email"]
    except:
        return
    return email