# -*- coding: utf-8 -*-
"""
BASIC Interpreter - A simple BASIC language interpreter.
Refactored for improved design, maintainability, and robustness.
"""
import sys
import re
import math
import random
from typing import Any, List, Tuple, Optional, Dict, Union, Set
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum, auto

class InterpreterError(Exception):
    """Base exception for interpreter errors."""
    pass

class ParserError(InterpreterError):
    """Exception for parsing errors."""
    pass

class ExecutionError(InterpreterError):
    """Exception for execution errors."""
    pass

# Constants
class Constants:
    """Global constants for the interpreter."""
    DEFAULT_START_LINE = 10
    DEFAULT_INCREMENT = 10
    COMPARISON_OPERATORS = {"=", "<>", "<", ">", "<=", ">="}
    ARITHMETIC_OPERATORS = {"+", "-", "*", "/"}
    LINE_NUMBER_VARIABLE = "#"

# State Management
class InterpreterState:
    """
    Manages the interpreter's state including code, variables, 
    loop tracking, and execution control.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the interpreter state to initial values."""
        self.code: Dict[int, str] = {}
        # Line number variable is initialized to 10
        self.variables: Dict[str, Any] = {Constants.LINE_NUMBER_VARIABLE: Constants.DEFAULT_START_LINE}
        self.stack: List[int] = []
        self.loops: Dict[str, Tuple[int, float, float]] = {}
        self.whiles: Dict[str, Tuple[int, str]] = {}
        self.paused: bool = False
    
    @property
    def current_line(self) -> int:
        """Get the current line number."""
        return self.variables.get(Constants.LINE_NUMBER_VARIABLE, 0)
    
    @current_line.setter
    def current_line(self, value: int):
        """Set the current line number."""
        self.variables[Constants.LINE_NUMBER_VARIABLE] = value
    
    def advance_line(self) -> None:
        """Advance to the next line in the code."""
        current = self.current_line
        self.current_line = next(
            (n for n in sorted(self.code.keys()) if n > current), 0)

# Expression Handling
class ExpressionType(Enum):
    """Enumeration of expression types."""
    NUMBER = auto()
    STRING = auto()
    VARIABLE = auto()
    BINARY = auto()
    FUNCTION = auto()

class Expression(ABC):
    """Base class for all expressions in the BASIC language."""
    
    @property
    @abstractmethod
    def type(self) -> ExpressionType:
        """Get the type of the expression."""
        pass
    
    @abstractmethod
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        """Accept a visitor for evaluation."""
        pass

class NumberExpression(Expression):
    """Represents a numeric literal."""
    
    def __init__(self, value: float):
        self.value = value
    
    @property
    def type(self) -> ExpressionType:
        return ExpressionType.NUMBER

    def accept(self, visitor: 'ExpressionVisitor') -> float:
        return visitor.visit_number(self)

class StringExpression(Expression):
    """Represents a string literal."""
    
    def __init__(self, value: str):
        self.value = value
    
    @property
    def type(self) -> ExpressionType:
        return ExpressionType.STRING

    def accept(self, visitor: 'ExpressionVisitor') -> str:
        return visitor.visit_string(self)

class VariableExpression(Expression):
    """Represents a variable reference."""
    
    def __init__(self, name: str):
        if CommandRegistry.is_reserved(name):
            raise ParserError(f"Cannot use reserved name '{name}' as variable")
        self.name = name
    
    @property
    def type(self) -> ExpressionType:
        return ExpressionType.VARIABLE

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_variable(self)

class BinaryExpression(Expression):
    """Represents a binary operation between two expressions."""
    
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    @property
    def type(self) -> ExpressionType:
        return ExpressionType.BINARY

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_binary(self)

class FunctionExpression(Expression):
    """Represents a function call."""
    
    def __init__(self, name: str, args: List[Expression]):
        if not CommandRegistry.is_reserved_function(name):
            raise ParserError(f"Unknown function: {name}")
        self.name = name
        self.args = args
    
    @property
    def type(self) -> ExpressionType:
        return ExpressionType.FUNCTION

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_function(self)

class ExpressionVisitor(ABC):
    """Base visitor interface for expressions."""
    
    @abstractmethod
    def visit_number(self, expr: NumberExpression) -> float:
        pass

    @abstractmethod
    def visit_string(self, expr: StringExpression) -> str:
        pass

    @abstractmethod
    def visit_variable(self, expr: VariableExpression) -> Any:
        pass

    @abstractmethod
    def visit_binary(self, expr: BinaryExpression) -> Any:
        pass

    @abstractmethod
    def visit_function(self, expr: FunctionExpression) -> Any:
        pass

class EvaluationVisitor(ExpressionVisitor):
    """Evaluates expressions in the context of the interpreter state."""
    
    def __init__(self, state: InterpreterState):
        self.state = state

    def visit_number(self, expr: NumberExpression) -> float:
        return expr.value

    def visit_string(self, expr: StringExpression) -> str:
        return expr.value

    def visit_variable(self, expr: VariableExpression) -> Any:
        return self.state.variables.get(expr.name, 0)

    def visit_binary(self, expr: BinaryExpression) -> Any:
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        # Handle arithmetic operations
        if expr.operator in Constants.ARITHMETIC_OPERATORS:
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise ExecutionError(f"Operator '{expr.operator}' requires numeric operands")
            
            if expr.operator == "+":
                return left + right
            elif expr.operator == "-":
                return left - right
            elif expr.operator == "*":
                return left * right
            elif expr.operator == "/":
                if right == 0:
                    raise ExecutionError("Division by zero")
                return left / right

        # Handle comparison operations
        if expr.operator in Constants.COMPARISON_OPERATORS:
            # Check operand types are comparable
            if isinstance(left, str) and isinstance(right, str) or \
               isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if expr.operator == "=":
                    return 1 if left == right else 0
                elif expr.operator == "<>":
                    return 1 if left != right else 0
                elif expr.operator == "<":
                    return 1 if left < right else 0
                elif expr.operator == ">":
                    return 1 if left > right else 0
                elif expr.operator == "<=":
                    return 1 if left <= right else 0
                elif expr.operator == ">=":
                    return 1 if left >= right else 0
            else:
                raise ExecutionError(f"Cannot compare {type(left).__name__} with {type(right).__name__}")

        raise ExecutionError(f"Unknown operator: {expr.operator}")

    def visit_function(self, expr: FunctionExpression) -> Any:
        """Evaluate a function call."""
        name = expr.name.lower()
        args = [arg.accept(self) for arg in expr.args]
        
        # Use FunctionRegistry to get and call the function
        return FunctionRegistry.call_function(name, args)

class ExpressionParser:
    """Parses strings into Expression trees."""
    
    def __init__(self, text: str):
        self.text = text.strip()
        self.pos = 0
        self.length = len(self.text)

    def parse(self) -> Expression:
        """Parse the input text into an expression tree."""
        expr = self.parse_expression()
        self.skip_whitespace()
        if self.pos < self.length:
            raise ParserError(f"Unexpected characters after expression: '{self.text[self.pos:]}'")
        return expr

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1

    def parse_expression(self) -> Expression:
        """Parse a full expression."""
        return self.parse_comparison()

    def parse_comparison(self) -> Expression:
        """Parse a comparison expression."""
        left = self.parse_term()
        self.skip_whitespace()

        if self.pos < self.length:
            op = ""
            if self.pos + 1 < self.length and self.text[self.pos:self.pos+2] in ["<=", ">=", "<>"]:
                op = self.text[self.pos:self.pos+2]
                self.pos += 2
            elif self.text[self.pos] in "<>=":
                op = self.text[self.pos]
                self.pos += 1
            if op:
                right = self.parse_term()
                return BinaryExpression(left, op, right)
        return left

    def parse_term(self) -> Expression:
        """Parse a term (addition/subtraction)."""
        left = self.parse_factor()
        self.skip_whitespace()

        while self.pos < self.length and self.text[self.pos] in "+-":
            op = self.text[self.pos]
            self.pos += 1
            self.skip_whitespace()
            right = self.parse_factor()
            left = BinaryExpression(left, op, right)
            self.skip_whitespace()
        return left

    def parse_factor(self) -> Expression:
        """Parse a factor (multiplication/division)."""
        left = self.parse_primary()
        self.skip_whitespace()

        while self.pos < self.length and self.text[self.pos] in "*/":
            op = self.text[self.pos]
            self.pos += 1
            self.skip_whitespace()
            right = self.parse_primary()
            left = BinaryExpression(left, op, right)
            self.skip_whitespace()
        return left

    def parse_primary(self) -> Expression:
        """Parse a primary expression (number, string, variable, etc.)."""
        self.skip_whitespace()
        if self.pos >= self.length:
            raise ParserError("Unexpected end of expression")

        char = self.text[self.pos]
        
        # Parse identifiers (variables and functions)
        if char.isalpha() or char == "_":
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] in "_$"):
                self.pos += 1
            name = self.text[start:self.pos]

            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == '(':
                # Function call
                self.pos += 1
                args = []
                self.skip_whitespace()

                if self.pos < self.length and self.text[self.pos] == ')':
                    self.pos += 1
                    return FunctionExpression(name, args)

                while True:
                    args.append(self.parse_expression())
                    self.skip_whitespace()
                    if self.pos >= self.length or self.text[self.pos] != ',':
                        break
                    self.pos += 1

                if self.pos < self.length and self.text[self.pos] == ')':
                    self.pos += 1
                else:
                    raise ParserError("Expected closing parenthesis")
                return FunctionExpression(name, args)
            return VariableExpression(name)

        # Parse numbers
        elif char.isdigit() or char == '.':
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                self.pos += 1
            number_str = self.text[start:self.pos]
            try:
                return NumberExpression(float(number_str))
            except ValueError:
                raise ParserError(f"Invalid number format: {number_str}")

        # Parse strings
        elif char == '"':
            self.pos += 1
            start = self.pos
            while self.pos < self.length and self.text[self.pos] != '"':
                self.pos += 1
            if self.pos >= self.length:
                raise ParserError("Unterminated string literal")
            value = self.text[start:self.pos]
            self.pos += 1
            return StringExpression(value)

        # Parse parenthesized expressions
        elif char == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == ')':
                self.pos += 1
                return expr
            raise ParserError("Expected closing parenthesis")

        raise ParserError(f"Unexpected character: {char}")

# Function Registry
class FunctionRegistry:
    """Registry of built-in functions for the BASIC interpreter."""
    
    _functions = {
        "abs": lambda args: abs(args[0]) if len(args) == 1 else 0,
        "sin": lambda args: math.sin(args[0]) if len(args) == 1 else 0,
        "cos": lambda args: math.cos(args[0]) if len(args) == 1 else 0,
        "tan": lambda args: math.tan(args[0]) if len(args) == 1 else 0,
        "atn": lambda args: math.atan(args[0]) if len(args) == 1 else 0,
        "exp": lambda args: math.exp(args[0]) if len(args) == 1 else 0,
        "log": lambda args: math.log(args[0]) if len(args) == 1 and args[0] > 0 else 0,
        "sqr": lambda args: math.sqrt(args[0]) if len(args) == 1 and args[0] >= 0 else 0,
        "int": lambda args: int(args[0]) if len(args) == 1 else 0,
        "rnd": lambda args: random.random() if not args else random.random() * args[0],
        "len": lambda args: len(args[0]) if len(args) == 1 and isinstance(args[0], str) else 0,
        "val": lambda args: float(args[0]) if len(args) == 1 and isinstance(args[0], str) else 0,
        "str": lambda args: str(args[0]) if len(args) == 1 else "",
        "mid": lambda args: args[0][int(args[1]-1):int(args[1]-1+args[2])] if len(args) == 3 and isinstance(args[0], str) else "",
        "left": lambda args: args[0][:int(args[1])] if len(args) == 2 and isinstance(args[0], str) else "",
        "right": lambda args: args[0][-int(args[1]):] if len(args) == 2 and isinstance(args[0], str) else "",
        "chr": lambda args: chr(int(args[0])) if len(args) == 1 else "",
        "asc": lambda args: ord(args[0][0]) if len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 0 else 0,
    }
    
    @classmethod
    def call_function(cls, name: str, args: List[Any]) -> Any:
        """Call a function by name with arguments."""
        name = name.lower()
        if name not in cls._functions:
            raise ExecutionError(f"Unknown function: {name}")
        
        try:
            return cls._functions[name](args)
        except Exception as e:
            raise ExecutionError(f"Error in function {name}: {str(e)}")
    
    @classmethod
    def is_function(cls, name: str) -> bool:
        """Check if a name refers to a built-in function."""
        return name.lower() in cls._functions

# Command Registry
class CommandRegistry:
    """Registry of built-in commands for the BASIC interpreter."""
    
    _commands = set()
    _reserved_names = set()
    _functions = set()
    
    @classmethod
    def register_command(cls, name: str, handler: Any) -> None:
        """Register a command handler."""
        cls._commands.add(name.lower())
        cls._reserved_names.add(name.lower())
    
    @classmethod
    def register_function(cls, name: str) -> None:
        """Register a function name as reserved."""
        cls._functions.add(name.lower())
        cls._reserved_names.add(name.lower())
    
    @classmethod
    def is_command(cls, name: str) -> bool:
        """Check if a name refers to a built-in command."""
        return name.lower() in cls._commands
    
    @classmethod
    def is_reserved(cls, name: str) -> bool:
        """Check if a name is reserved (command or function)."""
        return name.lower() in cls._reserved_names
    
    @classmethod
    def is_reserved_function(cls, name: str) -> bool:
        """Check if a name refers to a built-in function."""
        return name.lower() in cls._functions or FunctionRegistry.is_function(name.lower())

# Initialize command and function registries
def init_registries():
    """Initialize the command and function registries."""
    # Register commands
    for cmd in ["print", "let", "input", "goto", "gosub", "return", "if", 
                "for", "next", "end", "stop", "rem", "cls", "list", "run", 
                "new", "save", "load", "while", "wend"]:
        CommandRegistry.register_command(cmd, None)
    
    # Register functions
    for func in FunctionRegistry._functions.keys():
        CommandRegistry.register_function(func)

# Command Handling
class CommandBase(ABC):
    """Base class for all commands in the BASIC language."""
    
    def __init__(self, state: InterpreterState):
        self.state = state
    
    @abstractmethod
    def execute(self, args: str) -> None:
        """Execute the command with the given arguments."""
        pass

class PrintCommand(CommandBase):
    """Implements the PRINT command."""
    
    def execute(self, args: str) -> None:
        """Execute the PRINT command."""
        if not args:
            print()
            return
        
        parts = []
        pos = 0
        length = len(args)
        
        while pos < length:
            if args[pos] == '"':  # String literal
                end_quote = args.find('"', pos + 1)
                if end_quote == -1:
                    raise ParserError("Unterminated string in PRINT command")
                parts.append(args[pos+1:end_quote])
                pos = end_quote + 1
            elif args[pos:pos+1] == ";":  # No space separator
                parts.append("")
                pos += 1
            elif args[pos:pos+1] == ",":  # Tab separator
                parts.append("\t")
                pos += 1
            else:  # Expression
                expr_end = next((i for i, c in enumerate(args[pos:], pos) if c in ";,"), length)
                expr_text = args[pos:expr_end].strip()
                if expr_text:
                    parser = ExpressionParser(expr_text)
                    expr = parser.parse()
                    visitor = EvaluationVisitor(self.state)
                    result = expr.accept(visitor)
                    # Format numbers without trailing decimal
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    parts.append(str(result))
                pos = expr_end

        # Print with appropriate spacing
        result = ""
        for i, part in enumerate(parts):
            if i > 0 and part and parts[i-1] and parts[i-1] != "\t":
                result += " "
            result += part
        
        print(result, end="")
        if not parts or parts[-1] != "":
            print()

class LetCommand(CommandBase):
    """Implements the LET command."""
    
    def execute(self, args: str) -> None:
        """Execute the LET command."""
        if not args:
            raise ParserError("Missing assignment in LET command")
        
        # Find the assignment operator
        eq_pos = args.find("=")
        if eq_pos == -1:
            raise ParserError("Missing = in LET command")
        
        var_name = args[:eq_pos].strip()
        expr_text = args[eq_pos+1:].strip()
        
        if not var_name:
            raise ParserError("Missing variable name in LET command")
        
        if CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Cannot assign to reserved name: {var_name}")
        
        parser = ExpressionParser(expr_text)
        expr = parser.parse()
        visitor = EvaluationVisitor(self.state)
        value = expr.accept(visitor)
        
        self.state.variables[var_name] = value

class InputCommand(CommandBase):
    """Implements the INPUT command."""
    
    def execute(self, args: str) -> None:
        """Execute the INPUT command."""
        if not args:
            raise ParserError("Missing variable name in INPUT command")
        
        # Parse the prompt if provided
        prompt = ""
        var_name = args
        
        if '"' in args:
            prompt_end = args.find('"', 1)
            if prompt_end == -1:
                raise ParserError("Unterminated string in INPUT command")
            prompt = args[1:prompt_end]
            
            if prompt_end + 1 < len(args) and args[prompt_end+1] == ";":
                var_name = args[prompt_end+2:].strip()
            else:
                raise ParserError("Expected ; after prompt in INPUT command")
        
        if not var_name or CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Invalid variable name in INPUT command: {var_name}")
        
        # Get user input
        try:
            if prompt:
                user_input = input(prompt + "? ")
            else:
                user_input = input("? ")
            
            # Try to convert to number if possible
            try:
                value = float(user_input)
                if value == int(value):
                    value = int(value)
            except ValueError:
                value = user_input
            
            self.state.variables[var_name] = value
            
        except KeyboardInterrupt:
            print("\nInput interrupted")
            raise ExecutionError("Input interrupted")

class GotoCommand(CommandBase):
    """Implements the GOTO command."""
    
    def execute(self, args: str) -> None:
        """Execute the GOTO command."""
        if not args:
            raise ParserError("Missing line number in GOTO command")
        
        parser = ExpressionParser(args)
        expr = parser.parse()
        visitor = EvaluationVisitor(self.state)
        line_num = expr.accept(visitor)
        
        if not isinstance(line_num, (int, float)) or line_num != int(line_num):
            raise ExecutionError(f"Invalid line number in GOTO: {line_num}")
        
        line_num = int(line_num)
        if line_num not in self.state.code:
            raise ExecutionError(f"Line {line_num} does not exist")
        
        self.state.current_line = line_num

class GosubCommand(CommandBase):
    """Implements the GOSUB command."""
    
    def execute(self, args: str) -> None:
        """Execute the GOSUB command."""
        if not args:
            raise ParserError("Missing line number in GOSUB command")
        
        parser = ExpressionParser(args)
        expr = parser.parse()
        visitor = EvaluationVisitor(self.state)
        line_num = expr.accept(visitor)
        
        if not isinstance(line_num, (int, float)) or line_num != int(line_num):
            raise ExecutionError(f"Invalid line number in GOSUB: {line_num}")
        
        line_num = int(line_num)
        if line_num not in self.state.code:
            raise ExecutionError(f"Line {line_num} does not exist")
        
        self.state.stack.append(self.state.current_line)
        self.state.current_line = line_num

class ReturnCommand(CommandBase):
    """Implements the RETURN command."""
    
    def execute(self, args: str) -> None:
        """Execute the RETURN command."""
        if not self.state.stack:
            raise ExecutionError("RETURN without GOSUB")
        
        self.state.current_line = self.state.stack.pop()

class NextCommand(CommandBase):
    """Implements the NEXT command."""
    
    def execute(self, args: str) -> None:
        """Execute the NEXT command."""
        var_name = args.strip()
        
        if not var_name:
            raise ParserError("Missing variable name in NEXT command")
        
        if var_name not in self.state.loops:
            raise ExecutionError(f"NEXT without FOR: {var_name}")
        
        line_num, end_value, step_value = self.state.loops[var_name]
        current_value = self.state.variables[var_name] + step_value
        self.state.variables[var_name] = current_value
        
        # Check if the loop should continue
        should_continue = (step_value >= 0 and current_value <= end_value) or \
                         (step_value < 0 and current_value >= end_value)
        
        if should_continue:
            self.state.current_line = line_num
        else:
            del self.state.loops[var_name]

class WhileCommand(CommandBase):
    """Implements the WHILE command."""
    
    def execute(self, args: str) -> None:
        """Execute the WHILE command."""
        if not args:
            raise ParserError("Missing condition in WHILE command")
        
        # Evaluate the condition
        parser = ExpressionParser(args)
        condition = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = condition.accept(visitor)
        
        if not result:
            # Skip to the matching WEND
            current_line = self.state.current_line
            while_count = 1
            
            line_numbers = sorted(self.state.code.keys())
            current_index = line_numbers.index(current_line)
            
            for i in range(current_index + 1, len(line_numbers)):
                line_num = line_numbers[i]
                line = self.state.code[line_num].strip().upper()
                
                if line.startswith("WHILE "):
                    while_count += 1
                elif line == "WEND":
                    while_count -= 1
                    if while_count == 0:
                        self.state.current_line = line_num
                        break
            
            if while_count > 0:
                raise ExecutionError("WHILE without matching WEND")
        else:
            # Remember this WHILE for future reference
            self.state.whiles[str(self.state.current_line)] = (self.state.current_line, args)

class WendCommand(CommandBase):
    """Implements the WEND command."""
    
    def execute(self, args: str) -> None:
        """Execute the WEND command."""
        # Find the matching WHILE line
        while_line = -1
        condition = ""
        
        line_numbers = sorted(self.state.code.keys())
        current_index = line_numbers.index(self.state.current_line)
        
        while_count = 1
        for i in range(current_index - 1, -1, -1):
            line_num = line_numbers[i]
            line = self.state.code[line_num].strip().upper()
            
            if line == "WEND":
                while_count += 1
            elif line.startswith("WHILE "):
                while_count -= 1
                if while_count == 0:
                    while_line = line_num
                    condition = self.state.code[line_num][6:].strip()  # Extract condition
                    break
        
        if while_line == -1:
            raise ExecutionError("WEND without matching WHILE")
        
        # Re-evaluate the condition
        parser = ExpressionParser(condition)
        expr = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = expr.accept(visitor)
        
        if result:
            # Continue the loop
            self.state.current_line = while_line
        # else continue to the next line

class EndCommand(CommandBase):
    """Implements the END command."""
    
    def execute(self, args: str) -> None:
        """Execute the END command."""
        self.state.current_line = 0  # End execution

class StopCommand(CommandBase):
    """Implements the STOP command."""
    
    def execute(self, args: str) -> None:
        """Execute the STOP command."""
        self.state.paused = True
        print("Program paused. Type CONT to continue.")

class RemCommand(CommandBase):
    """Implements the REM command (remarks/comments)."""
    
    def execute(self, args: str) -> None:
        """Execute the REM command."""
        # Comments are ignored during execution
        pass

class ClsCommand(CommandBase):
    """Implements the CLS (clear screen) command."""
    
    def execute(self, args: str) -> None:
        """Execute the CLS command."""
        print("\033[2J\033[H", end="")  # ANSI clear screen sequence

class ListCommand(CommandBase):
    """Implements the LIST command."""
    
    def execute(self, args: str) -> None:
        """Execute the LIST command."""
        # Parse arguments for optional line range
        start_line = 0
        end_line = float('inf')
        
        if args:
            parts = args.split("-")
            if len(parts) == 1:
                try:
                    start_line = int(parts[0].strip())
                    end_line = start_line
                except ValueError:
                    raise ParserError("Invalid line number in LIST command")
            elif len(parts) == 2:
                try:
                    if parts[0].strip():
                        start_line = int(parts[0].strip())
                    if parts[1].strip():
                        end_line = int(parts[1].strip())
                except ValueError:
                    raise ParserError("Invalid line number in LIST command")
        
        # Display code in line number order
        for line_num in sorted(self.state.code.keys()):
            if line_num >= start_line and line_num <= end_line:
                print(f"{line_num} {self.state.code[line_num]}")

class RunCommand(CommandBase):
    """Implements the RUN command."""
    
    def execute(self, args: str) -> None:
        """Execute the RUN command."""
        # Reset variables but keep the code
        self.state.variables = {Constants.LINE_NUMBER_VARIABLE: Constants.DEFAULT_START_LINE}
        self.state.stack = []
        self.state.loops = {}
        self.state.whiles = {}
        self.state.paused = False
        
        # Start execution from the first line
        if self.state.code:
            self.state.current_line = min(self.state.code.keys())
        else:
            print("No code to run")

class NewCommand(CommandBase):
    """Implements the NEW command to clear all code."""
    
    def execute(self, args: str) -> None:
        """Execute the NEW command."""
        self.state.reset()
        print("Program cleared")

class SaveCommand(CommandBase):
    """Implements the SAVE command to save program to file."""
    
    def execute(self, args: str) -> None:
        """Execute the SAVE command."""
        filename = args.strip()
        if not filename:
            raise ParserError("Missing filename in SAVE command")
        
        try:
            with open(filename, 'w') as f:
                for line_num in sorted(self.state.code.keys()):
                    f.write(f"{line_num} {self.state.code[line_num]}\n")
            print(f"Program saved to {filename}")
        except Exception as e:
            raise ExecutionError(f"Error saving program: {str(e)}")

class LoadCommand(CommandBase):
    """Implements the LOAD command to load program from file."""
    
    def execute(self, args: str) -> None:
        """Execute the LOAD command."""
        filename = args.strip()
        if not filename:
            raise ParserError("Missing filename in LOAD command")
        
        try:
            self.state.reset()
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Parse line number and code
                        match = re.match(r'^\s*(\d+)\s+(.*)
class IfCommand(CommandBase):
    """Implements the IF command."""
    
    def execute(self, args: str) -> None:
        """Execute the IF command."""
        if not args:
            raise ParserError("Missing condition in IF command")
        
        # Split at THEN
        then_pos = args.upper().find("THEN")
        if then_pos == -1:
            raise ParserError("Missing THEN in IF command")
        
        condition_text = args[:then_pos].strip()
        then_clause = args[then_pos+4:].strip()
        
        if not condition_text or not then_clause:
            raise ParserError("Invalid IF-THEN statement")
        
        # Evaluate the condition
        parser = ExpressionParser(condition_text)
        condition = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = condition.accept(visitor)
        
        # Execute the THEN clause if the condition is true
        if result:
            # Check if it's a line number
            try:
                line_num = int(then_clause)
                if line_num in self.state.code:
                    self.state.current_line = line_num
                    return
                raise ExecutionError(f"Line {line_num} does not exist")
            except ValueError:
                # It's a command
                self._execute_command(then_clause)
    
    def _execute_command(self, command_text: str) -> None:
        """Execute a command in the THEN clause."""
        # Find the command name
        cmd_end = command_text.find(" ")
        if cmd_end == -1:
            cmd_name = command_text
            args = ""
        else:
            cmd_name = command_text[:cmd_end]
            args = command_text[cmd_end+1:]
        
        cmd_name = cmd_name.upper()
        
        # Create and execute the command
        if cmd_name == "PRINT":
            PrintCommand(self.state).execute(args)
        elif cmd_name == "LET":
            LetCommand(self.state).execute(args)
        elif cmd_name == "GOTO":
            GotoCommand(self.state).execute(args)
        elif cmd_name == "GOSUB":
            GosubCommand(self.state).execute(args)
        elif cmd_name == "RETURN":
            ReturnCommand(self.state).execute(args)
        elif cmd_name == "IF":
            IfCommand(self.state).execute(args)
        else:
            # Handle variable assignment without LET
            if "=" in command_text and not CommandRegistry.is_command(cmd_name):
                LetCommand(self.state).execute(command_text)
            else:
                raise ExecutionError(f"Unknown command in THEN clause: {cmd_name}")

class ForCommand(CommandBase):
    """Implements the FOR command."""
    
    def execute(self, args: str) -> None:
        """Execute the FOR command."""
        if not args:
            raise ParserError("Invalid FOR statement")
        
        # Extract parts: FOR var = start TO end [STEP step]
        to_pos = args.upper().find(" TO ")
        if to_pos == -1:
            raise ParserError("Missing TO in FOR statement")
        
        init_part = args[:to_pos].strip()
        end_part = args[to_pos+4:].strip()
        
        # Parse the init_part (var = start)
        eq_pos = init_part.find("=")
        if eq_pos == -1:
            raise ParserError("Missing = in FOR statement")
        
        var_name = init_part[:eq_pos].strip()
        start_expr = init_part[eq_pos+1:].strip()
        
        if not var_name or CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Invalid variable name in FOR: {var_name}")
        
        # Parse the end_part (end [STEP step])
        step_pos = end_part.upper().find(" STEP ")
        if step_pos == -1:
            end_expr = end_part
            step_expr = "1"  # Default step
        else:
            end_expr = end_part[:step_pos].strip()
            step_expr = end_part[step_pos+6:].strip()
        
        # Evaluate expressions
        visitor = EvaluationVisitor(self.state)
        
        parser = ExpressionParser(start_expr)
        start_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(end_expr)
        end_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(step_expr)
        step_value = parser.parse().accept(visitor)
        
        if not isinstance(start_value, (int, float)) or \
           not isinstance(end_value, (int, float)) or \
           not isinstance(step_value, (int, float)):
            raise ExecutionError("FOR requires numeric values")
        
        # Store the loop information
        self.state.variables[var_name] = start_value
        self.state.loops[var_name] = (self.state.current_line, end_value, step_value), line)
                        if match:
                            line_num = int(match.group(1))
                            code = match.group(2)
                            self.state.code[line_num] = code
                        else:
                            print(f"Warning: Invalid line format: {line}")
            print(f"Program loaded from {filename}")
        except Exception as e:
            raise ExecutionError(f"Error loading program: {str(e)}")

# Main Interpreter
class BasicInterpreter:
    """Main BASIC interpreter class."""
    
    def __init__(self):
        self.state = InterpreterState()
        init_registries()  # Initialize command and function registries
        self.command_handlers = self._init_command_handlers()
    
    def _init_command_handlers(self) -> Dict[str, CommandBase]:
        """Initialize command handlers."""
        return {
            "print": PrintCommand(self.state),
            "let": LetCommand(self.state),
            "input": InputCommand(self.state),
            "goto": GotoCommand(self.state),
            "gosub": GosubCommand(self.state),
            "return": ReturnCommand(self.state),
            "if": IfCommand(self.state),
            "for": ForCommand(self.state),
            "next": NextCommand(self.state),
            "while": WhileCommand(self.state),
            "wend": WendCommand(self.state),
            "end": EndCommand(self.state),
            "stop": StopCommand(self.state),
            "rem": RemCommand(self.state),
            "cls": ClsCommand(self.state),
            "list": ListCommand(self.state),
            "run": RunCommand(self.state),
            "new": NewCommand(self.state),
            "save": SaveCommand(self.state),
            "load": LoadCommand(self.state)
        }
    
    def add_line(self, line_text: str) -> None:
        """Add or replace a line in the program."""
        line_text = line_text.strip()
        if not line_text:
            return
        
        # Parse line number and code
        match = re.match(r'^\s*(\d+)\s*(.*)
class IfCommand(CommandBase):
    """Implements the IF command."""
    
    def execute(self, args: str) -> None:
        """Execute the IF command."""
        if not args:
            raise ParserError("Missing condition in IF command")
        
        # Split at THEN
        then_pos = args.upper().find("THEN")
        if then_pos == -1:
            raise ParserError("Missing THEN in IF command")
        
        condition_text = args[:then_pos].strip()
        then_clause = args[then_pos+4:].strip()
        
        if not condition_text or not then_clause:
            raise ParserError("Invalid IF-THEN statement")
        
        # Evaluate the condition
        parser = ExpressionParser(condition_text)
        condition = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = condition.accept(visitor)
        
        # Execute the THEN clause if the condition is true
        if result:
            # Check if it's a line number
            try:
                line_num = int(then_clause)
                if line_num in self.state.code:
                    self.state.current_line = line_num
                    return
                raise ExecutionError(f"Line {line_num} does not exist")
            except ValueError:
                # It's a command
                self._execute_command(then_clause)
    
    def _execute_command(self, command_text: str) -> None:
        """Execute a command in the THEN clause."""
        # Find the command name
        cmd_end = command_text.find(" ")
        if cmd_end == -1:
            cmd_name = command_text
            args = ""
        else:
            cmd_name = command_text[:cmd_end]
            args = command_text[cmd_end+1:]
        
        cmd_name = cmd_name.upper()
        
        # Create and execute the command
        if cmd_name == "PRINT":
            PrintCommand(self.state).execute(args)
        elif cmd_name == "LET":
            LetCommand(self.state).execute(args)
        elif cmd_name == "GOTO":
            GotoCommand(self.state).execute(args)
        elif cmd_name == "GOSUB":
            GosubCommand(self.state).execute(args)
        elif cmd_name == "RETURN":
            ReturnCommand(self.state).execute(args)
        elif cmd_name == "IF":
            IfCommand(self.state).execute(args)
        else:
            # Handle variable assignment without LET
            if "=" in command_text and not CommandRegistry.is_command(cmd_name):
                LetCommand(self.state).execute(command_text)
            else:
                raise ExecutionError(f"Unknown command in THEN clause: {cmd_name}")

class ForCommand(CommandBase):
    """Implements the FOR command."""
    
    def execute(self, args: str) -> None:
        """Execute the FOR command."""
        if not args:
            raise ParserError("Invalid FOR statement")
        
        # Extract parts: FOR var = start TO end [STEP step]
        to_pos = args.upper().find(" TO ")
        if to_pos == -1:
            raise ParserError("Missing TO in FOR statement")
        
        init_part = args[:to_pos].strip()
        end_part = args[to_pos+4:].strip()
        
        # Parse the init_part (var = start)
        eq_pos = init_part.find("=")
        if eq_pos == -1:
            raise ParserError("Missing = in FOR statement")
        
        var_name = init_part[:eq_pos].strip()
        start_expr = init_part[eq_pos+1:].strip()
        
        if not var_name or CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Invalid variable name in FOR: {var_name}")
        
        # Parse the end_part (end [STEP step])
        step_pos = end_part.upper().find(" STEP ")
        if step_pos == -1:
            end_expr = end_part
            step_expr = "1"  # Default step
        else:
            end_expr = end_part[:step_pos].strip()
            step_expr = end_part[step_pos+6:].strip()
        
        # Evaluate expressions
        visitor = EvaluationVisitor(self.state)
        
        parser = ExpressionParser(start_expr)
        start_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(end_expr)
        end_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(step_expr)
        step_value = parser.parse().accept(visitor)
        
        if not isinstance(start_value, (int, float)) or \
           not isinstance(end_value, (int, float)) or \
           not isinstance(step_value, (int, float)):
            raise ExecutionError("FOR requires numeric values")
        
        # Store the loop information
        self.state.variables[var_name] = start_value
        self.state.loops[var_name] = (self.state.current_line, end_value, step_value), line_text)
        if not match:
            # If no line number, use auto-incrementing line numbers
            line_num = self.state.variables.get(Constants.LINE_NUMBER_VARIABLE, Constants.DEFAULT_START_LINE)
            code = line_text
            # Update for next auto-line
            self.state.variables[Constants.LINE_NUMBER_VARIABLE] = line_num + Constants.DEFAULT_INCREMENT
        else:
            line_num = int(match.group(1))
            code = match.group(2).strip()
        
        # If code is empty, delete the line
        if not code:
            if line_num in self.state.code:
                del self.state.code[line_num]
                print(f"Line {line_num} deleted")
            return
        
        # Otherwise add or replace the line
        self.state.code[line_num] = code
    
    def parse_execute_line(self, line_text: str) -> None:
        """Parse and execute a single line."""
        line_text = line_text.strip()
        if not line_text:
            return
        
        # Check if it's a line with a line number
        match = re.match(r'^\s*(\d+)\s+(.*)
class IfCommand(CommandBase):
    """Implements the IF command."""
    
    def execute(self, args: str) -> None:
        """Execute the IF command."""
        if not args:
            raise ParserError("Missing condition in IF command")
        
        # Split at THEN
        then_pos = args.upper().find("THEN")
        if then_pos == -1:
            raise ParserError("Missing THEN in IF command")
        
        condition_text = args[:then_pos].strip()
        then_clause = args[then_pos+4:].strip()
        
        if not condition_text or not then_clause:
            raise ParserError("Invalid IF-THEN statement")
        
        # Evaluate the condition
        parser = ExpressionParser(condition_text)
        condition = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = condition.accept(visitor)
        
        # Execute the THEN clause if the condition is true
        if result:
            # Check if it's a line number
            try:
                line_num = int(then_clause)
                if line_num in self.state.code:
                    self.state.current_line = line_num
                    return
                raise ExecutionError(f"Line {line_num} does not exist")
            except ValueError:
                # It's a command
                self._execute_command(then_clause)
    
    def _execute_command(self, command_text: str) -> None:
        """Execute a command in the THEN clause."""
        # Find the command name
        cmd_end = command_text.find(" ")
        if cmd_end == -1:
            cmd_name = command_text
            args = ""
        else:
            cmd_name = command_text[:cmd_end]
            args = command_text[cmd_end+1:]
        
        cmd_name = cmd_name.upper()
        
        # Create and execute the command
        if cmd_name == "PRINT":
            PrintCommand(self.state).execute(args)
        elif cmd_name == "LET":
            LetCommand(self.state).execute(args)
        elif cmd_name == "GOTO":
            GotoCommand(self.state).execute(args)
        elif cmd_name == "GOSUB":
            GosubCommand(self.state).execute(args)
        elif cmd_name == "RETURN":
            ReturnCommand(self.state).execute(args)
        elif cmd_name == "IF":
            IfCommand(self.state).execute(args)
        else:
            # Handle variable assignment without LET
            if "=" in command_text and not CommandRegistry.is_command(cmd_name):
                LetCommand(self.state).execute(command_text)
            else:
                raise ExecutionError(f"Unknown command in THEN clause: {cmd_name}")

class ForCommand(CommandBase):
    """Implements the FOR command."""
    
    def execute(self, args: str) -> None:
        """Execute the FOR command."""
        if not args:
            raise ParserError("Invalid FOR statement")
        
        # Extract parts: FOR var = start TO end [STEP step]
        to_pos = args.upper().find(" TO ")
        if to_pos == -1:
            raise ParserError("Missing TO in FOR statement")
        
        init_part = args[:to_pos].strip()
        end_part = args[to_pos+4:].strip()
        
        # Parse the init_part (var = start)
        eq_pos = init_part.find("=")
        if eq_pos == -1:
            raise ParserError("Missing = in FOR statement")
        
        var_name = init_part[:eq_pos].strip()
        start_expr = init_part[eq_pos+1:].strip()
        
        if not var_name or CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Invalid variable name in FOR: {var_name}")
        
        # Parse the end_part (end [STEP step])
        step_pos = end_part.upper().find(" STEP ")
        if step_pos == -1:
            end_expr = end_part
            step_expr = "1"  # Default step
        else:
            end_expr = end_part[:step_pos].strip()
            step_expr = end_part[step_pos+6:].strip()
        
        # Evaluate expressions
        visitor = EvaluationVisitor(self.state)
        
        parser = ExpressionParser(start_expr)
        start_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(end_expr)
        end_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(step_expr)
        step_value = parser.parse().accept(visitor)
        
        if not isinstance(start_value, (int, float)) or \
           not isinstance(end_value, (int, float)) or \
           not isinstance(step_value, (int, float)):
            raise ExecutionError("FOR requires numeric values")
        
        # Store the loop information
        self.state.variables[var_name] = start_value
        self.state.loops[var_name] = (self.state.current_line, end_value, step_value), line_text)
        if match:
            self.add_line(line_text)
            return
        
        # Otherwise, execute as immediate mode command
        self.execute_command(line_text)
    
    def execute_command(self, command_text: str) -> None:
        """Execute a command in immediate mode."""
        command_text = command_text.strip()
        if not command_text:
            return
        
        # Find the command name and arguments
        space_pos = command_text.find(" ")
        if space_pos == -1:
            cmd_name = command_text.lower()
            args = ""
        else:
            cmd_name = command_text[:space_pos].lower()
            args = command_text[space_pos+1:]
        
        # Handle variable assignment without LET
        if "=" in command_text and not CommandRegistry.is_command(cmd_name):
            cmd_name = "let"
            args = command_text
        
        # Execute the command
        if cmd_name in self.command_handlers:
            try:
                self.command_handlers[cmd_name].execute(args)
            except (ParserError, ExecutionError) as e:
                print(f"Error: {str(e)}")
        else:
            print(f"Unknown command: {cmd_name}")
    
    def run_program(self) -> None:
        """Run the stored program."""
        if not self.state.code:
            print("No program to run")
            return
        
        # Start from the first line
        line_numbers = sorted(self.state.code.keys())
        if not line_numbers:
            return
        
        self.state.current_line = line_numbers[0]
        self.state.paused = False
        
        # Execute until end or error
        try:
            while self.state.current_line > 0 and not self.state.paused:
                line_text = self.state.code.get(self.state.current_line, "")
                if not line_text:
                    # Line might have been deleted during execution
                    self.state.advance_line()
                    continue
                
                # Extract the command name and arguments
                space_pos = line_text.find(" ")
                if space_pos == -1:
                    cmd_name = line_text.lower()
                    args = ""
                else:
                    cmd_name = line_text[:space_pos].lower()
                    args = line_text[space_pos+1:]
                
                # Execute the command
                current_line = self.state.current_line  # Save for later comparison
                
                if cmd_name in self.command_handlers:
                    self.command_handlers[cmd_name].execute(args)
                else:
                    # Handle variable assignment without LET
                    if "=" in line_text and not CommandRegistry.is_command(cmd_name):
                        self.command_handlers["let"].execute(line_text)
                    else:
                        print(f"Unknown command on line {self.state.current_line}: {cmd_name}")
                        self.state.advance_line()
                
                # If the command didn't change the line number, move to next line
                if self.state.current_line == current_line:
                    self.state.advance_line()
        
        except (ParserError, ExecutionError) as e:
            print(f"Error on line {self.state.current_line}: {str(e)}")
            self.state.paused = True
    
    def repl(self) -> None:
        """Start a Read-Eval-Print Loop for interactive use."""
        print("BASIC Interpreter")
        print("Type a line number followed by code to add to program")
        print("Type a command to execute immediately")
        print("Type HELP for available commands")
        
        while True:
            try:
                line = input("> ").strip()
                if not line:
                    continue
                
                if line.lower() == "exit" or line.lower() == "quit":
                    break
                elif line.lower() == "run":
                    self.run_program()
                elif line.lower() == "help":
                    self._print_help()
                elif line.lower() == "cont":
                    if self.state.paused:
                        self.state.paused = False
                        self.run_program()
                    else:
                        print("Program not paused")
                else:
                    self.parse_execute_line(line)
            
            except KeyboardInterrupt:
                print("\nProgram interrupted")
                self.state.paused = True
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _print_help(self) -> None:
        """Print help information."""
        print("Available commands:")
        print("  PRINT <expr>        - Display values")
        print("  LET var = <expr>    - Assign value to variable")
        print("  INPUT [\"prompt\";] var - Get user input")
        print("  GOTO <line>         - Jump to a line")
        print("  GOSUB <line>        - Call a subroutine")
        print("  RETURN              - Return from subroutine")
        print("  IF <cond> THEN <cmd> - Conditional execution")
        print("  FOR var = <start> TO <end> [STEP <step>] - Start a loop")
        print("  NEXT var            - End a loop")
        print("  WHILE <cond>        - Start a while loop")
        print("  WEND                - End a while loop")
        print("  END                 - End the program")
        print("  STOP                - Pause the program")
        print("  REM <comment>       - Add a comment")
        print("  CLS                 - Clear the screen")
        print("  LIST [start-end]    - List program lines")
        print("  RUN                 - Run the program")
        print("  NEW                 - Clear the program")
        print("  SAVE <filename>     - Save the program")
        print("  LOAD <filename>     - Load a program")
        print("  CONT                - Continue after STOP")
        print("  EXIT/QUIT           - Exit the interpreter")
        print("  HELP                - Show this help")

def main():
    """Main entry point."""
    interpreter = BasicInterpreter()
    
    # Check if a file was provided as argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                for line in f:
                    interpreter.add_line(line)
            print(f"Program loaded from {filename}")
            interpreter.run_program()
        except Exception as e:
            print(f"Error loading program: {str(e)}")
    
    # Start interactive mode
    interpreter.repl()

if __name__ == "__main__":
    main()
class IfCommand(CommandBase):
    """Implements the IF command."""
    
    def execute(self, args: str) -> None:
        """Execute the IF command."""
        if not args:
            raise ParserError("Missing condition in IF command")
        
        # Split at THEN
        then_pos = args.upper().find("THEN")
        if then_pos == -1:
            raise ParserError("Missing THEN in IF command")
        
        condition_text = args[:then_pos].strip()
        then_clause = args[then_pos+4:].strip()
        
        if not condition_text or not then_clause:
            raise ParserError("Invalid IF-THEN statement")
        
        # Evaluate the condition
        parser = ExpressionParser(condition_text)
        condition = parser.parse()
        visitor = EvaluationVisitor(self.state)
        result = condition.accept(visitor)
        
        # Execute the THEN clause if the condition is true
        if result:
            # Check if it's a line number
            try:
                line_num = int(then_clause)
                if line_num in self.state.code:
                    self.state.current_line = line_num
                    return
                raise ExecutionError(f"Line {line_num} does not exist")
            except ValueError:
                # It's a command
                self._execute_command(then_clause)
    
    def _execute_command(self, command_text: str) -> None:
        """Execute a command in the THEN clause."""
        # Find the command name
        cmd_end = command_text.find(" ")
        if cmd_end == -1:
            cmd_name = command_text
            args = ""
        else:
            cmd_name = command_text[:cmd_end]
            args = command_text[cmd_end+1:]
        
        cmd_name = cmd_name.upper()
        
        # Create and execute the command
        if cmd_name == "PRINT":
            PrintCommand(self.state).execute(args)
        elif cmd_name == "LET":
            LetCommand(self.state).execute(args)
        elif cmd_name == "GOTO":
            GotoCommand(self.state).execute(args)
        elif cmd_name == "GOSUB":
            GosubCommand(self.state).execute(args)
        elif cmd_name == "RETURN":
            ReturnCommand(self.state).execute(args)
        elif cmd_name == "IF":
            IfCommand(self.state).execute(args)
        else:
            # Handle variable assignment without LET
            if "=" in command_text and not CommandRegistry.is_command(cmd_name):
                LetCommand(self.state).execute(command_text)
            else:
                raise ExecutionError(f"Unknown command in THEN clause: {cmd_name}")

class ForCommand(CommandBase):
    """Implements the FOR command."""
    
    def execute(self, args: str) -> None:
        """Execute the FOR command."""
        if not args:
            raise ParserError("Invalid FOR statement")
        
        # Extract parts: FOR var = start TO end [STEP step]
        to_pos = args.upper().find(" TO ")
        if to_pos == -1:
            raise ParserError("Missing TO in FOR statement")
        
        init_part = args[:to_pos].strip()
        end_part = args[to_pos+4:].strip()
        
        # Parse the init_part (var = start)
        eq_pos = init_part.find("=")
        if eq_pos == -1:
            raise ParserError("Missing = in FOR statement")
        
        var_name = init_part[:eq_pos].strip()
        start_expr = init_part[eq_pos+1:].strip()
        
        if not var_name or CommandRegistry.is_reserved(var_name):
            raise ParserError(f"Invalid variable name in FOR: {var_name}")
        
        # Parse the end_part (end [STEP step])
        step_pos = end_part.upper().find(" STEP ")
        if step_pos == -1:
            end_expr = end_part
            step_expr = "1"  # Default step
        else:
            end_expr = end_part[:step_pos].strip()
            step_expr = end_part[step_pos+6:].strip()
        
        # Evaluate expressions
        visitor = EvaluationVisitor(self.state)
        
        parser = ExpressionParser(start_expr)
        start_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(end_expr)
        end_value = parser.parse().accept(visitor)
        
        parser = ExpressionParser(step_expr)
        step_value = parser.parse().accept(visitor)
        
        if not isinstance(start_value, (int, float)) or \
           not isinstance(end_value, (int, float)) or \
           not isinstance(step_value, (int, float)):
            raise ExecutionError("FOR requires numeric values")
        
        # Store the loop information
        self.state.variables[var_name] = start_value
        self.state.loops[var_name] = (self.state.current_line, end_value, step_value)