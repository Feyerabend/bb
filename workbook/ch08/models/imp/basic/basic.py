#!/usr/bin/env python3
import sys
import re
from typing import Any, List, Dict, Optional, Tuple, Union

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, line: str):
        self.line = line.strip()

    def _parse_number(self) -> int:
        n, i = 0, 0
        while i < len(self.line) and self.line[i].isdigit():
            n = n * 10 + int(self.line[i])
            i += 1
        self.line = self.line[i:].strip()
        return n

    def _parse_string_function(self) -> Optional[Any]:
        func_match = re.match(r'([A-Z]+)\$\((.*?)\)', self.line)
        if func_match:
            func_name = func_match.group(1)
            args = [a.strip() for a in func_match.group(2).split(',')]
            try:
                evaluated_args = [Parser(arg).expr() for arg in args]
                base_str = str(evaluated_args[0]) if len(evaluated_args) > 0 else ""
                string_functions = {
                    "LEFT": lambda s, l: s[:int(l)] if len(evaluated_args) > 1 else "",
                    "RIGHT": lambda s, l: s[-int(l):] if len(evaluated_args) > 1 else "",
                    "MID": lambda s, start, length=None: 
                        s[int(start)-1:int(start)-1+int(length)] if len(evaluated_args) > 2 
                        else s[int(start)-1:] if len(evaluated_args) > 1 
                        else "",
                    "LEN": lambda s: len(s),
                    "STR": lambda s: str(s)
                }
                if func_name in string_functions:
                    return string_functions[func_name](*((base_str,) + tuple(evaluated_args[1:])))
            except (IndexError, ValueError) as e:
                raise ParserError(f"Error in string function {func_name}: {e}")
        return None

    def expr(self) -> Union[str, int, float]:
        res = self.term()
        s = self.line
        while s and s[0] in "+-=<|>":
            op, self.line = s[0], s[1:].strip()
            next_term = self.term()
            def coerce_types(a: Any, b: Any) -> Tuple[Any, Any]:
                if isinstance(a, str) and isinstance(b, (int, float)):
                    return str(a), str(b)
                elif isinstance(a, (int, float)) and isinstance(b, str):
                    return str(a), str(b)
                return a, b
            res, next_term = coerce_types(res, next_term)
            ops = {
                "+": lambda x, y: x + y if isinstance(x, (int, float, str)) else None,
                "-": lambda x, y: x - y if isinstance(x, (int, float)) else None,
                "=": lambda x, y: 1 if x == y else 0,
                "<": lambda x, y: 1 if x < y else 0,
                ">": lambda x, y: 1 if x > y else 0
            }
            if op in ops:
                result = ops[op](res, next_term)
                if result is not None:
                    res = result
                else:
                    raise ValueError(f"Cannot perform operation {op} on {type(res)} and {type(next_term)}")
            s = self.line
        return res

    def term(self) -> Union[str, int, float]:
        res, s = self.factor(), self.line
        while s and s[0] in "*/":
            op, self.line = s[0], s[1:].strip()
            n = self.factor()
            res *= n if op == "*" else res / n if n != 0 else 0
            s = self.line
        return res

    def factor(self) -> Union[str, int, float]:
        str_func_result = self._parse_string_function()
        if str_func_result is not None:
            return str_func_result
        if self.line and self.line[0] == "(":
            self.line = self.line[1:].strip()
            res = self.expr()
            self.line = self.line[1:].strip()
            return res
        elif self.line.startswith('"'):
            return self._parse_string()
        elif self.line and self.line[0].isdigit():
            return self._parse_number()
        else:
            return self._parse_variable()

    def _parse_string(self) -> str:
        match = re.match(r'"([^"]*)"', self.line)
        if match:
            self.line = self.line[len(match.group(0)):].strip()
            return match.group(1)
        return ""

    def _parse_variable(self) -> Union[str, int, float]:
        i = 0
        while i < len(self.line) and (self.line[i].isalnum() or self.line[i] == "$"):
            i += 1
        var_name = self.line[:i]
        self.line = self.line[i:].strip()
        if var_name in Interpreter.vars:
            return Interpreter.vars[var_name]
        else:
            Interpreter.vars[var_name] = "" if var_name.endswith("$") else 0
            return Interpreter.vars[var_name]

class Command:
    def execute(self, args: str) -> None:
        pass

class PrintCommand(Command):
    def execute(self, args: str) -> None:
        expressions = args.split(";")
        output = []
        for expr in expressions:
            value = Parser(expr.strip()).expr()
            if isinstance(value, (list, tuple)):
                value = value[0]
            if str(value) == '0':
                continue
            output.append(str(value))
        print(" ".join(output).strip())

class InputCommand(Command):
    def execute(self, args: str) -> None:
        parts = args.split(";", 1)
        prompt = "> "
        var_name = args.strip()
        if len(parts) > 1:
            prompt = Parser(parts[0].strip())._parse_string() + " "
            var_name = parts[1].strip()
        input_value = input(prompt).strip()
        try:
            if var_name.endswith("$"):
                Interpreter.vars[var_name] = input_value
            else:
                Interpreter.vars[var_name] = (
                    int(input_value) if input_value.isdigit() 
                    else float(input_value) if '.' in input_value 
                    else None
                )
        except ValueError:
            Interpreter.vars[var_name] = None
        if var_name in Interpreter.vars and Interpreter.vars[var_name] is None:
            del Interpreter.vars[var_name]

class LetCommand(Command):
    def execute(self, args: str) -> None:
        var, expr = args.split("=", 1)
        try:
            Interpreter.vars[var.strip()] = Parser(expr.strip()).expr()
        except Exception as e:
            print(f"Error parsing expression: {e}")

class IfCommand(Command):
    def execute(self, args: str) -> None:
        match = re.search(r'\bTHEN\b', args, re.IGNORECASE)
        if match:
            cond = args[:match.start()].strip()
            then_stmt = args[match.end():].strip()
        else:
            cond = args.strip()
            then_stmt = ""
        if Parser(cond).expr():
            if then_stmt:
                Interpreter.execute_line(then_stmt)

class GotoCommand(Command):
    def execute(self, args: str) -> None:
        line_num = Parser(args).expr()
        if line_num in Interpreter.code:
            Interpreter.vars["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")

class GosubCommand(Command):
    def execute(self, args: str) -> None:
        line_num = Parser(args).expr()
        if line_num in Interpreter.code:
            Interpreter.stack.append(Interpreter.vars["#"])
            Interpreter.vars["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")

class ReturnCommand(Command):
    def execute(self, args: str) -> None:
        if Interpreter.stack:
            Interpreter.vars["#"] = Interpreter.stack.pop()

class ForCommand(Command):
    def execute(self, args: str) -> None:
        try:
            var, rest = args.split("=", 1)
            parts = rest.upper().split("TO", 1)
            if len(parts) < 2:
                print("Syntax error in FOR statement: missing TO clause")
                return
            start = Parser(parts[0].strip()).expr()
            end_value = Parser(parts[1].strip()).expr()
            var = var.strip()
            Interpreter.vars[var] = start
            Interpreter.loops[var] = (Interpreter.vars["#"], end_value)
        except ValueError:
            print("Syntax error in FOR statement")

class NextCommand(Command):
    def execute(self, args: str) -> None:
        var = args.strip()
        if var in Interpreter.loops:
            start_line, end_value = Interpreter.loops[var]
            Interpreter.vars[var] += 1
            if Interpreter.vars[var] <= end_value:
                Interpreter.vars["#"] = start_line + 1
            else:
                del Interpreter.loops[var]
                next_line = next(
                    ((n, ln) for (n, ln) in sorted(Interpreter.code.items()) if n > Interpreter.vars["#"]), 
                    (None, None)
                )
                Interpreter.vars["#"] = next_line[0] if next_line[0] else 0
        else:
            print(f"Error: NEXT without matching FOR for variable '{var}'")

class ListCommand(Command):
    def execute(self, args: str) -> None:
        for n, ln in sorted(Interpreter.code.items()):
            print(f"{n:3} {ln}")

class ByeCommand(Command):
    def execute(self, args: str) -> None:
        sys.exit(0)

class StopCommand(Command):
    def execute(self, args: str) -> None:
        print("STOP command executed. Exiting program.")
        sys.exit(0)

class RunCommand(Command):
    def execute(self, args: str) -> None:
        if Interpreter.code:
            Interpreter.vars["#"] = min(Interpreter.code.keys())
            Interpreter.run()

class Interpreter:
    code: Dict[int, str] = {}
    vars: Dict[str, Any] = {"#": 10}
    stack: List[int] = []
    loops: Dict[str, Tuple[int, int]] = {}
    commands = {
        "print": PrintCommand(),
        "input": InputCommand(),
        "goto": GotoCommand(),
        "if": IfCommand(),
        "run": RunCommand(),
        "let": LetCommand(),
        "gosub": GosubCommand(),
        "return": ReturnCommand(),
        "for": ForCommand(),
        "next": NextCommand(),
        "list": ListCommand(),
        "bye": ByeCommand(),
        "stop": StopCommand(),
    }

    @classmethod
    def load_program(cls, filename: str) -> None:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    line_number, line_code = cls.parse_line(line)
                    cls.code[line_number] = line_code

    @staticmethod
    def parse_line(line: str) -> Tuple[int, str]:
        line_number, *code_parts = line.split(maxsplit=1)
        line_number = int(line_number)
        code = code_parts[0] if code_parts else ""
        return line_number, code

    @classmethod
    def execute_line(cls, line: str) -> None:
        line = line.strip()
        if not line:
            return
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        if cmd in cls.commands:
            cls.commands[cmd].execute(args)
        elif "=" in line:
            LetCommand().execute(line)
        else:
            print(f"Syntax error: Unknown command '{cmd}'")

    @classmethod
    def run(cls) -> None:
        first_line = min(cls.code.keys(), default=None)
        if first_line is None:
            print("No program loaded!")
            return
        cls.vars["#"] = first_line
        while cls.vars["#"] > 0:
            next_line = next(
                ((n, ln) for (n, ln) in sorted(cls.code.items()) if n >= cls.vars["#"]), 
                (0, None)
            )
            if next_line[1] is None:
                break
            cls.vars["#"], line = next_line
            if line:
                cls.execute_line(line)
                if cls.vars["#"] == next_line[0]:
                    cls.vars["#"] += 1
            else:
                break

    @classmethod
    def evaluate_expression(cls, expr: str) -> Tuple[Any, str]:
        try:
            parser = Parser(expr)
            result = parser.expr()
            return result, expr
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            return 0, expr

def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            for line in f:
                parser = Parser(line)
                lineno = parser._parse_number()
                if lineno:
                    Interpreter.code[lineno] = parser.line
                else:
                    Interpreter.execute_line(parser.line)
        Interpreter.run()
    else:
        for line in sys.stdin:
            parser = Parser(line)
            lineno = parser._parse_number()
            if lineno:
                Interpreter.code[lineno] = parser.line
            else:
                Interpreter.execute_line(parser.line)

if __name__ == "__main__":
    main()