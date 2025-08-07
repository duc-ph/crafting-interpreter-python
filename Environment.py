from typing import Optional
from Token import Token


class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeError(f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(f"Undefined variable '{name.lexeme}'.")