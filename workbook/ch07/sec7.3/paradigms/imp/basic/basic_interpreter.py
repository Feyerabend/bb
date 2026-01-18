# basic_interpreter.py
import sys
import re
import math
import random
from typing import Any, List, Optional, Tuple
from abc import ABC, abstractmethod

DEBUG = True  # Keep debug enabled to verify fixes

def debug_print(*args, **kwargs):
    if DEBUG:
        print("DEBUG:", *args, **kwargs)

# --- Exceptions ---
class InterpreterError(Exception):
    pass

class ParserError(InterpreterError):
    pass

class ExecutionError(InterpreterError):
    pass

# --- State Management ---
class InterpreterState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.code = {}
        self.variables = {"#": 10}
        self.stack = []
        self.loops = {}
        self.whiles = {}
        self.paused = False

# --- Expression Handling ---
class Expression(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class NumberExpression(Expression):
    def __init__(self, value: float):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_number(self)
    
    def __str__(self):
        return str(self.value)

class StringExpression(Expression):
    def __init__(self, value: str):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_string(self)
    
    def __str__(self):
        return f'"{self.value}"'

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name
        if CommandFactory.is_reserved(name.rstrip('$')):
            raise ParserError(f"Cannot use reserved name '{name}' as variable")
    
    def accept(self, visitor):
        return visitor.visit_variable(self)
    
    def __str__(self):
        return self.name

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary(self)
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

class UnaryExpression(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary(self)
    
    def __str__(self):
        return f"({self.operator}{self.operand})"

class FunctionExpression(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    
    def accept(self, visitor):
        return visitor.visit_function(self)
    
    def __str__(self):
        return f"{self.name}({', '.join(str(arg) for arg in self.args)})"

class ExpressionVisitor(ABC):
    @abstractmethod
    def visit_number(self, expr: NumberExpression):
        pass
    
    @abstractmethod
    def visit_string(self, expr: StringExpression):
        pass
    
    @abstractmethod
    def visit_variable(self, expr: VariableExpression):
        pass
    
    @abstractmethod
    def visit_binary(self, expr: BinaryExpression):
        pass
    
    @abstractmethod
    def visit_unary(self, expr: UnaryExpression):
        pass
    
    @abstractmethod
    def visit_function(self, expr: FunctionExpression):
        pass

class EvaluationVisitor:
    def __init__(self, state: InterpreterState):
        self.state = state

    def visit_number(self, expr: NumberExpression) -> float:
        return expr.value
    
    def visit_string(self, expr: StringExpression) -> str:
        return expr.value
    
    def visit_variable(self, expr: VariableExpression) -> Any:
        debug_print(f"Retrieving variable: {expr.name}, value: {self.state.variables.get(expr.name)}")
        return self.state.variables.get(expr.name, "" if expr.name.endswith("$") else 0)
    
    def visit_binary(self, expr: BinaryExpression) -> Any:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        
        if expr.operator in ["+", "-", "*", "/"]:
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise ExecutionError(f"Arithmetic operator '{expr.operator}' requires numeric operands")
            return {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x / y if y != 0 else 0
            }[expr.operator](left, right)
        
        if expr.operator in ["=", "<>", "<", ">", "<=", ">="]:
            if isinstance(left, str) and isinstance(right, str) or \
               isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return {
                    "=": lambda x, y: 1 if x == y else 0,
                    "<>": lambda x, y: 1 if x != y else 0,
                    "<": lambda x, y: 1 if x < y else 0,
                    ">": lambda x, y: 1 if x > y else 0,
                    "<=": lambda x, y: 1 if x <= y else 0,
                    ">=": lambda x, y: 1 if x >= y else 0
                }[expr.operator](left, right)
            raise ExecutionError(f"Cannot compare {type(left).__name__} with {type(right).__name__}")
        
        raise ExecutionError(f"Unknown operator: {expr.operator}")
    
    def visit_unary(self, expr: UnaryExpression) -> float:
        operand = expr.operand.accept(self)
        if not isinstance(operand, (int, float)):
            raise ExecutionError(f"Unary operator '{expr.operator}' requires numeric operand")
        if expr.operator == "-":
            return -operand
        raise ExecutionError(f"Unknown unary operator: {expr.operator}")
    
    def visit_function(self, expr: FunctionExpression) -> Any:
        args = [arg.accept(self) for arg in expr.args]
        name = expr.name.lower()
        debug_print(f"Evaluating function: {name}, args: {args}")
        
        function_map = {
            "sin": lambda x: math.sin(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else math.sin(0),
            "cos": lambda x: math.cos(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else math.cos(0),
            "tan": lambda x: math.tan(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else math.tan(0),
            "atn": lambda x: math.atan(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else math.atan(0),
            "abs": lambda x: abs(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else 0,
            "sqr": lambda x: math.sqrt(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) and x[0] >= 0 else 0,
            "log": lambda x: math.log(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) and x[0] > 0 else 0,
            "exp": lambda x: math.exp(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else 0,
            "int": lambda x: int(x[0]) if len(x) == 1 and isinstance(x[0], (int, float)) else 0,
            "rnd": lambda x: random.random(),
            "left": lambda x: x[0][:int(x[1])] if len(x) == 2 and isinstance(x[0], str) and isinstance(x[1], (int, float)) else "",
            "right": lambda x: x[0][-int(x[1]):] if len(x) == 2 and isinstance(x[0], str) and isinstance(x[1], (int, float)) else "",
            "mid": lambda x: x[0][int(x[1])-1:int(x[1])-1+int(x[2])] if len(x) == 3 and isinstance(x[0], str) and isinstance(x[1], (int, float)) and isinstance(x[2], (int, float)) else "",
            "len": lambda x: len(x[0]) if len(x) == 1 and isinstance(x[0], str) else 0,
            "str": lambda x: str(x[0]) if len(x) == 1 else "",
            "val": lambda x: float(x[0]) if len(x) == 1 and isinstance(x[0], str) else 0,
            "chr": lambda x: chr(int(x[0])) if len(x) == 1 and isinstance(x[0], (int, float)) else "",
            "asc": lambda x: ord(x[0][0]) if len(x) == 1 and isinstance(x[0], str) and x[0] else 0
        }
        
        if name in function_map:
            try:
                return function_map[name](args)
            except (ValueError, TypeError) as e:
                raise ExecutionError(f"Invalid arguments for function {name}: {e}")
        raise ExecutionError(f"Unknown function: {name}")

class ExpressionParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.pos = 0
        self.length = len(self.text)
    
    def parse(self) -> Expression:
        expr = self.parse_expression()
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] != ':':
            debug_print(f"Warning: Unconsumed input: '{self.text[self.pos:]}'")
        return expr

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1
    
    def parse_expression(self) -> Expression:
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expression:
        left = self.parse_term()
        self.skip_whitespace()
        
        if self.pos < self.length:
            for op in ["<=", ">=", "<>", "=", "<", ">"]:
                if self.text[self.pos:self.pos+len(op)] == op:
                    self.pos += len(op)
                    right = self.parse_term()
                    return BinaryExpression(left, op, right)
        return left
    
    def parse_term(self) -> Expression:
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
        self.skip_whitespace()
        if self.pos >= self.length:
            return NumberExpression(0)
        
        char = self.text[self.pos]
        
        if char == '-':
            self.pos += 1
            operand = self.parse_primary()
            return UnaryExpression("-", operand)
        
        if char.isalpha() or char == "_":
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] in "_$"):
                self.pos += 1
            name = self.text[start:self.pos]
            
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == '(':
                if not CommandFactory.is_reserved_function(name):
                    raise ParserError(f"Unknown function: {name}")
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
                    return FunctionExpression(name, args)
                raise ParserError(f"Expected closing parenthesis at position {self.pos}")
            
            if CommandFactory.is_reserved_function(name):
                return FunctionExpression(name, [])
            return VariableExpression(name)
        
        elif char.isdigit() or char == '.':
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                self.pos += 1
            try:
                return NumberExpression(float(self.text[start:self.pos]))
            except ValueError:
                raise ParserError(f"Invalid number format: {self.text[start:self.pos]}")
        
        elif char == '"':
            self.pos += 1
            start = self.pos
            while self.pos < self.length and self.text[self.pos] != '"':
                if self.pos > 0 and self.text[self.pos-1] == '\\':
                    continue
                self.pos += 1
            if self.pos >= self.length:
                raise ParserError("Unterminated string literal")
            value = self.text[start:self.pos]
            self.pos += 1
            return StringExpression(value)
        
        elif char == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == ')':
                self.pos += 1
                return expr
            raise ParserError(f"Expected closing parenthesis at position {self.pos}")
        
        raise ParserError(f"Unexpected character at position {self.pos}: {char}")

    def parse_number(self) -> NumberExpression:
        n, i = 0, 0
        while i < len(self.text) and self.text[i].isdigit():
            n = n * 10 + int(self.text[i])
            i += 1
        self.text = self.text[i:].strip()
        return NumberExpression(n)

# --- Command Handling ---
class Command(ABC):
    def __init__(self, state: InterpreterState):
        self.state = state
    
    @abstractmethod
    def execute(self, args: str) -> None:
        pass

class ParsedCommand(Command):
    def execute(self, args: str) -> None:
        try:
            self.process(args)
        except Exception as e:
            print(f"Error in {self.__class__.__name__}: {e}")

    @abstractmethod
    def process(self, args: str) -> None:
        pass
    
    def parse_expression(self, expr: str) -> Any:
        debug_print(f"Parsing expression: {expr}")
        parser = ExpressionParser(expr)
        expression = parser.parse()
        evaluator = EvaluationVisitor(self.state)
        result = expression.accept(evaluator)
        debug_print(f"Evaluated {expr} to {result}")
        return result

class PrintCommand(ParsedCommand):
    def process(self, args: str) -> None:
        debug_print(f"Processing PRINT: {args}")
        if not args.strip():
            print()
            return
        
        trailing_semicolon = args.strip().endswith(";")
        args = args.rstrip(";").rstrip()
        output = []
        
        for part in args.split(";"):
            part = part.strip()
            if not part:
                continue
                
            if part == ",":
                output.append(" ")
                continue
                
            if part.upper().startswith("USING"):
                try:
                    _, format_str, expr = part.split(maxsplit=2)
                    format_str = format_str.strip('"\'')
                    result = self.parse_expression(expr)
                    if not isinstance(result, (int, float)):
                        raise ExecutionError("USING format requires numeric value")
                    output.append(self.format_using(result, format_str))
                    continue
                except Exception as e:
                    print(f"Error in USING clause: {e}")
                    return
                    
            if part.startswith(("'", '"')) and part.endswith(part[0]):
                output.append(part[1:-1])
                continue
                
            try:
                result = self.parse_expression(part)
                debug_print(f"PRINT output: {result} (type: {type(result)})")
                if isinstance(result, float):
                    if abs(result) < 1e-5:  # Relaxed threshold for small values
                        result = 0.0
                        output.append("0")
                    elif result.is_integer():
                        output.append(str(int(result)))
                    else:
                        formatted = f"{result:.6f}".rstrip("0").rstrip(".")
                        output.append(formatted if formatted else "0")
                else:
                    output.append(str(result) if result else "")
            except Exception as e:
                print(f"Error evaluating expression '{part}': {e}")
                return
        
        print("".join(output), end="" if trailing_semicolon else "\n")

    def format_using(self, value: float, format_str: str) -> str:
        format_map = {
            "#.##": "{:.2f}",
            "#.###": "{:.3f}",
            "#,###.##": "{:,.2f}"
        }
        if format_str in format_map:
            return format_map[format_str].format(value)
        raise ExecutionError(f"Unsupported format string: {format_str}")

class InputCommand(ParsedCommand):
    def process(self, args: str) -> None:
        parts = args.split(";", 1)
        prompt = "> "
        var_name = args.strip()
        
        if len(parts) > 1:
            prompt_text = parts[0].strip()
            var_name = parts[1].strip()
            prompt = str(self.parse_expression(prompt_text)) + " "
        
        input_value = input(prompt).strip()
        try:
            self.state.variables[var_name] = float(input_value) if '.' in input_value else int(input_value)
        except ValueError:
            self.state.variables[var_name] = input_value if var_name.endswith("$") else 0

class LetCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            var, expr = args.split("=", 1)
            var = var.strip()
            if CommandFactory.is_reserved(var.rstrip('$')):
                raise ParserError(f"Cannot assign to reserved word '{var}'")
            value = self.parse_expression(expr.strip())
            debug_print(f"Assigning {var} = {value}")
            self.state.variables[var] = value
        except ValueError:
            raise ParserError(f"Invalid LET syntax: {args}")

class IfCommand(ParsedCommand):
    def process(self, args: str) -> None:
        parts = re.split(r"\bTHEN\b", args, flags=re.IGNORECASE)
        if len(parts) != 2:
            raise ParserError("Invalid IF syntax: Missing 'THEN'")
            
        condition = parts[0].strip()
        rest = parts[1].strip()
        
        then_part = rest
        else_part = ""
        if "ELSE" in rest.upper():
            then_else = re.split(r"\bELSE\b", rest, flags=re.IGNORECASE)
            then_part = then_else[0].strip()
            else_part = then_else[1].strip()
        
        condition_value = self.parse_expression(condition)
        engine = InterpreterEngine(self.state)
        
        if condition_value != 0:
            if then_part.isdigit():
                self.state.variables["#"] = int(then_part)
            else:
                engine.execute_line(then_part)
        elif else_part:
            if else_part.isdigit():
                self.state.variables["#"] = int(else_part)
            else:
                engine.execute_line(else_part)

class GotoCommand(ParsedCommand):
    def process(self, args: str) -> None:
        line_num = int(self.parse_expression(args.strip()))
        if line_num in self.state.code:
            self.state.variables["#"] = line_num
        else:
            raise ExecutionError(f"Line {line_num} does not exist")

class GosubCommand(ParsedCommand):
    def process(self, args: str) -> None:
        line_num = int(self.parse_expression(args.strip()))
        if line_num in self.state.code:
            self.state.stack.append(self.state.variables["#"] + 1)
            self.state.variables["#"] = line_num
        else:
            raise ExecutionError(f"Line {line_num} does not exist")

class ReturnCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.stack:
            self.state.variables["#"] = self.state.stack.pop()
        else:
            raise ExecutionError("RETURN without GOSUB")

class ForCommand(ParsedCommand):
    def process(self, args: str) -> None:
        parts = args.split("=", 1)
        if len(parts) != 2:
            raise ParserError("Invalid FOR syntax: Missing '='")
        
        var = parts[0].strip()
        if not var.isalnum():
            raise ParserError(f"Invalid loop variable: {var}")
        
        rest = parts[1].strip()
        to_parts = rest.split("TO", 1)
        if len(to_parts) != 2:
            raise ParserError("Invalid FOR syntax: Missing 'TO'")
        
        start_expr = to_parts[0].strip()
        rest = to_parts[1].strip()
        
        step = 1
        limit_expr = rest
        if "STEP" in rest.upper():
            step_parts = rest.split("STEP", 1)
            limit_expr = step_parts[0].strip()
            step = self.parse_expression(step_parts[1].strip())
            if not isinstance(step, (int, float)):
                raise ParserError("STEP must be numeric")
        
        start = self.parse_expression(start_expr)
        limit = self.parse_expression(limit_expr)
        if not isinstance(start, (int, float)) or not isinstance(limit, (int, float)):
            raise ParserError("START and LIMIT must be numeric")
        
        self.state.variables[var] = start
        current_line = self.state.variables["#"]
        next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), current_line)
        self.state.loops[var] = (next_line, limit, step)

class NextCommand(Command):
    def execute(self, args: str) -> None:
        var = args.strip()
        if not var:
            raise ExecutionError("NEXT requires a variable name")
        
        if var not in self.state.loops:
            raise ExecutionError(f"No matching FOR loop for variable '{var}'")
        
        start_line, limit, step = self.state.loops[var]
        current_value = self.state.variables.get(var, 0)
        current_value += step
        self.state.variables[var] = current_value
        
        if step > 0 and current_value <= limit or step < 0 and current_value >= limit:
            self.state.variables["#"] = start_line
        else:
            self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)
            del self.state.loops[var]

class WhileCommand(ParsedCommand):
    def process(self, args: str) -> None:
        if not args.strip():
            raise ParserError("WHILE requires a condition")
        
        condition = args.strip()
        loop_id = f"while_{self.state.variables['#']}"
        self.state.whiles[loop_id] = (self.state.variables["#"], condition)
        
        if not self.parse_expression(condition):
            self.skip_to_wend()

    def skip_to_wend(self):
        current_line = self.state.variables["#"]
        wend_count = 1
        
        for line_num in sorted(self.state.code.keys()):
            if line_num <= current_line:
                continue
                
            line = self.state.code[line_num].strip().upper()
            if line.startswith("WHILE"):
                wend_count += 1
            elif line.startswith("WEND"):
                wend_count -= 1
                if wend_count == 0:
                    self.state.variables["#"] = line_num + 1
                    return
        
        raise ExecutionError("No matching WEND for WHILE")

class WendCommand(ParsedCommand):
    def process(self, args: str) -> None:
        loop_id = next((id for id in sorted(self.state.whiles.keys(), reverse=True) if id.startswith("while_")), None)
        
        if loop_id and loop_id in self.state.whiles:
            start_line, condition = self.state.whiles[loop_id]
            if self.parse_expression(condition):
                self.state.variables["#"] = start_line
            else:
                del self.state.whiles[loop_id]
                self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)
        else:
            raise ExecutionError("WEND without matching WHILE")

class ListCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program loaded.")
            return
            
        start_line, end_line = self.parse_range(args)
        for line_num, line_code in sorted(self.state.code.items()):
            if start_line <= line_num <= end_line:
                print(f"{line_num:3} {line_code}")

    def parse_range(self, args: str) -> Tuple[int, int]:
        default_start = min(self.state.code.keys(), default=1)
        default_end = max(self.state.code.keys(), default=1)
        
        if not args.strip():
            return default_start, default_end
            
        parts = [part.strip() for part in args.strip().split("-") if part.strip()]
        try:
            if len(parts) == 1:
                start = int(self.parse_expression(parts[0]))
                return start, default_end
            elif len(parts) == 2:
                start = int(self.parse_expression(parts[0])) if parts[0] else default_start
                end = int(self.parse_expression(parts[1]))
                return min(start, end), max(start, end)
            raise ParserError("Invalid range format")
        except Exception as e:
            print(f"Error parsing range: {e}. Listing all lines.")
            return default_start, default_end

class RenumberCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program to renumber.")
            return
            
        start_line, increment = self.parse_args(args)
        old_lines = sorted(self.state.code.keys())
        new_code = {}
        line_mapping = {}
        
        for i, old_line in enumerate(old_lines):
            new_line = start_line + i * increment
            line_mapping[old_line] = new_line
            new_code[new_line] = self.state.code[old_line]
        
        for new_line in new_code:
            new_code[new_line] = self.update_line_references(new_code[new_line], line_mapping)
        
        self.state.code.clear()
        self.state.code.update(new_code)
        print("Program renumbered successfully.")

    def parse_args(self, args: str) -> Tuple[int, int]:
        default_start, default_increment = 10, 10
        if not args.strip():
            return default_start, default_increment
            
        try:
            parts = [part.strip() for part in args.split(",")]
            start = int(parts[0]) if parts else default_start
            increment = int(parts[1]) if len(parts) > 1 else default_increment
            if start <= 0 or increment <= 0:
                raise ValueError("Start line and increment must be positive")
            return start, increment
        except Exception as e:
            print(f"Error parsing RENUMBER arguments: {e}. Using defaults ({default_start}, {default_increment})")
            return default_start, default_increment

    def update_line_references(self, line: str, line_mapping: dict) -> str:
        parts = line.split(None, 1)
        if not parts:
            return line
            
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ["goto", "gosub"] and args.strip().isdigit():
            old_line = int(args.strip())
            if old_line in line_mapping:
                return f"{cmd} {line_mapping[old_line]}"
            print(f"Warning: Referenced line {old_line} in {cmd} does not exist.")
        
        elif cmd == "if":
            match = re.search(r'\bTHEN\b\s*(\d+)', args, re.IGNORECASE)
            if match:
                old_line = int(match.group(1))
                if old_line in line_mapping:
                    return line.replace(match.group(1), str(line_mapping[old_line]))
                print(f"Warning: Referenced line {old_line} in IF...THEN does not exist.")
        
        return line

class DeleteCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program loaded.")
            return
            
        start_line, end_line = self.parse_range(args)
        lines_to_delete = [line_num for line_num in self.state.code if start_line <= line_num <= end_line]
        
        for line_num in lines_to_delete:
            del self.state.code[line_num]
            
        print(f"Deleted {len(lines_to_delete)} line(s)." if lines_to_delete else "No lines found in the specified range.")

    def parse_range(self, args: str) -> Tuple[int, int]:
        default_start = min(self.state.code.keys(), default=1)
        default_end = max(self.state.code.keys(), default=1)
        
        if not args.strip():
            return default_start, default_end
            
        parts = [part.strip() for part in args.strip().split("-") if part.strip()]
        try:
            if len(parts) == 1:
                start = int(self.parse_expression(parts[0]))
                return start, default_end
            elif len(parts) == 2:
                start = int(self.parse_expression(parts[0])) if parts[0] else default_start
                end = int(self.parse_expression(parts[1]))
                return min(start, end), max(start, end)
            raise ParserError("Invalid range format")
        except Exception as e:
            print(f"Error parsing range: {e}. No lines deleted.")
            return default_start, default_start

class RunCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program loaded!")
            return
            
        start_line = min(self.state.code.keys()) if not args.strip() else int(self.parse_expression(args.strip()))
        if start_line not in self.state.code:
            raise ExecutionError(f"Line {start_line} does not exist")
            
        self.state.variables["#"] = start_line
        InterpreterEngine(self.state).run()

class EndCommand(Command):
    def execute(self, args: str) -> None:
        self.state.variables["#"] = 0

class ByeCommand(Command):
    def execute(self, args: str) -> None:
        sys.exit(0)

class StopCommand(Command):
    def execute(self, args: str) -> None:
        print("Program paused.")
        self.state.paused = True
        current_line = self.state.variables["#"]
        self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)

class ContinueCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.paused:
            if self.state.variables["#"] == 0 or self.state.variables["#"] not in self.state.code:
                print("No more lines to continue.")
                self.state.paused = False
                return
            print("Resuming program...")
            self.state.paused = False
            InterpreterEngine(self.state).run()
        else:
            print("Program is not paused.")

class SaveCommand(Command):
    def execute(self, args: str) -> None:
        filename = self.parse_filename(args)
        if not filename:
            raise ParserError("Filename must be a non-empty quoted string")
            
        if not filename.endswith(".bas"):
            filename += ".bas"
            
        try:
            with open(filename, "w") as file:
                for line_number in sorted(self.state.code.keys()):
                    file.write(f"{line_number} {self.state.code[line_number]}\n")
            print(f"Program saved to '{filename}'")
        except Exception as e:
            raise ExecutionError(f"Error saving program: {e}")

    def parse_filename(self, args: str) -> str:
        args = args.strip()
        if args.startswith(("'", '"')) and args.endswith(args[0]):
            return args[1:-1].strip()
        return ""

class LoadCommand(Command):
    def execute(self, args: str) -> None:
        filename = self.parse_filename(args)
        if not filename:
            raise ParserError("Filename must be a non-empty quoted string")
            
        if not filename.endswith(".bas"):
            filename += ".bas"
            
        try:
            self.state.code.clear()
            engine = InterpreterEngine(self.state)
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        line_number, line_code = engine.parse_line(line)
                        if line_number <= 0:
                            raise ParserError(f"Invalid line number: {line_number}")
                        self.state.code[line_number] = line_code
            print(f"Program loaded from '{filename}'" if self.state.code else f"Warning: No valid program lines loaded from '{filename}'")
        except FileNotFoundError:
            raise ExecutionError(f"File '{filename}' not found")
        except Exception as e:
            raise ExecutionError(f"Error loading program: {e}")

    def parse_filename(self, args: str) -> str:
        args = args.strip()
        if args.startswith(("'", '"')) and args.endswith(args[0]):
            return args[1:-1].strip()
        return ""

class NewCommand(Command):
    def execute(self, args: str) -> None:
        self.state.reset()
        print("Program cleared.")

class RemCommand(Command):
    def execute(self, args: str) -> None:
        pass

class CommandFactory:
    _reserved_functions = {
        "sin", "cos", "tan", "atn", "abs", "sqr", "log", "exp", "int", "rnd",
        "left", "right", "mid", "len", "str", "val", "chr", "asc"
    }
    _reserved_keywords = {
        "print", "input", "let", "if", "goto", "gosub", "return", "for", "next",
        "while", "wend", "list", "ren", "del", "run", "end", "stop", "bye", "continue",
        "save", "load", "new", "rem", "to", "step", "then", "else", "using"
    }
    
    _commands = {
        "print": PrintCommand,
        "input": InputCommand,
        "let": LetCommand,
        "if": IfCommand,
        "goto": GotoCommand,
        "gosub": GosubCommand,
        "return": ReturnCommand,
        "for": ForCommand,
        "next": NextCommand,
        "while": WhileCommand,
        "wend": WendCommand,
        "list": ListCommand,
        "ren": RenumberCommand,
        "del": DeleteCommand,
        "run": RunCommand,
        "end": EndCommand,
        "bye": ByeCommand,
        "stop": StopCommand,
        "continue": ContinueCommand,
        "save": SaveCommand,
        "load": LoadCommand,
        "new": NewCommand,
        "rem": RemCommand
    }
    
    @classmethod
    def create_command(cls, name: str, state: InterpreterState) -> Optional[Command]:
        return cls._commands.get(name.lower(), lambda x: None)(state)
    
    @classmethod
    def is_reserved_function(cls, name: str) -> bool:
        return name.lower() in cls._reserved_functions
    
    @classmethod
    def is_reserved_keyword(cls, name: str) -> bool:
        return name.lower() in cls._reserved_keywords
    
    @classmethod
    def is_reserved(cls, name: str) -> bool:
        return cls.is_reserved_function(name) or cls.is_reserved_keyword(name)

# --- Core Engine ---
class InterpreterEngine:
    def __init__(self, state: InterpreterState):
        self.state = state
    
    def parse_line(self, line: str) -> Tuple[int, str]:
        line_number, *code_parts = line.split(maxsplit=1)
        return int(line_number), code_parts[0] if code_parts else ""
    
    def execute_line(self, line: str) -> None:
        debug_print(f"Executing line: {line}")
        for statement in split_statements(line.strip()):
            if not statement:
                continue
                
            parts = statement.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            command = CommandFactory.create_command(cmd, self.state)
            if command:
                debug_print(f"Executing command: {cmd}, args: {args}")
                command.execute(args)
            elif "=" in statement and not statement.upper().startswith("IF"):
                debug_print(f"Implicit LET: {statement}")
                LetCommand(self.state).execute(statement)
            else:
                print(f"Syntax error: Unknown command '{statement}'")
    
    def run(self) -> None:
        try:
            while self.state.variables["#"] > 0 and not self.state.paused:
                current_line = self.state.variables["#"]
                if current_line not in self.state.code:
                    self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
                    continue
                    
                self.execute_line(self.state.code[current_line])
                if self.state.variables["#"] == current_line:
                    self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
        except KeyboardInterrupt:
            print("Program paused.")
            self.state.paused = True
            self.state.variables["#"] = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)

def split_statements(line: str) -> List[str]:
    statements = []
    current = []
    in_string = False
    quote_char = None
    
    for i, char in enumerate(line):
        if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
            in_string = not in_string
            quote_char = char if in_string else None
            current.append(char)
        elif char == ':' and not in_string:
            statement = ''.join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)
    
    if current:
        statements.append(''.join(current).strip())
    return statements

def main():
    state = InterpreterState()
    engine = InterpreterEngine(state)
    
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        line_number, line_code = engine.parse_line(line)
                        state.code[line_number] = line_code
            engine.run()
        except Exception as e:
            print(f"Error loading/running program: {e}")
        while state.paused:
            try:
                line = input("> ").strip()
                if line:
                    engine.execute_line(line)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)
    else:
        print("BASIC Interpreter. Type BYE to exit.")
        while True:
            try:
                line = input("> ").strip()
                if not line:
                    continue
                
                parser = ExpressionParser(line)
                try:
                    lineno = int(parser.parse_number().accept(EvaluationVisitor(state)))
                    state.code[lineno] = parser.text
                except (ValueError, ParserError):
                    engine.execute_line(line)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)

if __name__ == "__main__":
    main()