def test_index_redirect_login(client):
    response = client.get("/index", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_index_logged_in(client):
    response = client.post(
        "/login",
        data=dict(email="oliver.epper@gmail.com", password="test"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Hello &lt;oliver.epper@gmail.com&gt;" in response.data
