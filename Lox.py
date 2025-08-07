import sys
from Interpreter import Interpreter
from Parser import Parser
from Scanner import Scanner
from ErrorReporter import hadError, hadRuntimeError


interpreter = Interpreter()


def runFile(path: str):
    with open(path, 'r') as f:
        bytes = f.read()

    run(bytes)
    if hadError:
        sys.exit(65)
    if hadRuntimeError:
        sys.exit(70)


def runPrompt():
    while True:
        line = input("> ")
        if line == '':
            continue

        if line is None:
            break

        run(line)
        hadError = False


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scanTokens()
    parser = Parser(tokens)
    statements = parser.parse()

    if hadError:
        return

    interpreter.interpret(statements)


def main(args):
    if len(args) > 1:
        print("Usage: jlox [script]")
        sys.exit(64)
    elif len(args) == 1:
        runFile(args[0])
    else:
        runPrompt()
