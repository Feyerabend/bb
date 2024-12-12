import re

TOKEN_TYPES = [
    ('COMMAND', r'[A-Z]+'),  # commands like "USER", "PASS"
    ('NUMBER', r'\d+'),  # numbers like "220", "250"
    ('STRING', r'\S+'),  # any non-whitespace string
    ('NEWLINE', r'\n'),  # newline (here: end of message)
    ('WHITESPACE', r'\s+'),  # ignore whitespace
]

def tokenize(input_string):
    tokens = []
    position = 0
    while position < len(input_string):
        match = None
        for token_type, regex in TOKEN_TYPES:
            pattern = re.compile(regex)
            match = pattern.match(input_string, position)
            if match:
                value = match.group(0)
                if token_type != 'WHITESPACE':  # skip whitespace
                    tokens.append((token_type, value))
                position = match.end()
                break
        if not match:
            raise ValueError(f'Invalid character at position {position}')
    return tokens

class ShiftReduceParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.stack = []
        self.index = 0
        self.parse_tree = []

    def shift(self):
        token = self.tokens[self.index]
        self.stack.append(token)
        self.index += 1
        print(f"Shift: {token} -> Stack: {self.stack}")  # show/debug

    def reduce(self):
        print(f"Stack before reduce: {self.stack}")  # show/debug
        # Rule 1
        if len(self.stack) >= 2 and self.stack[-2][0] == 'COMMAND' and self.stack[-1][0] == 'NUMBER':
            rhs = [self.stack.pop(), self.stack.pop()]  # pop NUMBER and COMMAND
            lhs = ('S', rhs)
            self.stack.append(lhs)  # push new non-terminal
            self.parse_tree.append(lhs)  # store the parse tree step
            print(f"Reduced to S --> COMMAND NUMBER: {lhs}")  # show/debug
            return True

        # Rule 2
        elif len(self.stack) >= 2 and self.stack[-2][0] == 'COMMAND' and self.stack[-1][0] == 'STRING':
            rhs = [self.stack.pop(), self.stack.pop()]  # pop STRING and COMMAND
            lhs = ('S', rhs)
            self.stack.append(lhs)
            self.parse_tree.append(lhs)
            print(f"Reduced to S --> COMMAND STRING: {lhs}")  # show/debug
            return True
        
        # Rule 3
        elif len(self.stack) >= 2 and self.stack[-2][0] == 'S' and self.stack[-1][0] == 'S':
            rhs = [self.stack.pop(), self.stack.pop()]  # pop two S elements
            lhs = ('S', rhs)
            self.stack.append(lhs)
            self.parse_tree.append(lhs)
            print(f"Reduced to S --> S S: {lhs}")  # show/debug
            return True

        return False

    def parse(self):
        while self.index < len(self.tokens) or len(self.stack) > 1:
            # shift: next token onto the stack, if we have tokens left
            if self.index < len(self.tokens):
                token = self.tokens[self.index]
                if token[0] == 'NEWLINE':  # ignore NEWLINE
                    self.index += 1
                    continue
                self.shift()

            # reduce: reduction, if the top of the stack matches a rule
            reduced = False
            while self.reduce():  # try to apply reductions until no more can be applied
                reduced = True

            # if no reduction occurred and there are no more tokens to shift, exit loop
            if not reduced and self.index >= len(self.tokens):
                break

        # if we have exactly one item on the stack, we have a valid parse
        if len(self.stack) == 1 and isinstance(self.stack[0], tuple) and self.stack[0][0] == 'S':
            return self.parse_tree
        else:
            raise ValueError("Parsing failed: Invalid input or incomplete grammar")

# example
input_string = "USER 1234\nPASS secret\n"
tokens = tokenize(input_string)

# print tokens to verify
for token in tokens:
    print(token)

# parse tokens using bottom-up parser
parser = ShiftReduceParser(tokens)
parse_tree = parser.parse()

# output parse tree
for node in parse_tree:
    print(node)
