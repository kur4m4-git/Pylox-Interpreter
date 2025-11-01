
"""Tokenizes Lox source code into a list of tokens, treating newlines as semicolons."""

from typing import List

from Token import Token
from TokenType import TokenType
from RuntimeError import error


class Scanner:
    """Scans Lox source code and produces a list of tokens."""

    def __init__(self, source: str):
        """Initialize the scanner with source code.

        Args:
            source: The Lox source code to scan.
        """
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> List[Token]:
        """Scan the source code and return a list of tokens.

        Returns:
            List of tokens, including EOF.
        """
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        """Scan a single token from the source code."""
        char = self.advance()
        if char == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ",":
            self.add_token(TokenType.COMMA)
        elif char == ".":
            self.add_token(TokenType.DOT)
        elif char == "-":
            self.add_token(TokenType.MINUS)
        elif char == "+":
            self.add_token(TokenType.PLUS)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)
        elif char == "*":
            self.add_token(TokenType.STAR)
        elif char == "!":
            self.add_token(
                TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
            )
        elif char == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
        elif char == "<":
            self.add_token(
                TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
            )
        elif char == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
        elif char == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif char in (" ", "\r", "\t"):
            pass
        elif char == "\n":
            self.line += 1
            self.add_token(TokenType.SEMICOLON)  # Treat newline as semicolon
        elif char == '"':
            self.string()
        elif self.is_digit(char):
            self.number()
        elif self.is_alpha(char):
            self.identifier()
        else:
            error(self.line, None, "Unexpected character.")

    def is_at_end(self) -> bool:
        """Check if the scanner has reached the end of the source.

        Returns:
            True if at the end, False otherwise.
        """
        return self.current >= len(self.source)

    def advance(self) -> str:
        """Advance to the next character and return it.

        Returns:
            The current character.
        """
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, type: TokenType, literal: object = None) -> None:
        """Add a token to the token list.

        Args:
            type: The token type.
            literal: The literal value, if any.
        """
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        """Check if the next character matches the expected one.

        Args:
            expected: The expected character.

        Returns:
            True if the character matches and is consumed, False otherwise.
        """
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        """Look at the next character without consuming it.

        Returns:
            The next character, or empty string if at end.
        """
        if self.is_at_end():
            return ""
        return self.source[self.current]

    def string(self) -> None:
        """Scan a string literal."""
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end():
            error(self.line, None, "Unterminated string.")
            return
        self.advance()  # Consume closing "
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, char: str) -> bool:
        """Check if a character is a digit.

        Args:
            char: The character to check.

        Returns:
            True if the character is a digit, False otherwise.
        """
        return char.isdigit()

    def number(self) -> None:
        """Scan a number literal."""
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def peek_next(self) -> str:
        """Look at the character after the next one.

        Returns:
            The character after the next one, or empty string if at end.
        """
        if self.current + 1 >= len(self.source):
            return ""
        return self.source[self.current + 1]

    def is_alpha(self, char: str) -> bool:
        """Check if a character is alphabetic or underscore.

        Args:
            char: The character to check.

        Returns:
            True if the character is alphabetic or underscore, False otherwise.
        """
        return char.isalpha() or char == "_"

    def is_alphanumeric(self, char: str) -> bool:
        """Check if a character is alphanumeric or underscore.

        Args:
            char: The character to check.

        Returns:
            True if the character is alphanumeric or underscore, False otherwise.
        """
        return self.is_alpha(char) or self.is_digit(char)

    def identifier(self) -> None:
        """Scan an identifier or keyword."""
        while self.is_alphanumeric(self.peek()):
            self.advance()
        text = self.source[self.start : self.current]
        keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }
        type_ = keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type_)
