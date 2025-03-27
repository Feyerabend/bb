#!/usr/bin/env python3
import sys
import re

class Parser:
    def __init__(self, line):
        self.line = line.strip()

    def num(self):
        n, i = 0, 0
        while i < len(self.line) and self.line[i].isdigit():
            n = n * 10 + int(self.line[i])
            i += 1
        self.line = self.line[i:].strip()
        return n

    def string_function(self):
        func_match = re.match(r'([A-Z]+)\$\((.*?)\)', self.line)
        if func_match:
            func_name = func_match.group(1)
            args = [a.strip() for a in func_match.group(2).split(',')]
            evaluated_args = [Parser(arg).expr() for arg in args]
            base_str = str(evaluated_args[0]) if len(evaluated_args) > 0 else ""
            
            if func_name == "LEFT":
                # LEFT$(string, length)
                length = int(evaluated_args[1]) if len(evaluated_args) > 1 else 0
                return base_str[:length]
            
            elif func_name == "RIGHT":
                # RIGHT$(string, length)
                length = int(evaluated_args[1]) if len(evaluated_args) > 1 else 0
                return base_str[-length:]
            
            elif func_name == "MID":
                # MID$(string, start, [length])
                start = int(evaluated_args[1]) - 1 if len(evaluated_args) > 1 else 0
                length = int(evaluated_args[2]) if len(evaluated_args) > 2 else len(base_str) - start
                return base_str[start:start+length]
            
            elif func_name == "LEN":
                # LEN$(string)
                return len(base_str)
            
            elif func_name == "STR":
                # STR$(number) - converts number to string
                return str(base_str)
        
        return None

    def expr(self):
        res = self.term()
        s = self.line
        while s and s[0] in "+-=<|>":
            op, self.line = s[0], s[1:].strip()
            next_term = self.term()

            def coerce_types(a, b):
                if isinstance(a, str) and isinstance(b, (int, float)):
                    return str(a), str(b)
                elif isinstance(a, (int, float)) and isinstance(b, str):
                    return str(a), str(b)
                return a, b

            res, next_term = coerce_types(res, next_term)
            
            if op == "+":
                if isinstance(res, str) and isinstance(next_term, str):
                    res += next_term
                elif isinstance(res, (int, float)) and isinstance(next_term, (int, float)):
                    res += next_term
                else:
                    raise ValueError(f"Cannot add {type(res)} and {type(next_term)}")
            
            elif op == "-":
                if isinstance(res, (int, float)) and isinstance(next_term, (int, float)):
                    res -= next_term
                else:
                    raise ValueError("Subtraction only supported for numeric types")
            
            elif op == "=":
                res = 1 if res == next_term else 0
            
            elif op == "<":
                res = 1 if res < next_term else 0
            
            elif op == ">":
                res = 1 if res > next_term else 0
            
            s = self.line
        return res

    def term(self):
        res, s = self.factor(), self.line
        while s and s[0] in "*/":
            op, self.line = s[0], s[1:].strip()
            n = self.factor()
            if op == "*": res *= n
            if op == "/" and n != 0: res /= n
        return res

    def factor(self):
        str_func_result = self.string_function()
        if str_func_result is not None:
            return str_func_result

        if self.line and self.line[0] == "(":
            self.line = self.line[1:].strip()
            res = self.expr()
            self.line = self.line[1:].strip()  # closing ')'
            return res
        elif self.line.startswith('"'):
            return self.string()
        elif self.line and self.line[0].isdigit():
            return self.num()
        else:
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
 
    def string(self):
        match = re.match(r'"([^"]*)"', self.line)
        if match:
            self.line = self.line[len(match.group(0)):].strip()
            return match.group(1)
        return ""


class Command:
    def execute(self, args):
        pass


class PrintCommand(Command):
    def execute(self, args):
        expressions = args.split(";")
        output = []
        for expr in expressions:
            value = Parser(expr.strip()).expr()
            if isinstance(value, (list, tuple)):
                value = value[0]
            if str(value) == '0': # hack to get rid of 0
                continue
            output.append(str(value))
        print(" ".join(output).strip())


class InputCommand(Command):
    def execute(self, args):
        parts = args.split(";", 1)
        prompt = "> "
        var_name = args.strip()

        if len(parts) > 1:
            prompt = Parser(parts[0].strip()).string() + " "
            var_name = parts[1].strip()

        input_value = input(prompt).strip()

        if var_name.endswith("$"):  # String
            Interpreter.vars[var_name] = input_value
        else:  # Numeric
            try:
                Interpreter.vars[var_name] = int(input_value)
            except ValueError:
                try:
                    Interpreter.vars[var_name] = float(input_value)
                except ValueError:
                    Interpreter.vars[var_name] = None

        # Make sure no unintended output happens
        if var_name in Interpreter.vars and Interpreter.vars[var_name] is None:
            del Interpreter.vars[var_name]


class LetCommand(Command):
    def execute(self, args):
        var, expr = args.split("=", 1)
        try:
            Interpreter.vars[var.strip()] = Parser(expr.strip()).expr()
        except Exception as e:
            print(f"Error parsing expression: {e}")


class IfCommand(Command):
    def execute(self, args):
        # find " THEN " respecting quotes
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
    def execute(self, args):
        line_num = Parser(args).expr()
        if line_num in Interpreter.code:
            Interpreter.vars["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")


class GosubCommand(Command):
    def execute(self, args):
        line_num = Parser(args).expr()
        if line_num in Interpreter.code:
            Interpreter.stack.append(Interpreter.vars["#"])
            Interpreter.vars["#"] = line_num
        else:
            print(f"Error: Line {line_num} does not exist.")


class ReturnCommand(Command):
    def execute(self, args):
        if Interpreter.stack:
            Interpreter.vars["#"] = Interpreter.stack.pop()


class ForCommand(Command):
    def execute(self, args):
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
    def execute(self, args):
        var = args.strip()
        if var in Interpreter.loops:
            start_line, end_value = Interpreter.loops[var]
            Interpreter.vars[var] += 1
            if Interpreter.vars[var] <= end_value:
                Interpreter.vars["#"] = start_line + 1  # line after the FOR line
            else:
                del Interpreter.loops[var]  # exit
                # move to next executable line after loop
                next_line = next(((n, ln) for (n, ln) in sorted(Interpreter.code.items()) if n > Interpreter.vars["#"]), (None, None))
                Interpreter.vars["#"] = next_line[0] if next_line[0] else 0
        else:
            print(f"Error: NEXT without matching FOR for variable '{var}'")


class ListCommand(Command):
    def execute(self, args):
        for n, ln in sorted(Interpreter.code.items()):
            print(f"{n:3} {ln}")


class ByeCommand(Command):
    def execute(self, args):
        sys.exit(0)


class StopCommand(Command):
    def execute(self, args):
        print("STOP command executed. Exiting program.")
        sys.exit(0)  # exit


class RunCommand(Command):
    def execute(self, args):
        if Interpreter.code:
            Interpreter.vars["#"] = min(Interpreter.code.keys())  # start at lowest line number
            Interpreter.run()


class Interpreter:
    code = {}
    vars = {"#": 10} # first line, can be overridden
    stack = []
    loops = {}
    loop_stack = []  # stack to track loops (I, N, line number)

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

    @staticmethod
    def load_program(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    line_number, line_code = Interpreter.parse_line(line)
                    Interpreter.code[line_number] = line_code

    @staticmethod
    def parse_line(line):
        line_number, *code_parts = line.split(maxsplit=1)
        line_number = int(line_number)
        code = code_parts[0] if code_parts else ""
        return line_number, code

    @staticmethod
    def execute_line(line):
        line = line.strip()
        if not line:
            return
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        if cmd in Interpreter.commands:
            Interpreter.commands[cmd].execute(args)
        elif "=" in line:
            LetCommand().execute(line)
        else:
            print(f"Syntax error: Unknown command '{cmd}'")

    @staticmethod
    def run():
        first_line = min(Interpreter.code.keys(), default=None)
        if first_line is None:
            print("No program loaded!")
            return
        Interpreter.vars["#"] = first_line  # start
        while Interpreter.vars["#"] > 0:
            next_line = next(((n, ln) for (n, ln) in sorted(Interpreter.code.items()) if n >= Interpreter.vars["#"]), (0, None))
            if next_line[1] is None:
                break
            Interpreter.vars["#"], line = next_line
            if line:
                Interpreter.execute_line(line)
                if Interpreter.vars["#"] == next_line[0]:
                    Interpreter.vars["#"] += 1
            else:
                break

    @staticmethod
    def evaluate_expression(expr):
        try:
            parser = Parser(expr)
            result = parser.expr()
            return result, expr
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            return 0, expr


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            for line in f:
                parser = Parser(line)
                lineno = parser.num()
                if lineno:
                    Interpreter.code[lineno] = parser.line
                else:
                    Interpreter.execute_line(parser.line)
        Interpreter.run()
    else:
        for line in sys.stdin:
            parser = Parser(line)
            lineno = parser.num()
            if lineno:
                Interpreter.code[lineno] = parser.line
            else:
                Interpreter.execute_line(parser.line)


if __name__ == "__main__":
    main()
