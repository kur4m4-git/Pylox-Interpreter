from typing import List, Optional
from typing import TYPE_CHECKING

from Token import Token
from TokenType import TokenType
from RuntimeError import error
from statements import Stmt, Print, Expression, Var, Block, If, While, Function, Return, Class
from expressions import Expr, Binary, Unary, Literal, Grouping, Variable, Assign, Logical, Call, Get, Set, This

if TYPE_CHECKING:
    from LoxClass import LoxClass


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


class Parser:
    """Parses a list of tokens into an AST."""

    def __init__(self, tokens: List[Token]):
    
        self.tokens = tokens
        self.current = 0
        self.errors: List[str] = []  # Store parsing errors

    def parse(self) -> List[Stmt]:
        """Parse tokens into a list of statements."""
        statements: List[Stmt] = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def class_declaration(self) -> Stmt:
        """Parse a class declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods: List[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods)

    def var_declaration(self) -> Stmt:
        """Parse a variable declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume_semicolon("Expect ';' or newline after variable declaration.")
        return Var(name, initializer)

    def statement(self) -> Stmt:
        """Parse a statement."""
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self) -> Stmt:
        """Parse a for statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match(TokenType.VAR):
            initializer = self.var_declaration()
        elif not self.match(TokenType.SEMICOLON):
            initializer = self.expression_statement()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()
        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def if_statement(self) -> Stmt:
        """Parse an if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def print_statement(self) -> Stmt:
        """Parse a print statement."""
        value = self.expression()
        self.consume_semicolon("Expect ';' or newline after value.")
        return Print(value)

    def return_statement(self) -> Stmt:
        """Parse a return statement."""
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.EOF):
            value = self.expression()
        self.consume_semicolon("Expect ';' or newline after return value.")
        return Return(keyword, value)

    def while_statement(self) -> Stmt:
        """Parse a while statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def expression_statement(self) -> Stmt:
        """Parse an expression statement."""
        expr = self.expression()
        self.consume_semicolon("Expect ';' or newline after expression.")
        return Expression(expr)

    def function(self, kind: str) -> Function:
        """Parse a function declaration."""
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: List[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(
                self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
            )
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.errors.append(f"[line {self.peek().line}] Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def block(self) -> List[Stmt]:
        """Parse a block of statements."""
        statements: List[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            decl = self.declaration()
            if decl is not None:
                statements.append(decl)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self) -> Expr:
        """Parse an expression."""
        return self.assignment()

    def assignment(self) -> Expr:
        """Parse an assignment expression."""
        expr = self.or_expr()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            if isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            self.errors.append(f"[line {equals.line}] Invalid assignment target.")
        return expr

    def or_expr(self) -> Expr:
        """Parse a logical OR expression."""
        expr = self.and_expr()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
        return expr

    def and_expr(self) -> Expr:
        """Parse a logical AND expression."""
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def equality(self) -> Expr:
        """Parse an equality expression."""
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        """Parse a comparison expression."""
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        """Parse a term expression."""
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        """Parse a factor expression."""
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        """Parse a unary expression."""
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self) -> Expr:
        """Parse a call expression."""
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        """Parse the arguments of a call expression."""
        arguments: List[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.errors.append(f"[line {self.peek().line}] Can't have more than 255 arguments.")
                arguments.append(self.expression())
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        """Parse a primary expression."""
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.THIS):
            return This(self.previous())
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        self.errors.append(f"[line {self.peek().line}] Expect expression.")
        raise ParseError()

    def consume(self, type: TokenType, message: str) -> Token:

        if self.check(type):
            return self.advance()
        self.errors.append(f"[line {self.peek().line}] {message}")
        raise ParseError()

    def consume_semicolon(self, message: str) -> None:
       
        if self.check(TokenType.SEMICOLON) or self.check(TokenType.EOF):
            if self.check(TokenType.SEMICOLON):
                self.advance()
            return
        self.errors.append(f"[line {self.peek().line}] {message}")
        raise ParseError()

    def match(self, *types: TokenType) -> bool:
        
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
       
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return
            self.advance()
