from enum import Enum
from typing import Union, Any
from dataclasses import dataclass


class TokenType(Enum):
    """Enumeration of all possible token types."""
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    FUNCTION = "FUNCTION"
    PARENTHESIS = "PARENTHESIS"
    VARIABLE = "VARIABLE"      # For future variable support
    CONSTANT = "CONSTANT"      # For future constant support
    COMMA = "COMMA"           # For function arguments


@dataclass
class Token:
    """
    Represents a single token in an arithmetic expression.
    
    Using dataclass for cleaner code and automatic methods.
    """
    type: TokenType
    value: Union[float, str]
    position: int = 0  # Position in original expression for error reporting
    
    def __str__(self):
        return f"{self.type.value}({self.value})"
    
    def is_number(self) -> bool:
        """Check if token is a number."""
        return self.type == TokenType.NUMBER
    
    def is_operator(self) -> bool:
        """Check if token is an operator."""
        return self.type == TokenType.OPERATOR
    
    def is_function(self) -> bool:
        """Check if token is a function."""
        return self.type == TokenType.FUNCTION