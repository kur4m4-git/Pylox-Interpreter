"""Implements the LoxInstance for instances of Lox classes."""

from typing import TYPE_CHECKING, Any, Dict

from RuntimeError import RuntimeErr

if TYPE_CHECKING:
    from LoxClass import LoxClass


class LoxInstance:
    """Represents an instance of a Lox class with fields and methods."""

    def __init__(self, klass: "LoxClass") -> None:
        """Initialize a Lox instance.

        Args:
            klass: The Lox class this instance belongs to.
        """
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Any) -> Any:
        """Get a field or method from the instance.

        Args:
            name: The token representing the field or method name.

        Returns:
            The field or method value.

        Raises:
            RuntimeErr: If the property is not found.
        """
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeErr(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Any, value: Any) -> None:
        """Set a field on the instance.

        Args:
            name: The token representing the field name.
            value: The value to set.
        """
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        """Return the string representation of the instance.

        Returns:
            The class name with <instance> suffix.
        """
        return f"{self.klass.name} instance"

