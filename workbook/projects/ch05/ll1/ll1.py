class LL1Parser:
    def __init__(self, input):
        self.input = input
        self.pos = 0

    def lookahead(self):
        return self.input[self.pos] if self.pos < len(self.input) else None

    def eat(self, expected):
        if self.lookahead() == expected:
            self.pos += 1
        else:
            raise Exception(f"Error: Expected {expected} but found {self.lookahead()}")

    def E(self):
        self.T()
        self.E_prime()

    def E_prime(self):
        if self.lookahead() == '+':
            self.eat('+')
            self.T()
            self.E_prime()

    def T(self):
        if self.lookahead() == 'i':  # assuming 'i' represents an integer
            self.eat('i')
            self.T_prime()
        elif self.lookahead() == '(':
            self.eat('(')
            self.E()
            self.eat(')')

    def T_prime(self):
        if self.lookahead() == '*':
            self.eat('*')
            self.T()
            self.T_prime()

    def parse(self):
        self.E()
        if self.lookahead() is None:
            print("Input parsed successfully!")
        else:
            print("Error: Unexpected input at end")

# Example usage
input_string = "i+i*i"  # example input
parser = LL1Parser(input_string)
parser.parse()
