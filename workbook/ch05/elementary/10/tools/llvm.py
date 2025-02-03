# This function will generate the LLVM IR for the instructions provided
def generate_llvm_ir(instructions):
    llvm_ir = []
    
    # A dictionary to store variables (to simulate variable names and values)
    variables = {}
    
    for instruction in instructions:
        # Determine instruction type
        if instruction["TYPE"] == "LABEL":
            llvm_ir.append(f"{instruction['RESULT']}:")
        
        elif instruction["TYPE"] == "LOAD":
            var_name = instruction["RESULT"]
            value = instruction["ARG1"]
            # Store loaded value in the variable dictionary
            variables[var_name] = value
            llvm_ir.append(f"  {var_name} = load i32, i32* {value}, align 4")
        
        elif instruction["TYPE"] == "=":
            var_name = instruction["RESULT"]
            value = instruction["ARG1"]
            variables[var_name] = value
            llvm_ir.append(f"  {var_name} = {value}")
        
        elif instruction["TYPE"] == "*":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = mul i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == "+":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = add i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == "-":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = sub i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == "/":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = sdiv i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == ">":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = icmp sgt i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == "<":
            var_name = instruction["RESULT"]
            operand1 = instruction["ARG1"]
            operand2 = instruction["ARG2"]
            llvm_ir.append(f"  {var_name} = icmp slt i32 {operand1}, {operand2}")
        
        elif instruction["TYPE"] == "IF_NOT":
            condition = instruction["ARG1"]
            label = instruction["ARG2"]
            llvm_ir.append(f"  br i1 {condition}, label %{label}, label %next")
        
        elif instruction["TYPE"] == "GOTO":
            label = instruction["ARG1"]
            llvm_ir.append(f"  br label %{label}")
        
        elif instruction["TYPE"] == "RETURN":
            llvm_ir.append("  ret void")
        
        elif instruction["TYPE"] == "CALL":
            function_name = instruction["RESULT"]
            llvm_ir.append(f"  call void @{function_name}()")
    
    # Add the final return for the main function
    llvm_ir.append("  ret i32 0")
    
    return "\n".join(llvm_ir)


# Example instructions from the provided data
instructions = [
    {"TYPE": "LABEL", "ARG1": None, "ARG2": None, "RESULT": "multiply"},
    {"TYPE": "LOAD", "ARG1": "x.g", "ARG2": None, "RESULT": "t0"},
    {"TYPE": "=", "ARG1": "t0", "ARG2": None, "RESULT": "multiply.a.l"},
    {"TYPE": "LOAD", "ARG1": "y.g", "ARG2": None, "RESULT": "t1"},
    {"TYPE": "=", "ARG1": "t1", "ARG2": None, "RESULT": "multiply.b.l"},
    {"TYPE": "LOAD", "ARG1": "0", "ARG2": None, "RESULT": "t2"},
    {"TYPE": "=", "ARG1": "t2", "ARG2": None, "RESULT": "z.g"},
    {"TYPE": "LABEL", "ARG1": None, "ARG2": None, "RESULT": "L0"},
    {"TYPE": "LOAD", "ARG1": "multiply.b.l", "ARG2": None, "RESULT": "t3"},
    {"TYPE": "LOAD", "ARG1": "0", "ARG2": None, "RESULT": "t4"},
    {"TYPE": ">", "ARG1": "t3", "ARG2": "t4", "RESULT": "t5"},
    {"TYPE": "IF_NOT", "ARG1": "t5", "ARG2": "L1", "RESULT": None},
    {"TYPE": "LOAD", "ARG1": "2", "ARG2": None, "RESULT": "t6"},
    {"TYPE": "LOAD", "ARG1": "multiply.a.l", "ARG2": None, "RESULT": "t7"},
    {"TYPE": "*", "ARG1": "t6", "ARG2": "t7", "RESULT": "t8"},
    {"TYPE": "=", "ARG1": "t8", "ARG2": None, "RESULT": "multiply.a.l"},
    {"TYPE": "LOAD", "ARG1": "multiply.b.l", "ARG2": None, "RESULT": "t9"},
    {"TYPE": "LOAD", "ARG1": "2", "ARG2": None, "RESULT": "t10"},
    {"TYPE": "/", "ARG1": "t9", "ARG2": "t10", "RESULT": "t11"},
    {"TYPE": "=", "ARG1": "t11", "ARG2": None, "RESULT": "multiply.b.l"},
    {"TYPE": "GOTO", "ARG1": "L0", "ARG2": None, "RESULT": None},
    {"TYPE": "LABEL", "ARG1": None, "ARG2": None, "RESULT": "L1"},
    {"TYPE": "RETURN", "ARG1": None, "ARG2": None, "RESULT": None},
]

# Generate the LLVM IR
llvm_ir_code = generate_llvm_ir(instructions)
print(llvm_ir_code)