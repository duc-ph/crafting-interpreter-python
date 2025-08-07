import sys

from Token import Token
from TokenType import TokenType

hadError = False
hadRuntimeError = False


def error_at_line(line: int, message: str):
    report(line, "", message)


def report(line: int, where: str, message: str):
    global hadError
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
    hadError = True


def error_at_token(token: Token, message: str) -> None:
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)

def runtime_error(error: RuntimeError):
    print(error)
    hadRuntimeError = True