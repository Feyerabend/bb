import re
import pprint


class TACParser:
    def __init__(self, code):
        self.tokens = code.splitlines()
        self.current = 0
        self.symbol_table = { }

    def parse(self):
        program = []
        while not self.is_end():
            statement = self.parse_statement()
            if statement:
                program.append(statement)
        return program

    def parse_array_initialization(self):
        line = self.peek().strip()
        match = re.match(r"(\w+)\s*=\s*(\w+)\[(\d+)\]", line)
        if match:
            array_name, array_type, size = match.groups()
            size = int(size)
            self.symbol_table[array_name] = {'type': 'array', 'value': {'type': array_type, 'size': size}}
            self.advance()
            return {'type': 'array_initialization', 'name': array_name, 'type': array_type, 'size': size}
        raise ValueError(f"Invalid array initialization: {line}")

    def parse_statement(self):
        line = self.peek().strip()

        if "=" in line and re.match(r"\w+\s*=\s*\w+\[\d+\]", line):
            return self.parse_array_initialization()

        if "=" in line and "[" in line:
            return self.parse_array_assignment()

        if "=" in line and not line.startswith("if") and not line.startswith("label"):
            return self.parse_assignment()

        # if ..
        if line.startswith("if"):
            return self.parse_if_statement()

        # goto ..
        if line.startswith("goto"):
            return self.parse_goto_statement()

        # label:
        if line.endswith(":"):
            return self.parse_label()

        # print ..
        if line.startswith("print"):
            return self.parse_print_statement()

        # unhandled line; advance cursor
        self.advance()
        return None

    def parse_assignment(self):
        line = self.advance().strip()
        left, right = map(str.strip, line.split("=", 1))
        expr = self.parse_expression(right)
        self.update_symbol_table(left, expr)
        return {"type": "assignment", "left": left, "right": expr}

    def parse_array_assignment(self):
        line = self.peek().strip()
        
        # match tarray access pattern: array_name[index] = value
        match = re.match(r"(\w+)\[(\d+)\]\s*=\s*(\d+)", line)
        if match:
            array_name, index, value = match.groups()
            index = int(index)
            value = int(value)
            
            # array defined?
            if array_name not in self.symbol_table or self.symbol_table[array_name]['type'] != 'array':
                raise ValueError(f"Invalid array access: {line}")
            
            # assignment: array_name[index] = value
            self.symbol_table[array_name][index] = value  # array stored as a list
            
            self.advance()  # move to next line
            return {'type': 'array_assignment', 'array': array_name, 'index': index, 'value': value}

        raise ValueError(f"Invalid array access: {line}")

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
        label_name = line.split()[0].strip(":")
        return {"type": "label", "name": label_name}

    def parse_print_statement(self):
        line = self.advance().strip()
        _, value = line.split()
        return {"type": "print", "value": value}

    def parse_expression(self, expr):
        expr = expr.strip()
        if self.is_constant(expr):
            return {"type": "term", "value": expr, "is_constant": True}

        if expr.startswith('(') and expr.endswith(')'):
            return self.parse_expression(expr[1:-1])

        tokens = re.split(r"([+\-*/<>=!&|]+)", expr)
        tokens = [token.strip() for token in tokens if token.strip()]

        if len(tokens) == 1:
            return {"type": "term", "value": tokens[0], "is_constant": self.is_constant(tokens[0])}
        elif len(tokens) == 3:
            left = self.parse_expression(tokens[0])
            operator = tokens[1]
            right = self.parse_expression(tokens[2])
            return {"type": "binary_op", "left": left, "operator": operator, "right": right}
        else:
            raise ValueError(f"Invalid expression: {expr}")

    def extract_array_access(self, expr):
        match = re.match(r"(\w+)\[(.+)\]", expr)
        if not match:
            raise ValueError(f"Invalid array access: {expr}")
        array_name, index = match.groups()
        return array_name, self.parse_expression(index)

    def update_symbol_table(self, name, value):
        if "is_constant" in value and value["is_constant"]:
            # if constant, detect type based on value
            if '.' in value["value"]:
                value_type = "float"  # contains decimal point
            else:
                value_type = "int"
            self.symbol_table[name] = {"type": value_type, "value": value["value"]}
        elif value.get("type") == "array":
            if name not in self.symbol_table:
                self.symbol_table[name] = {"type": "array", "contents": {}, "base_type": value["value"]["type"]}
            self.symbol_table[name]["contents"][value["index"]["value"]] = value["value"]
        else:
            # other variables (non-constants, non-arrays)
            self.symbol_table[name] = {"type": "variable", "value": None}

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

    def is_constant(self, value):
        return re.match(r"^\d+(\.\d+)?$", value) is not None


def test_tac_parser():
    code_1 = """
x = 10
t1 = x < 15
label_1:
if t1 goto label_2
t2 = x + 1
x = t2
print x
goto label_1
label_2:
"""
    parser_1 = TACParser(code_1)
    result_1 = parser_1.parse()
    print("\Parse 1")
    pprint.pprint(result_1)
    print("\nSymbol Table 1:")
    pprint.pprint(parser_1.symbol_table)

    code_2 = """
int_array = int[10]
float_array = float[5]
int_array[0] = 42
t1 = int_array[0]
float_array[2] = 3.14
t2 = float_array[2]
print t1
print t2
"""
    parser_2 = TACParser(code_2)
    result_2 = parser_2.parse()
    print("\nParse 2")
    pprint.pprint(result_2)
    print("\nSymbol Table 2:")
    pprint.pprint(parser_2.symbol_table)

    code_3 = """
x = 9
y = 20.786
t1 = x + 5
t2 = y + 3.14
print t1
print t2
"""
    parser_3 = TACParser(code_3)
    result_3 = parser_3.parse()

    print("\nParse 3")
    pprint.pprint(result_3)
    print("\nSymbol Table:")
    pprint.pprint(parser_3.symbol_table)


if __name__ == "__main__":
    test_tac_parser()

