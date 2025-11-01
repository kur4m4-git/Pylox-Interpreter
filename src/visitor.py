"""
Defines the Visitor interface for the Lox interpreter's visitor pattern.
"""

from abc import ABC, abstractmethod
from expressions import *
from statements import *


class Visitor(ABC):
    """Interface for visiting expression and statement nodes."""
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> object:
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> object:
        pass

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> object:
        pass

    @abstractmethod
    def visit_get_expr(self, expr: Get) -> object:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> object:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> object:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> object:
        pass

    @abstractmethod
    def visit_set_expr(self, expr: Set) -> object:
        pass

    @abstractmethod
    def visit_super_expr(self, expr: Super) -> object:
        pass

    @abstractmethod
    def visit_this_expr(self, expr: This) -> object:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> object:
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> object:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> None:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: Class) -> None:
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> None:
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: Function) -> None:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> None:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> None:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> None:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> None:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> None:
        pass