class AST(object):
    pass


class String(AST):
    def __init__(self, value: str):
        self.value = value


class Load(AST):
    def __init__(self, child: String):
        self.child = child


class Create(AST):
    def __init__(self, child: String):
        self.child = child


class Append(AST):
    def __init__(self, left: AST, right: String):
        self.left = left
        self.right = right
