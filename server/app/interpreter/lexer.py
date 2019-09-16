from .token import Token, TokenType


def _build_reserved_keywords():
    tt_list = list(TokenType)
    start_index = tt_list.index(TokenType.LOAD)
    end_index = tt_list.index(TokenType.CREATE)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tt_list[start_index : end_index + 1]
    }
    return reserved_keywords


RESERVED_KEYWORDS = _build_reserved_keywords()


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def _error(self):
        # FIXME:
        raise Exception("Something bad happend.")

    def _peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None

    def _advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def _string(self):
        """Handles identifiers and keywords"""
        token = Token(type=None, value=None)
        buf = ""
        while self.current_char is not None and not (
            self.current_char == '-' and self._peek() == '>'
        ):
            buf += self.current_char
            self._advance()
            if RESERVED_KEYWORDS.get(buf.upper()):
                break

        token_type = RESERVED_KEYWORDS.get(buf.upper())
        if token_type is None:
            token.type = TokenType.STRING
            token.value = buf.strip()
        else:
            # reserved keyword
            token.type = token_type
            token.value = buf.upper()

        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self._advance()

            if self.current_char.isalnum():
                return self._string()

            if self.current_char == "-" and self._peek() == ">":
                token = Token(type=TokenType.APPEND, value=TokenType.APPEND.value)
                self._advance()
                self._advance()
                return token

            else:
                self._error()

        return Token(type=TokenType.EOF, value=None)
