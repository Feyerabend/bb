from typing import List
from .tokens import Token
from ..core.exceptions import ValidationError


class ExpressionValidator:
    """Validates arithmetic expressions for correctness."""
    
    def validate(self, tokens: List[Token]) -> bool:
        """Validate a list of tokens."""
        if not tokens:
            raise ValidationError("Empty expression")
        
        # Check for balanced parentheses
        self._check_balanced_parentheses(tokens)
        
        # Check for valid token sequence
        self._check_token_sequence(tokens)
        
        return True
    
    def _check_balanced_parentheses(self, tokens: List[Token]) -> None:
        """Check if parentheses are balanced."""
        count = 0
        for token in tokens:
            if token.value == '(':
                count += 1
            elif token.value == ')':
                count -= 1
                if count < 0:
                    raise ValidationError("Unmatched closing parenthesis")
        
        if count != 0:
            raise ValidationError("Unmatched opening parenthesis")
    
    def _check_token_sequence(self, tokens: List[Token]) -> None:
        """Check if token sequence is valid."""
        prev_token = None
        
        for token in tokens:
            if prev_token:
                # Add validation rules here
                pass
            prev_token = token