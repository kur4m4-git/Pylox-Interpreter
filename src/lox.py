"""Entry point for the PyLox interpreter, providing REPL and file execution."""

import sys
from typing import List

from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver
from RuntimeError import error
from TokenType import TokenType


class Lox:

    had_error: bool = False
    had_runtime_error: bool = False

    def __init__(self):
        self.interpreter = Interpreter()

    def main(self, args: List[str]) -> None:
        if len(args) > 2:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 2:
            self.run_file(args[1])
        else:
            self.run_prompt()

    def run_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as file:
                source = file.read()
            self.run(source)
            if Lox.had_error:
                sys.exit(65)
            if Lox.had_runtime_error:
                sys.exit(70)
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")
            sys.exit(66)

    def run_prompt(self) -> None:
        print("Welcome to python-lox 1.3.0!")
        while True:
            try:
                line = input("> ")
                if line == "":
                    break
                self.run(line + "\n")  # Append newline to ensure semicolon token
                Lox.had_error = False
                Lox.had_runtime_error = False
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nExiting REPL.")
                break

    def run(self, source: str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        if Lox.had_error:
            return
        resolver = Resolver(self.interpreter)
        resolver.resolve(statements)
        if Lox.had_error:
            return
        self.interpreter.interpret(statements)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}")
        Lox.had_error = True

    @staticmethod
    def runtime_error(err: error) -> None:
        print(f"{err}\n[line {err.token.line}]")
        Lox.had_runtime_error = True


def main() -> None:
    lox = Lox()
    lox.main(sys.argv)


if __name__ == "__main__":
    main()
