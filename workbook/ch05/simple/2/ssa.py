ssa_program = [
    {"type": "assignment", "left": "x_0", "right": {"type": "term", "value": 10}},
    {"type": "assignment", "left": "t1_0", "right": {"type": "binary_op", "left": "x_0", "operator": "<", "right": 15}},
    {"type": "label", "name": "label_1"},
    {"type": "if", "condition": {"type": "term", "value": "t1_0"}, "label": "label_2"},
    {"type": "assignment", "left": "t2_0", "right": {"type": "binary_op", "left": "x_0", "operator": "+", "right": 1}},
    {"type": "assignment", "left": "x_1", "right": {"type": "term", "value": "t2_0"}},
    {"type": "goto", "label": "label_1"},
    {"type": "label", "name": "label_2"},
    {"type": "phi", "left": "x", "args": ["x_0", "x_1"]},
    {"type": "assignment", "left": "t1", "right": {"type": "term", "value": "t1_0"}}
]

def optimize_program_first(program):
    constants = {}
    optimized_program = []

    for instruction in program:
        if instruction["type"] == "assignment":
            left = instruction["left"]
            right = instruction["right"]

            if right["type"] == "term" and isinstance(right["value"], (int, float)):
                # Handle constant assignment
                constants[left] = right["value"]
                optimized_program.append({"type": "assignment", "left": left, "right": {"type": "term", "value": right["value"]}})
            elif right["type"] == "binary_op":
                # Handle binary operations
                left_operand = constants.get(right["left"], right["left"])
                right_operand = constants.get(right["right"], right["right"])

                if isinstance(left_operand, (int, float)) and isinstance(right_operand, (int, float)):
                    # Perform constant folding
                    if right["operator"] == "+":
                        value = left_operand + right_operand
                    elif right["operator"] == "-":
                        value = left_operand - right_operand
                    elif right["operator"] == "*":
                        value = left_operand * right_operand
                    elif right["operator"] == "/":
                        value = left_operand / right_operand
                    else:
                        # Handle unknown operators
                        value = None

                    if value is not None:
                        constants[left] = value
                        optimized_program.append({"type": "assignment", "left": left, "right": {"type": "term", "value": value}})
                else:
                    # Leave the binary operation as-is if operands aren't constants
                    optimized_program.append({"type": "assignment", "left": left, "right": {"type": "binary_op", "left": left_operand, "operator": right["operator"], "right": right_operand}})
            else:
                # General case: Keep the assignment as-is
                optimized_program.append(instruction)
        elif instruction["type"] == "if":
            condition = instruction["condition"]["value"]
            if condition in constants:
                condition = constants[condition]
            optimized_program.append({"type": "if", "condition": {"type": "term", "value": condition}, "label": instruction["label"]})
        elif instruction["type"] == "goto":
            optimized_program.append({"type": "goto", "label": instruction["label"]})
        elif instruction["type"] == "label":
            optimized_program.append({"type": "label", "name": instruction["name"]})
        else:
            # Handle unrecognized instructions
            optimized_program.append(instruction)

    return optimized_program

def resolve_phi_after_optimization(program):
    resolved_program = []
    phi_nodes = {}

    for instruction in program:
        if isinstance(instruction, dict) and instruction["type"] == "phi":
            left = instruction["left"]
            args = instruction["args"]
            if len(set(args)) == 1:
                phi_nodes[left] = args[0]  # Single unique value, directly assign it
            else:
                phi_nodes[left] = args  # Retain `phi` if unresolved
        else:
            resolved_program.append(instruction)

    # Replace `phi` nodes in assignments
    for instruction in resolved_program:
        if isinstance(instruction, dict) and instruction["type"] == "assignment":
            right = instruction["right"]
            if right["type"] == "term" and right["value"] in phi_nodes:
                right["value"] = phi_nodes[right["value"]]
    
    return resolved_program

# Step 1: Optimize the program
optimized_program = optimize_program_first(ssa_program)

# Step 2: Resolve phi functions
fully_resolved_program = resolve_phi_after_optimization(optimized_program)

def print_program(program):
    for line in program:
        if isinstance(line, dict):
            if line["type"] == "assignment":
                left = line["left"]
                right = line["right"]
                if right["type"] == "term":
                    print(f"{left} = {right['value']}")
                elif right["type"] == "binary_op":
                    left_operand = right["left"]
                    operator = right["operator"]
                    right_operand = right["right"]
                    print(f"{left} = {left_operand} {operator} {right_operand}")
            elif line["type"] == "if":
                condition = line["condition"]["value"]
                label = line["label"]
                print(f"if {condition} goto {label}")
            elif line["type"] == "goto":
                label = line["label"]
                print(f"goto {label}")
            elif line["type"] == "label":
                print(f"label {line['name']}:")
            else:
                print(f"Unknown instruction type: {line}")
        else:
            print(f"Unknown line format: {line}")

print("Final Optimized and Resolved Program:")
print_program(fully_resolved_program)