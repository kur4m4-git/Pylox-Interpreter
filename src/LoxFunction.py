
"""Implements the LoxFunction for callable Lox functions."""

from typing import TYPE_CHECKING, Any, List

from Environment import Environment
from Return import Return
from callable import LoxCallable
from statements import Function

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxInstance import LoxInstance


class LoxFunction(LoxCallable):
    """Represents a callable Lox function with parameters and a body."""

    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool) -> None:
        """Initialize a Lox function.

        Args:
            declaration: The function declaration statement.
            closure: The environment enclosing the function.
            is_initializer: True if the function is a class initializer.
        """
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        """Bind the function to an instance, creating a method.

        Args:
            instance: The instance to bind to.

        Returns:
            A new LoxFunction bound to the instance.
        """
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        """Execute the function with the given arguments.

        Args:
            interpreter: The interpreter executing the function.
            arguments: The arguments passed to the function.

        Returns:
            The return value of the function, or None for initializers.
        """
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def arity(self) -> int:
        """Return the number of parameters the function accepts.

        Returns:
            The number of parameters.
        """
        return len(self.declaration.params)

    def __str__(self) -> str:
        """Return the string representation of the function.

        Returns:
            The function name with <fn> prefix.
        """
        return f"<fn {self.declaration.name.lexeme}>"

