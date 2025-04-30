# -*- coding: utf-8 -*-
# bloated code .. refactor and separate
#!/usr/bin/env python3
import sys
import re
import math
import random
from typing import Any, List, Optional, Tuple
from abc import ABC, abstractmethod

DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print("DEBUG:", *args, **kwargs)

class InterpreterError(Exception):
    pass

class ParserError(InterpreterError):
    pass

class ExecutionError(InterpreterError):
    pass

class InterpreterState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InterpreterState, cls).__new__(cls)
            cls._instance.code = {}
            cls._instance.variables = {"#": 10}
            cls._instance.stack = []
            cls._instance.loops = {}
            cls._instance.whiles = {}
            cls._instance.paused = False
        return cls._instance
    
    def reset(self):
        self.code = {}
        self.variables = {"#": 10}
        self.stack = []
        self.loops = {}
        self.whiles = {}
        self.paused = False

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
        if CommandFactory.is_reserved_keyword(name):
            raise ParserError(f"Cannot use reserved keyword '{name}' as a variable name")
        if CommandFactory.is_reserved_function(name):
            raise ParserError(f"Cannot use function name '{name}' as a variable name")
    
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

class FunctionExpression(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    
    def accept(self, visitor):
        return visitor.visit_function(self)
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}({args_str})"

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
    def visit_function(self, expr: FunctionExpression):
        pass

class EvaluationVisitor:
    def __init__(self):
        self.state = InterpreterState()

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
                raise ValueError(f"Arithmetic operator '{expr.operator}' requires numeric operands")
            if expr.operator == "+":
                return left + right
            elif expr.operator == "-":
                return left - right
            elif expr.operator == "*":
                return left * right
            elif expr.operator == "/":
                return left / right if right != 0 else 0
        
        if expr.operator in ["=", "<>", "<", ">", "<=", ">="]:
            if isinstance(left, str) and isinstance(right, str):
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
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
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
                raise ValueError(f"Cannot compare {type(left).__name__} with {type(right).__name__}")
        
        raise ValueError(f"Unknown operator: {expr.operator}")
    
    def visit_function(self, expr: FunctionExpression) -> Any:
        args = [arg.accept(self) for arg in expr.args]
        
        name = expr.name.lower()
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
            return math.sqrt(args[0]) if len(args) == 1 and args[0] >= 0 else 0
        elif name == "log":
            return math.log(args[0]) if len(args) == 1 and args[0] > 0 else 0
        elif name == "exp":
            return math.exp(args[0]) if len(args) == 1 else 0
        elif name == "int":
            return int(args[0]) if len(args) == 1 else 0
        elif name == "rnd":
            if len(args) == 0:
                return random.random()
            elif len(args) == 1 and isinstance(args[0], (int, float)):
                random.seed(args[0])
                return random.random()
            return 0
        elif name == "left":
            return args[0][:int(args[1])] if len(args) == 2 and isinstance(args[0], str) else ""
        elif name == "right":
            return args[0][-int(args[1]):] if len(args) == 2 and isinstance(args[0], str) else ""
        elif name == "mid":
            start = int(args[1]) - 1
            length = int(args[2]) if len(args) == 3 else len(args[0])
            return args[0][start:start + length] if len(args) >= 2 and isinstance(args[0], str) else ""
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
            return ord(args[0][0]) if len(args) == 1 and isinstance(args[0], str) and args[0] else 0
        
        raise ValueError(f"Unknown function: {name}")

class ExpressionParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.pos = 0
        self.length = len(self.text)
    
    def parse(self) -> Expression:
        expr = self.parse_expression()
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == ':' and not self.in_string():
            return expr
        if self.pos < self.length:
            debug_print(f"Warning: Unconsumed input: '{self.text[self.pos:]}'")
        return expr

    def in_string(self) -> bool:
        in_string = False
        quote_char = None
        i = 0
        while i < self.pos:
            if self.text[i] in ('"', "'") and (i == 0 or self.text[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = self.text[i]
                elif self.text[i] == quote_char:
                    in_string = False
                    quote_char = None
            i += 1
        return in_string

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1
    
    def parse_expression(self) -> Expression:
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expression:
        left = self.parse_term()
        self.skip_whitespace()
        
        if self.pos < self.length:
            if self.pos + 1 < self.length:
                op2 = self.text[self.pos:self.pos+2]
                if op2 in ["<=", ">=", "<>"]:
                    self.pos += 2
                    right = self.parse_term()
                    return BinaryExpression(left, op2, right)
            
            if self.text[self.pos] in "<>=":
                op = self.text[self.pos]
                self.pos += 1
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
        debug_print(f"Parsing primary at pos={self.pos}, text='{self.text[self.pos:self.pos+10]}...'")
        
        if self.pos >= self.length:
            return NumberExpression(0)
        
        char = self.text[self.pos]
        
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
                    self.skip_whitespace()
                    args.append(self.parse_expression())
                    self.skip_whitespace()
                    
                    if self.pos >= self.length or self.text[self.pos] != ',':
                        break
                    self.pos += 1
                
                if self.pos < self.length and self.text[self.pos] == ')':
                    self.pos += 1
                else:
                    raise ParserError(f"Expected closing parenthesis at position {self.pos}")
                
                return FunctionExpression(name, args)
            else:
                if CommandFactory.is_reserved_function(name):
                    return FunctionExpression(name, [])
                return VariableExpression(name)
        
        elif char.isdigit() or char == '.':
            start = self.pos
            decimal_point = False
            
            while self.pos < self.length:
                if self.text[self.pos] == '.' and not decimal_point:
                    decimal_point = True
                elif not self.text[self.pos].isdigit():
                    break
                self.pos += 1
            
            number_str = self.text[start:self.pos]
            debug_print(f"Parsed number: {number_str}")
            
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
            self.skip_whitespace()
            expr = self.parse_expression()
            self.skip_whitespace()
            
            if self.pos < self.length and self.text[self.pos] == ')':
                self.pos += 1
                return expr
            else:
                raise ParserError(f"Expected closing parenthesis at position {self.pos}")
        
        else:
            raise ParserError(f"Unexpected character at position {self.pos}: {char}")

    def parse_number(self) -> NumberExpression:
        n, i = 0, 0
        while i < len(self.text) and self.text[i].isdigit():
            n = n * 10 + int(self.text[i])
            i += 1
        self.text = self.text[i:].strip()
        return NumberExpression(n)
    
    def parse_string(self) -> StringExpression:
        match = re.match(r'"([^"]*)"', self.text)
        if match:
            self.text = self.text[len(match.group(0)):].strip()
            return StringExpression(match.group(1))
        return StringExpression("")
    
    def parse_variable(self) -> VariableExpression:
        i = 0
        while i < len(self.text) and (self.text[i].isalnum() or self.text[i] == "$"):
            i += 1
        var_name = self.text[:i]
        self.text = self.text[i:].strip()
        return VariableExpression(var_name)

class Command(ABC):
    def __init__(self):
        self.state = InterpreterState()
    
    @abstractmethod
    def execute(self, args: str) -> None:
        pass

class ParsedCommand(Command):
    def execute(self, args: str) -> None:
        self.preprocess(args)
        self.process(args)
        self.postprocess(args)
    
    def preprocess(self, args: str) -> None:
        pass
    
    @abstractmethod
    def process(self, args: str) -> None:
        pass
    
    def postprocess(self, args: str) -> None:
        pass
    
    def parse_expression(self, expr: str) -> Any:
        parser = ExpressionParser(expr)
        expression = parser.parse()
        evaluator = EvaluationVisitor()
        return expression.accept(evaluator)

class PrintCommand(Command):
    def execute(self, args: str) -> None:
        if not args.strip():
            print()
            return
        
        trailing_semicolon = args.strip().endswith(";")
        args = args.rstrip(";").rstrip() if trailing_semicolon else args
        
        parts = args.split(";")
        output = []
        tab_positions = [8, 16, 24, 32]
        current_tab = 0

        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if part == ",":
                if current_tab < len(tab_positions):
                    current_length = sum(len(s) for s in output)
                    padding = tab_positions[current_tab] - current_length
                    if padding > 0:
                        output.append(" " * padding)
                    current_tab += 1
                else:
                    output.append(" ")
                continue

            if part.upper().startswith("USING") and len(part.split()) > 1:
                try:
                    using_parts = part.split(maxsplit=2)
                    if len(using_parts) < 3:
                        raise ValueError("Invalid USING syntax")
                    format_str = using_parts[1].strip('"\'')
                    expr = using_parts[2].strip()
                    
                    parser = ExpressionParser(expr)
                    expr_node = parser.parse()
                    evaluator = EvaluationVisitor()
                    result = expr_node.accept(evaluator)
                    
                    if not isinstance(result, (int, float)):
                        raise ValueError("USING format requires a numeric value")
                    
                    formatted = self.format_using(result, format_str)
                    output.append(formatted)
                    continue
                except Exception as e:
                    print(f"Error in USING clause '{part}': {e}")
                    return

            if (part.startswith("'") and part.endswith("'")) or (part.startswith('"') and part.endswith('"')):
                output.append(part[1:-1])
                continue
            
            try:
                parser = ExpressionParser(part)
                expr = parser.parse()
                evaluator = EvaluationVisitor()
                result = expr.accept(evaluator)
                debug_print(f"Evaluated '{part}' = '{result}' (type: {type(result)})")
                
                if isinstance(result, float):
                    formatted = f"{result:.6f}".rstrip("0").rstrip(".")
                    output.append(formatted)
                elif isinstance(result, int):
                    output.append(str(result))
                else:
                    output.append(str(result))
            except Exception as e:
                print(f"Error evaluating expression '{part}': {e}")
                return
        
        print("".join(output), end="" if trailing_semicolon else "\n")

    def format_using(self, value: float, format_str: str) -> str:
        if format_str == "#.##":
            return f"{value:.2f}"
        elif format_str == "#.###":
            return f"{value:.3f}"
        elif format_str == "#,###.##":
            return f"{value:,.2f}"
        else:
            raise ValueError(f"Unsupported format string: {format_str}")

class InputCommand(ParsedCommand):
    def process(self, args: str) -> None:
        parts = args.split(";", 1)
        prompt = ""
        var_name = args.strip()
        
        if len(parts) > 1:
            prompt_text = parts[0].strip()
            var_name = parts[1].strip()
            
            try:
                parser = ExpressionParser(prompt_text)
                prompt_expr = parser.parse()
                evaluator = EvaluationVisitor()
                prompt = str(prompt_expr.accept(evaluator)) + " "
            except Exception as e:
                print(f"Error in INPUT prompt: {e}")
                prompt = "> "
        
        input_value = input(prompt).strip()
        
        try:
            if var_name.endswith("$"):
                self.state.variables[var_name] = input_value
            else:
                try:
                    if '.' in input_value:
                        self.state.variables[var_name] = float(input_value)
                    else:
                        self.state.variables[var_name] = int(input_value)
                except ValueError:
                    self.state.variables[var_name] = input_value
        except Exception as e:
            print(f"Error processing INPUT: {e}")

class LetCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            var, expr = args.split("=", 1)
            var = var.strip()
            expr = expr.strip()
            
            if CommandFactory.is_reserved(var):
                raise ParserError(f"Cannot assign to reserved word '{var}'")
            
            debug_print(f"LET assignment: var={var}, expr={expr}")
            
            parser = ExpressionParser(expr)
            expression = parser.parse()
            evaluator = EvaluationVisitor()
            value = expression.accept(evaluator)
            debug_print(f"Evaluated to: {value} (type: {type(value)})")
            
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            
            self.state.variables[var] = value
        except Exception as e:
            print(f"Error in LET statement: {e}")
            if var and not CommandFactory.is_reserved(var):
                self.state.variables[var] = 0

class IfCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            parts = re.split(r"then", args, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) != 2:
                raise ValueError("Invalid IF syntax: Missing 'THEN'")

            condition = parts[0].strip()
            rest = parts[1].strip()
            
            else_part = ""
            if "ELSE" in rest.upper():
                then_else = re.split(r"else", rest, maxsplit=1, flags=re.IGNORECASE)
                then_part = then_else[0].strip()
                else_part = then_else[1].strip()
            else:
                then_part = rest
            
            parser = ExpressionParser(condition)
            condition_node = parser.parse()
            condition_value = condition_node.accept(EvaluationVisitor())
            
            debug_print(f"IF condition evaluated to: {condition_value} (type: {type(condition_value)})")
            
            engine = InterpreterEngine()
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
            print(f"Error in IF statement: {e}")

class GotoCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            if args.strip().isdigit():
                line_num = int(args.strip())
            else:
                line_num = int(self.parse_expression(args))
                
            if line_num in self.state.code:
                self.state.variables["#"] = line_num
            else:
                print(f"Error: Line {line_num} does not exist.")
        except Exception as e:
            print(f"Error in GOTO statement: {e}")

class GosubCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            if args.strip().isdigit():
                line_num = int(args.strip())
            else:
                line_num = int(self.parse_expression(args))
                
            if line_num in self.state.code:
                self.state.stack.append(self.state.variables["#"] + 1)
                self.state.variables["#"] = line_num
            else:
                print(f"Error: Line {line_num} does not exist.")
        except Exception as e:
            print(f"Error in GOSUB statement: {e}")

class ReturnCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.stack:
            self.state.variables["#"] = self.state.stack.pop()
        else:
            print("RETURN without GOSUB")
            self.state.variables["#"] = 0

class ForCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            parts = args.split("=", 1)
            if len(parts) != 2:
                raise ValueError("Invalid FOR syntax: Missing '='")
            
            var = parts[0].strip()
            if not var.isalnum():
                raise ValueError(f"Invalid loop variable: {var}")
            
            rest = parts[1].strip()
            to_parts = rest.split("TO", 1)
            if len(to_parts) != 2:
                raise ValueError("Invalid FOR syntax: Missing 'TO'")
            
            start_expr = to_parts[0].strip()
            rest = to_parts[1].strip()
            
            step = 1
            limit_expr = rest
            if "STEP" in rest.upper():
                step_parts = rest.split("STEP", 1)
                limit_expr = step_parts[0].strip()
                step_expr = step_parts[1].strip()
                
                parser = ExpressionParser(step_expr)
                step_node = parser.parse()
                step = step_node.accept(EvaluationVisitor())
                if not isinstance(step, (int, float)):
                    raise ValueError("STEP must be numeric")
            
            parser = ExpressionParser(start_expr)
            start_node = parser.parse()
            start = start_node.accept(EvaluationVisitor())
            if not isinstance(start, (int, float)):
                raise ValueError("START must be numeric")
            
            parser = ExpressionParser(limit_expr)
            limit_node = parser.parse()
            limit = limit_node.accept(EvaluationVisitor())
            if not isinstance(limit, (int, float)):
                raise ValueError("LIMIT must be numeric")
            
            self.state.variables[var] = start
            
            current_line = self.state.variables["#"]
            next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), current_line)
            
            self.state.loops[var] = (next_line, limit, step)
            
            debug_print(f"FOR loop init: var={var}, start={start}, limit={limit}, step={step}, next_line={next_line}")
        except Exception as e:
            print(f"Error in FOR statement: {e}")

class NextCommand(Command):
    def execute(self, args: str) -> None:
        var = args.strip()
        if not var:
            print("Error: NEXT requires a variable name")
            return
        
        if var not in self.state.loops:
            print(f"Error: No matching FOR loop for variable '{var}'")
            return
        
        start_line, limit, step = self.state.loops[var]
        current_value = self.state.variables.get(var, 0)
        current_value += step
        self.state.variables[var] = current_value
        
        if step > 0:
            continue_loop = current_value <= limit
        else:
            continue_loop = current_value >= limit
        
        debug_print(f"NEXT: var={var}, value={current_value}, limit={limit}, step={step}, continue={continue_loop}")
        
        if continue_loop:
            self.state.variables["#"] = start_line
        else:
            current_line = self.state.variables["#"]
            next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
            self.state.variables["#"] = next_line
            del self.state.loops[var]

class WhileCommand(ParsedCommand):
    def process(self, args: str) -> None:
        try:
            if not args.strip():
                print("Syntax error in WHILE statement: missing condition")
                return
            
            condition = args.strip()
            loop_id = f"while_{self.state.variables['#']}"
            self.state.whiles[loop_id] = (self.state.variables["#"], condition)
            
            try:
                condition_result = self.parse_expression(condition)
            except Exception as e:
                print(f"Error evaluating WHILE condition: {e}")
                return
                
            if not condition_result:
                self.skip_to_wend()
        except Exception as e:
            print(f"Syntax error in WHILE statement: {e}")

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
                    
        print("Error: No matching WEND for WHILE")
        self.state.variables["#"] = 0

class WendCommand(ParsedCommand):
    def process(self, args: str) -> None:
        loop_id = None
        for id in sorted(self.state.whiles.keys(), reverse=True):
            if id.startswith("while_"):
                loop_id = id
                break
        
        if loop_id and loop_id in self.state.whiles:
            start_line, condition = self.state.whiles[loop_id]
            
            if self.parse_expression(condition):
                self.state.variables["#"] = start_line + 1
            else:
                del self.state.whiles[loop_id]
                next_line = next(
                    ((n, ln) for (n, ln) in sorted(self.state.code.items()) if n > self.state.variables["#"]), 
                    (None, None)
                )
                self.state.variables["#"] = next_line[0] if next_line[0] else 0
        else:
            print("Error: WEND without matching WHILE")
            self.state.variables["#"] = 0

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
            parts = args.strip().split("-")
            parts = [part.strip() for part in parts if part.strip()]

            if len(parts) == 1:
                start = self.evaluate_line(parts[0])
                return start, default_end
            elif len(parts) == 2:
                start = self.evaluate_line(parts[0]) if parts[0] else default_start
                end = self.evaluate_line(parts[1])
                if start > end:
                    print(f"Warning: Start line {start} is greater than end line {end}. Swapping.")
                    start, end = end, start
                return start, end
            else:
                raise ValueError("Invalid range format")
        except (ValueError, ParserError) as e:
            print(f"Error parsing range: {e}. Listing all lines.")
            return default_start, default_end

    def evaluate_line(self, expr: str) -> int:
        if not expr:
            return min(self.state.code.keys(), default=1)
        parser = ExpressionParser(expr)
        expression = parser.parse()
        evaluator = EvaluationVisitor()
        result = expression.accept(evaluator)
        line_num = int(result)
        if line_num <= 0:
            raise ValueError("Line number must be positive")
        return line_num

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
        current_line = self.state.variables["#"]
        next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
        self.state.variables["#"] = next_line

class SaveCommand(Command):
    def execute(self, args: str) -> None:
        try:
            filename = self.parse_filename(args)
            if not filename:
                raise ValueError("Filename must be a non-empty quoted string")
            
            if not filename.endswith(".bas"):
                filename += ".bas"
            
            with open(filename, "w") as file:
                for line_number in sorted(self.state.code.keys()):
                    code = self.state.code[line_number]
                    file.write(f"{line_number} {code}\n")
            
            print(f"Program saved to '{filename}'")
        except Exception as e:
            print(f"Error saving program: {e}")

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
                raise ValueError("Filename must be a non-empty quoted string")
            
            if not filename.endswith(".bas"):
                filename += ".bas"
            
            self.state.code.clear()
            
            engine = InterpreterEngine()
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        try:
                            line_number, line_code = engine.parse_line(line)
                            if line_number <= 0:
                                raise ValueError(f"Invalid line number: {line_number}")
                            self.state.code[line_number] = line_code
                        except Exception as e:
                            print(f"Warning: Skipping invalid line '{line}': {e}")
            
            if not self.state.code:
                print(f"Warning: No valid program lines loaded from '{filename}'")
            else:
                print(f"Program loaded from '{filename}'")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error loading program: {e}")

    def parse_filename(self, args: str) -> str:
        args = args.strip()
        if (args.startswith('"') and args.endswith('"')) or (args.startswith("'") and args.endswith("'")):
            return args[1:-1].strip()
        return ""

class ContinueCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.paused:
            if self.state.variables["#"] == 0 or self.state.variables["#"] not in self.state.code:
                print("No more lines to continue.")
                self.state.paused = False
                return
            print("Resuming program...")
            self.state.paused = False
            InterpreterEngine().run()
        else:
            print("Program is not paused.")
            self.state.paused = False

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
                raise ValueError("Invalid number of arguments")

            if start <= 0 or increment <= 0:
                raise ValueError("Start line and increment must be positive")
            return start, increment
        except ValueError as e:
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
                else:
                    print(f"Warning: Referenced line {old_line} in {cmd} does not exist.")
                    return line
            except ValueError:
                return line

        elif cmd == "if":
            match = re.search(r'\bTHEN\b\s*(\d+)', args, re.IGNORECASE)
            if match:
                old_line = int(match.group(1))
                if old_line in line_mapping:
                    return line.replace(match.group(1), str(line_mapping[old_line]))
                else:
                    print(f"Warning: Referenced line {old_line} in IF...THEN does not exist.")
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
            parts = args.strip().split("-")
            parts = [part.strip() for part in parts if part.strip()]

            if len(parts) == 1:
                start = self.evaluate_line(parts[0])
                return start, default_end
            elif len(parts) == 2:
                start = self.evaluate_line(parts[0]) if parts[0] else default_start
                end = self.evaluate_line(parts[1])
                if start > end:
                    print(f"Warning: Start line {start} is greater than end line {end}. Swapping.")
                    start, end = end, start
                return start, end
            else:
                raise ValueError("Invalid range format")
        except (ValueError, ParserError) as e:
            print(f"Error parsing range: {e}. No lines deleted.")
            return default_start, default_start

    def evaluate_line(self, expr: str) -> int:
        if not expr:
            return min(self.state.code.keys(), default=1)
        parser = ExpressionParser(expr)
        expression = parser.parse()
        evaluator = EvaluationVisitor()
        result = expression.accept(evaluator)
        line_num = int(result)
        if line_num <= 0:
            raise ValueError("Line number must be positive")
        return line_num

class RunCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program loaded!")
            return

        start_line = self.parse_start_line(args)

        if start_line not in self.state.code:
            print(f"Error: Line {start_line} does not exist.")
            return

        min_line = min(self.state.code.keys())
        if start_line != min_line:
            print(f"Warning: Starting at line {start_line} may skip initialization code.")

        self.state.variables["#"] = start_line
        InterpreterEngine().run()
        print()

    def parse_start_line(self, args: str) -> int:
        default_start = min(self.state.code.keys())

        if not args.strip():
            return default_start

        try:
            parser = ExpressionParser(args.strip())
            expr = parser.parse()
            evaluator = EvaluationVisitor()
            start_line = int(expr.accept(evaluator))

            if start_line <= 0:
                raise ValueError("Line number must be positive")
            return start_line
        except (ValueError, ParserError) as e:
            print(f"Error parsing start line: {e}. Starting at line {default_start}")
            return default_start

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
        "while", "wend", "list", "ren", "del", "run", "end", "stop", "bye", "continue",
        "save", "load", "new", "rem",
        "to", "step", "then", "else", "using"
    }
    
    _commands = {
        "print": PrintCommand,
        "input": InputCommand,
        "goto": GotoCommand,
        "if": IfCommand,
        "run": RunCommand,
        "let": LetCommand,
        "gosub": GosubCommand,
        "return": ReturnCommand,
        "for": ForCommand,
        "next": NextCommand,
        "list": ListCommand,
        "ren": RenumberCommand,
        "del": DeleteCommand,
        "while": WhileCommand,
        "wend": WendCommand,
        "bye": ByeCommand,
        "stop": StopCommand,
        "end": EndCommand,
        "continue": ContinueCommand,
        "save": SaveCommand,
        "load": LoadCommand,
        "new": NewCommand,
        "rem": RemCommand
    }
    
    @classmethod
    def create_command(cls, name: str) -> Optional[Command]:
        name = name.lower()
        if name in cls._commands:
            return cls._commands[name]()
        return None
    
    @classmethod
    def register_command(cls, name: str, command_class: type) -> None:
        cls._commands[name.lower()] = command_class
    
    @classmethod
    def is_reserved_function(cls, name: str) -> bool:
        return name.lower() in cls._reserved_functions
    
    @classmethod
    def is_reserved_keyword(cls, name: str) -> bool:
        return name.lower() in cls._reserved_keywords
    
    @classmethod
    def is_reserved(cls, name: str) -> bool:
        return cls.is_reserved_function(name) or cls.is_reserved_keyword(name)

def split_statements(line: str) -> List[str]:
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
            current.append(char)
            i += 1
        elif char == quote_char and in_string:
            in_string = False
            quote_char = None
            current.append(char)
            i += 1
        elif char == ':' and not in_string:
            statement = ''.join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            i += 1
        else:
            current.append(char)
            i += 1
    
    statement = ''.join(current).strip()
    if statement:
        statements.append(statement)
    
    return statements

class InterpreterEngine:
    def __init__(self):
        self.state = InterpreterState()
    
    def load_program(self, filename: str) -> None:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    line_number, line_code = self.parse_line(line)
                    self.state.code[line_number] = line_code
    
    def parse_line(self, line: str) -> Tuple[int, str]:
        line_number, *code_parts = line.split(maxsplit=1)
        line_number = int(line_number)
        code = code_parts[0] if code_parts else ""
        return line_number, code
    
    def execute_line(self, line: str) -> None:
        line = line.strip()
        if not line:
            return
        
        statements = split_statements(line)
        
        for statement in statements:
            if not statement:
                continue
            
            parts = statement.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            command = CommandFactory.create_command(cmd)
            if command:
                command.execute(args)
            elif "=" in statement and not statement.upper().startswith("IF"):
                let_command = CommandFactory.create_command("let")
                let_command.execute(statement)
            else:
                print(f"Syntax error: Unknown command or statement '{statement}'")
    
    def run(self) -> None:
        try:
            while self.state.variables["#"] > 0 and not self.state.paused:
                current_line = self.state.variables["#"]
                if current_line not in self.state.code:
                    next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
                    self.state.variables["#"] = next_line
                    continue
                    
                line = self.state.code[current_line]
                if line:
                    self.execute_line(line)
                    if self.state.variables["#"] == current_line:
                        next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
                        self.state.variables["#"] = next_line
        except KeyboardInterrupt:
            print("Program paused by interrupt.")
            self.state.paused = True
            current_line = self.state.variables["#"]
            next_line = next((n for n in sorted(self.state.code.keys()) if n > current_line), 0)
            self.state.variables["#"] = next_line
    
    def evaluate_expression(self, expr: str) -> Any:
        try:
            parser = ExpressionParser(expr)
            expression = parser.parse()
            evaluator = EvaluationVisitor()
            return expression.accept(evaluator)
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            return 0

def main() -> None:
    interpreter = InterpreterEngine()
    
    if len(sys.argv) > 1:
        interpreter.load_program(sys.argv[1])
        try:
            interpreter.run()
        except KeyboardInterrupt:
            print("\nProgram paused by interrupt.")
            interpreter.state.paused = True
            current_line = interpreter.state.variables["#"]
            next_line = next((n for n in sorted(interpreter.state.code.keys()) if n > current_line), 0)
            interpreter.state.variables["#"] = next_line
        while interpreter.state.paused:
            try:
                line = input("> ").strip()
                if line:
                    interpreter.execute_line(line)
            except KeyboardInterrupt:
                print("\nProgram terminated by interrupt.")
                sys.exit(0)
            except EOFError:
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
                    lineno_expr = parser.parse_number()
                    lineno = lineno_expr.accept(EvaluationVisitor())
                    if lineno:
                        interpreter.state.code[lineno] = parser.text
                    else:
                        interpreter.execute_line(parser.text)
                except Exception as e:
                    print(f"Error parsing line: {e}")
            except KeyboardInterrupt:
                print("Program terminated by interrupt.")
                sys.exit(0)
            except EOFError:
                print("\nExiting.")
                sys.exit(0)

if __name__ == "__main__":
    main()
