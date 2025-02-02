class TACToLLVMConverter:
    def __init__(self):
        self.temp_counter = 0
        self.var_map = {}

    def generate_temp(self):
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def convert(self, tac):
        llvm_ir = []
        for line in tac:
            line = line.strip()
            if not line:
                continue

            # Handle LOAD (e.g., "t0 = LOAD 4")
            if line.startswith("t") and "LOAD" in line:
                dest, value = line.split(" = ")
                dest = dest.strip()
                value = int(value.split()[1].strip())
                temp_name = self.generate_temp()
                llvm_ir.append(f"  {temp_name} = alloca i32")
                llvm_ir.append(f"  store i32 {value}, i32* {temp_name}")
                self.var_map[dest] = temp_name

            # Handle addition (e.g., "t2 = + t0 t1")
            elif '=' in line and '+' in line:
                parts = line.split()
                dest = parts[0]  # Left-hand side (e.g., t2)
                op1 = parts[2]   # First operand (e.g., t0)
                op2 = parts[3]   # Second operand (e.g., t1)
                temp_name = self.generate_temp()
                llvm_ir.append(f"  {temp_name} = add i32 {self.var_map[op1]}, {self.var_map[op2]}")
                self.var_map[dest] = temp_name

            # Handle assignments (e.g., "sum.g = t4")
            elif "=" in line:
                dest, src = line.split(" = ")
                dest = dest.strip()
                src = src.strip()
                llvm_ir.append(f"  store i32 {self.var_map[src]}, i32* {self.var_map[dest]}")

        llvm_ir.append("  ret i32 0")  # Add return for main
        return llvm_ir


def main():
    tac_code = [
        "main:",
        "t0 = LOAD 4",
        "t1 = LOAD 2",
        "t2 = + t0 t1",
        "t3 = LOAD z",
        "t4 = + t2 t3",
        "sum.g = t4"
    ]

    converter = TACToLLVMConverter()
    llvm_code = converter.convert(tac_code)

    print("Generated LLVM IR:")
    for line in llvm_code:
        print(line)


if __name__ == "__main__":
    main()