# -*- coding: utf-8 -*-
import sys
import re
import math
import random
from typing import Any, List, Tuple, Optional, Dict
from abc import ABC, abstractmethod

class InterpreterError(Exception):
    """Base exception for interpreter errors."""
    pass

class ParserError(InterpreterError):
    """Exception for parsing errors."""
    pass

class ExecutionError(InterpreterError):
    """Exception for execution errors."""
    pass

# State Management
class InterpreterState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.code: Dict[int, str] = {}
        self.variables: Dict[str, Any] = {"#": 10}  # Line number
        self.stack: List[int] = []
        self.loops: Dict[str, Tuple[int, float, float]] = {}
        self.whiles: Dict[str, Tuple[int, str]] = {}
        self.paused: bool = False

# Expression Handling
class Expression(ABC):
    @abstractmethod
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        pass

class NumberExpression(Expression):
    def __init__(self, value: float):
        self.value = value

    def accept(self, visitor: 'ExpressionVisitor') -> float:
        return visitor.visit_number(self)

class StringExpression(Expression):
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor: 'ExpressionVisitor') -> str:
        return visitor.visit_string(self)

class VariableExpression(Expression):
    def __init__(self, name: str):
        if CommandFactory.is_reserved(name):
            raise ParserError(f"Cannot use reserved name '{name}' as variable")
        self.name = name

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_variable(self)

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_binary(self)

class FunctionExpression(Expression):
    def __init__(self, name: str, args: List[Expression]):
        if not CommandFactory.is_reserved_function(name):
            raise ParserError(f"Unknown function: {name}")
        self.name = name
        self.args = args

    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_function(self)

class ExpressionVisitor(ABC):
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

        if expr.operator in ["+", "-", "*", "/"]:
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

        if expr.operator in ["=", "<>", "<", ">", "<=", ">="]:
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
            raise ExecutionError(f"Cannot compare {type(left).__name__} with {type(right).__name__}")

        raise ExecutionError(f"Unknown operator: {expr.operator}")

    def visit_function(self, expr: FunctionExpression) -> Any:
        args = [arg.accept(self) for arg in expr.args]
        name = expr.name.lower()

        try:
            if name == "sin":
                return math.sin(args[0]) if len(args) == 1 else math.sin(0)
            elif name == "cos":
                return math.cos(args[0]) if len(args) == 1 else math.cos(0)
            elif name == "tan":
                return math.tan(args[0]) if len(args) == 1 else math.tan(0)
            elif name == "atn":
                return math.atan(args[0]) if len(args) == 1 else math.atan(0)
            elif name == "abs":
                return abs(args[0]) if len(args) == 1 else 0
            elif name == "sqr":
                if len(args) == 1 and args[0] >= 0:
                    return math.sqrt(args[0])
                raise ExecutionError("Invalid argument for SQR")
            elif name == "log":
                if len(args) == 1 and args[0] > 0:
                    return math.log(args[0])
                raise ExecutionError("Invalid argument for LOG")
            elif name == "exp":
                return math.exp(args[0]) if len(args) == 1 else 0
            elif name == "int":
                return int(args[0]) if len(args) == 1 else 0
            elif name == "rnd":
                if len(args) == 0:
                    return random.random()
                if len(args) == 1 and isinstance(args[0], (int, float)):
                    random.seed(int(args[0]))
                    return random.random()
                raise ExecutionError("Invalid arguments for RND")
            elif name == "left":
                if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], (int, float)):
                    return args[0][:int(args[1])]
                raise ExecutionError("Invalid arguments for LEFT")
            elif name == "right":
                if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], (int, float)):
                    return args[0][-int(args[1]):]
                raise ExecutionError("Invalid arguments for RIGHT")
            elif name == "mid":
                if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], (int, float)):
                    start = int(args[1]) - 1
                    length = int(args[2]) if len(args) == 3 else len(args[0])
                    return args[0][start:start + length]
                raise ExecutionError("Invalid arguments for MID")
            elif name == "len":
                return len(args[0]) if len(args) == 1 and isinstance(args[0], str) else 0
            elif name == "str":
                return str(args[0]) if len(args) == 1 else ""
            elif name == "val":
                try:
                    return float(args[0]) if len(args) == 1 and isinstance(args[0], str) else 0
                except ValueError:
                    return 0
            elif name == "chr":
                return chr(int(args[0])) if len(args) == 1 and isinstance(args[0], (int, float)) else ""
            elif name == "asc":
                if len(args) == 1 and isinstance(args[0], str) and args[0]:
                    return ord(args[0][0])
                raise ExecutionError("Invalid arguments for ASC")
            raise ExecutionError(f"Unknown function: {name}")
        except Exception as e:
            raise ExecutionError(f"Error executing function {name}: {e}")

class ExpressionParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.pos = 0
        self.length = len(self.text)

    def parse(self) -> Expression:
        expr = self.parse_expression()
        self.skip_whitespace()
        if self.pos < self.length:
            raise ParserError(f"Unexpected characters after expression: '{self.text[self.pos:]}'")
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
            raise ParserError("Unexpected end of expression")

        char = self.text[self.pos]
        if char.isalpha() or char == "_":
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isalnum() or self.text[self.pos] in "_$"):
                self.pos += 1
            name = self.text[start:self.pos]

            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == '(':
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

        elif char.isdigit() or char == '.':
            start = self.pos
            while self.pos < self.length and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                self.pos += 1
            number_str = self.text[start:self.pos]
            try:
                return NumberExpression(float(number_str))
            except ValueError:
                raise ParserError(f"Invalid number format: {number_str}")

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

        elif char == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == ')':
                self.pos += 1
                return expr
            raise ParserError("Expected closing parenthesis")

        raise ParserError(f"Unexpected character: {char}")

# Command Handling
class Command(ABC):
    def __init__(self, state: InterpreterState):
        self.state = state

    @abstractmethod
    def execute(self, args: str) -> None:
        pass

    def parse_expression(self, expr: str) -> Any:
        parser = ExpressionParser(expr)
        expression = parser.parse()
        evaluator = EvaluationVisitor(self.state)
        return expression.accept(evaluator)

class PrintCommand(Command):
    def execute(self, args: str) -> None:
        if not args.strip():
            print()
            return

        trailing_semicolon = args.strip().endswith(";")
        args = args.rstrip(";").rstrip()
        parts = args.split(";")
        output = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith('"') and part.endswith('"'):
                output.append(part[1:-1])
                continue

            try:
                result = self.parse_expression(part)
                if isinstance(result, float) and result.is_integer():
                    output.append(str(int(result)))
                else:
                    output.append(str(result))
            except Exception as e:
                raise ExecutionError(f"Error evaluating '{part}': {e}")

        print("".join(output), end="" if trailing_semicolon else "\n")

class InputCommand(Command):
    def execute(self, args: str) -> None:
        parts = args.split(";", 1)
        prompt = "> "
        var_name = args.strip()

        if len(parts) > 1:
            prompt_text = parts[0].strip()
            var_name = parts[1].strip()
            try:
                prompt = str(self.parse_expression(prompt_text)) + " "
            except Exception as e:
                raise ExecutionError(f"Error in INPUT prompt: {e}")

        input_value = input(prompt).strip()
        try:
            if var_name.endswith("$"):
                self.state.variables[var_name] = input_value
            else:
                try:
                    self.state.variables[var_name] = float(input_value) if '.' in input_value else int(input_value)
                except ValueError:
                    self.state.variables[var_name] = input_value
        except Exception as e:
            raise ExecutionError(f"Error processing INPUT: {e}")

class LetCommand(Command):
    def execute(self, args: str) -> None:
        try:
            var, expr = args.split("=", 1)
            var = var.strip()
            expr = expr.strip()
            if CommandFactory.is_reserved(var):
                raise ParserError(f"Cannot assign to reserved word '{var}'")
            value = self.parse_expression(expr)
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            self.state.variables[var] = value
        except Exception as e:
            raise ExecutionError(f"Error in LET statement: {e}")

class IfCommand(Command):
    def execute(self, args: str) -> None:
        try:
            parts = re.split(r"then", args, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) != 2:
                raise ParserError("Invalid IF syntax: Missing 'THEN'")

            condition = parts[0].strip()
            rest = parts[1].strip()
            then_part = rest
            else_part = ""

            if "ELSE" in rest.upper():
                then_else = re.split(r"else", rest, maxsplit=1, flags=re.IGNORECASE)
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
        except Exception as e:
            raise ExecutionError(f"Error in IF statement: {e}")

class GotoCommand(Command):
    def execute(self, args: str) -> None:
        try:
            line_num = int(self.parse_expression(args))
            if line_num in self.state.code:
                self.state.variables["#"] = line_num
            else:
                raise ExecutionError(f"Line {line_num} does not exist")
        except Exception as e:
            raise ExecutionError(f"Error in GOTO statement: {e}")

class GosubCommand(Command):
    def execute(self, args: str) -> None:
        try:
            line_num = int(self.parse_expression(args))
            if line_num in self.state.code:
                self.state.stack.append(self.state.variables["#"] + 1)
                self.state.variables["#"] = line_num
            else:
                raise ExecutionError(f"Line {line_num} does not exist")
        except Exception as e:
            raise ExecutionError(f"Error in GOSUB statement: {e}")

class ReturnCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.stack:
            self.state.variables["#"] = self.state.stack.pop()
        else:
            raise ExecutionError("RETURN without GOSUB")

class ForCommand(Command):
    def execute(self, args: str) -> None:
        try:
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
            if not isinstance(start, (int, float)):
                raise ParserError("START must be numeric")

            limit = self.parse_expression(limit_expr)
            if not isinstance(limit, (int, float)):
                raise ParserError("LIMIT must be numeric")

            self.state.variables[var] = start
            current_line = self.state.variables["#"]
            next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), current_line)
            self.state.loops[var] = (next_line, limit, step)
        except Exception as e:
            raise ExecutionError(f"Error in FOR statement: {e}")

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

        if step > 0:
            continue_loop = current_value <= limit
        else:
            continue_loop = current_value >= limit

        if continue_loop:
            self.state.variables["#"] = start_line
        else:
            self.state.variables["#"] = next(
                (n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)
            del self.state.loops[var]

class WhileCommand(Command):
    def execute(self, args: str) -> None:
        try:
            if not args.strip():
                raise ParserError("WHILE requires a condition")

            condition = args.strip()
            loop_id = f"while_{self.state.variables['#']}"
            self.state.whiles[loop_id] = (self.state.variables["#"], condition)

            if not self.parse_expression(condition):
                self.skip_to_wend()
        except Exception as e:
            raise ExecutionError(f"Error in WHILE statement: {e}")

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

class WendCommand(Command):
    def execute(self, args: str) -> None:
        loop_id = next((id for id in sorted(self.state.whiles.keys(), reverse=True) if id.startswith("while_")), None)
        if not loop_id or loop_id not in self.state.whiles:
            raise ExecutionError("WEND without matching WHILE")

        start_line, condition = self.state.whiles[loop_id]
        if self.parse_expression(condition):
            self.state.variables["#"] = start_line
        else:
            del self.state.whiles[loop_id]
            self.state.variables["#"] = next(
                (n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)

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

        try:
            parts = [part.strip() for part in args.split("-") if part.strip()]
            if len(parts) == 1:
                start = int(self.parse_expression(parts[0]))
                return start, default_end
            elif len(parts) == 2:
                start = int(self.parse_expression(parts[0])) if parts[0] else default_start
                end = int(self.parse_expression(parts[1]))
                if start > end:
                    start, end = end, start
                return start, end
            raise ParserError("Invalid range format")
        except Exception as e:
            print(f"Error parsing range: {e}. Listing all lines.")
            return default_start, default_end

class RemCommand(Command):
    def execute(self, args: str) -> None:
        pass

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
        self.state.variables["#"] = next(
            (n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)

class SaveCommand(Command):
    def execute(self, args: str) -> None:
        try:
            filename = self.parse_filename(args)
            if not filename:
                raise ParserError("Filename must be a non-empty quoted string")
            if not filename.endswith(".bas"):
                filename += ".bas"
            with open(filename, "w") as file:
                for line_number in sorted(self.state.code.keys()):
                    file.write(f"{line_number} {self.state.code[line_number]}\n")
            print(f"Program saved to '{filename}'")
        except Exception as e:
            raise ExecutionError(f"Error saving program: {e}")

    def parse_filename(self, args: str) -> str:
        args = args.strip()
        if (args.startswith('"') and args.endswith('"')) or (args.startswith("'") and args.endswith("'")):
            return args[1:-1].strip()
        return ""

class LoadCommand(Command):
    def execute(self, args: str) -> None:
        try:
            filename = self.parse_filename(args)
            if not filename:
                raise ParserError("Filename must be a non-empty quoted string")
            if not filename.endswith(".bas"):
                filename += ".bas"
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
            print(f"Program loaded from '{filename}'")
        except FileNotFoundError:
            raise ExecutionError(f"File '{filename}' not found")
        except Exception as e:
            raise ExecutionError(f"Error loading program: {e}")

    def parse_filename(self, args: str) -> str:
        args = args.strip()
        if (args.startswith('"') and args.endswith('"')) or (args.startswith("'") and args.endswith("'")):
            return args[1:-1].strip()
        return ""

class ContinueCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.paused:
            print("Program is not paused.")
            return
        if self.state.variables["#"] not in self.state.code:
            print("No more lines to continue.")
            self.state.paused = False
            return
        print("Resuming program...")
        self.state.paused = False
        InterpreterEngine(self.state).run()

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
        default_start = 10
        default_increment = 10

        if not args.strip():
            return default_start, default_increment

        try:
            parts = [part.strip() for part in args.split(",")]
            if len(parts) == 1:
                start = int(parts[0])
                increment = default_increment
            elif len(parts) == 2:
                start = int(parts[0])
                increment = int(parts[1])
            else:
                raise ParserError("Invalid number of arguments")
            if start <= 0 or increment <= 0:
                raise ParserError("Start line and increment must be positive")
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

        if cmd in ["goto", "gosub"]:
            try:
                old_line = int(args.strip())
                if old_line in line_mapping:
                    return f"{cmd} {line_mapping[old_line]}"
                return line
            except ValueError:
                return line

        elif cmd == "if":
            match = re.search(r'\bTHEN\b\s*(\d+)', args, re.IGNORECASE)
            if match:
                old_line = int(match.group(1))
                if old_line in line_mapping:
                    return line.replace(match.group(1), str(line_mapping[old_line]))
            return line

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

        if lines_to_delete:
            print(f"Deleted {len(lines_to_delete)} line(s).")
        else:
            print("No lines found in the specified range.")

    def parse_range(self, args: str) -> Tuple[int, int]:
        default_start = min(self.state.code.keys(), default=1)
        default_end = max(self.state.code.keys(), default=1)

        if not args.strip():
            return default_start, default_end

        try:
            parts = [part.strip() for part in args.split("-") if part.strip()]
            if len(parts) == 1:
                start = int(self.parse_expression(parts[0]))
                return start, default_end
            elif len(parts) == 2:
                start = int(self.parse_expression(parts[0])) if parts[0] else default_start
                end = int(self.parse_expression(parts[1]))
                if start > end:
                    start, end = end, start
                return start, end
            raise ParserError("Invalid range format")
        except Exception as e:
            print(f"Error parsing range: {e}. No lines deleted.")
            return default_start, default_start

class RunCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            raise ExecutionError("No program loaded")

        start_line = min(self.state.code.keys())
        if args.strip():
            start_line = int(self.parse_expression(args))

        if start_line not in self.state.code:
            raise ExecutionError(f"Line {start_line} does not exist")

        self.state.variables["#"] = start_line
        InterpreterEngine(self.state).run()

class NewCommand(Command):
    def execute(self, args: str) -> None:
        self.state.reset()
        print("Program cleared.")

class CommandFactory:
    _reserved_functions = {
        "sin", "cos", "tan", "atn", "abs", "sqr", "log", "exp", "int", "rnd",
        "left", "right", "mid", "len", "str", "val", "chr", "asc"
    }
    _reserved_keywords = {
        "print", "input", "let", "if", "goto", "gosub", "return", "for", "next",
        "while", "wend", "list", "ren", "del", "run", "end", "stop", "bye",
        "continue", "save", "load", "new", "rem", "to", "step", "then", "else"
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
        "stop": StopCommand,
        "bye": ByeCommand,
        "continue": ContinueCommand,
        "save": SaveCommand,
        "load": LoadCommand,
        "new": NewCommand,
        "rem": RemCommand
    }

    @classmethod
    def create_command(cls, name: str, state: InterpreterState) -> Optional[Command]:
        name = name.lower()
        command_class = cls._commands.get(name)
        if command_class:
            return command_class(state)
        return None

    @classmethod
    def is_reserved_function(cls, name: str) -> bool:
        return name.lower() in cls._reserved_functions

    @classmethod
    def is_reserved_keyword(cls, name: str) -> bool:
        return name.lower() in cls._reserved_keywords

    @classmethod
    def is_reserved(cls, name: str) -> bool:
        return cls.is_reserved_function(name) or cls.is_reserved_keyword(name)

# Interpreter Engine
class InterpreterEngine:
    def __init__(self, state: InterpreterState):
        self.state = state

    def parse_line(self, line: str) -> Tuple[int, str]:
        parts = line.split(maxsplit=1)
        if not parts or not parts[0].isdigit():
            raise ParserError(f"Invalid line format: {line}")
        line_number = int(parts[0])
        code = parts[1] if len(parts) > 1 else ""
        return line_number, code

    def execute_line(self, line: str) -> None:
        statements = self.split_statements(line)
        for statement in statements:
            parts = statement.split(None, 1)
            cmd = parts[0].lower() if parts else ""
            args = parts[1] if len(parts) > 1 else ""

            command = CommandFactory.create_command(cmd, self.state)
            if command:
                command.execute(args)
            elif "=" in statement and not cmd.upper() == "IF":
                let_command = LetCommand(self.state)
                let_command.execute(statement)
            else:
                raise ExecutionError(f"Unknown command: {statement}")

    def split_statements(self, line: str) -> List[str]:
        statements = []
        current = []
        in_string = False
        quote_char = None
        i = 0

        while i < len(line):
            char = line[i]
            if char in ('"', "'") and not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char and in_string:
                in_string = False
                quote_char = None
            elif char == ':' and not in_string:
                statement = ''.join(current).strip()
                if statement:
                    statements.append(statement)
                current = []
                i += 1
                continue
            current.append(char)
            i += 1

        statement = ''.join(current).strip()
        if statement:
            statements.append(statement)
        return statements

    def run(self) -> None:
        try:
            while self.state.variables["#"] > 0 and not self.state.paused:
                current_line = self.state.variables["#"]
                if current_line not in self.state.code:
                    self.state.variables["#"] = next(
                        (n for n in sorted(self.state.code.keys()) if n > current_line), 0)
                    continue
                line = self.state.code[current_line]
                self.execute_line(line)
                if self.state.variables["#"] == current_line:
                    self.state.variables["#"] = next(
                        (n for n in sorted(self.state.code.keys()) if n > current_line), 0)
        except KeyboardInterrupt:
            print("Program interrupted")
            self.state.paused = True
            self.state.variables["#"] = next(
                (n for n in sorted(self.state.code.keys()) if n > self.state.variables["#"]), 0)

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
            print(f"Error: {e}")
            state.paused = True
    else:
        print("BASIC Interpreter. Type BYE to exit.")
        while True:
            try:
                line = input("> ").strip()
                if not line:
                    continue
                if line.lower() == "bye":
                    break
                if line[0].isdigit():
                    line_number, code = engine.parse_line(line)
                    state.code[line_number] = code
                else:
                    engine.execute_line(line)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()