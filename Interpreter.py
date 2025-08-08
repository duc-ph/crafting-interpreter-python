from Clock import Clock
from Return import Return
from typing import List
from Environment import Environment
from ErrorReporter import runtime_error
import Expr
import Stmt
from TokenType import TokenType
from LoxFunction import LoxFunction
from LoxCallable import LoxCallable


class Interpreter(Expr.Visitor[object], Stmt.Visitor[object]):
    def __init__(self):
        super().__init__()
        self.globals = Environment()  # track the global env
        self.environment = self.globals  # track the current env
        self.globals.define('clock', Clock())

    def interpret(self, statements: List[Stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)

        except Exception as e:
            runtime_error(e)

    def visit_literal_expr(self, expr: Expr.Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Expr.Logical) -> object:
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        # We look at the left operand to see if we can short-circuit.
        # If not, and only then, do we evaluate the right operand,
        # unlike binary expr.
        return self.evaluate(expr.right)

    def visit_grouping_expr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Expr.Unary) -> object:
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.MINUS:
                return -right
            case TokenType.BANG:
                return not self.is_truthy(right)

        return None

    def visit_variable_expr(self, expr) -> object:
        return self.environment.get(expr.name)

    def visit_binary_expr(self, expr: Expr.Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                return left - right
            case TokenType.SLASH:
                return left / right
            case TokenType.STAR:
                return left * right
            case TokenType.PLUS:
                return left + right

            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right

            case TokenType.BANG_EQUAL:
                return not left == right
            case TokenType.EQUAL_EQUAL:
                return left == right

        return None

    def visit_call_expr(self, expr: Expr.Call) -> object:
        callee = self.evaluate(expr.callee)
        arguments = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(
                expr.paren, "Can only call functions and classes.")

        func = callee

        if len(arguments) != func.arity():
            raise RuntimeError(
                expr.paren, f"Expected {func.arity()} arguments but got {len(arguments)}.")

        return func.call(interpreter=self, arguments=arguments)

    def is_truthy(self, obj: object) -> bool:
        if obj == None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def evaluate(self, expr: Expr.Expr) -> object:
        return expr.accept(self)

    def execute(self, stmt: Stmt.Stmt):
        stmt.accept(self)

    def executeBlock(self, statements: List[Stmt.Stmt], environment: Environment) -> None:
        previous_env = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:  # restore the previous env after execution, even if there is exception
            self.environment = previous_env

    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.executeBlock(stmt.statements, Environment(
            enclosing=self.environment))
        return

    def visit_expression_stmt(self, stmt: Stmt.Expr) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Stmt.Function):
        func = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, func)

    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch:
            self.execute(stmt.elseBranch)

    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        value = self.evaluate(stmt.expresssion)
        print(self.stringify(value))
    
    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        value = None
        if stmt.value:
            value = self.evaluate(stmt.value)
        
        raise Return(value)

    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Expr.Assign) -> object:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, int) or isinstance(obj, float):
            s = str(obj)
            if s.endswith('.0'):
                s = s[:-2]
                return s
        return str(obj)
