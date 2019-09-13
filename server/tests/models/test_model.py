from app.models import Log, User


def test_user_logs_relationship(client):
    user = User.query.filter_by(email="oliver.epper@gmail.com").first()
    log = Log(title="Golf")
    log.owner = user
    assert len(user.my_logs) > 0


def test_golf_log_exists(client):
    log = Log.query.filter_by(title="Golf").first()
    assert log.owner.email == "oliver.epper@gmail.com"
