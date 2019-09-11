from collections import namedtuple

import pytest

from app import create_app, db
from app.console.registration import get_registration_token
from app.models import User
from config import TestConfig


@pytest.fixture(scope="module")
def client():
    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        db.create_all()
        user = User(email="oliver.epper@gmail.com")
        user.set_password("test")
        db.session.add(user)
        db.session.commit()
        yield client


@pytest.fixture(scope="module")
def password_reset_token():
    user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    token = user.get_password_reset_token()
    yield token


@pytest.fixture(scope="module")
def registration_tokens():
    tokens = namedtuple('tokens','new_user existing_user')
    tokens.new_user = get_registration_token('oliver.epper+new_user@gmail.com')
    tokens.existing_user = get_registration_token('oliver.epper@gmail.com')
    yield tokens
