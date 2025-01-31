import sys

# Global variables for LLVM IR generation
llvm_code = []
temp_counter = 0
label_counter = 0

# Function to generate a new temporary variable
def new_temp():
    global temp_counter
    temp_counter += 1
    return f"%t{temp_counter}"

# Function to generate a new label
def new_label():
    global label_counter
    label_counter += 1
    return f"L{label_counter}"

# Function to emit LLVM IR
def emit(op, arg1=None, arg2=None, result=None):
    if op == "LOAD":
        llvm_code.append(f"{result} = load i32, i32* @{arg1}")
    elif op == "STORE":
        llvm_code.append(f"store i32 {arg1}, i32* @{result}")
    elif op == "ADD":
        llvm_code.append(f"{result} = add i32 {arg1}, {arg2}")
    elif op == "SUB":
        llvm_code.append(f"{result} = sub i32 {arg1}, {arg2}")
    elif op == "MUL":
        llvm_code.append(f"{result} = mul i32 {arg1}, {arg2}")
    elif op == "DIV":
        llvm_code.append(f"{result} = sdiv i32 {arg1}, {arg2}")
    elif op == "CMP":
        llvm_code.append(f"{result} = icmp eq i32 {arg1}, {arg2}")
    elif op == "BR":
        llvm_code.append(f"br i1 {arg1}, label %{result}, label %{arg2}")
    elif op == "LABEL":
        llvm_code.append(f"{arg1}:")
    elif op == "RETURN":
        llvm_code.append("ret void")
    elif op == "CALL":
        llvm_code.append(f"call void @{arg1}()")
    else:
        raise ValueError(f"Unknown operation: {op}")

# Function to process a single line of TAC
def process_tac_line(line):
    parts = line.strip().split()
    if not parts:
        return

    op = parts[0]
    if op == "LOAD":
        _, src, dest = parts
        emit("LOAD", src, result=dest)
    elif op == "STORE":
        _, src, dest = parts
        emit("STORE", src, result=dest)
    elif op == "ADD":
        _, src1, src2, dest = parts
        emit("ADD", src1, src2, dest)
    elif op == "SUB":
        _, src1, src2, dest = parts
        emit("SUB", src1, src2, dest)
    elif op == "MUL":
        _, src1, src2, dest = parts
        emit("MUL", src1, src2, dest)
    elif op == "DIV":
        _, src1, src2, dest = parts
        emit("DIV", src1, src2, dest)
    elif op == "CMP":
        _, src1, src2, dest = parts
        emit("CMP", src1, src2, dest)
    elif op == "IF_NOT":
        _, cond, label = parts
        emit("BR", cond, label, new_label())
    elif op == "GOTO":
        _, label = parts
        emit("BR", "1", label, label)
    elif op == "LABEL":
        _, label = parts
        emit("LABEL", label)
    elif op == "RETURN":
        emit("RETURN")
    elif op == "CALL":
        _, func = parts
        emit("CALL", func)
    else:
        raise ValueError(f"Unknown operation: {op}")

# Function to generate LLVM IR from TAC
def generate_llvm(tac_lines):
    global llvm_code
    llvm_code = []

    # Emit global variable declarations
    llvm_code.append("@a.g = global i32 0")
    llvm_code.append("@b.g = global i32 0")
    llvm_code.append("@gcd.g = global i32 0")

    # Process each line of TAC
    for line in tac_lines:
        process_tac_line(line)

    return llvm_code

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python tac_to_llvm.py <tac_file>")
        return

    # Read TAC file
    tac_file = sys.argv[1]
    with open(tac_file, "r") as file:
        tac_lines = file.readlines()

    # Generate LLVM IR
    llvm_ir = generate_llvm(tac_lines)

    # Print LLVM IR
    for line in llvm_ir:
        print(line)

if __name__ == "__main__":
    main()
