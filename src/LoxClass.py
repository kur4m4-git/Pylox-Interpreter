"""Implements the LoxClass for representing Lox classes and their methods."""

from typing import TYPE_CHECKING, Any, Dict, Optional

from callable import LoxCallable
from LoxFunction import LoxFunction

if TYPE_CHECKING:
    from Interpreter import Interpreter
    from LoxInstance import LoxInstance


class LoxClass(LoxCallable):

    def __init__(
        self, name: str, superclass: Optional["LoxClass"], methods: Dict[str, LoxFunction]
    ) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> Optional[LoxFunction]:
    
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def __str__(self) -> str:
        
        return self.name

