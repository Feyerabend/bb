
import re
import sys
import os.path


TOKENS = [
    ('CLASS', r'\bclass\b'),
    ('INHERITS', r'\binherits\b'),
    ('DEF', r'\bdef\b'),
    ('PRINT', r'\bprint\b'),
    ('THIS', r'\bthis\b'),
    ('STRING', r'"[^"]*"'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('SEMI', r';'),
    ('DOT', r'\.'),
    ('SKIP', r'\s+'),
]

def lex(src):
    tokens = []
    pos = 0
    while pos < len(src):
        for tok_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(src, pos)
            if match:
                if tok_type != 'SKIP':
                    tokens.append((tok_type, match.group(0)))
                pos = match.end()
                break
        else:
            raise SyntaxError(f"Unexpected char: {src[pos]}")
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, tok_type):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] == tok_type

    def consume(self, expected_type):
        if self.peek(expected_type):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        else:
            current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else "EOF"
            raise SyntaxError(f"Expected {expected_type}, got {current_token[0]}")

    def parse_class(self):
        self.consume('CLASS')
        name = self.consume('ID')[1]
        parent = 'Object'
        if self.peek('INHERITS'):
            self.consume('INHERITS')
            parent = self.consume('ID')[1]
        self.consume('LBRACE')
        methods = []
        while not self.peek('RBRACE'):
            if self.peek('DEF'):
                self.consume('DEF')
                methods.append(self.parse_method())
        self.consume('RBRACE')
        return {'name': name, 'parent': parent, 'methods': methods}

    def parse_method(self):
        name = self.consume('ID')[1]
        self.consume('LPAREN')
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while not self.peek('RBRACE'):
            if self.peek('PRINT'):
                self.consume('PRINT')
                body.append(self.parse_print())
        self.consume('RBRACE')
        return {'name': name, 'body': body}

    def parse_print(self):
        self.consume('LPAREN')
        expr = self.consume('STRING')[1]
        self.consume('RPAREN')
        self.consume('SEMI')
        return {'type': 'print', 'value': f'{expr[:-1]}\\n"'}


def generate_c_code(ast):
    c_code = ['\n#include "oop_runtime.h"\n\n']
    class_name = ast["name"]

    # class struct
    c_code.append(f'typedef struct {ast["name"]} {{\n')
    c_code.append(f'    Object base;\n')
    c_code.append(f'}} {ast["name"]};\n\n')
    
    # VTable struct
    c_code.append(f'typedef struct {ast["name"]}VTable {{\n')
    c_code.append('    ObjectVTable base;\n')
    for method in ast['methods']:
        c_code.append(f'    void (*{method["name"]})(Object* self);\n')
    c_code.append(f'}} {ast["name"]}VTable;\n\n')
    
    # method implementations
    for method in ast['methods']:
        c_code.append(f'void {ast["name"]}_{method["name"]}(Object* self) {{\n')
        for stmt in method['body']:
            if stmt['type'] == 'print': # we only have one to care about
                c_code.append(f'    printf({stmt["value"]});\n')
        c_code.append('}\n\n')
    
    # VTable instance
    c_code.append(f'{class_name}VTable {class_name.lower()}_vtable = {{\n')
    c_code.append('    .base = { .destroy = object_destroy },\n')  # inherit default destructor
    for method in ast['methods']:
        c_code.append(f'    .{method["name"]} = {class_name}_{method["name"]},\n')
    c_code.append('};\n\n')
    
    # constructor
    c_code.append(f'{class_name}* {class_name}_create() {{\n')
    c_code.append(f'    {class_name}* self = malloc(sizeof({class_name}));\n')
    c_code.append(f'    self->base.vtable = (ObjectVTable*)&{class_name.lower()}_vtable;\n')
    c_code.append('    return self;\n}\n\n')
    
    # main
    c_code.append('int main() {\n')
    c_code.append(f'    {class_name}* obj = {class_name}_create();\n')
    c_code.append(f'    (({class_name}VTable*)obj->base.vtable)->{ast["methods"][0]["name"]}((Object*)obj);\n')
    c_code.append('    DELETE(obj);\n')
    c_code.append('    return 0;\n}\n')
    
    return ''.join(c_code)

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <inputfile.oo>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}.c"
    
    with open(input_file, 'r') as f:
        src = f.read()

    try:
        tokens = lex(src)
        parser = Parser(tokens)
        ast = parser.parse_class()
        c_code = generate_c_code(ast)
        
        with open(output_file, 'w') as f:
            f.write(c_code)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
