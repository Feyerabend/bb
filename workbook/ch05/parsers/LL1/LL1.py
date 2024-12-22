
import re

class LL1Parser:
    def __init__(self, input):
        self.tokens = self.tokenize(input)
        self.tokens.append('$')  # end-of-input marker $
        self.pos = 0
        self.stack = ['$', 'E']  # stack starts with $ and the start symbol

        # parsing table
        self.table = {
            'E': {
                'num': ['T', 'E\''],
                '(': ['T', 'E\'']
            },
            'E\'': {
                '+': ['+', 'T', 'E\''],
                '-': ['-', 'T', 'E\''],
                ')': [],
                '$': []
            },
            'T': {
                'num': ['F', 'T\''],
                '(': ['F', 'T\'']
            },
            'T\'': {
                '+': [],
                '-': [],
                '*': ['*', 'F', 'T\''],
                '/': ['/', 'F', 'T\''],
                ')': [],
                '$': []
            },
            'F': {
                'num': ['num'],
                '(': ['(', 'E', ')']
            }
        }

    def tokenize(self, input):
        token_pattern = r'\d+\.\d+|\d+|[+\-*/%^()]'
        raw_tokens = re.findall(token_pattern, input)
        tokens = []
        for token in raw_tokens:
            if re.match(r'^\d+(\.\d+)?$', token):
                tokens.append('num')  # map numbers to 'num'
            else:
                tokens.append(token)  # keep operators and parentheses as-is
        print(f"Tokens: {tokens}")
        return tokens

    def lookahead(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        while self.stack:
            top = self.stack.pop()
            token = self.lookahead()

            if top in self.table:  # non-terminal
                if token in self.table[top]:
                    production = self.table[top][token]
                    print(f"Applying production {top} → {' '.join(production) if production else 'ε'}")
                    self.stack.extend(reversed(production))  # push production onto the stack
                else:
                    raise Exception(f"Error: Unexpected token {token} for {top}")

            elif top == token:  # terminal matches input
                if token == '$':
                    print("Parsing completed successfully!")
                    return
                print(f"Consuming: {token}")
                self.pos += 1

            else:
                raise Exception(f"Error: Unexpected token {token}. Expected {top}")

        if self.lookahead() == '$':
            print("Parsing completed successfully!")
        else:
            raise Exception(f"Error: Unexpected input at end. Found {self.lookahead()}")


input_string = "3 + 2 * 4"
parser = LL1Parser(input_string)
parser.parse()