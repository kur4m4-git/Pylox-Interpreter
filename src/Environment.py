"""Implements the Environment class for managing variable scopes in Lox."""

from typing import Any, Dict, Optional

from RuntimeError import RuntimeErr
from Token import Token


class Environment:
    """Manages a scope of variables in the Lox interpreter."""

    def __init__(self, enclosing: Optional["Environment"] = None) -> None:

        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RuntimeErr(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: Token) -> Any:
        return self.ancestor(distance).values.get(name.lexeme)

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeErr(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

