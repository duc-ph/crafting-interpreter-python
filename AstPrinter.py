
from Expr import Binary, Expr, Grouping, Literal, Unary, ExprVisitor
# from Token import Token
# from TokenType import TokenType


class AstPrinter(ExprVisitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = ["(" + name]
        for expr in exprs:
            parts.append(" " + expr.accept(self))
        parts.append(")")
        return "".join(parts)


# if __name__ == '__main__':
#     expression = Binary(
#         Unary(
#             Token(TokenType.MINUS, '-', None, 1),
#             Literal(123)
#         ),
#         Token(TokenType.STAR, "*", None, 1),
#         Grouping(Literal(45.67))
#     )
#     print(AstPrinter().print(expression))
