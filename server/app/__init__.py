import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask, Response, current_app, json, request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
mail = Mail()
login = LoginManager()
login.login_view = "console.login"
login.login_message = "Please login to access this page."
babel = Babel()
moment = Moment()


class ApiResult(object):
    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self):
        return Response(
            json.dumps(self.value), status=self.status, mimetype="application/json"
        )


class ApiException(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status

    def to_result(self):
        return ApiResult({"message": self.message}, status=self.status)


class ApiFlask(Flask):
    def make_response(self, rv):
        if isinstance(rv, ApiResult):
            return rv.to_response()
        return Flask.make_response(self, rv)


def create_app(config=Config):
    app = ApiFlask(__name__)
    CORS(app)
    app.config.from_object(config)
    if not app.config["TESTING"]:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            app.instance_path, __name__ + ".db"
        )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if app.config["SECRET_KEY"] is None:
        secret_key_filename = os.path.join(app.instance_path, "secret_key")
        try:
            app.config["SECRET_KEY"] = open(secret_key_filename, "rb").read()
        except IOError:
            print("Error. No secret key. Create it with:")
            if not os.path.isdir(os.path.dirname(secret_key_filename)):
                print("mkdir -p ", os.path.dirname(secret_key_filename))
            print("head -c 32 /dev/urandom >", secret_key_filename)
            exit(1)

    app.register_error_handler(ApiException, lambda err: err.to_result())

    # init plugins
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    mail.init_app(app)
    login.init_app(app)
    babel.init_app(app)
    moment.init_app(app)

    # register blueprints
    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.console import bp as console_bp

    app.register_blueprint(console_bp)

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    from app.message_service import bp as message_service_bp

    app.register_blueprint(message_service_bp)

    if not app.debug:
        # log errors per email
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"],
                subject="Logbuch Fehler",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # create and utilize a log file
        # TODO: That should use instance_path
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/Logbuch.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Starte Logbuch-Server")

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])
