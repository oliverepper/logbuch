from .ast import String, Append, Create, Load, AST
from app.models import Log, Entry


class NodeVisitor(object):
    def visit(self, node):
        func_name = "visit_" + type(node).__name__
        func = getattr(self, func_name, self.generic_visit)
        return func(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} function")


class Interpreter(NodeVisitor):
    def __init__(self, user, session):
        self.log = None
        self.user = user
        self.session = session

    def visit_String(self, node: String):
        entry = Entry(content=node.value, creator=self.user)
        self.user.my_logs[0].entries.append(entry)
        self.session.add(self.user)
        self.session.commit()
        print(f"Erzeuge Eintrag <{node.value}> in Deinem Std.-Logbuch.")

    def visit_Create(self, node):
        log = Log(title=node.child.value)
        log.owner = self.user
        self.session.add(log)
        self.log = log

    def visit_Load(self, node):
        log = Log.query.filter_by(title=node.child.value).first()
        if log:
            self.log = log
        else:
            raise Exception(f"Log <{node.child.value}> not found")

    def visit_Append(self, node):
        self.visit(node.left)
        entry = Entry(content=node.right.value, creator=self.user)
        self.log.entries.append(entry)
        self.session.commit()
        print(f"Erzeuge Eintrag <{node.right.value}> im Logbuch {self.log.title}")
