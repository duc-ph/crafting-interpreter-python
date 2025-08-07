from dataclasses import dataclass
from TokenType import TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: object
    line: int

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
