from flask import request, render_template

from app.message_service import bp
from app.models import User


@bp.route("/sms", methods=["POST"])
def sms():
    sender = request.form["From"]
    body = request.form["Body"]
    user = User.query.filter_by(cellphone=sender).first()
    return render_template("message_service/sms.xml", user=user, body=body)