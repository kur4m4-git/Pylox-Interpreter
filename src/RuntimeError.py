

from sys import stderr
from Token import Token
from TokenType import TokenType

had_err: bool = False


class RuntimeErr(Exception):
    """Exception for runtime errors."""
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)


class ParseErr(Exception):
    """Exception for parse errors."""
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)
        error(line=self.token.line, token=self.token, msg=self.message)


def error(line: int = 0, token: Token = None, msg: str = "default message") -> None:
    """Report an error with line number, token, and message."""
    if token is None:
        report(line, "", msg)
    elif token.type == TokenType.EOF:
        report(token.line, " at end", msg)
    else:
        report(token.line, f" at {token.lexeme}", msg)


def report(line: int, where: str, message: str) -> None:
    """Print error message and set error flag."""
    print(f"[line {line}] Error{where}: {message}", file=stderr)
    set_err_status(True)


def get_err_status() -> bool:
    """Return the current error status."""
    global had_err
    return had_err


def set_err_status(status: bool) -> None:
    """Set the error status."""
    global had_err
    had_err = status
