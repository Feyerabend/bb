#!/usr/bin/env python3
# Basic Interpreter
import sys
import re
from typing import Any, List, Optional, Tuple
from abc import ABC, abstractmethod

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
        return cls._instance
    
    def reset(self):
        self.code = {}
        self.variables = {"#": 10}
        self.stack = []
        self.loops = {}

class Expression(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class NumberExpression(Expression):
    def __init__(self, value: int):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_number(self)

class StringExpression(Expression):
    def __init__(self, value: str):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_string(self)

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_variable(self)

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary(self)

class FunctionExpression(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args
    
    def accept(self, visitor):
        return visitor.visit_function(self)

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

class EvaluationVisitor(ExpressionVisitor):
    def __init__(self):
        self.state = InterpreterState()
    
    def visit_number(self, expr: NumberExpression):
        return expr.value
    
    def visit_string(self, expr: StringExpression):
        return expr.value
    
    def visit_variable(self, expr: VariableExpression):
        if expr.name in self.state.variables:
            return self.state.variables[expr.name]
        else:
            self.state.variables[expr.name] = "" if expr.name.endswith("$") else 0
            return self.state.variables[expr.name]
    
    def visit_binary(self, expr: BinaryExpression):
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        
        if isinstance(left, str) and isinstance(right, (int, float)):
            right = str(right)
        elif isinstance(left, (int, float)) and isinstance(right, str):
            left = str(left)
        
        operations = {
            "+": lambda x, y: x + y if isinstance(x, (int, float, str)) else None,
            "-": lambda x, y: x - y if isinstance(x, (int, float)) else None,
            "*": lambda x, y: x * y if isinstance(x, (int, float)) and isinstance(y, (int, float)) else None,
            "/": lambda x, y: x / y if isinstance(x, (int, float)) and isinstance(y, (int, float)) and y != 0 else 0,
            "=": lambda x, y: 1 if x == y else 0,
            "<": lambda x, y: 1 if x < y else 0,
            ">": lambda x, y: 1 if x > y else 0
        }
        
        if expr.operator in operations:
            result = operations[expr.operator](left, right)
            if result is not None:
                return result
            
        raise ValueError(f"Cannot perform {expr.operator} operation on {type(left)} and {type(right)}")
    
    def visit_function(self, expr: FunctionExpression):
        args = [arg.accept(self) for arg in expr.args]
        base_str = str(args[0]) if args else ""
        
        string_functions = {
            "LEFT": lambda s, l: s[:int(l)] if len(args) > 1 else "",
            "RIGHT": lambda s, l: s[-int(l):] if len(args) > 1 else "",
            "MID": lambda s, start, length=None: 
                s[int(start)-1:int(start)-1+int(length)] if len(args) > 2 
                else s[int(start)-1:] if len(args) > 1 
                else "",
            "LEN": lambda s: len(s),
            "STR": lambda s: str(s)
        }
        
        if expr.name in string_functions:
            try:
                return string_functions[expr.name](*((base_str,) + tuple(args[1:])))
            except (IndexError, ValueError) as e:
                raise ParserError(f"Error in string function {expr.name}: {e}")
        
        raise ParserError(f"Unknown function: {expr.name}")

class ParsingStrategy(ABC):
    @abstractmethod
    def parse(self, text: str) -> Expression:
        pass

class ExpressionParser(ParsingStrategy):
    def __init__(self, text: str):
        self.text = text.strip()
    
    def parse(self, text: str = None) -> Expression:
        if text is not None:
            self.text = text.strip()
        return self.parse_expr()
    
    def parse_expr(self) -> Expression:
        left = self.parse_term()
        while self.text and self.text[0] in "+-=<>":
            op = self.text[0]
            self.text = self.text[1:].strip()
            right = self.parse_term()
            left = BinaryExpression(left, op, right)
        return left
    
    def parse_term(self) -> Expression:
        left = self.parse_factor()
        while self.text and self.text[0] in "*/":
            op = self.text[0]
            self.text = self.text[1:].strip()
            right = self.parse_factor()
            left = BinaryExpression(left, op, right)
        return left
    
    def parse_factor(self) -> Expression:
        func_match = re.match(r'([A-Z]+)\$\((.*?)\)', self.text)
        if func_match:
            func_name = func_match.group(1)
            args_text = func_match.group(2)
            self.text = self.text[len(func_match.group(0)):].strip()
            
            args = []
            for arg in [a.strip() for a in args_text.split(',')]:
                if arg:
                    arg_parser = ExpressionParser(arg)
                    args.append(arg_parser.parse())
            
            return FunctionExpression(func_name, args)
        
        if self.text and self.text[0] == "(":
            self.text = self.text[1:].strip()
            expr = self.parse_expr()
            if self.text and self.text[0] == ")":
                self.text = self.text[1:].strip()
                return expr
            else:
                raise ParserError("Missing closing parenthesis")
        
        if self.text.startswith('"'):
            return self.parse_string()
        
        if self.text and self.text[0].isdigit():
            return self.parse_number()
        
        return self.parse_variable()
    
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

class PrintCommand(ParsedCommand):
    def process(self, args: str) -> None:
        expressions = args.split(";")
        output = []
        for expr in expressions:
            if not expr.strip():
                continue
            value = self.parse_expression(expr.strip())
            if str(value) == '0':
                continue
            output.append(str(value))
        print(" ".join(output).strip())

class InputCommand(ParsedCommand):
    def process(self, args: str) -> None:
        parts = args.split(";", 1)
        prompt = "> "
        var_name = args.strip()
        
        if len(parts) > 1:
            parser = ExpressionParser(parts[0].strip())
            prompt_expr = parser.parse()
            evaluator = EvaluationVisitor()
            prompt = str(prompt_expr.accept(evaluator)) + " "
            var_name = parts[1].strip()
        
        input_value = input(prompt).strip()
        
        try:
            if var_name.endswith("$"):
                self.state.variables[var_name] = input_value
            else:
                self.state.variables[var_name] = (
                    int(input_value) if input_value.isdigit() 
                    else float(input_value) if '.' in input_value 
                    else None
                )
        except ValueError:
            self.state.variables[var_name] = None
        
        if var_name in self.state.variables and self.state.variables[var_name] is None:
            del self.state.variables[var_name]

class LetCommand(ParsedCommand):
    def process(self, args: str) -> None:
        var, expr = args.split("=", 1)
        try:
            self.state.variables[var.strip()] = self.parse_expression(expr.strip())
        except Exception as e:
            print(f"Error parsing expression: {e}")

class IfCommand(ParsedCommand):
    def process(self, args: str) -> None:
        match = re.search(r'\bTHEN\b', args, re.IGNORECASE)
        if match:
            cond = args[:match.start()].strip()
            then_stmt = args[match.end():].strip()
        else:
            cond = args.strip()
            then_stmt = ""
        
        if self.parse_expression(cond):
            if then_stmt:
                InterpreterEngine().execute_line(then_stmt)

class GotoCommand(ParsedCommand):
    def process(self, args: str) -> None:
        line_num = self.parse_expression(args)
        if line_num in self.state.code:
            self.state.variables["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")

class GosubCommand(ParsedCommand):
    def process(self, args: str) -> None:
        line_num = self.parse_expression(args)
        if line_num in self.state.code:
            self.state.stack.append(self.state.variables["#"] + 1)
            self.state.variables["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")

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
            var, rest = args.split("=", 1)
            parts = rest.upper().split("TO", 1)
            if len(parts) < 2:
                print("Syntax error in FOR statement: missing TO clause")
                return
            
            start = self.parse_expression(parts[0].strip())
            end_value = self.parse_expression(parts[1].strip())
            
            var = var.strip()
            self.state.variables[var] = start
            self.state.loops[var] = (self.state.variables["#"], end_value)
        except ValueError:
            print("Syntax error in FOR statement")

class NextCommand(ParsedCommand):
    def process(self, args: str) -> None:
        var = args.strip()
        if var in self.state.loops:
            start_line, end_value = self.state.loops[var]
            self.state.variables[var] += 1
            
            if self.state.variables[var] <= end_value:
                self.state.variables["#"] = start_line + 1
            else:
                del self.state.loops[var]
                next_line = next(
                    ((n, ln) for (n, ln) in sorted(self.state.code.items()) if n > self.state.variables["#"]), 
                    (None, None)
                )
                self.state.variables["#"] = next_line[0] if next_line[0] else 0
        else:
            print(f"Error: NEXT without matching FOR for variable '{var}'")

class ListCommand(Command):
    def execute(self, args: str) -> None:
        for n, ln in sorted(self.state.code.items()):
            print(f"{n:3} {ln}")

class ByeCommand(Command):
    def execute(self, args: str) -> None:
        sys.exit(0)

class StopCommand(Command):
    def execute(self, args: str) -> None:
        print("STOP command executed. Exiting program.")
        sys.exit(0)

class RenumberCommand(Command):
    def execute(self, args: str) -> None:
        if not self.state.code:
            print("No program to renumber.")
            return

        old_lines = sorted(self.state.code.keys())
        new_code = {}
        line_mapping = {}
        start_line = 10
        increment = 10

        for i, old_line in enumerate(old_lines):
            new_line = start_line + i * increment
            line_mapping[old_line] = new_line
            new_code[new_line] = self.state.code[old_line]

        for new_line in new_code:
            new_code[new_line] = self.update_line_references(new_code[new_line], line_mapping)

        self.state.code.clear()
        self.state.code.update(new_code)
        print("Program renumbered successfully.")

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

class RunCommand(Command):
    def execute(self, args: str) -> None:
        if self.state.code:
            self.state.variables["#"] = min(self.state.code.keys())
            InterpreterEngine().run()

class CommandFactory:
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
        "bye": ByeCommand,
        "stop": StopCommand,
        "end": StopCommand
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
        
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        command = CommandFactory.create_command(cmd)
        if command:
            command.execute(args)
        elif "=" in line:
            let_command = CommandFactory.create_command("let")
            let_command.execute(line)
        else:
            print(f"Syntax error: Unknown command '{cmd}'")
    
    def run(self) -> None:
        first_line = min(self.state.code.keys(), default=None)
        if first_line is None:
            print("No program loaded!")
            return
        
        self.state.variables["#"] = first_line
        while self.state.variables["#"] > 0:
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
        with open(sys.argv[1], "r") as f:
            for line in f:
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
        interpreter.run()
    else:
        for line in sys.stdin:
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

if __name__ == "__main__":
    main()
