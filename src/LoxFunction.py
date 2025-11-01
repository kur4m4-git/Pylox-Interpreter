
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

    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        
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
        
        return len(self.declaration.params)

    def __str__(self) -> str:
       
        return f"<fn {self.declaration.name.lexeme}>"

