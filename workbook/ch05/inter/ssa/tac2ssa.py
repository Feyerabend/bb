import re

# generate temp. variable names
def generate_temp_var(temp_count):
    return f"t{temp_count}"

# tokenize input string (handle parentheses)
def tokenize(expr):
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

    for token in tokens:
        if token.isdigit() or token.isalpha():  # operand
            stack.append(token)
        elif token == '(':
            stack.append('(')
        elif token == ')':
            operands = []
            while stack and stack[-1] != '(':
                operands.append(stack.pop())
            if not stack or stack[-1] != '(':
                raise IndexError(f"Mismatched parentheses. Stack state: {stack}")
            stack.pop()  # remove '('
            operands.reverse()
            while len(operands) >= 3:
                arg1 = operands.pop(0)
                operator = operands.pop(0)
                arg2 = operands.pop(0)
                result = generate_temp_var(temp_count)
                temp_count += 1
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                operands.insert(0, result)
            stack.extend(operands)
        elif token in '+-*/':  # operator
            while (len(stack) >= 3 and precedence(stack[-2]) >= precedence(token)):
                arg2 = stack.pop()
                operator = stack.pop()
                arg1 = stack.pop()
                result = generate_temp_var(temp_count)
                temp_count += 1
                tac.append(f"{result} = {arg1} {operator} {arg2}")
                stack.append(result)
            stack.append(token)

    while len(stack) > 1:
        arg2 = stack.pop()
        operator = stack.pop()
        arg1 = stack.pop()
        result = generate_temp_var(temp_count)
        temp_count += 1
        tac.append(f"{result} = {arg1} {operator} {arg2}")
        stack.append(result)

    return tac

# Convert TAC to SSA
def convert_to_ssa(tac):
    var_map = {}
    ssa_tac = []
    for instr in tac:
        result, operation = instr.split(" = ")
        # Increment variable version for result
        if result not in var_map:
            var_map[result] = 0
        else:
            var_map[result] += 1
        new_result = f"{result}_{var_map[result]}"

        # Replace arguments with their latest SSA version
        args = re.split(r' (\+|-|\*|/) ', operation)
        updated_args = []
        for arg in args:
            if arg in var_map:
                updated_args.append(f"{arg}_{var_map[arg]}")
            else:
                updated_args.append(arg)
        new_operation = " ".join(updated_args)
        ssa_tac.append(f"{new_result} = {new_operation}")
    return ssa_tac

def main():
    expr = "a + (b * c) / 5 - 8"
    print("Input:", expr)
    tokens = tokenize(expr)
    tac = parse_to_tac(tokens)
    print("\nGenerated Three-Address Code (TAC):")
    for line in tac:
        print(line)
    ssa_tac = convert_to_ssa(tac)
    print("\nEnhanced TAC in SSA Form:")
    for line in ssa_tac:
        print(line)

if __name__ == "__main__":
    main()
