"""
Implements the resolver for static variable resolution in Lox.
Ensures variables are resolved to their correct scopes.
"""

from expressions import *
from statements import *
from Interpreter import Interpreter
from Token import Token

# from TokenType import TokenType
from RuntimeError import error


class Resolver:
    """Resolves variable references to their correct scopes."""

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = None
        self.current_class = None

    def resolve(self, statements: list[Stmt]) -> None:
        """Resolve all variables in a list of statements."""
        for stmt in statements:
            self.resolve_stmt(stmt)

    def resolve_stmt(self, stmt: Stmt) -> None:
        """Resolve variables in a statement."""
        stmt.accept(self)

    def resolve_expr(self, expr: Expr) -> None:
        """Resolve variables in an expression."""
        expr.accept(self)

    def begin_scope(self) -> None:
        """Start a new scope."""
        self.scopes.append({})

    def end_scope(self) -> None:
        """End the current scope."""
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        """Declare a variable in the current scope."""
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            error(name.line, name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        """Define a variable in the current scope."""
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token) -> None:
        """Resolve a variable to its scope depth."""
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def visit_block_stmt(self, stmt: Block) -> None:
        """Resolve a block statement."""
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: Class) -> None:
        """Resolve a class declaration."""
        enclosing_class = self.current_class
        self.current_class = "class"
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass is not None:
            if stmt.superclass.name.lexeme == stmt.name.lexeme:
                error(
                    stmt.superclass.name.line,
                    stmt.superclass.name,
                    "A class can't inherit from itself.",
                )
            self.resolve_expr(stmt.superclass)
            self.begin_scope()
            self.scopes[-1]["super"] = True
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = "method"
            if method.name.lexeme == "init":
                declaration = "initializer"
            self.resolve_function(method, declaration)
        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class

    def visit_var_stmt(self, stmt: Var) -> None:
        """Resolve a variable declaration."""
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_variable_expr(self, expr: Variable) -> None:
        """Resolve a variable expression."""
        if (
            self.scopes
            and expr.name.lexeme in self.scopes[-1]
            and self.scopes[-1][expr.name.lexeme] is False
        ):
            error(
                expr.name.line,
                expr.name,
                "Can't read local variable in its own initializer.",
            )
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign) -> None:
        """Resolve an assignment expression."""
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: Function) -> None:
        """Resolve a function declaration."""
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, "function")

    def resolve_function(self, function: Function, ftype: str) -> None:
        """Resolve a function's parameters and body."""
        enclosing_function = self.current_function
        self.current_function = ftype
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_expression_stmt(self, stmt: Expression) -> None:
        """Resolve an expression statement."""
        self.resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt: If) -> None:
        """Resolve an if statement."""
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        """Resolve a print statement."""
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        """Resolve a return statement."""
        if self.current_function is None:
            error(stmt.keyword.line, stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.current_function == "initializer":
                error(
                    stmt.keyword.line,
                    stmt.keyword,
                    "Can't return a value from an initializer.",
                )
            self.resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt: While) -> None:
        """Resolve a while statement."""
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_binary_expr(self, expr: Binary) -> None:
        """Resolve a binary expression."""
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        """Resolve a function call expression."""
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)

    def visit_get_expr(self, expr: Get) -> None:
        """Resolve a property access expression."""
        self.resolve_expr(expr.object)

    def visit_set_expr(self, expr: Set) -> None:
        """Resolve a property assignment expression."""
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)

    def visit_literal_expr(self, expr: Literal) -> None:
        """Resolve a literal expression (no variables)."""
        pass

    def visit_logical_expr(self, expr: Logical) -> None:
        """Resolve a logical expression."""
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_unary_expr(self, expr: Unary) -> None:
        """Resolve a unary expression."""
        self.resolve_expr(expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        """Resolve a grouped expression."""
        self.resolve_expr(expr.expression)

    def visit_this_expr(self, expr: This) -> None:
        """Resolve a this expression."""
        if self.current_class is None:
            error(
                expr.keyword.line, expr.keyword, "Can't use 'this' outside of a class."
            )
        self.resolve_local(expr, expr.keyword)

    def visit_super_expr(self, expr: Super) -> None:
        """Resolve a super expression."""
        if self.current_class is None:
            error(
                expr.keyword.line, expr.keyword, "Can't use 'super' outside of a class."
            )
        elif self.current_class != "class":
            error(
                expr.keyword.line,
                expr.keyword,
                "Can't use 'super' in a class with no superclass.",
            )
        self.resolve_local(expr, expr.keyword)
