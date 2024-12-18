import re

# Generate temporary variable names
def generate_temp_var(temp_count):
    return f"t{temp_count}"

# Tokenize the input string (handle parentheses)
def tokenize(expr):
    # Regular expression to match numbers, variables, and operators
    token_pattern = r'\d+|[a-zA-Z]+|[()+\-*/]'
    tokens = re.findall(token_pattern, expr)
    print("Tokens:", tokens)  # Debugging statement to print the tokens
    return tokens

# Handle precedence
def precedence(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0

# Convert the tokens into TAC
def parse_to_tac(tokens):
    tac = []  # Stores the Three Address Code instructions
    temp_count = 0  # Counter for temporary variables
    stack = []  # Stack for operands and operators

    # Loop through each token
    for token in tokens:
        print(f"\nProcessing token: {token}")  # Debugging statement for each token
        if token.isdigit() or token.isalpha():  # Operand (numbers or variables)
            stack.append(token)
            print(f"Stack after operand '{token}': {stack}")  # Debugging statement to print stack
        elif token == '(':  # Left parenthesis - push to stack
            stack.append('(')
            print(f"Stack after '(': {stack}")  # Debugging statement to print stack
        elif token == ')':  # Right parenthesis - pop until left parenthesis
            print(f"Processing ')', Stack before popping: {stack}")  # Debugging before popping
            while stack and stack[-1] != '(':
                if len(stack) < 3:
                    raise IndexError(f"Not enough operands or operators in the stack for popping. Stack state: {stack}")
                
                arg2 = stack.pop()
                arg1 = stack.pop()
                operator = stack.pop()
                result = generate_temp_var(temp_count)
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                stack.append(result)  # Push result back to stack
                print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Stack after pushing result: {stack}")  # Debugging
            if stack and stack[-1] == '(':  # Pop '('
                stack.pop()
            print(f"Stack after ')': {stack}")  # Debugging statement for stack after ')'
        elif token in '+-*/':  # Operator
            print(f"Processing operator: {token}, Stack before checking precedence: {stack}")  # Debugging before operator
            while (len(stack) >= 3 and precedence(stack[-2]) >= precedence(token)):
                if len(stack) < 3:
                    raise IndexError(f"Not enough operands or operators in the stack for popping. Stack state: {stack}")
                
                arg2 = stack.pop()
                arg1 = stack.pop()
                operator = stack.pop()
                result = generate_temp_var(temp_count)
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                stack.append(result)  # Push result back to stack
                print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Stack after pushing result: {stack}")  # Debugging
            stack.append(token)
            print(f"Stack after adding operator '{token}': {stack}")  # Debugging

    # Generate final result
    print(f"\nStack before final processing: {stack}")  # Debugging before final popping
    while len(stack) > 1:
        if len(stack) < 3:
            raise IndexError(f"Not enough operands or operators in the stack for final processing. Stack state: {stack}")
        
        arg2 = stack.pop()
        arg1 = stack.pop()
        operator = stack.pop()
        result = generate_temp_var(temp_count)
        tac.append(f"{result} = {arg1} {operator} {arg2}")
        stack.append(result)  # Push final result back to stack
        print(f"Generated TAC: {result} = {arg1} {operator} {arg2}, Stack after pushing result: {stack}")  # Debugging

    # Print TAC instructions
    print("\nGenerated Three-Address Code:")
    for instruction in tac:
        print(instruction)

def main():
    # Input expression
    expr = "a + ( b * c ) / 5 - 8"
    print("Input:")
    print(expr)

    # Tokenize the expression
    tokens = tokenize(expr)

    # Parse the tokens to generate Three Address Code (TAC)
    parse_to_tac(tokens)

if __name__ == "__main__":
    main()