import re

TOKEN_SPEC = [
    ("NUMBER", r"\d+"),            # integer or decimal number
    ("IDENTIFIER", r"[a-zA-Z_]\w*"), # identifiers (variables)
    ("ASSIGN", r"="),             # assignment
    ("PLUS", r"\+"),              # addition
    ("MINUS", r"-"),              # subtraction
    ("TIMES", r"\*"),             # multiplication
    ("DIVIDE", r"/"),             # division operator
    ("LPAREN", r"\("),            # left parenthesis
    ("RPAREN", r"\)"),            # right parenthesis
    ("SEMICOLON", r";"),          # terminator for statements
    ("SKIP", r"[ \t]+"),          # skip spaces and tabs
    ("MISMATCH", r"."),           # any other character
]

def tokenize(code):
    token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
    token_re = re.compile(token_regex)
    tokens = []
    for match in token_re.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character: {value}")
        else:
            tokens.append((kind, value))
    return tokens

# example
code = "x = 2025; y = 1477; z = x + y - 5 * (7 + 9) / 2;"
tokens = tokenize(code)
print(tokens)
# Output: [('
# IDENTIFIER', 'x'),
#   ('ASSIGN', '='),
#   ('NUMBER', '2025'),
#   ('SEMICOLON', ';'),
# ('IDENTIFIER', 'y'),
#   ('ASSIGN', '='),
#   ('NUMBER', '1477'),
#   ('SEMICOLON', ';'),
# ('IDENTIFIER', 'z'),
#   ('ASSIGN', '='),
#       ('IDENTIFIER', 'x'),
#       ('PLUS', '+'),
#       ('IDENTIFIER', 'y'),
#       ('MINUS', '-'),
#           ('NUMBER', '5'),
#           ('TIMES', '*'),
#               ('LPAREN', '('),
#                   ('NUMBER', '7'),
#                   ('PLUS', '+'),
#                   ('NUMBER', '9'),
#               ('RPAREN', ')'),
#           ('DIVIDE', '/'),
#           ('NUMBER', '2'),
#           ('SEMICOLON', ';')]
