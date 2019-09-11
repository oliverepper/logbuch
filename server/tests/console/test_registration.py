from contextlib import contextmanager


@contextmanager
def login(client):
    response = client.post(
        "/login",
        data=dict(email="oliver.epper@gmail.com", password="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    yield
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


# register user already logged in
def test_register_user_already_logged_in(client):
    with login(client):
        response = client.get("/register", follow_redirects=True)
        assert response.status_code == 200
        assert b"You&#39;re already logged in. No need to register." in response.data


# register user already exists
def test_register_user_already_exists(client):
    response = client.post(
        "/register",
        data=dict(email='oliver.epper@gmail.com'),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Please use a different email adress." in response.data


# complete registration, user already logged in
def test_complete_registration_with_user_already_logged_in(client):
    with login(client):
        response = client.post(
            "/complete_registration/" + "invalid_token",
            data=dict(password="test", password_repeat="test"),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"You&#39;re already logged in." in response.data


# complete registration, token invalid
def test_complete_registration_with_invalid_token(client):
    response = client.post(
        "/complete_registration/" + "invalid_token",
        data=dict(password="password", password_repeat="password"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your registration token is invalid." in response.data


# complete registration, user already exists
def test_complete_registration_with_valid_token_users_exists(client, registration_tokens):
    response = client.post(
        "/complete_registration/" + registration_tokens.existing_user,
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"User: &lt;oliver.epper@gmail.com&gt; already exists." in response.data


# register new user
def test_get_registration_token(client):
    response = client.post(
        "/register",
        data=dict(email='oliver.epper+not_in_database@gmail.com'),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Please check your email for instructions to create your account." in response.data


def test_complete_registration_with_valid_token(client, registration_tokens):
    response = client.post(
        "/complete_registration/" + registration_tokens.new_user,
        data=dict(password="test", password_repeat="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Congratulations! Your registration is complete." in response.data
