import re
import sys

class TACParser:
    def __init__(self):
        self.current_function = None
        self.variables = {}
        self.tmp_counter = 0
        self.current_instruction = {}

    def fresh_var(self):
        self.tmp_counter += 1
        return f"%t{self.tmp_counter}"

    def parse_tac_lines(self, lines):
        instructions = []
        current_block = []
        for line in lines:
            if not line.strip():
                continue
            
            line = line.strip()
            if line.startswith("TYPE:"):
                if self.current_instruction:
                    current_block.append(self.current_instruction)
                    self.current_instruction = {}
                
                self.current_instruction["type"] = line[len("TYPE:"):].strip()
            elif line.startswith("ARG1:"):
                self.current_instruction["arg1"] = line[len("ARG1:"):].strip()
            elif line.startswith("ARG2:"):
                self.current_instruction["arg2"] = line[len("ARG2:"):].strip()
            elif line.startswith("RESULT:"):
                self.current_instruction["result"] = line[len("RESULT:"):].strip()

            if "type" in self.current_instruction and "arg1" in self.current_instruction and \
               "arg2" in self.current_instruction and "result" in self.current_instruction:
                current_block.append(self.current_instruction)
                self.current_instruction = {}

        return current_block

class LLVMGenerator:
    def __init__(self):
        self.llvm_code = []
        self.funcs = set()

    def start_function(self, name):
        if name not in self.funcs:
            self.llvm_code.append(f"define void @{name}() {{")
            self.funcs.add(name)

    def end_function(self):
        self.llvm_code.append("  ret void")
        self.llvm_code.append("}")

    def add_instruction(self, instruction):
        self.llvm_code.append("  " + instruction)

    def get_or_allocate(self, var):
        if var == "NULL" or var is None or var == "":
            return "null"
        return var

    def generate_llvm(self, parsed_data):
        instr_type = parsed_data["type"]
        arg1 = parsed_data["arg1"]
        arg2 = parsed_data["arg2"]
        result = parsed_data["result"]

        # Generate based on the instruction type
        if instr_type == "LABEL":
            self.add_instruction(f"{result}:")

        elif instr_type == "LOAD":
            llvm_var = result
            if arg1 != "NULL":
                self.add_instruction(f"{llvm_var} = load i32, i32* {arg1}")
            else:
                # Special handling for NULL case
                self.add_instruction(f"{llvm_var} = null")

        elif instr_type == "=":
            llvm_var = result
            if arg1 != "NULL":
                self.add_instruction(f"{llvm_var} = load i32, i32* {arg1}")
            else:
                # Special handling for NULL case
                self.add_instruction(f"{llvm_var} = null")

        elif instr_type in {"+", "-", "*", "/", ">", "<", ">=", "<=", "!="}:
            llvm_op = {
                "+": "add", "-": "sub", "*": "mul", "/": "sdiv",
                ">": "icmp sgt", "<": "icmp slt", ">=": "icmp sge",
                "<=": "icmp sle", "!=": "icmp ne"
            }[instr_type]
            llvm_var = result
            self.add_instruction(f"{llvm_var} = {llvm_op} i32 {arg1}, {arg2}")

        elif instr_type == "IF_NOT":
            cond_var = arg1
            self.add_instruction(f"br i1 {cond_var}, label %{arg2}, label %fail")

        elif instr_type == "GOTO":
            self.add_instruction(f"br label %{arg1}")

        elif instr_type == "CALL":
            # Special handling for CALL
            self.add_instruction(f"call void @{arg1}()")

        elif instr_type == "RETURN":
            self.add_instruction("ret void")

    def generate_code(self):
        return "\n".join(self.llvm_code)


def main(input_file):
    with open(input_file, "r") as f:
        tac_lines = f.readlines()

    parser = TACParser()
    llvm_generator = LLVMGenerator()

    # Parse the TAC lines into instructions
    instructions = parser.parse_tac_lines(tac_lines)

    # Generate LLVM code for each parsed instruction
    current_function = None
    for parsed_data in instructions:
        # Check if the current instruction is a function definition
        if parsed_data['type'] == 'CALL' and parsed_data['arg1'] not in llvm_generator.funcs:
            current_function = parsed_data['arg1']
            llvm_generator.start_function(current_function)
        llvm_generator.generate_llvm(parsed_data)

    llvm_generator.end_function()  # Close last function

    llvm_output = llvm_generator.generate_code()

    if llvm_output.strip():
        print(llvm_output)
    else:
        print("No LLVM output generated. Check TAC input format.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tac_to_llvm.py <input_tac_file>")
    else:
        main(sys.argv[1])