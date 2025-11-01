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
        """Initialize the interpreter with a global environment."""
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Expr, int] = {}

    def interpret(self, stmts: List[Stmt]) -> None:
        """Interpret a list of statements.

        Args:
            stmts: List of Lox statements to execute.
        """
        try:
            for stmt in stmts:
                self.execute(stmt)
        except RuntimeErr as err:
            error(err.token.line, err.token, err.message)

    def execute(self, stmt: Stmt) -> None:
        """Execute a single statement.

        Args:
            stmt: The statement to execute.
        """
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        """Resolve a variable's scope depth.

        Args:
            expr: The expression to resolve.
            depth: The scope depth for the variable.
        """
        self.locals[expr] = depth

    def lookup_variable(self, name: Token, expr: Expr) -> Any:
        """Look up a variable in the current scope or globals.

        Args:
            name: The variable's token.
            expr: The expression containing the variable.

        Returns:
            The variable's value.
        """
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name)
        return self.globals.get(name)

    def visit_literal_expr(self, expr: Literal) -> Any:
        """Evaluate a literal expression.

        Args:
            expr: The literal expression.

        Returns:
            The literal value.
        """
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> Any:
        """Evaluate a logical expression (and, or).

        Args:
            expr: The logical expression.

        Returns:
            The evaluated result.
        """
        left = expr.left.accept(self)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return expr.right.accept(self)

    def visit_get_expr(self, expr: Get) -> Any:
        """Evaluate a property access expression.

        Args:
            expr: The get expression.

        Returns:
            The property value.

        Raises:
            RuntimeErr: If the object is not an instance.
        """
        obj = expr.object.accept(self)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise RuntimeErr(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr: Set) -> Any:
        """Evaluate a property assignment expression.

        Args:
            expr: The set expression.

        Returns:
            The assigned value.

        Raises:
            RuntimeErr: If the object is not an instance.
        """
        obj = expr.object.accept(self)
        if not isinstance(obj, LoxInstance):
            raise RuntimeErr(expr.name, "Only instances have fields.")
        value = expr.value.accept(self)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Super) -> Any:
        """Evaluate a super expression.

        Args:
            expr: The super expression.

        Returns:
            The bound method.

        Raises:
            RuntimeErr: If the method is undefined.
        """
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
        """Evaluate a this expression.

        Args:
            expr: The this expression.

        Returns:
            The instance value.
        """
        return self.lookup_variable(expr.keyword, expr)

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        """Evaluate a grouped expression.

        Args:
            expr: The grouping expression.

        Returns:
            The inner expression's value.
        """
        return expr.expression.accept(self)

    def visit_unary_expr(self, expr: Unary) -> Any:
        """Evaluate a unary expression.

        Args:
            expr: The unary expression.

        Returns:
            The evaluated result.
        """
        right = expr.right.accept(self)
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        return None

    def visit_variable_expr(self, expr: Variable) -> Any:
        """Evaluate a variable expression.

        Args:
            expr: The variable expression.

        Returns:
            The variable's value.
        """
        return self.lookup_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign) -> Any:
        """Evaluate an assignment expression.

        Args:
            expr: The assignment expression.

        Returns:
            The assigned value.
        """
        value = expr.value.accept(self)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> Any:
        """Evaluate a binary expression.

        Args:
            expr: The binary expression.

        Returns:
            The evaluated result.

        Raises:
            RuntimeErr: If operands are invalid.
        """
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
        """Evaluate a function call expression.

        Args:
            expr: The call expression.

        Returns:
            The function's return value.

        Raises:
            RuntimeErr: If callee is not callable or argument count is wrong.
        """
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
        """Execute an expression statement.

        Args:
            stmt: The expression statement.
        """
        stmt.expression.accept(self)

    def visit_function_stmt(self, stmt: Function) -> None:
        """Execute a function declaration.

        Args:
            stmt: The function statement.
        """
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_class_stmt(self, stmt: Class) -> None:
        """Execute a class declaration.

        Args:
            stmt: The class statement.

        Raises:
            RuntimeErr: If superclass is not a class.
        """
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
        """Execute an if statement.

        Args:
            stmt: The if statement.
        """
        if self.is_truthy(stmt.condition.accept(self)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        """Execute a print statement with Python-like behavior.

        Args:
            stmt: The print statement.
        """
        value = stmt.expression.accept(self)
        print(value)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        """Execute a return statement.

        Args:
            stmt: The return statement.
        """
        value = None
        if stmt.value is not None:
            value = stmt.value.accept(self)
        raise Return(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        """Execute a variable declaration.

        Args:
            stmt: The variable declaration statement.
        """
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer.accept(self)
        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        """Execute a while statement.

        Args:
            stmt: The while statement.
        """
        while self.is_truthy(stmt.condition.accept(self)):
            self.execute(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:
        """Execute a block statement.

        Args:
            stmt: The block statement.
        """
        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        """Execute a block of statements in a new environment.

        Args:
            statements: List of statements in the block.
            environment: The new environment for the block.
        """
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def is_truthy(self, obj: Any) -> bool:
        """Determine if an object is truthy, aligned with Python.

        Args:
            obj: The object to evaluate.

        Returns:
            True if the object is truthy, False otherwise.
        """
        return bool(obj)

    def is_equal(self, a: Any, b: Any) -> bool:
        """Check if two objects are equal.

        Args:
            a: First object.
            b: Second object.

        Returns:
            True if objects are equal, False otherwise.
        """
        return a == b

    def check_number_operand(self, operator: Token, operand: Any) -> None:
        """Ensure operand is a number for unary operations.

        Args:
            operator: The operator token.
            operand: The operand to check.

        Raises:
            RuntimeErr: If operand is not a number.
        """
        if isinstance(operand, (int, float)):
            return
        raise RuntimeErr(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        """Ensure both operands are numbers for binary operations.

        Args:
            operator: The operator token.
            left: The left operand.
            right: The right operand.

        Raises:
            RuntimeErr: If operands are not numbers.
        """
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeErr(operator, "Operands must be numbers.")

    def stringify(self, obj: Any) -> str:
        """Convert an object to its string representation, Python-like.

        Args:
            obj: The object to convert.

        Returns:
            The string representation.
        """
        if obj is None:
            return "None"
        return str(obj)