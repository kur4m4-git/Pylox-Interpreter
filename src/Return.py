"""
Defines the Return exception for handling return statements in Lox.
"""

class Return(Exception):
    """Exception to handle return values from functions."""
    def __init__(self, value: object):
        self.value = value
        super().__init__()