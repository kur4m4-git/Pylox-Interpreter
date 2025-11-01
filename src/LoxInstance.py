"""Implements the LoxInstance for instances of Lox classes."""

from typing import TYPE_CHECKING, Any, Dict

from RuntimeError import RuntimeErr

if TYPE_CHECKING:
    from LoxClass import LoxClass


class LoxInstance:

    def __init__(self, klass: "LoxClass") -> None:
       
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Any) -> Any:
        
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeErr(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Any, value: Any) -> None:
        
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        
        return f"{self.klass.name} instance"

