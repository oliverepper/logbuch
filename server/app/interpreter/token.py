from enum import Enum


class TokenType(Enum):
    STRING = "STRING"
    APPEND = "->"
    EOF = "EOF"
    # reserved keywords
    LOAD = "LOAD"
    CREATE = "CREATE"


class Token(object):
    def __init__(self, type: TokenType, value):
        self.type = type
        self.value = value


    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


    __str__ = __repr__