import logging
import os
import sys
from logging.handlers import RotatingFileHandler, SMTPHandler

from config import Config
from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
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
            print("head -c 32 /dev/urandom > ", secret_key_filename)
            sys.exit(1)

    # init plugins
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # register blueprints
    from app.console import bp as console_bp
    app.register_blueprint(console_bp)

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
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/Logbuch.log",
            maxBytes=10240,
            backupCount=10
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
