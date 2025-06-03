class ParserError(Exception):
    """Base exception for all parser-related errors."""
    pass


class TokenizationError(ParserError):
    """Raised when tokenization fails."""
    pass


class EvaluationError(ParserError):
    """Raised when expression evaluation fails."""
    pass


class ValidationError(ParserError):
    """Raised when expression validation fails."""
    pass


class OperatorError(ParserError):
    """Raised when operator handling fails."""
    pass


class FunctionError(ParserError):
    """Raised when function evaluation fails."""
    pass

