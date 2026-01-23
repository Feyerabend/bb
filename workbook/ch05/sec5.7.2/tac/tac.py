import re

# generate temp. variable names
def generate_temp_var(temp_count):
    return f"t{temp_count}"

# tokenize input string (handle parentheses)
def tokenize(expr):
    # regexp to match numbers, variables, and operators
    token_pattern = r'\d+|[a-zA-Z]+|[()+\-*/]'
    tokens = re.findall(token_pattern, expr)
    print("Tokens:", tokens)
    return tokens

def precedence(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0

# convert to TAC
def parse_to_tac(tokens):
    tac = []  # Three Address Code instructions
    temp_count = 0  # counter for temp vars
    stack = []  # operands and operators

    # loop through each token
    for token in tokens:
        print(f"\nProcessing token: {token}")

        if token.isdigit() or token.isalpha():  # operand (numbers or variables)
            stack.append(token)
            print(f"Stack after operand '{token}': {stack}")

        elif token == '(':  # left parenthesis - push to stack
            stack.append('(')
            print(f"Stack after '(': {stack}")

        elif token == ')':  # right parenthesis - pop until left parenthesis
            print(f"Processing ')', Stack before popping: {stack}")
            operands = []  # temporary list for operands within parentheses
            while stack and stack[-1] != '(':
                operands.append(stack.pop())  # collect operands and operators
            if not stack or stack[-1] != '(':
                raise IndexError(f"Mismatched parentheses. Stack state: {stack}")
            stack.pop()  # remove '('

            # generate TAC for the operands collected
            operands.reverse()  # reverse to get the correct order
            while len(operands) >= 3:
                arg1 = operands.pop(0)
                operator = operands.pop(0)
                arg2 = operands.pop(0)
                result = generate_temp_var(temp_count)
                temp_count += 1
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                operands.insert(0, result)  # push result back to operands list
                print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Remaining operands: {operands}")
            stack.extend(operands)  # push any remaining operands back to the stack
            print(f"Stack after ')': {stack}")

        elif token in '+-*/':  # Operator
            print(f"Processing operator: {token}, Stack before checking precedence: {stack}")
            while (len(stack) >= 3 and precedence(stack[-2]) >= precedence(token)):
                arg2 = stack.pop()
                operator = stack.pop()
                arg1 = stack.pop()
                result = generate_temp_var(temp_count)
                temp_count += 1
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                stack.append(result)  # Push result back to stack
                print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Stack after pushing result: {stack}")
            stack.append(token)
            print(f"Stack after adding operator '{token}': {stack}")

    # final
    print(f"\nStack before final processing: {stack}")
    while len(stack) > 1:
        arg2 = stack.pop()
        operator = stack.pop()
        arg1 = stack.pop()
        result = generate_temp_var(temp_count)
        temp_count += 1
        tac.append(f"{result} = {arg1} {operator} {arg2}")
        stack.append(result)  # push final result back to stack
        print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Stack after pushing result: {stack}")

    print("\nGenerated Three-Address Code:")
    for instruction in tac:
        print(instruction)

def main():
    # input
    expr = "a + (b * c) / 5 - 8"
    print("Input:")
    print(expr)

    tokens = tokenize(expr)

    parse_to_tac(tokens)

if __name__ == "__main__":
    main()