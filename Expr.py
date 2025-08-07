from dataclasses import dataclass
from typing import List, Any, TypeVar, Generic
from abc import ABC, abstractmethod
from Token import Token
R = TypeVar('R')

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        pass

class ExprVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: 'Assign') -> R:
        pass
    @abstractmethod
    def visit_binary_expr(self, expr: 'Binary') -> R:
        pass
    @abstractmethod
    def visit_grouping_expr(self, expr: 'Grouping') -> R:
        pass
    @abstractmethod
    def visit_literal_expr(self, expr: 'Literal') -> R:
        pass
    @abstractmethod
    def visit_unary_expr(self, expr: 'Unary') -> R:
        pass
    @abstractmethod
    def visit_variable_expr(self, expr: 'Variable') -> R:
        pass

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_assign_expr(self)

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_binary_expr(self)

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_grouping_expr(self)

@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_literal_expr(self)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_unary_expr(self)

@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: 'ExprVisitor[R]') -> R:
        return visitor.visit_variable_expr(self)

