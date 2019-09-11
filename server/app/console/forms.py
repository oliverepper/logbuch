from flask import redirect, request, url_for
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from flask_wtf import FlaskForm
from urllib.parse import urljoin, urlparse
from wtforms import BooleanField, HiddenField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    url = urlparse(urljoin(request.host_url, target))
    return url.scheme in ("http", "https") and ref_url.netloc == url.netloc


def get_redirect_target():
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def strip_filter(value):
    if value is not None and hasattr(value, "strip"):
        return value.strip()
    return value


class BaseForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get("filters", [])
            if _l("Email") in unbound_field.args:
                filters.append(strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)


class RedirectForm(BaseForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        BaseForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ""

    def redirect(self, endpoint="main.index", **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("remember me"))
    submit = SubmitField(_l("Sign In"))


class RequestRegistrationForm(BaseForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Send Registration Token"))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l("Please use a different email adress."))


class RequestPasswordResetForm(BaseForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


class SetPasswordForm(BaseForm):
    # FIXME: Length min=4 needs changing
    password = PasswordField(_l("Password"), validators=[DataRequired(), Length(min=4)])
    password_repeat = PasswordField(
        _l("Repeat Password"), validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(_l("Set Password"))


class ChangePasswordForm(SetPasswordForm):
    old_password = PasswordField(_l("Old Password"), validators=[DataRequired()])

    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError(_l("Old password is invalid."))
