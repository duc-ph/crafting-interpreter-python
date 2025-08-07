from dataclasses import dataclass
from typing import List, Any, TypeVar, Generic
from abc import ABC, abstractmethod
from Token import Token
from Expr import Expr

R = TypeVar('R')

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: 'StmtVisitor[R]') -> R:
        pass

class StmtVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: 'Block') -> R:
        pass
    @abstractmethod
    def visit_expression_stmt(self, stmt: 'Expression') -> R:
        pass
    @abstractmethod
    def visit_print_stmt(self, stmt: 'Print') -> R:
        pass
    @abstractmethod
    def visit_var_stmt(self, stmt: 'Var') -> R:
        pass

@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: 'StmtVisitor[R]') -> R:
        return visitor.visit_block_stmt(self)

@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: 'StmtVisitor[R]') -> R:
        return visitor.visit_expression_stmt(self)

@dataclass
class Print(Stmt):
    expresssion: Expr

    def accept(self, visitor: 'StmtVisitor[R]') -> R:
        return visitor.visit_print_stmt(self)

@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: 'StmtVisitor[R]') -> R:
        return visitor.visit_var_stmt(self)

