from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from Interpreter import Interpreter


class LoxCallable:

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        raise NotImplementedError

    def arity(self) -> int:
        raise NotImplementedError

