def test_login(client):
    response = client.post(
        "/sms",
        data=dict(From="+4915123595397", Body="Einfach den Ball mal besser treffen!"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b'Hallo &lt;oliver.epper@gmail.com&gt;! Ich logge: Einfach den Ball mal besser treffen!'
        in response.data
    )
