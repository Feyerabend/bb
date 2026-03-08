#!/usr/bin/env python3
"""
BASIC Interpreter with Graphics — HTTP Server version
Simulates Pimoroni DisplayPack 2.0 (320x240) display for Raspberry Pi Pico 2W
"""

import sys
import re
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading


# Exception hierarchy

class InterpreterError(Exception):
    """Base for all interpreter errors."""

class ParserError(InterpreterError):
    """Raised when the expression parser encounters invalid syntax."""

class ExecutionError(InterpreterError):
    """Raised during program execution (type mismatches, missing lines, etc.)."""

class StackError(ExecutionError):
    """Raised on GOSUB/RETURN stack violations."""

class UndefinedLineError(ExecutionError):
    """Raised when a GOTO/GOSUB targets a non-existent line."""


# Graphics command buffer
class GraphicsBuffer:
    """Stores graphics commands to send to client"""
    def __init__(self):
        self.commands = []
        
    def add_command(self, cmd_type: str, **kwargs):
        """Add a graphics command"""
        self.commands.append({"type": cmd_type, **kwargs})
        
    def clear(self):
        """Clear all commands"""
        self.commands = []
        
    def get_json(self):
        """Get commands as JSON"""
        return json.dumps(self.commands)


# Interpreter state  (singleton, but properly reset-able)

_GOSUB_STACK_LIMIT = 256
_LOOP_DEPTH_LIMIT  = 128

class InterpreterState:
    """
    Holds all mutable interpreter state.

    The singleton is created once; call ``InterpreterState.reset()`` to
    clear it between programs without touching the singleton machinery.
    """

    _instance: Optional["InterpreterState"] = None

    def __new__(cls) -> "InterpreterState":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self) -> None:
        self.code:      Dict[int, str]            = {}
        self.variables: Dict[str, Any]            = {"#": 10}
        self.stack:     List[int]                 = []
        self.loops:     Dict[str, Tuple[int, Any]] = {}
        self.graphics:  GraphicsBuffer            = GraphicsBuffer()
        self.output:    List[str]                 = []  # Console output buffer

    def reset(self) -> None:
        """Wipe all program state (code, variables, stack, loops)."""
        self._init()



# AST node hierarchy

class Expression(ABC):
    """Abstract base for all AST expression nodes."""

    @abstractmethod
    def accept(self, visitor: "ExpressionVisitor") -> Any:
        ...


class NumberExpression(Expression):
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def accept(self, visitor: "ExpressionVisitor") -> Any:
        return visitor.visit_number(self)


class StringExpression(Expression):
    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value

    def accept(self, visitor: "ExpressionVisitor") -> Any:
        return visitor.visit_string(self)


class VariableExpression(Expression):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, visitor: "ExpressionVisitor") -> Any:
        return visitor.visit_variable(self)


class BinaryExpression(Expression):
    __slots__ = ("left", "operator", "right")

    def __init__(
        self,
        left: Expression,
        operator: str,
        right: Expression,
    ) -> None:
        self.left     = left
        self.operator = operator
        self.right    = right

    def accept(self, visitor: "ExpressionVisitor") -> Any:
        return visitor.visit_binary(self)


class FunctionExpression(Expression):
    __slots__ = ("name", "args")

    def __init__(self, name: str, args: List[Expression]) -> None:
        self.name = name
        self.args = args

    def accept(self, visitor: "ExpressionVisitor") -> Any:
        return visitor.visit_function(self)


# Visitor interface + concrete evaluation visitor

class ExpressionVisitor(ABC):
    """Visitor interface — one method per concrete Expression subclass."""

    @abstractmethod
    def visit_number(self, expr: NumberExpression) -> Any: ...

    @abstractmethod
    def visit_string(self, expr: StringExpression) -> Any: ...

    @abstractmethod
    def visit_variable(self, expr: VariableExpression) -> Any: ...

    @abstractmethod
    def visit_binary(self, expr: BinaryExpression) -> Any: ...

    @abstractmethod
    def visit_function(self, expr: FunctionExpression) -> Any: ...


class EvaluationVisitor(ExpressionVisitor):
    """Walks the AST and returns the computed value of each node."""

    def __init__(self) -> None:
        self.state = InterpreterState()


    # - leaf nodes

    def visit_number(self, expr: NumberExpression) -> int:
        return expr.value

    def visit_string(self, expr: StringExpression) -> str:
        return expr.value

    def visit_variable(self, expr: VariableExpression) -> Any:
        name = expr.name
        if name not in self.state.variables:
            # Auto-initialise: string vars (ending with $) -> "", numeric -> 0
            self.state.variables[name] = "" if name.endswith("$") else 0
        return self.state.variables[name]


    # - binary operations

    def visit_binary(self, expr: BinaryExpression) -> Any:
        left  = expr.left.accept(self)
        right = expr.right.accept(self)

        # Coerce mixed string/number for concatenation with +
        if expr.operator == "+" and isinstance(left, str) != isinstance(right, str):
            left  = str(left)
            right = str(right)

        op = expr.operator
        try:
            if op == "+":
                return left + right
            if op == "-":
                return left - right       # type: ignore[operator]
            if op == "*":
                return left * right       # type: ignore[operator]
            if op == "/":
                if right == 0:
                    raise ExecutionError("Division by zero")
                return left / right       # type: ignore[operator]
            if op == "=":
                return 1 if left == right else 0
            if op == "<":
                return 1 if left < right else 0   # type: ignore[operator]
            if op == ">":
                return 1 if left > right else 0   # type: ignore[operator]
        except TypeError as exc:
            raise ExecutionError(
                f"Type error for operator '{op}' on "
                f"{type(left).__name__} and {type(right).__name__}: {exc}"
            ) from exc

        raise ExecutionError(f"Unknown operator: '{op}'")


    # - built-in functions

    def visit_function(self, expr: FunctionExpression) -> Any:
        args: List[Any] = [a.accept(self) for a in expr.args]
        name = expr.name

        if not args:
            raise ParserError(f"Function '{name}' requires at least one argument")

        s = str(args[0])

        try:
            if name == "LEFT":
                n = int(args[1]) if len(args) > 1 else 0
                return s[:n]
            if name == "RIGHT":
                n = int(args[1]) if len(args) > 1 else 0
                return s[-n:] if n else ""
            if name == "MID":
                start = int(args[1]) - 1 if len(args) > 1 else 0
                length = int(args[2]) if len(args) > 2 else len(s) - start
                return s[start: start + length]
            if name == "LEN":
                return len(s)
            if name == "STR":
                return str(args[0])
        except (IndexError, ValueError) as exc:
            raise ParserError(f"Error in function {name}: {exc}") from exc

        raise ParserError(f"Unknown function: '{name}'")



# Expression parser

class ExpressionParser:
    """
    Recursive-descent parser that produces an Expression AST.

    Grammar (simplified):
        expr   = term  { ('+' | '-' | '=' | '<' | '>') term }
        term   = factor { ('*' | '/') factor }
        factor = FUNC'$(' args ')' | '(' expr ')' | STRING | NUMBER | VARIABLE
    """

    def __init__(self, text: str) -> None:
        self.text = text.strip()
        self.pos  = 0

    def parse(self) -> Expression:
        if not self.text:
            raise ParserError("Empty expression")
        try:
            expr = self._expr()
            if self.pos < len(self.text):
                raise ParserError(f"Unexpected text after expression: '{self.text[self.pos:]}'")
            return expr
        except IndexError:
            raise ParserError("Unexpected end of input")
        except Exception as e:
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Parse error: {e}")

    def _expr(self) -> Expression:
        try:
            left = self._term()
            while self._peek_char() in ("+", "-", "=", "<", ">"):
                op = self._next_char()
                right = self._term()
                left = BinaryExpression(left, op, right)
            return left
        except Exception as e:
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Error in expression: {e}")

    def _term(self) -> Expression:
        try:
            left = self._factor()
            while self._peek_char() in ("*", "/"):
                op = self._next_char()
                right = self._factor()
                left = BinaryExpression(left, op, right)
            return left
        except Exception as e:
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Error in term: {e}")

    def _factor(self) -> Expression:
        try:
            self._skip_whitespace()

            if not self._peek_char():
                raise ParserError("Unexpected end of expression")

            if self._peek_char() == "(":
                self._next_char()
                expr = self._expr()
                if self._next_char() != ")":
                    raise ParserError("Expected ')'")
                return expr

            if self._peek_char() == '"':
                return self._parse_string()

            # Try number first (before name, since digits are alphanumeric)
            if self._peek_char().isdigit() or (self._peek_char() == "-" and len(self.text) > self.pos + 1 and self.text[self.pos + 1].isdigit()):
                return self.parse_number()

            # Try function or variable
            name = self._parse_name()
            if name and self._peek_char() == "(":
                # It's a function call
                self._next_char()
                args = self._parse_args()
                if self._next_char() != ")":
                    raise ParserError("Expected ')' after function arguments")
                # Strip trailing '$' from function name
                func_name = name.rstrip("$").upper()
                return FunctionExpression(func_name, args)

            if name:
                return VariableExpression(name)

            # If nothing else, error
            raise ParserError(f"Unexpected character: '{self._peek_char()}'")
        except Exception as e:
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Error in factor: {e}")

    def _parse_string(self) -> StringExpression:
        self._next_char()  # skip opening quote
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1
        if self.pos >= len(self.text):
            raise ParserError("Unterminated string literal")
        value = self.text[start:self.pos]
        self._next_char()  # skip closing quote
        return StringExpression(value)

    def _parse_name(self) -> str:
        self._skip_whitespace()
        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] in ("_", "$", "#")):
            self.pos += 1
        return self.text[start:self.pos]

    def parse_number(self) -> NumberExpression:
        """Parse a number (exposed for line number parsing)."""
        self._skip_whitespace()
        start = self.pos
        if self._peek_char() == "-":
            self.pos += 1
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        if start == self.pos:
            raise ParserError(f"Expected a number at position {self.pos}")
        try:
            value = int(self.text[start:self.pos])
        except ValueError as exc:
            raise ParserError(f"Invalid number: '{self.text[start:self.pos]}'") from exc
        return NumberExpression(value)

    def _parse_args(self) -> List[Expression]:
        args = []
        self._skip_whitespace()
        if self._peek_char() == ")":
            return args

        args.append(self._expr())
        while self._peek_char() == ",":
            self._next_char()
            args.append(self._expr())
        return args

    def _peek_char(self) -> str:
        try:
            self._skip_whitespace()
            return self.text[self.pos] if self.pos < len(self.text) else ""
        except Exception:
            return ""

    def _next_char(self) -> str:
        try:
            self._skip_whitespace()
            if self.pos >= len(self.text):
                raise ParserError("Unexpected end of expression")
            ch = self.text[self.pos]
            self.pos += 1
            return ch
        except Exception as e:
            if isinstance(e, ParserError):
                raise
            raise ParserError(f"Parse error: {e}")

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in (" ", "\t"):
            self.pos += 1


# Command hierarchy

class Command(ABC):
    def __init__(self) -> None:
        self.state = InterpreterState()

    @abstractmethod
    def execute(self, args: str) -> None:
        ...


class PrintCommand(Command):
    def execute(self, args: str) -> None:
        if not args.strip():
            print()
            return
            
        # Split by both semicolons and commas
        parts = []
        current = ""
        in_quotes = False
        
        try:
            for char in args:
                if char == '"':
                    in_quotes = not in_quotes
                    current += char
                elif (char == ';' or char == ',') and not in_quotes:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                else:
                    current += char
            
            # Don't forget the last part
            if current.strip():
                parts.append(current.strip())
            
            values = []
            for p in parts:
                if not p:
                    continue
                try:
                    tree = ExpressionParser(p).parse()
                    val = tree.accept(EvaluationVisitor())
                    values.append(str(val))
                except Exception as e:
                    # If parsing fails, try to use the string as-is
                    values.append(p)
                    
            output = " ".join(values)
            self.state.output.append(output)
            print(output)
        except Exception as e:
            raise ExecutionError(f"PRINT error: {e}")


class InputCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("INPUT requires a variable name")
            # For server mode, we'll just auto-assign a default value
            # In real implementation, this would wait for user input from client
            m = re.match(r'(?:"([^"]+)"\s*;\s*)?(\w+\$?)', args.strip())
            if not m:
                raise ParserError("INPUT syntax: [\"prompt\";] variable")
            
            prompt = m.group(1) or ""
            varname = m.group(2)
            
            # Auto-assign defaults for server mode
            if varname.endswith("$"):
                self.state.variables[varname] = "test"
            else:
                self.state.variables[varname] = 0
            
            output = f"{prompt} [{varname}=={self.state.variables[varname]}]"
            self.state.output.append(output)
            print(output)
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"INPUT error: {e}")


class LetCommand(Command):
    def execute(self, args: str) -> None:
        try:
            m = re.match(r"(\w+\$?)\s*=\s*(.+)", args.strip())
            if not m:
                raise ParserError(f"Invalid LET syntax - use: variable = expression")
            varname = m.group(1)
            expr = m.group(2)
            tree = ExpressionParser(expr).parse()
            value = tree.accept(EvaluationVisitor())
            self.state.variables[varname] = value
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"LET error: {e}")


class GotoCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("GOTO requires a line number")
            tree = ExpressionParser(args).parse()
            target = tree.accept(EvaluationVisitor())
            if target not in self.state.code:
                raise UndefinedLineError(f"Line {target} does not exist")
            self.state.variables["#"] = target
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError, UndefinedLineError)):
                raise
            raise ExecutionError(f"GOTO error: {e}")


class GosubCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("GOSUB requires a line number")
            if len(self.state.stack) >= _GOSUB_STACK_LIMIT:
                raise StackError(f"GOSUB stack overflow (limit {_GOSUB_STACK_LIMIT})")
            tree = ExpressionParser(args).parse()
            target = tree.accept(EvaluationVisitor())
            if target not in self.state.code:
                raise UndefinedLineError(f"GOSUB to undefined line {target}")
            self.state.stack.append(self.state.variables["#"])
            self.state.variables["#"] = target
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError, StackError, UndefinedLineError)):
                raise
            raise ExecutionError(f"GOSUB error: {e}")


class ReturnCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.stack:
            raise StackError("RETURN without GOSUB")
        self.state.variables["#"] = self.state.stack.pop()


class ForCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("FOR requires: variable = start TO end")
            m = re.match(r"(\w+)\s*=\s*(.+?)\s+to\s+(.+)", args, re.IGNORECASE)
            if not m:
                raise ParserError("FOR syntax: variable = start TO end")
            varname = m.group(1)
            start_expr = m.group(2)
            end_expr = m.group(3)

            start_val = ExpressionParser(start_expr).parse().accept(EvaluationVisitor())
            end_val = ExpressionParser(end_expr).parse().accept(EvaluationVisitor())

            if len(self.state.loops) >= _LOOP_DEPTH_LIMIT:
                raise ExecutionError(f"FOR/NEXT nesting limit ({_LOOP_DEPTH_LIMIT}) exceeded")

            self.state.variables[varname] = start_val
            self.state.loops[varname] = (self.state.variables["#"], end_val)
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"FOR error: {e}")


class NextCommand(Command):
    def execute(self, args: str) -> None:
        try:
            varname = args.strip()
            if not varname:
                raise ParserError("NEXT requires a variable name")
            if varname not in self.state.loops:
                raise ExecutionError(f"NEXT without FOR: '{varname}'")

            loop_start, loop_end = self.state.loops[varname]
            self.state.variables[varname] += 1

            if self.state.variables[varname] <= loop_end:
                self.state.variables["#"] = loop_start
            else:
                del self.state.loops[varname]
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"NEXT error: {e}")


class IfCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("IF requires: condition THEN statement")
            m = re.match(r"(.+?)\s+then\s+(.+)", args, re.IGNORECASE)
            if not m:
                raise ParserError("IF syntax: condition THEN statement")
            cond_expr = m.group(1)
            then_stmt = m.group(2).strip()

            tree = ExpressionParser(cond_expr).parse()
            result = tree.accept(EvaluationVisitor())

            if result:
                InterpreterEngine().execute_line(then_stmt)
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"IF error: {e}")


class ListCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            output = "[LIST] No program stored."
            self.state.output.append(output)
            print(output)
            return
        for lineno in sorted(self.state.code):
            output = f"{lineno} {self.state.code[lineno]}"
            self.state.output.append(output)
            print(output)


class RenumberCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("[REN] No program to renumber.")
            return
        old_lines = sorted(self.state.code)
        mapping = {old: (i + 1) * 10 for i, old in enumerate(old_lines)}
        new_code = {}
        for old, new in mapping.items():
            line = self.state.code[old]
            line = self._replace_line_refs(line, mapping)
            new_code[new] = line
        self.state.code = new_code
        print(f"[REN] Renumbered {len(new_code)} lines.")

    @staticmethod
    def _replace_line_refs(line: str, mapping: Dict[int, int]) -> str:
        for pattern in [r"\bGOTO\s+(\d+)", r"\bGOSUB\s+(\d+)"]:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                old = int(m.group(1))
                new = mapping.get(old, old)
                if old not in mapping:
                    print(f"[REN] Warning: line {old} referenced not found")
                line = line.replace(m.group(1), str(new), 1)
        if re.search(r"\bIF\b.+\bTHEN\s+(\d+)", line, re.IGNORECASE):
            m = re.search(r"\bTHEN\s+(\d+)", line, re.IGNORECASE)
            if m:
                old = int(m.group(1))
                new = mapping.get(old, old)
                if old not in mapping:
                    print(f"[REN] Warning: line {old} referenced in IF..THEN not found")
                return line.replace(m.group(1), str(new), 1)
        return line


class RunCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program loaded.")
            return
        print("Running program... (Press Ctrl+C to stop)")
        self.state.variables["#"] = min(self.state.code)
        # Use the engine's run method which already handles KeyboardInterrupt
        from sys import modules
        # Find the InterpreterEngine instance that has this state
        engine = InterpreterEngine()
        engine.state = self.state
        engine.run()


class HelpCommand(Command):
    _TEXT = """\
Commands
  PRINT expr [, expr ...]   Print values (comma or semicolon-separated)
  INPUT [prompt ;] var      Read input into var (string vars end with $)
  LET var = expr            Assign a value  (LET is optional: var = expr works)
  IF cond THEN stmt         Conditional single-line branch
  GOTO lineno               Jump to a line number
  GOSUB lineno              Call subroutine at lineno  (stack limit: 256)
  RETURN                    Return from subroutine
  FOR var = start TO end    Begin a counted loop  (depth limit: 128)
  NEXT var                  End of counted loop
  RUN                       Run the stored program from the first line
  LIST                      Print the stored program
  REN                       Renumber stored lines in steps of 10
  STOP / END                Halt program execution
  BYE                       Exit the interpreter
  HELP                      Show this message

Graphics Commands (DisplayPack 2.0: 320x240)
  CLS [color]               Clear screen (color: 0-65535, default black)
  PIXEL x, y, color         Draw pixel at (x,y)
  LINE x1, y1, x2, y2, col  Draw line
  RECT x, y, w, h, col      Draw rectangle outline
  RECTF x, y, w, h, col     Draw filled rectangle
  CIRCLE x, y, r, col       Draw circle outline
  CIRCLEF x, y, r, col      Draw filled circle
  TEXT x, y, "text", col    Draw text at position

Built-in functions
  LEFT$(s, n)               First n characters of s
  RIGHT$(s, n)              Last n characters of s
  MID$(s, i, n)             n characters starting at position i (1-based)
  LEN$(s)                   Length of s
  STR$(x)                   Convert number x to string

Operators  + - * /  =  <  >
  + on strings performs concatenation.

Tips
  Lines that start with a number are stored in the program.
  Lines without a number are executed immediately.\
"""

    def execute(self, args: str) -> None:
        for line in self._TEXT.split('\n'):
            self.state.output.append(line)
            print(line)


class ByeCommand(Command):
    def execute(self, args: str) -> None:
        print("Goodbye!")
        # Set a flag that the REPL will check
        self.state.variables["__SHUTDOWN__"] = True


class StopCommand(Command):
    def execute(self, args: str) -> None:
        print("Program stopped.")
        self.state.variables["#"] = 0


# Graphics commands

class ClsCommand(Command):
    """Clear screen"""
    def execute(self, args: str) -> None:
        try:
            color = 0  # Default black
            if args.strip():
                tree = ExpressionParser(args).parse()
                color = tree.accept(EvaluationVisitor())
            
            # Clear the entire graphics buffer and start fresh
            self.state.graphics.clear()
            self.state.graphics.add_command("cls", color=int(color))
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"CLS error: {e}")


class PixelCommand(Command):
    """Draw a pixel"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("PIXEL requires arguments: x, y, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 3:
            raise ParserError("PIXEL requires 3 arguments: x, y, color")
        
        try:
            x = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("pixel", x=int(x), y=int(y), color=int(color))
        except Exception as e:
            raise ExecutionError(f"PIXEL error: {e}")


class LineCommand(Command):
    """Draw a line"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("LINE requires arguments: x1, y1, x2, y2, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 5:
            raise ParserError("LINE requires 5 arguments: x1, y1, x2, y2, color")
        
        try:
            x1 = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y1 = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            x2 = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            y2 = ExpressionParser(parts[3]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[4]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("line", x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2), color=int(color))
        except Exception as e:
            raise ExecutionError(f"LINE error: {e}")


class RectCommand(Command):
    """Draw rectangle outline"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("RECT requires arguments: x, y, w, h, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 5:
            raise ParserError("RECT requires 5 arguments: x, y, w, h, color")
        
        try:
            x = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            w = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            h = ExpressionParser(parts[3]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[4]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("rect", x=int(x), y=int(y), w=int(w), h=int(h), color=int(color), filled=False)
        except Exception as e:
            raise ExecutionError(f"RECT error: {e}")


class RectFCommand(Command):
    """Draw filled rectangle"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("RECTF requires arguments: x, y, w, h, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 5:
            raise ParserError("RECTF requires 5 arguments: x, y, w, h, color")
        
        try:
            x = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            w = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            h = ExpressionParser(parts[3]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[4]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("rect", x=int(x), y=int(y), w=int(w), h=int(h), color=int(color), filled=True)
        except Exception as e:
            raise ExecutionError(f"RECTF error: {e}")


class CircleCommand(Command):
    """Draw circle outline"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("CIRCLE requires arguments: x, y, r, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 4:
            raise ParserError("CIRCLE requires 4 arguments: x, y, r, color")
        
        try:
            x = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            r = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[3]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("circle", x=int(x), y=int(y), r=int(r), color=int(color), filled=False)
        except Exception as e:
            raise ExecutionError(f"CIRCLE error: {e}")


class CircleFCommand(Command):
    """Draw filled circle"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError("CIRCLEF requires arguments: x, y, r, color")
            
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 4:
            raise ParserError("CIRCLEF requires 4 arguments: x, y, r, color")
        
        try:
            x = ExpressionParser(parts[0]).parse().accept(EvaluationVisitor())
            y = ExpressionParser(parts[1]).parse().accept(EvaluationVisitor())
            r = ExpressionParser(parts[2]).parse().accept(EvaluationVisitor())
            color = ExpressionParser(parts[3]).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("circle", x=int(x), y=int(y), r=int(r), color=int(color), filled=True)
        except Exception as e:
            raise ExecutionError(f"CIRCLEF error: {e}")


class TextCommand(Command):
    """Draw text"""
    def execute(self, args: str) -> None:
        if not args.strip():
            raise ParserError('TEXT requires arguments: x, y, "text", color')
            
        # Parse: x, y, "text", color
        try:
            m = re.match(r'([^,]+),\s*([^,]+),\s*"([^"]*)",\s*(.+)', args)
            if not m:
                raise ParserError('TEXT format: x, y, "text", color')
            
            x = ExpressionParser(m.group(1)).parse().accept(EvaluationVisitor())
            y = ExpressionParser(m.group(2)).parse().accept(EvaluationVisitor())
            text = m.group(3)
            color = ExpressionParser(m.group(4)).parse().accept(EvaluationVisitor())
            
            self.state.graphics.add_command("text", x=int(x), y=int(y), text=text, color=int(color))
        except Exception as e:
            raise ExecutionError(f"TEXT error: {e}")


class RemCommand(Command):
    """REM - Remark/Comment - does nothing"""
    def execute(self, args: str) -> None:
        # Comments do nothing
        pass


class WaitCommand(Command):
    """WAIT - Pause execution for milliseconds"""
    def execute(self, args: str) -> None:
        import time
        try:
            if not args.strip():
                # Default wait 100ms
                ms = 100
            else:
                tree = ExpressionParser(args).parse()
                ms = tree.accept(EvaluationVisitor())
            
            # Sleep for the specified milliseconds
            time.sleep(int(ms) / 1000.0)
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"WAIT error: {e}")


class SaveCommand(Command):
    """SAVE - Save current program to a file"""
    def execute(self, args: str) -> None:
        try:
            filename = args.strip()
            if not filename:
                raise ParserError("SAVE requires a filename")
            
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'
            
            if not self.state.code:
                print("No program to save.")
                return
            
            with open(filename, 'w') as f:
                for lineno in sorted(self.state.code):
                    f.write(f"{lineno} {self.state.code[lineno]}\n")
            
            print(f"Program saved to {filename}")
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"SAVE error: {e}")


class LoadCommand(Command):
    """LOAD - Load a program from a file"""
    def execute(self, args: str) -> None:
        try:
            filename = args.strip()
            if not filename:
                raise ParserError("LOAD requires a filename")
            
            # Add .bas extension if not present
            if not filename.endswith('.bas'):
                filename += '.bas'
            
            # Clear current program
            self.state.code.clear()
            
            # Load from file
            engine = InterpreterEngine()
            engine.state = self.state
            engine.load_program(filename)
            
            print(f"Program loaded from {filename}")
            print(f"Loaded {len(self.state.code)} lines")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            if isinstance(e, (ParserError, ExecutionError)):
                raise
            raise ExecutionError(f"LOAD error: {e}")


# Command factory

class CommandFactory:
    _commands: Dict[str, Type[Command]] = {
        "print":   PrintCommand,
        "input":   InputCommand,
        "goto":    GotoCommand,
        "if":      IfCommand,
        "run":     RunCommand,
        "let":     LetCommand,
        "gosub":   GosubCommand,
        "return":  ReturnCommand,
        "for":     ForCommand,
        "next":    NextCommand,
        "list":    ListCommand,
        "ren":     RenumberCommand,
        "help":    HelpCommand,
        "bye":     ByeCommand,
        "stop":    StopCommand,
        "end":     StopCommand,
        "rem":     RemCommand,
        "wait":    WaitCommand,
        "save":    SaveCommand,
        "load":    LoadCommand,
        # Graphics commands
        "cls":     ClsCommand,
        "pixel":   PixelCommand,
        "line":    LineCommand,
        "rect":    RectCommand,
        "rectf":   RectFCommand,
        "circle":  CircleCommand,
        "circlef": CircleFCommand,
        "text":    TextCommand,
    }

    @classmethod
    def create_command(cls, name: str) -> Optional[Command]:
        return cls._commands[name.lower()]() if name.lower() in cls._commands else None

    @classmethod
    def register_command(cls, name: str, command_class: Type[Command]) -> None:
        cls._commands[name.lower()] = command_class


# Interpreter engine

_MAX_STEPS = 1_000_000  # hard cap to detect infinite loops


class InterpreterEngine:
    def __init__(self) -> None:
        self.state = InterpreterState()

    # - public interface

    def load_program(self, filename: str) -> None:
        """Load a BASIC program from a file."""
        try:
            with open(filename) as fh:
                for raw in fh:
                    raw = raw.strip()
                    if raw:
                        lineno, code = self._split_line(raw)
                        self.state.code[lineno] = code
        except OSError as exc:
            raise ExecutionError(f"Cannot open '{filename}': {exc}") from exc

    def execute_line(self, line: str) -> None:
        """Execute a single (already stripped) line of BASIC code."""
        line = line.strip()
        if not line:
            return

        try:
            parts = line.split(None, 1)
            cmd   = parts[0].lower()
            args  = parts[1] if len(parts) > 1 else ""

            command = CommandFactory.create_command(cmd)
            if command:
                command.execute(args)
            elif "=" in line:
                # Implicit LET:  X = expr
                CommandFactory.create_command("let").execute(line)  # type: ignore[union-attr]
            else:
                print(f"? Syntax error: Unknown command '{cmd}'")
        except ParserError as e:
            print(f"? Syntax error: {e}")
        except ExecutionError as e:
            print(f"? Error: {e}")
        except Exception as e:
            print(f"? Error: {e}")

    def run(self) -> None:
        """Run the loaded program from the first line."""
        if not self.state.code:
            print("[RUN] No program loaded.")
            return

        self.state.variables["#"] = min(self.state.code)
        steps = 0

        try:
            while self.state.variables["#"] > 0:
                steps += 1
                if steps > _MAX_STEPS:
                    print(f"[RUN] Execution limit ({_MAX_STEPS} steps) reached — possible infinite loop")
                    break

                pc = self.state.variables["#"]

                if pc not in self.state.code:
                    # Skip to the next defined line
                    nxt = next((n for n in sorted(self.state.code) if n > pc), 0)
                    self.state.variables["#"] = nxt
                    continue

                line = self.state.code[pc]
                try:
                    self.execute_line(line)
                except (ExecutionError, StackError, UndefinedLineError) as exc:
                    print(f"[ERROR at line {pc}] {exc}")
                    break

                # Advance PC only if the command itself didn't change it
                if self.state.variables["#"] == pc:
                    nxt = next((n for n in sorted(self.state.code) if n > pc), 0)
                    self.state.variables["#"] = nxt

        except KeyboardInterrupt:
            print(f"\n[BREAK] Program interrupted at line {self.state.variables['#']}")
            self.state.variables["#"] = 0  # halt cleanly
            # Don't re-raise - let the REPL continue

    def evaluate_expression(self, expr: str) -> Any:
        """Public helper to evaluate a single expression string."""
        try:
            tree = ExpressionParser(expr).parse()
            return tree.accept(EvaluationVisitor())
        except InterpreterError as exc:
            print(f"[EVAL] Error in '{expr}': {exc}")
            return 0

    # - private helpers

    @staticmethod
    def _split_line(line: str) -> Tuple[int, str]:
        head, *rest = line.split(maxsplit=1)
        try:
            return int(head), rest[0] if rest else ""
        except ValueError as exc:
            raise ParserError(f"Line number expected, got '{head}'") from exc



# REPL / file-load entry point

def _feed_line(engine: InterpreterEngine, raw: str) -> None:
    """
    Dispatch a line from the REPL or a file.

    Lines that start with a digit are treated as numbered program lines to
    store (or overwrite).  Everything else is an immediate command — RUN,
    LIST, PRINT, LET, etc. — and is executed straight away.
    """
    raw = raw.strip()
    if not raw:
        return

    # Check if it's a numbered line
    if raw[0].isdigit():
        # Numbered line: split off the line number and store the rest.
        parser = ExpressionParser(raw)
        try:
            lineno_expr = parser.parse_number()
            lineno      = lineno_expr.accept(EvaluationVisitor())
            # Store only the text AFTER the line number
            engine.state.code[lineno] = parser.text[parser.pos:].strip()
        except (ParserError, InterpreterError) as exc:
            print(f"? Syntax error: {exc}")
        except Exception as e:
            print(f"? Error storing line: {e}")
    else:
        # Immediate command: execute directly.
        engine.execute_line(raw)


# HTTP Server

class BASICHTTPHandler(BaseHTTPRequestHandler):
    engine = InterpreterEngine()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        """Serve the HTML client or graphics data"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read the client HTML - try current directory first
            html_content = None
            for path in ['client.html', 'display_client.html']:
                try:
                    with open(path, 'r') as f:
                        html_content = f.read()
                        break
                except FileNotFoundError:
                    continue
            
            if html_content:
                self.wfile.write(html_content.encode())
            else:
                # Fallback: serve embedded minimal client
                fallback_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>DisplayPack 2.0</title>
<style>body{background:#000;color:#0f0;font-family:monospace;text-align:center;padding:50px;}
canvas{background:#000;border:1px solid #333;image-rendering:pixelated;}</style></head>
<body><h1>DisplayPack 2.0 - 320x240</h1>
<canvas id="c" width="320" height="240"></canvas>
<p id="s">●</p>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d'),s=document.getElementById('s');
function rgb(col){const r=((col>>11)&0x1F)*255/31,g=((col>>5)&0x3F)*255/63,b=(col&0x1F)*255/31;
return`rgb(${Math.round(r)},${Math.round(g)},${Math.round(b)})`;}
function draw(cmds){if(!cmds)return;cmds.forEach(cmd=>{try{switch(cmd.type){
case 'cls':ctx.fillStyle=rgb(cmd.color||0);ctx.fillRect(0,0,320,240);break;
case 'pixel':ctx.fillStyle=rgb(cmd.color);ctx.fillRect(cmd.x,cmd.y,1,1);break;
case 'line':ctx.strokeStyle=rgb(cmd.color);ctx.beginPath();ctx.moveTo(cmd.x1,cmd.y1);ctx.lineTo(cmd.x2,cmd.y2);ctx.stroke();break;
case 'rect':ctx.fillStyle=rgb(cmd.color);ctx.strokeStyle=rgb(cmd.color);
if(cmd.filled)ctx.fillRect(cmd.x,cmd.y,cmd.w,cmd.h);else ctx.strokeRect(cmd.x,cmd.y,cmd.w,cmd.h);break;
case 'circle':ctx.fillStyle=rgb(cmd.color);ctx.strokeStyle=rgb(cmd.color);ctx.beginPath();ctx.arc(cmd.x,cmd.y,cmd.r,0,Math.PI*2);
if(cmd.filled)ctx.fill();else ctx.stroke();break;
case 'text':ctx.fillStyle=rgb(cmd.color);ctx.font='12px monospace';ctx.fillText(cmd.text,cmd.x,cmd.y);break;
}}catch(e){console.error(e);}});}
async function fetch_graphics(){try{const r=await fetch('/graphics'),d=await r.json();
if(d.graphics&&d.graphics.length>0){ctx.fillStyle='#000';ctx.fillRect(0,0,320,240);draw(d.graphics);}
s.style.color='#0f0';}catch(e){s.style.color='#f00';}}
fetch_graphics();setInterval(fetch_graphics,500);
</script></body></html>"""
                self.wfile.write(fallback_html.encode())
                print("Warning: client.html not found, serving embedded fallback client")
                
        elif self.path == '/graphics':
            # Return current graphics commands as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "graphics": self.engine.state.graphics.commands,
                "output": []  # Don't send output - that's in the REPL
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()


def repl_thread(engine, shutdown_event):
    """Run REPL in separate thread"""
    print("BASIC Interpreter REPL")
    print("Commands: HELP for help, BYE to quit, Ctrl+C to break running program")
    print("Graphics will be displayed in the web browser\n")
    
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print()   # newline after ^C, then back to prompt
            continue
        
        _feed_line(engine, line)
        
        # Check if BYE command was issued
        if engine.state.variables.get("__SHUTDOWN__"):
            shutdown_event.set()
            break


def main():
    """Start HTTP server and REPL"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='BASIC Interpreter with Graphics - DisplayPack 2.0 Simulator')
    parser.add_argument('program', nargs='?', help='BASIC program file to load')
    parser.add_argument('-r', '--run', action='store_true', help='Run the program immediately after loading')
    parser.add_argument('-p', '--port', type=int, default=8080, help='HTTP server port (default: 8080)')
    args = parser.parse_args()
    
    port = args.port
    
    print(f"BASIC Interpreter with Graphics - HTTP Server")
    print(f"DisplayPack 2.0 Simulator (320x240)")
    print(f"")
    print(f"Working directory: {os.getcwd()}")
    
    # Check for client.html
    if os.path.exists('client.html'):
        print(f"✓ client.html found")
    else:
        print(f"⚠ client.html not found - will use embedded fallback")
    
    print(f"")
    print(f"Web display: http://localhost:{port}")
    print(f"Open this URL in your browser to see the display")
    print(f"=" * 60)
    print()
    
    # Create shutdown event
    shutdown_event = threading.Event()
    
    # Start REPL in a separate thread
    engine = BASICHTTPHandler.engine
    
    # Load program file if specified
    if args.program:
        try:
            print(f"Loading program: {args.program}")
            engine.load_program(args.program)
            print(f"Program loaded successfully")
            if args.run:
                print("Running program...")
                print()
                engine.run()
                print()
        except Exception as e:
            print(f"Error loading program: {e}")
            print()
    
    repl = threading.Thread(target=repl_thread, args=(engine, shutdown_event), daemon=False)
    repl.start()
    
    # Start HTTP server in main thread
    server = HTTPServer(('', port), BASICHTTPHandler)
    
    def check_shutdown():
        """Check if shutdown was requested"""
        while not shutdown_event.is_set():
            shutdown_event.wait(0.5)
        server.shutdown()
    
    shutdown_checker = threading.Thread(target=check_shutdown, daemon=True)
    shutdown_checker.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.shutdown()
        print("Server shut down cleanly.")


if __name__ == "__main__":
    main()
