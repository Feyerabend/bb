class LLVMGenerator:
    def __init__(self):
        self.temp_count = 0
        self.variables = {}  # To store global variables (like a.g, b.g)
        self.instructions = []  # To store the generated LLVM instructions
    
    def get_temp(self):
        temp_var = f"t{self.temp_count}"
        self.temp_count += 1
        return temp_var
    
    def add_instruction(self, instr):
        self.instructions.append(instr)
    
    def load(self, var):
        return f"load i32, i32* @{var}"
    
    def store(self, var, value):
        return f"store i32 {value}, i32* @{var}"
    
    def icmp(self, op, val1, val2):
        return f"icmp {op} i32 {val1}, {val2}"
    
    def br(self, condition, true_label, false_label):
        return f"br i1 {condition}, label %{true_label}, label %{false_label}"

    def generate_llvm(self, tac_program):
        for line in tac_program:
            parts = line.split()
            op = parts[1]
            
            if op == "=":
                # Simple assignment: result = arg1
                result, arg1 = parts[0], parts[2]
                self.add_instruction(f"{result} = {self.load(arg1)}")
            
            elif op == "IF_NOT":
                # Conditional: IF_NOT arg1 GOTO label
                arg1, label = parts[2], parts[4]
                t_cond = self.get_temp()
                self.add_instruction(f"{t_cond} = {self.icmp('ne', arg1, '0')}")
                self.add_instruction(f"IF_NOT {t_cond} GOTO {label}")
            
            elif op == "GOTO":
                # Unconditional jump: GOTO label
                label = parts[1]
                self.add_instruction(f"GOTO {label}")
            
            elif op == ">":
                # Greater than comparison
                result, arg1, arg2 = parts[0], parts[2], parts[4]
                t_cmp = self.get_temp()
                self.add_instruction(f"{t_cmp} = {self.icmp('sgt', arg1, arg2)}")
                self.add_instruction(f"{result} = {t_cmp}")
            
            elif op == "<":
                # Less than comparison
                result, arg1, arg2 = parts[0], parts[2], parts[4]
                t_cmp = self.get_temp()
                self.add_instruction(f"{t_cmp} = {self.icmp('slt', arg1, arg2)}")
                self.add_instruction(f"{result} = {t_cmp}")
            
            elif op == "-":
                # Subtraction: result = arg1 - arg2
                result, arg1, arg2 = parts[0], parts[2], parts[4]
                t_sub = self.get_temp()
                self.add_instruction(f"{t_sub} = sub i32 {arg1}, {arg2}")
                self.add_instruction(f"{result} = {t_sub}")
            
            elif op == "LOAD":
                # LOAD operation: result = LOAD value
                result, value = parts[0], parts[2]
                self.add_instruction(f"{result} = {self.load(value)}")
        
        return self.instructions
    
    def print_llvm(self, output_file=None):
        llvm_code = "\n".join(self.instructions)
        if output_file:
            with open(output_file, "w") as f:
                f.write(llvm_code)
        else:
            print(llvm_code)


# Example TAC program as input
tac_program = [
    "t0 = LOAD b.g",
    "t1 = LOAD 0",
    "t2 = != t0 t1",
    "IF_NOT t2 GOTO L1",
    "t3 = LOAD a.g",
    "t4 = LOAD b.g",
    "t5 = > t3 t4",
    "IF_NOT t5 GOTO L2",
    "t6 = LOAD a.g",
    "t7 = LOAD b.g",
    "t8 = - t6 t7",
    "a.g = t8",
    "L2:",
    "t9 = LOAD a.g",
    "t10 = LOAD b.g",
    "t11 = <= t9 t10",
    "IF_NOT t11 GOTO L3",
    "t12 = LOAD b.g",
    "t13 = LOAD a.g",
    "t14 = - t12 t13",
    "b.g = t14",
    "L3:",
    "GOTO L0",
    "L1:",
    "t15 = LOAD a.g",
    "gcd.g = t15",
    "RETURN"
]

# Initialize the LLVM generator
llvm_gen = LLVMGenerator()

# Generate LLVM IR from the TAC program
llvm_gen.generate_llvm(tac_program)

# Print the LLVM IR to the screen or save it to a file
llvm_gen.print_llvm(output_file="output.ll")