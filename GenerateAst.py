from typing import List
import os


def define_ast(output_dir: str, base_name: str, types: List[str]):
    path = os.path.join(output_dir, f'{base_name}.py')

    with open(path, "w", encoding="utf-8") as f:
        f.write("from dataclasses import dataclass\n")
        f.write("from typing import List, Any, TypeVar, Generic\n")
        f.write("from abc import ABC, abstractmethod\n")
        f.write("from Token import Token\n")
        if base_name != "Expr":
            f.write("from Expr import Expr\n\n")

        f.write("R = TypeVar('R')\n\n")

        # Base abstract class
        f.write(f"class {base_name}(ABC):\n")
        f.write("    @abstractmethod\n")
        f.write(
            "    def accept(self, visitor: 'Visitor[R]') -> R:\n")
        f.write("        pass\n\n")

        # Visitor abstract base class
        f.write("class Visitor(Generic[R], ABC):\n")
        for type_def in types:
            class_name = type_def.split(":")[0].strip()
            f.write(f"    @abstractmethod\n")
            f.write(
                f"    def visit_{class_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: '")
            f.write(f"{class_name}') -> R:\n")
            f.write("        pass\n")
        f.write("\n")

        # Expression subclasses
        for type_def in types:
            class_name, fields = [part.strip() for part in type_def.split(":")]
            f.write("@dataclass\n")
            f.write(f"class {class_name}({base_name}):\n")

            fields = [field.strip() for field in fields.split(",")]
            for field in fields:
                type_hint, name = field.split()
                f.write(f"    {name}: {type_hint}\n")

            f.write("\n")
            f.write(
                "    def accept(self, visitor: 'Visitor[R]') -> R:\n")
            f.write(
                f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n\n")


def main():
    output_dir = './'
    define_ast(
        output_dir,
        "Expr",
        [
            "Assign: Token name, Expr value",
            "Binary   : Expr left, Token operator, Expr right",
            "Grouping : Expr expression",
            "Literal  : Any value",
            "Logical: Expr left, Token operator, Expr right",
            "Unary    : Token operator, Expr right",
            "Variable: Token name"
        ]
    )

    define_ast(
        output_dir,
        "Stmt",
        [
            "Block: List[Stmt] statements",
            "Expression: Expr expression",
            "If: Expr condition, Stmt thenBranch, Stmt elseBranch",
            "Print: Expr expresssion",
            "Var: Token name, Expr initializer",
            "While: Expr condition, Stmt body"
        ]
    )


if __name__ == "__main__":
    main()
