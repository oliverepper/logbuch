from flask import render_template, request

from app import db
from app.message_service import bp
from app.models import Entry, User
from app.interpreter.lexer import Lexer
from app.interpreter.parser import Parser
from app.interpreter.interpreter import Interpreter


@bp.route("/sms", methods=["POST"])
def sms():
    sender = request.form["From"]
    body = request.form["Body"]
    user = User.query.filter_by(cellphone=sender).first()
    p = Parser(Lexer(body))
    command = p.parse()
    i = Interpreter(user=user, session=db.session)
    i.visit(command)
    # user.my_logs[0].entries.append(Entry(content=body))
    # db.session.add(user)
    # db.session.commit()
    return render_template("message_service/sms.xml", user=user, body=body)
