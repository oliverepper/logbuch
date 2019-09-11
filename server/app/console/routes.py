from flask import flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.console import bp
from app.console.forms import (ChangePasswordForm, LoginForm,
                               RequestPasswordResetForm,
                               RequestRegistrationForm, SetPasswordForm)
from app.console.registration import (send_password_reset_email,
                                      send_registration_email,
                                      verify_registration_token)
from app.models import User


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("console/index.html", current_user=current_user)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("console.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid login or password"))
            return form.redirect()
        login_user(user, remember=form.remember_me.data)
        return form.redirect("console.index")
    return render_template("console/login.html", title=_("Sign In"), form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("console.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash(_("You're already logged in. No need to register."))
        return redirect(url_for("console.index"))
    form = RequestRegistrationForm()
    if form.validate_on_submit():
        send_registration_email(email=form.email.data)
        flash(_("Please check your email for instructions to create your account."))
        return redirect(url_for("console.index"))
    return render_template("console/register.html", title=_("Register"), form=form)


@bp.route("/complete_registration/<token>", methods=["GET", "POST"])
def complete_registration(token):
    if current_user.is_authenticated:
        flash(_("You're already logged in."))
        return redirect(url_for("console.index"))
    email = verify_registration_token(token)
    if email is None:
        flash(_("Your registration token is invalid."))
        return redirect(url_for("console.index"))
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email)
        db.session.add(user)
    else:
        flash(_("User: %(user)s already exists.", user=user))
        return redirect(url_for("console.login"))
    form = SetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        login_user(user)
        flash(_("Congratulations! Your registration is complete."))
        return redirect(url_for("console.index"))
    return render_template(
        "console/set_password.html",
        title=_("Complete Registration"),
        email=user.email,
        form=form,
    )


@bp.route("/request_password_reset", methods=["GET", "POST"])
def request_password_reset():
    if current_user.is_authenticated:
        flash(
            _("You're already logged in. No need to reset your password. Just change it.")
        )
        return redirect(url_for("console.change_password"))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.allow_password_reset = True
            db.session.commit()
            send_password_reset_email(user)
            flash(_("Check your email for instructions to reset your password."))
        return redirect(url_for("console.login"))
    return render_template(
        "console/request_password_reset.html", title=_("Request Password Reset"), form=form
    )


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        flash(
            _("You're already logged in. No need to reset your password. Just change it.")
        )
        return redirect(url_for("console.change_password"))
    user = User.verify_password_reset_token(token)
    if not user:
        flash(_("Your password reset token was invalid."))
        return redirect(url_for("console.index"))
    if not user.allow_password_reset:
        flash(_("Looks like you've already reset your password once with that link."))
        return redirect(url_for("console.index"))
    form = SetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.allow_password_reset = False
        db.session.commit()
        login_user(user)
        flash(_("Your password has been reset."))
        return redirect(url_for("console.index"))
    return render_template("console/set_password.html", title=_("Reset Password"), form=form)


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash(_("You're password has been changed."))
        return redirect(url_for("console.index"))
    return render_template(
        "console/change_password.html", title=_("Change Password"), form=form
    )
