from app.models import User


def test_password_reset_not_allowed(client):
    user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    assert not user.allow_password_reset


def test_request_password_reset(client):
    response = client.post(
        "/request_password_reset",
        data=dict(email="oliver.epper@gmail.com"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Check your email for instructions to reset your password." in response.data

    user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    assert user.allow_password_reset


def test_reset_password_form(client, password_reset_token):
    response = client.get("/reset_password/" + password_reset_token, follow_redirects=True)
    assert response.status_code == 200
    assert b"Reset Password" in response.data


def test_password_reset(client, password_reset_token):
    _user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    user = User.verify_password_reset_token(password_reset_token)
    assert user.id == _user.id

    response = client.post(
        "reset_password/" + password_reset_token,
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your password has been reset." in response.data
    assert not user.allow_password_reset


def test_password_reset_user_logged_in(client, password_reset_token):
    response = client.post(
        "reset_password/" + password_reset_token,
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You&#39;re already logged in. No need to reset your password." in response.data


def test_logout(client):
    response = client.get("logout", follow_redirects=True)
    assert response.status_code == 200


def test_password_reset_with_invalid_token(client):
    response = client.post(
        "reset_password/" + "invalid_token",
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Your password reset token was invalid.' in response.data


def test_password_reset_with_token_already_used_once(client, password_reset_token):
    _user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    user = User.verify_password_reset_token(password_reset_token)
    assert user.id == _user.id

    response = client.post(
        "reset_password/" + password_reset_token,
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Looks like you&#39;ve already reset your password once with that link."
        in response.data
    )
    assert not user.allow_password_reset
