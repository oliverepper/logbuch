from collections import namedtuple

import pytest

from app import create_app, db
from app.console.registration import get_registration_token
from app.models import User, Log
from config import TestConfig


@pytest.fixture(scope="module")
def client():
    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        db.create_all()
        user_one = User(email="oliver.epper@gmail.com", cellphone="+4915123595397")
        user_one.set_password("test")
        user_two = User(email="oliver.epper+test@gmail.com")
        user_two.set_password("test")
        db.session.add_all([user_one, user_two])
        db.session.commit()
        yield client


@pytest.fixture(scope="module")
def session(client):
    yield db.session


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


@pytest.fixture(scope="module")
def api_tokens():
    api_tokens = namedtuple('api_tokens', 'token_user_one token_user_two')
    users = User.query.all()
    for user in users:
        user.update_api_token()
    api_tokens.token_user_one = users[0].api_token
    api_tokens.token_user_two = users[1].api_token
    db.session.commit()
    yield api_tokens