
import sys

class TACToLLVM:
    def __init__(self):
        self.variables = set()
        self.label_positions = {}
        self.llvm_code = []
        self.temp_count = 0

    def fresh_temp(self):
        self.temp_count += 1
        return f"%t{self.temp_count}"

    def parse_tac(self, tac_lines):
        # 1: Collect labels and variables
        for line in tac_lines:
            line = line.strip()
            if not line or line.startswith("#"):  # empty lines, comments ..
                continue
            if line.endswith(":"):
                self.label_positions[line[:-1]] = None  # Labels are placeholders
            else:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == '=':
                    self.variables.add(parts[0])  # destination variables

        # start LLVM Code
        self.llvm_code.append("define i32 @main() {")
        self.llvm_code.append("entry:")

        # allocate space for variables
        for var in self.variables:
            self.llvm_code.append(f"  %{var} = alloca i32")

        # 2: Generate LLVM instructions
        for idx, line in enumerate(tac_lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith(":"):
                label = line[:-1]
                self.llvm_code.append(f"{label}:") # replace the placeholder
                self.label_positions[label] = len(self.llvm_code)
                continue

            parts = line.split()
            if len(parts) == 3 and parts[1] == '=':
                # assignment (x = y)
                self.llvm_code.append(f"  %{parts[0]} = load i32, i32* %{parts[2]}")
            elif len(parts) == 4 and parts[2] == "LOAD":
                # immediate load (x = LOAD 3)
                self.llvm_code.append(f"  store i32 {parts[3]}, i32* %{parts[0]}")
            elif len(parts) == 5 and parts[1] == '=':
                # arithmetic operations (t0 = + t1 t2)
                dest, op, src1, src2 = parts[0], parts[2], parts[3], parts[4]
                llvm_op = {
                    '+': 'add',
                    '-': 'sub',
                    '*': 'mul',
                    '/': 'sdiv',
                    '>': 'icmp sgt',
                    '<': 'icmp slt',
                    '!=': 'icmp ne',
                    '<=': 'icmp sle'
                }.get(op)

                if llvm_op:
                    temp1 = self.fresh_temp()
                    temp2 = self.fresh_temp()
                    self.llvm_code.append(f"  {temp1} = load i32, i32* %{src1}")
                    self.llvm_code.append(f"  {temp2} = load i32, i32* %{src2}")
                    result = self.fresh_temp()
                    self.llvm_code.append(f"  {result} = {llvm_op} i32 {temp1}, {temp2}")
                    self.llvm_code.append(f"  store i32 {result}, i32* %{dest}")
                else:
                    raise ValueError(f"Unknown operation: {op}")
            elif parts[0] == "IF_NOT":
                # conditional jump (IF_NOT cond GOTO label)
                temp = self.fresh_temp()
                self.llvm_code.append(f"  {temp} = load i32, i32* %{parts[1]}")
                self.llvm_code.append(f"  %cond{self.temp_count} = icmp eq i32 {temp}, 0")
                self.llvm_code.append(f"  br i1 %cond{self.temp_count}, label %{parts[3]}, label %continue_{idx}")
                self.llvm_code.append(f"continue_{idx}:")
            elif parts[0] == "GOTO":
                # unconditional jump
                self.llvm_code.append(f"  br label %{parts[1]}")
            elif parts[0] == "CALL":
                # function call (not supported yet, treating as jump)
                self.llvm_code.append(f"  call void @{parts[1]}()")
            elif parts[0] == "RETURN":
                # return (assuming returning 0 for now)
                self.llvm_code.append("  ret i32 0")
            else:
                raise ValueError(f"Unknown instruction: {line}")

        self.llvm_code.append("}")

    def write_llvm(self, output_file):
        with open(output_file, "w") as f:
            f.write("\n".join(self.llvm_code) + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 llvm.py <input_tac_file> <output_llvm_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r") as f:
        tac_lines = f.readlines()

    converter = TACToLLVM()
    converter.parse_tac(tac_lines)
    converter.write_llvm(output_file)
    print(f"LLVM IR written to {output_file}")

if __name__ == "__main__":
    main()
