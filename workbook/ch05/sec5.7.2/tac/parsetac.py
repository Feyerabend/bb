
import re

class TACParser:
    def __init__(self, code):
        self.tokens = code.splitlines()
        self.current = 0

    def parse(self):
        program = []
        while not self.is_end():
            statement = self.parse_statement()
            if statement:
                program.append(statement)
        return program

    def parse_statement(self):
        line = self.peek().strip()
        
        # assignment
        if "=" in line and not line.startswith("if") and not line.startswith("label"):
            return self.parse_assignment()

        # if ..
        if line.startswith("if"):
            return self.parse_if_statement()

        # goto ..
        if line.startswith("goto"):
            return self.parse_goto_statement()

        # label:
        if line.startswith("label"):
            return self.parse_label()

        # print ..
        if line.startswith("print"):
            return self.parse_print_statement()

        # unknown
        self.advance()
        return None

    def parse_assignment(self):
        line = self.advance().strip()
        left, right = map(str.strip, line.split("=", 1))
        return {"type": "assignment", "left": left, "right": self.parse_expression(right)}

    def parse_expression(self, expr):
        # split terms and operators
        tokens = re.split(r"([+\-*/<>=!&|]+)", expr)
        tokens = [token.strip() for token in tokens if token.strip()]
        
        if len(tokens) == 1:
            return {"type": "term", "value": tokens[0]}
        elif len(tokens) == 3:
            return {"type": "binary_op", "left": tokens[0], "operator": tokens[1], "right": tokens[2]}
        else:
            raise ValueError(f"Invalid expression: {expr}")

    def parse_if_statement(self):
        line = self.advance().strip()
        _, condition, _, label = line.split()
        return {"type": "if", "condition": self.parse_expression(condition), "label": label}

    def parse_goto_statement(self):
        line = self.advance().strip()
        _, label = line.split()
        return {"type": "goto", "label": label}

    def parse_label(self):
        line = self.advance().strip()
        label_name = line.split()[1].strip(":")
        return {"type": "label", "name": label_name}

    def parse_print_statement(self):
        line = self.advance().strip()
        _, value = line.split()
        return {"type": "print", "value": value}

    def peek(self):
        if not self.is_end():
            return self.tokens[self.current]
        return None

    def advance(self):
        if not self.is_end():
            self.current += 1
            return self.tokens[self.current - 1]
        return None

    def is_end(self):
        return self.current >= len(self.tokens)


def test_tac_parser():
    code = """
x = 10
t1 = x < 15
label label_1:
if t1 goto label_2
t2 = x + 1
x = t2
print x
goto label_1
label label_2:
"""
    parser = TACParser(code)
    result = parser.parse()

    import pprint
    pprint.pprint(result)

if __name__ == "__main__":
    test_tac_parser()
