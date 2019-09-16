from app.interpreter.lexer import Lexer
from app.interpreter.parser import Parser
from app.interpreter.interpreter import Interpreter
from app.models import User


def test_simple_entry(session):
    text = "Hallo Interpreter"
    user = User.query.first()
    lx=Lexer(text)
    p=Parser(lx)
    command=p.parse()
    i=Interpreter(user=user, session=session)
    i.visit(command)
    assert user.my_logs[0].entries[0].content == text

def test_create_log(session):
    text = "Hallo Interpreter!"
    cmd = "CREATE Test -> " + text
    user = User.query.first()
    lx = Lexer(cmd)
    p = Parser(lx)
    command = p.parse()
    i=Interpreter(user=user, session=session)
    i.visit(command)
    assert len(user.my_logs) > 1

def test_load_log(session):
    text = "Hallo Interpreter!"
    cmd = "LOAD Golf -> " + text
    user = User.query.first()
    lx = Lexer(cmd)
    p = Parser(lx)
    command = p.parse()
    i=Interpreter(user=user, session=session)
    i.visit(command)
    assert user.my_logs[0].entries[-1].content == text
