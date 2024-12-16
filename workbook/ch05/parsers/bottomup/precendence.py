
class OperatorPrecedenceParser:
    def __init__(self):
        # precedence and associativity (left or right)
        self.operators = {
            '+': (1, 'L'),  # precedence 1, left-associative
            '-': (1, 'L'),
            '*': (2, 'L'),
            '/': (2, 'L')
        }

    def is_operator(self, token):
        return token in self.operators

    def precedence(self, operator):
        return self.operators[operator][0]

    def associativity(self, operator):
        return self.operators[operator][1]

    def to_postfix(self, infix_tokens):
        output = []
        stack = []
        for token in infix_tokens:
            if token.isnumeric():
                output.append(token)
            elif self.is_operator(token):
                while (stack and stack[-1] != '(' and
                       (self.precedence(stack[-1]) > self.precedence(token) or
                        (self.precedence(stack[-1]) == self.precedence(token) and
                         self.associativity(token) == 'L'))):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # pop the '('
        while stack:
            output.append(stack.pop())
        return output

    def to_prefix(self, infix_tokens):
        reversed_tokens = infix_tokens[::-1]
        # swap '(' with ')' and vice versa
        swapped_tokens = ['(' if t == ')' else ')' if t == '(' else t for t in reversed_tokens]
        postfix = self.to_postfix(swapped_tokens)
        return postfix[::-1]

    def evaluate_postfix(self, postfix_tokens):
        stack = []
        for token in postfix_tokens:
            if token.isnumeric():
                stack.append(int(token))
            elif self.is_operator(token):
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    stack.append(a / b)
        return stack[0]

    def evaluate_prefix(self, prefix_tokens):
        stack = []
        for token in reversed(prefix_tokens):
            if token.isnumeric():
                stack.append(int(token))
            elif self.is_operator(token):
                a = stack.pop()
                b = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    stack.append(a / b)
        return stack[0]


# example
parser = OperatorPrecedenceParser()

infix = "3 + 5 * ( 2 - 8 ) / 4"
infix_tokens = infix.split()  # simple tokenize

# to postfix and prefix from infix
postfix = parser.to_postfix(infix_tokens)
prefix = parser.to_prefix(infix_tokens)

# eval to make it more interesting, check
postfix_result = parser.evaluate_postfix(postfix)
prefix_result = parser.evaluate_prefix(prefix)

print("Infix:  ", infix)
print("Postfix:", ' '.join(postfix))
print("Prefix: ", ' '.join(prefix))
print("Postfix Result:", postfix_result)
print("Prefix Result: ", prefix_result)
