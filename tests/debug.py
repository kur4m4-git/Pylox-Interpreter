
"""Debug utility to print the AST of Lox code in a human-readable format."""

from typing import List

from Scanner import Scanner
from Parser import Parser
from statements import Stmt, Print, Expression, Var, Block, If, While, Function, Return, Class
from expressions import Expr, Binary, Unary, Literal, Grouping, Variable, Assign, Logical, Call, Get, Set, This


def debug_program(statements: List[Stmt]) -> str:
    
    stmts = [debug_statement(stmt) for stmt in statements if stmt is not None]
    return "\n".join(stmts) + "\n" if stmts else ""


def debug_statement(stmt: Stmt) -> str:
    if stmt is None:
        return "NoneStatement"
    if isinstance(stmt, Print):
        return f"print {debug_expression(stmt.expression)}"
    if isinstance(stmt, Expression):
        return debug_expression(stmt.expression)
    if isinstance(stmt, Var):
        res = f"var {stmt.name.lexeme}"
        if stmt.initializer is not None:
            res += f" = {debug_expression(stmt.initializer)}"
        return res
    if isinstance(stmt, Block):
        return debug_block_statement(stmt.statements)
    if isinstance(stmt, If):
        res = f"if ({debug_expression(stmt.condition)}) {{\n"
        res += debug_block_statement([stmt.then_branch])
        res += "}"
        if stmt.else_branch is not None:
            res += " else {\n"
            res += debug_block_statement([stmt.else_branch])
            res += "}"
        return res
    if isinstance(stmt, While):
        return f"while ({debug_expression(stmt.condition)}) {{\n{debug_block_statement([stmt.body])}}}"
    if isinstance(stmt, Function):
        res = f"fun {stmt.name.lexeme}("
        res += ", ".join(param.lexeme for param in stmt.parameters)
        res += ") {\n"
        res += debug_block_statement(stmt.body)
        res += "}"
        return res
    if isinstance(stmt, Return):
        res = "return"
        if stmt.value is not None:
            res += f" {debug_expression(stmt.value)}"
        return res
    if isinstance(stmt, Class):
        res = f"class {stmt.name.lexeme}"
        if stmt.superclass is not None:
            res += f" < {stmt.superclass.name.lexeme}"
        res += " {\n"
        res += "\n".join(debug_statement(method) for method in stmt.methods)
        res += "\n}"
        return res
    return "Unknown Statement"


def debug_block_statement(statements: List[Stmt]) -> str:
    return debug_program(statements)


def debug_expression(expr: Expr) -> str:
    
    if expr is None:
        return "NoneExpression"
    if isinstance(expr, Literal):
        return str(expr.value) if expr.value is not None else "nil"
    if isinstance(expr, Variable):
        return expr.name.lexeme
    if isinstance(expr, Assign):
        return f"{expr.name.lexeme} = {debug_expression(expr.value)}"
    if isinstance(expr, Binary):
        return f"({debug_expression(expr.left)} {expr.operator.lexeme} {debug_expression(expr.right)})"
    if isinstance(expr, Unary):
        return f"({expr.operator.lexeme}{debug_expression(expr.right)})"
    if isinstance(expr, Grouping):
        return f"({debug_expression(expr.expression)})"
    if isinstance(expr, Logical):
        return f"({debug_expression(expr.left)} {expr.operator.lexeme} {debug_expression(expr.right)})"
    if isinstance(expr, Call):
        res = debug_expression(expr.callee)
        res += "("
        res += ", ".join(debug_expression(arg) for arg in expr.arguments)
        res += ")"
        return res
    if isinstance(expr, Get):
        return f"{debug_expression(expr.object)}.{expr.name.lexeme}"
    if isinstance(expr, Set):
        return f"{debug_expression(expr.object)}.{expr.name.lexeme} = {debug_expression(expr.value)}"
    if isinstance(expr, This):
        return "this"
    return "expression"


def main():
    print("PyLox AST Debugger (enter empty line to parse, Ctrl+C to exit)")
    while True:
        try:
            src = ""
            while True:
                inp = input(">> ")
                if inp == "":
                    break
                src += inp + "\n"  # Append newline for semicolon-free input
            if not src.strip():
                continue
            scanner = Scanner(src)
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            statements = parser.parse()
            print(debug_program(statements))
            if parser.errors:
                print("\nerrors ::")
                print("\n".join(parser.errors))
        except KeyboardInterrupt:
            print("\nExiting debugger.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
