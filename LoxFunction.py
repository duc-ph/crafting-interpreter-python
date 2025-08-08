from __future__ import annotations
from typing import List, TYPE_CHECKING
from Environment import Environment
from LoxCallable import LoxCallable
from Return import Return
import Stmt

if TYPE_CHECKING:
    from Interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: 'Interpreter', arguments: List[object]) -> object:
        environment = Environment(enclosing=self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.executeBlock(
                statements=self.declaration.body, environment=environment)
        except Return as returnValue:
            return returnValue.value

    def arity(self) -> int:
        return len(self.declaration.params)

    def toString(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
