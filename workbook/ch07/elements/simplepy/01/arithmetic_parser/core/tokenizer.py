import re
from typing import List, Optional
from ..components.tokens import Token, TokenType
from ..components.operators.base import OperatorRegistry
from ..components.functions.base import FunctionRegistry
from .exceptions import TokenizationError


class Tokenizer:
    """Converts string expressions into tokens."""
    
    def __init__(self, operator_registry: OperatorRegistry, function_registry: Optional[FunctionRegistry] = None):
        self.operator_registry = operator_registry
        self.function_registry = function_registry
        
        # Patterns for different token types
        self.number_pattern = re.compile(r'-?\d*\.?\d*')
        self.identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
    
    def tokenize(self, expression: str) -> List[Token]:
        """Convert expression string to list of tokens."""
        tokens = []
        
        # Handle empty or whitespace-only input
        if not expression or expression.isspace():
            raise TokenizationError("Empty or whitespace-only expression")
        
        # Track original positions for error reporting
        original = expression
        expression = expression.replace(' ', '')  # Remove whitespace
        i = 0
        orig_i = 0  # Original position before whitespace removal
        
        while i < len(expression):
            char = expression[i]
            
            # Numbers and potential unary minus
            if char.isdigit() or char == '.' or char == '-':
                # Check if '-' is unary (start of number) or binary (operator)
                if char == '-' and i > 0:
                    prev_char = expression[i - 1]
                    # If previous is a number or ')', treat '-' as operator
                    if prev_char.isdigit() or prev_char == ')':
                        tokens.append(Token(TokenType.OPERATOR, '-', orig_i))
                        i += 1
                        orig_i += 1
                        continue
                
                number_match = self.number_pattern.match(expression, i)
                if number_match:
                    value_str = number_match.group()
                    # Validate number format
                    if value_str in ('-', '.', '-.'):
                        raise TokenizationError(f"Invalid number format: '{value_str}' at position {orig_i}")
                    if value_str.count('.') > 1:
                        raise TokenizationError(f"Multiple decimal points in number: '{value_str}' at position {orig_i}")
                    value = float(value_str)
                    tokens.append(Token(TokenType.NUMBER, value, orig_i))
                    i += len(value_str)
                    orig_i += len(value_str)
                    continue
            
            # Operators (handle multi-character operators)
            matched_operator = None
            for symbol in self.operator_registry.get_all_symbols():
                if expression[i:].startswith(symbol):
                    if matched_operator is None or len(symbol) > len(matched_operator):
                        matched_operator = symbol
            if matched_operator:
                tokens.append(Token(TokenType.OPERATOR, matched_operator, orig_i))
                i += len(matched_operator)
                orig_i += len(matched_operator)
                continue
            
            # Parentheses
            if char in '()':
                tokens.append(Token(TokenType.PARENTHESIS, char, orig_i))
                i += 1
                orig_i += 1
                continue
            
            # Comma
            if char == ',':
                tokens.append(Token(TokenType.COMMA, char, orig_i))
                i += 1
                orig_i += 1
                continue
            
            # Identifiers (functions)
            if char.isalpha():
                identifier_match = self.identifier_pattern.match(expression, i)
                if identifier_match:
                    name = identifier_match.group()
                    if self.function_registry is None:
                        raise TokenizationError(f"Functions are disabled, cannot use '{name}' at position {orig_i}")
                    if self.function_registry.is_registered(name):
                        tokens.append(Token(TokenType.FUNCTION, name, orig_i))
                    else:
                        raise TokenizationError(f"Unknown identifier: '{name}' at position {orig_i}")
                    i += len(name)
                    orig_i += len(name)
                    continue
            
            raise TokenizationError(f"Unexpected character: '{char}' at position {orig_i}")
        
        return tokens