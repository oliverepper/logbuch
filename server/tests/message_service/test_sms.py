from app import db
from app.models import Log, User


def test_login(client):
    user = User.query.first()
    user.my_logs.append(Log(title="Golf"))
    db.session.add(user)
    db.session.commit()
    response = client.post(
        "/sms",
        data=dict(From="+4915123595397", Body="Einfach den Ball mal besser treffen!"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b"Hallo &lt;oliver.epper@gmail.com&gt;! Ich logge: Einfach den Ball mal besser treffen!"
        in response.data
    )
