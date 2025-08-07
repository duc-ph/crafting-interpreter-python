from typing import List
from Token import Token
from TokenType import TokenType
from ErrorReporter import error_at_line


class Scanner:
    def __init__(self, source: str):
        self.source: str = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def scanTokens(self) -> List[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)

    def scanToken(self) -> None:
        c = self.advance()

        match c:
            case '(':
                self.addToken(TokenType.LEFT_PAREN)
            case ')':
                self.addToken(TokenType.RIGHT_PAREN)
            case '{':
                self.addToken(TokenType.LEFT_BRACE)
            case '}':
                self.addToken(TokenType.RIGHT_BRACE)
            case ',':
                self.addToken(TokenType.COMMA)
            case '.':
                self.addToken(TokenType.DOT)
            case '-':
                self.addToken(TokenType.MINUS)
            case '+':
                self.addToken(TokenType.PLUS)
            case ';':
                self.addToken(TokenType.SEMICOLON)
            case '*':
                self.addToken(TokenType.STAR)

            # Two-character operators
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match(
                    '=') else TokenType.BANG)
            case '=':
                self.addToken(TokenType.EQUAL_EQUAL if self.match(
                    '=') else TokenType.EQUAL)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match(
                    '=') else TokenType.LESS)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match(
                    '=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.isAtEnd():
                        self.advance()
                else:
                    self.addToken(TokenType.SLASH)

            # Skipping white spaces
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\n':
                self.line += 1

            # String
            case '"':
                self.string()

            case _:
                # Numbers
                if c.isdigit():
                    self.number()

                # Identifiers
                elif self.isAlpha(c):
                    self.identifier()

                # Everything else
                else:
                    error_at_line(self.line, "Unexpected character.")

    def identifier(self) -> None:
        while self.isAlphaNumeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        type = self.keywords.get(text, None)
        if type is None:
            type = TokenType.IDENTIFIER

        self.addToken(type)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peekNext().isdigit():
            # Consume the '.'
            self.advance()

        while self.peek().isdigit():
            self.advance()

        self.addToken(TokenType.NUMBER, float(
            self.source[self.start: self.current]))

    def string(self) -> None:
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.isAtEnd():
            error_at_line(self.line, "Unterminated string.")
            return

        # The closing "
        self.advance()

        # Trim the surrounding quotes
        value = self.source[self.start + 1: self.current - 1]
        self.addToken(TokenType.STRING, value)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current-1]

    def addToken(self, type: TokenType, literal: object = None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if len(expected) != 1:
            raise ValueError("Expected a single character")

        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.isAtEnd():
            return '\0'
        return self.source[self.current]

    def peekNext(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def isAlpha(self, c: str) -> bool:
        return c.isalpha() or c == '_'

    def isAlphaNumeric(self, c: str) -> bool:
        return c.isalnum() or c == '_'
