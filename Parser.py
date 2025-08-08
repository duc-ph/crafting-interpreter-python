from typing import List
from ErrorReporter import error_at_token
import Expr
import Stmt
from Token import Token
from TokenType import TokenType


class ParseError(RuntimeError):
    pass


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current: int = 0

    def parse(self) -> List[Stmt.Stmt]:
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())

        return statements

    def expression(self) -> Expr.Expr:
        return self.assignment()

    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.FUN):
                return self.function("function")

            if self.match(TokenType.VAR):
                return self.varDeclaration()

            return self.statement()
        except ParseError:
            self.synchronize()

    def statement(self) -> Stmt.Stmt:
        if self.match(TokenType.FOR):
            return self.forStatement()

        if self.match(TokenType.IF):
            return self.ifStatement()

        if self.match(TokenType.PRINT):
            return self.printStatement()

        if self.match(TokenType.RETURN):
            return self.returnStatement()

        if self.match(TokenType.WHILE):
            return self.whileStatement()

        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expressionStatement()

    def forStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        # Initializer
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        # Condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        # Increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        # Body
        body = self.statement()
        if increment:
            body = Stmt.Block([
                body,
                Stmt.Expression(increment)
            ])

        if not condition:
            condition = Expr.Literal(True)

        body = Stmt.While(condition, body)

        if initializer:
            body = Stmt.Block([
                initializer,
                body
            ])

        return body

    def ifStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()

        # This eagerly looks for an else clause, therefore else is attached to the
        # nearest if.
        # Example: if (a) if (b) whenTrue(); else whenFalse();
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return Stmt.If(condition, thenBranch, elseBranch)

    def printStatement(self) -> Stmt.Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def returnStatement(self) -> Stmt.Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        return Stmt.Return(keyword, value)

    def varDeclaration(self) -> Stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def whileStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return Stmt.While(condition, body)

    def expressionStatement(self) -> Stmt.Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def function(self, kind: str) -> Stmt.Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(
                TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    error_at_token(
                        self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(
                    TokenType.IDENTIFIER, "Expect parameter name."))

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Stmt.Function(name, parameters, body)

    def block(self) -> List[Stmt.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self) -> Expr.Expr:
        expr = self.logic_or()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            error_at_token(equals, "Invalid assignment target.")
        return expr

    def logic_or(self) -> Expr.Expr:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def logic_and(self) -> Expr.Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr

    def equality(self) -> Expr.Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr.Expr:
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def term(self) -> Expr.Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr.Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        return self.call()

    def finishCall(self, callee: Expr.Expr) -> Expr.Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    error_at_token(
                        self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())

        paren = self.consume(TokenType.RIGHT_PAREN,
                             "Expect ')' after arguments.")
        return Expr.Call(callee, paren, arguments)

    def call(self) -> Expr.Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break

        return expr

    def primary(self) -> Expr.Expr:
        if self.match(TokenType.FALSE):
            return Expr.Literal(False)

        if self.match(TokenType.TRUE):
            return Expr.Literal(True)

        if self.match(TokenType.NIL):
            return Expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)

        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())

        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types: TokenType) -> bool:
        """Check if the current token has any of the given types."""
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type: TokenType) -> bool:
        """
        Returns True if the current token is of given type.
        Unlike `match`, this doesn't consume the token.
        """
        if self.isAtEnd():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1
        return self.previous()

    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        if self.current == 0:
            return None

        return self.tokens[self.current - 1]

    def error(self, token: Token, message: str) -> ParseError:
        error_at_token(token, message)
        return ParseError()

    def synchronize(self) -> None:
        """Skip tokens until the start of the next statement."""
        self.advance()
        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in {
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN
            }:
                return
            self.advance()
