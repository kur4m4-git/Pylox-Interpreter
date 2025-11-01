"""Implements the LoxClass for representing Lox classes and their methods."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from callable import LoxCallable
from LoxFunction import LoxFunction

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxInstance import LoxInstance


class LoxClass(LoxCallable):
    """Represents a Lox class with methods and optional superclass."""

    def __init__(
        self, name: str, superclass: Optional["LoxClass"], methods: Dict[str, LoxFunction]
    ) -> None:
        """Initialize a Lox class.

        Args:
            name: The name of the class.
            superclass: The parent class, if any.
            methods: Dictionary of method names to LoxFunction objects.
        """
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> Optional[LoxFunction]:
        """Find a method by name in the class or its superclass.

        Args:
            name: The method name to find.

        Returns:
            The LoxFunction if found, else None.
        """
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        """Create an instance and call its initializer.

        Args:
            interpreter: The interpreter executing the call.
            arguments: The arguments to pass to the initializer.

        Returns:
            The initialized instance.
        """
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        """Return the number of parameters for the initializer.

        Returns:
            The number of parameters, or 0 if no initializer exists.
        """
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def __str__(self) -> str:
        """Return the string representation of the class.

        Returns:
            The class name.
        """
        return self.name

