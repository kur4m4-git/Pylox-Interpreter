"""Implements the Environment class for managing variable scopes in Lox."""

from typing import Any, Dict, Optional

from RuntimeError import RuntimeErr
from Token import Token


class Environment:
    """Manages a scope of variables in the Lox interpreter."""

    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        """Initialize an environment.

        Args:
            enclosing: The parent environment, or None for the global scope.
        """
        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any) -> None:
        """Define a variable in the current environment.

        Args:
            name: The variable name.
            value: The variable value.
        """
        self.values[name] = value

    def get(self, name: Token) -> Any:
        """Get a variable's value by name.

        Args:
            name: The token representing the variable name.

        Returns:
            The variable's value.

        Raises:
            RuntimeErr: If the variable is undefined.
        """
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RuntimeErr(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: Token) -> Any:
        """Get a variable's value at a specific scope distance.

        Args:
            distance: The number of scopes to traverse.
            name: The token representing the variable name.

        Returns:
            The variable's value.
        """
        return self.ancestor(distance).values.get(name.lexeme)

    def assign(self, name: Token, value: Any) -> None:
        """Assign a value to an existing variable.

        Args:
            name: The token representing the variable name.
            value: The value to assign.

        Raises:
            RuntimeErr: If the variable is undefined.
        """
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeErr(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        """Assign a value to a variable at a specific scope distance.

        Args:
            distance: The number of scopes to traverse.
            name: The token representing the variable name.
            value: The value to assign.
        """
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> "Environment":
        """Get the environment at a specific scope distance.

        Args:
            distance: The number of scopes to traverse.

        Returns:
            The environment at the specified distance.
        """
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

