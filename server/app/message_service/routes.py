from flask import render_template, request

from app import db
from app.message_service import bp
from app.models import Entry, User


@bp.route("/sms", methods=["POST"])
def sms():
    sender = request.form["From"]
    body = request.form["Body"]
    user = User.query.filter_by(cellphone=sender).first()
    # FIXME: will die if user has no logs
    user.my_logs[0].entries.append(Entry(content=body))
    db.session.add(user)
    db.session.commit()
    return render_template("message_service/sms.xml", user=user, body=body)
