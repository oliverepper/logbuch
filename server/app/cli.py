import os

import click

from . import db
from .models import Entry, Log, User


def register_app(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument("lang")
    def init(lang):
        """Initialize a new language."""
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system(
            "pybabel init -i messages.pot -d app/translations -l " + lang
        ):
            raise RuntimeError("init command failed")
        os.remove("messages.pot")

    @translate.command()
    def update():
        """Update all languages."""
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system("pybabel update -i messages.pot -d app/translations"):
            raise RuntimeError("update command failed")
        os.remove("messages.pot")

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system("pybabel compile -d app/translations"):
            raise RuntimeError("compile command failed")

    @app.cli.group()
    def logbuch():
        """Prepopulate or clean Logbuchs database."""
        pass

    @logbuch.command()
    def init_db():
        """Prepopulate Logbuchs DB"""
        oliver = User(
            email="oliver.epper@gmail.com",
            cellphone="+4915123595397",
            username="Oliver",
        )
        oliver.set_password("test")
        log = Log(title="Golf 🏌️‍♂️")
        log.entries.append(Entry(content="Hallo Logbuch 👋", creator=oliver))
        oliver.my_logs.append(log)
        oliver.my_logs.append(Log(title="Fitness"))

        maike = User(
            email="maike.epper@gmail.com",
            cellphone="+4915221654065",
            username="Maike",
        )
        maike.set_password("test")
        log = Log(title="Golf 🏌️‍♀️")
        log.entries.append(Entry(content="Hallo Logbuch 👋", creator=maike))
        maike.my_logs.append(log)
        maike.my_logs.append(Log(title="Schwimmen 🏊‍♀️"))

        for user in [oliver, maike]:
            db.session.add(user)
        db.session.commit()
