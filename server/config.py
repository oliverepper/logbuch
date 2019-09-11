import os


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SENDER_EMAIL = ["logbuch@oliver-epper.de"]
    ADMINS = ["oliver.epper@gmail.com"]

    LANGUAGES = ["en", "de", "de_DE"]


class TestConfig(Config):
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 8025)
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    WTF_CSRF_ENABLED = False
    TESTING = True
