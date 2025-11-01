from typing import Any, Dict, List

from Environment import Environment
from LoxClass import LoxClass
from LoxFunction import LoxFunction
from LoxInstance import LoxInstance
from Return import Return
from RuntimeError import RuntimeErr, error
from Token import Token
from TokenType import TokenType
from callable import LoxCallable
from expressions import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from statements import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return as ReturnStmt,
    Stmt,
    Var,
    While,
)
from visitor import Visitor


class Interpreter(Visitor):
    """Interprets Lox ASTs by visiting nodes and executing them."""

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Expr, int] = {}

    def interpret(self, stmts: List[Stmt]) -> None:
        
        try:
            for stmt in stmts:
                self.execute(stmt)
        except RuntimeErr as err:
            error(err.token.line, err.token, err.message)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def lookup_variable(self, name: Token, expr: Expr) -> Any:
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name)
        return self.globals.get(name)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> Any:
        left = expr.left.accept(self)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return expr.right.accept(self)

    def visit_get_expr(self, expr: Get) -> Any:
        obj = expr.object.accept(self)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise RuntimeErr(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr: Set) -> Any:
        obj = expr.object.accept(self)
        if not isinstance(obj, LoxInstance):
            raise RuntimeErr(expr.name, "Only instances have fields.")
        value = expr.value.accept(self)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super) -> Any:
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(
            distance,
            Token(TokenType.SUPER, "super", None, expr.keyword.line),
        )
        obj = self.environment.get_at(
            distance - 1,
            Token(TokenType.THIS, "this", None, expr.keyword.line),
        )
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeErr(
                expr.method, f"Undefined property '{expr.method.lexeme}'."
            )
        return method.bind(obj)

    def visit_this_expr(self, expr: This) -> Any:
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return expr.expression.accept(self)

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = expr.right.accept(self)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        return None

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.lookup_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = expr.value.accept(self)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        if expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        if expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        if expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        if expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        if expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if float(right) == 0.0:
                raise RuntimeErr(expr.operator, "Can't divide by zero.")
            return float(left) / float(right)
        if expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        if expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise RuntimeErr(
                expr.operator,
                "Operands must be two numbers or two strings.",
            )
        return None

    def visit_call_expr(self, expr: Call) -> Any:
        callee = expr.callee.accept(self)
        arguments = [arg.accept(self) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise RuntimeErr(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise RuntimeErr(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )
        return callee.call(self, arguments)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        stmt.expression.accept(self)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_class_stmt(self, stmt: Class) -> None:
        superclass = None
        if stmt.superclass is not None:
            superclass = stmt.superclass.accept(self)
            if not isinstance(superclass, LoxClass):
                raise RuntimeErr(stmt.superclass.name, "Superclass must be a class.")
        self.environment.define(stmt.name.lexeme, None)
        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if stmt.superclass is not None:
            self.environment = self.environment.enclosing
        self.environment.assign(stmt.name, klass)

    def visit_if_stmt(self, stmt: If) -> None:
        if self.is_truthy(stmt.condition.accept(self)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = stmt.expression.accept(self)
        print(value)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        value = None
        if stmt.value is not None:
            value = stmt.value.accept(self)
        raise Return(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer.accept(self)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self.is_truthy(stmt.condition.accept(self)):
            self.execute(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:

        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def is_truthy(self, obj: Any) -> bool:
       
        return bool(obj)

    def is_equal(self, a: Any, b: Any) -> bool:
       
        return a == b

    def check_number_operand(self, operator: Token, operand: Any) -> None:
        
        if isinstance(operand, (int, float)):
            return
        raise RuntimeErr(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
       
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeErr(operator, "Operands must be numbers.")

    def stringify(self, obj: Any) -> str:
       
        if obj is None:
            return "None"
        return str(obj)
