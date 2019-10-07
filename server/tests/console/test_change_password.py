def test_login(client):
    response = client.post(
        "/login",
        data=dict(email="oliver.epper@gmail.com", password="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_change_password(client):
    response = client.post(
        "/change_password",
        data=dict(old_password="test", password="new_password", password_repeat="new_password"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your password has been changed." in response.data