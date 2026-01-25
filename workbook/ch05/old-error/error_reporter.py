from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class ErrorSeverity(Enum):
    WARNING = "Warning"
    ERROR = "Error"
    FATAL = "Fatal Error"

class ErrorCategory(Enum):
    LEXICAL = "Lexical"
    SYNTAX = "Syntax"
    SEMANTIC = "Semantic"
    RUNTIME = "Runtime"

@dataclass
class CompilerError:
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    context: Optional[str] = None
    suggestion: Optional[str] = None
    
    def __str__(self):
        parts = [f"[{self.severity.value}]"]
        
        if self.line is not None:
            if self.column is not None:
                parts.append(f"Line {self.line}, Column {self.column}")
            else:
                parts.append(f"Line {self.line}")
        
        parts.append(f"({self.category.value})")
        parts.append(self.message)
        
        result = " ".join(parts)
        
        if self.context:
            result += f"\n  Context: {self.context}"
        
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        
        return result

class ErrorReporter:
    def __init__(self, source_code: str = ""):
        self.errors: List[CompilerError] = []
        self.warnings: List[CompilerError] = []
        self.source_lines = source_code.split('\n') if source_code else []
        self.max_errors = 50  # Stop after this many errors
    
    def report(self, severity: ErrorSeverity, category: ErrorCategory, 
               message: str, line: Optional[int] = None, 
               column: Optional[int] = None, suggestion: Optional[str] = None):
        """Report an error or warning"""
        
        # Get context from source code
        context = None
        if line is not None and self.source_lines and 0 < line <= len(self.source_lines):
            context = self.source_lines[line - 1].strip()
            if column is not None and context:
                # Add a pointer to the error location
                pointer = " " * (column - 1) + "^"
                context = f"{context}\n  {pointer}"
        
        error = CompilerError(
            severity=severity,
            category=category,
            message=message,
            line=line,
            column=column,
            context=context,
            suggestion=suggestion
        )
        
        if severity == ErrorSeverity.WARNING:
            self.warnings.append(error)
        else:
            self.errors.append(error)
        
        # Check if we've hit the error limit
        if len(self.errors) >= self.max_errors:
            fatal = CompilerError(
                severity=ErrorSeverity.FATAL,
                category=ErrorCategory.SYNTAX,
                message=f"Too many errors ({self.max_errors}), stopping compilation",
                suggestion="Fix the earlier errors first"
            )
            self.errors.append(fatal)
            raise TooManyErrorsException(f"Exceeded maximum error count: {self.max_errors}")
    
    def has_errors(self) -> bool:
        """Check if any errors were reported"""
        return len(self.errors) > 0
    
    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors were reported"""
        return any(e.severity == ErrorSeverity.FATAL for e in self.errors)
    
    def print_report(self, show_warnings: bool = True):
        """Print a formatted error report"""
        if not self.errors and not self.warnings:
            print("✓ No errors found")
            return
        
        if self.errors:
            print("=" * 70)
            print(f"ERRORS FOUND: {len(self.errors)}")
            print("=" * 70)
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. {error}")
            print()
        
        if show_warnings and self.warnings:
            print("=" * 70)
            print(f"WARNINGS: {len(self.warnings)}")
            print("=" * 70)
            for i, warning in enumerate(self.warnings, 1):
                print(f"\n{i}. {warning}")
            print()
        
        # Summary
        if self.errors:
            print("=" * 70)
            print(f"Compilation failed with {len(self.errors)} error(s)", end="")
            if self.warnings:
                print(f" and {len(self.warnings)} warning(s)")
            else:
                print()
            print("=" * 70)
    
    def get_summary(self) -> str:
        """Get a brief summary of errors and warnings"""
        if not self.errors and not self.warnings:
            return "No issues found"
        
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        
        return ", ".join(parts)

class TooManyErrorsException(Exception):
    """Raised when too many errors are encountered"""
    pass

# Common error patterns and their suggestions
ERROR_SUGGESTIONS = {
    "undeclared_variable": "Did you forget to declare this variable with 'let'?",
    "redeclared_variable": "This variable was already declared. Use '=' for assignment instead of 'let'.",
    "missing_semicolon": "Add a semicolon ';' at the end of the statement.",
    "missing_brace": "Check that all '{' braces have matching '}' braces.",
    "unexpected_token": "This token is not expected here. Check your syntax.",
    "unexpected_eof": "The file ended unexpectedly. Did you forget to close a brace or statement?",
    "division_by_zero": "Ensure the divisor is not zero before performing division.",
    "type_mismatch": "Check that the types of values being compared or combined are compatible.",
    "invalid_number": "Use only digits and optionally one decimal point in numbers.",
    "unterminated_string": "Strings must end with a closing quote (\").",
    "invalid_character": "This character is not valid in the language. Check for typos.",
}

def get_suggestion(error_type: str) -> str:
    """Get a suggestion for a common error type"""
    return ERROR_SUGGESTIONS.get(error_type, "Review the code and fix the issue.")
