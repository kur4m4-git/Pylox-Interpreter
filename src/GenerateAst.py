#!/usr/bin/env python3


import sys


def define_ast(output_dir: str, base_name: str, types: list[str]) -> None:
    """Generate a Python file with AST classes for the given base name."""
    path = f"{output_dir}/{base_name.lower()}.py"
    with open(path, "w") as file:
        file.write("from abc import ABC, abstractmethod\n")
        file.write("from Token import Token\n")
        if base_name == "Expr":
            file.write("\nclass Expr(ABC):\n")
            file.write("    @abstractmethod\n")
            file.write("    def accept(self, visitor):\n")
            file.write("        pass\n")
        else:
            file.write("from expressions import Expr\n")
            file.write("\nclass Stmt(ABC):\n")
            file.write("    @abstractmethod\n")
            file.write("    def accept(self, visitor):\n")
            file.write("        pass\n")

        for type_def in types:
            class_name = type_def.split(":")[0].strip()
            fields = type_def.split(":")[1].strip()
            define_type(file, base_name, class_name, fields)


def define_type(file, base_name: str, class_name: str, fields: str) -> None:
    file.write(f"\nclass {class_name}({base_name}):\n")
    fields_list = [f.strip() for f in fields.split(",")]
    file.write(f"    def __init__(self, {', '.join(fields_list)}):\n")
    for field in fields_list:
        field_name = field.split(":")[0].strip()
        file.write(f"        self.{field_name} = {field_name}\n")
    file.write(f"\n    def accept(self, visitor):\n")
    file.write(f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: GenerateAst <output directory>")
        sys.exit(1)
    output_dir = sys.argv[1]

    define_ast(output_dir, "Expr", [
        "Assign   : name:Token, value:Expr",
        "Binary   : left:Expr, operator:Token, right:Expr",
        "Call     : callee:Expr, paren:Token, arguments:list[Expr]",
        "Get      : object:Expr, name:Token",
        "Grouping : expression:Expr",
        "Literal  : value:object",
        "Logical  : left:Expr, operator:Token, right:Expr",
        "Set      : object:Expr, name:Token, value:Expr",
        "Super    : keyword:Token, method:Token",
        "This     : keyword:Token",
        "Unary    : operator:Token, right:Expr",
        "Variable : name:Token"
    ])

    define_ast(output_dir, "Stmt", [
        "Block      : statements:list[Stmt]",
        "Class      : name:Token, superclass:Variable|None, methods:list[Function]",
        "Expression : expression:Expr",
        "Function   : name:Token, params:list[Token], body:list[Stmt]",
        "If         : condition:Expr, then_branch:Stmt, else_branch:Stmt|None",
        "Print      : expression:Expr",
        "Return     : keyword:Token, value:Expr|None",
        "Var        : name:Token, initializer:Expr|None",
        "While      : condition:Expr, body:Stmt"
    ])
