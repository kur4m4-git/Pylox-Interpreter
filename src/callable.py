"""Defines the LoxCallable interface for callable Lox objects."""

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from Interpreter import Interpreter


class LoxCallable:
    """Interface for callable Lox objects, such as functions and classes."""

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        """Execute the callable with the given arguments.

        Args:
            interpreter: The interpreter executing the callable.
            arguments: The arguments passed to the callable.

        Returns:
            The result of the execution.
        """
        raise NotImplementedError

    def arity(self) -> int:
        """Return the number of parameters the callable accepts.

        Returns:
            The number of parameters.
        """
        raise NotImplementedError

