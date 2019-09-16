from .lexer import Lexer
from .token import Token, TokenType
from .ast import Load, Create, Append, String


class Parser(object):
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.last_node = None

    def _error(self):
        raise Exception("Something bad happend.")

    def _eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self._error()

    def _string(self):
        node = String(self.current_token.value)
        self._eat(TokenType.STRING)
        return node

    def _expr(self):
        token = self.current_token
        if token.type == TokenType.STRING:
            return self._string()
        elif token.type == TokenType.CREATE or token.type == TokenType.LOAD:
            token_type_value = token.type.value
            self._eat(token.type)
            title = self._string()
            if token_type_value == "CREATE":
                left = Create(title)
            elif token_type_value == "LOAD":
                left = Load(title)
            self._eat(TokenType.APPEND)
            right = self._string()
            append = Append(left, right)
            return append
        return None

    def parse(self):
        command = self._expr()
        if self.current_token.type != TokenType.EOF:
            self._error()
        return command
