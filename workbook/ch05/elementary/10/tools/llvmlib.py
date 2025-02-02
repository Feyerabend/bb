class Type:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

i32 = Type("i32")
i32_ptr = Type("i32*")

class Instruction:
    def __init__(self, result, op, operands, result_type=None):
        self.result = result
        self.op = op
        self.operands = operands
        self.result_type = result_type

    def __str__(self):
        if self.result_type:
            return f"  %{self.result} = {self.op} {self.result_type} " + ", ".join(self.operands)
        return f"  %{self.result} = {self.op} " + ", ".join(self.operands)


class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def __str__(self):
        return "\n".join(str(instr) for instr in self.instructions)


class Function:
    def __init__(self, name):
        self.name = name
        self.current_block = BasicBlock("entry")
        self.blocks = [self.current_block]

    def new_block(self, name):
        new_block = BasicBlock(name)
        self.blocks.append(new_block)
        self.current_block = new_block


class CodeBuilder:
    def __init__(self):
        self.function = Function("main")
        self.temp_count = 0

    def generate_temp(self):
        self.temp_count += 1
        return self.temp_count - 1

    def alloca(self, var_name, var_type):
        instruction = Instruction(var_name, "alloca", [str(var_type)], str(var_type))
        self.function.current_block.add_instruction(instruction)
        return var_name

    def store(self, value, pointer, value_type):
        instruction = Instruction("", "store", [str(value_type) + " " + value, str(value_type) + "* " + pointer])
        self.function.current_block.add_instruction(instruction)

    def load(self, pointer, result_type):
        result = self.generate_temp()
        instruction = Instruction(result, "load", [str(result_type) + "* " + pointer], str(result_type))
        self.function.current_block.add_instruction(instruction)
        return result

    def add(self, op1, op2, result_type):
        result = self.generate_temp()
        instruction = Instruction(result, "add", [str(result_type) + " " + str(op1), str(result_type) + " " + str(op2)], str(result_type))
        self.function.current_block.add_instruction(instruction)
        return result

    def ret(self, value):
        instruction = Instruction("", "ret", [str(value)], "")
        self.function.current_block.add_instruction(instruction)

    def br(self, label):
        instruction = Instruction("", "br", [f"label %{label}"], "")
        self.function.current_block.add_instruction(instruction)

    def convert(self):
        llvm_code = f"define i32 @{self.function.name}(i32, i32) {{\n"
        llvm_code += f"  ; Block entry\n"
        llvm_code += f"  ; Block exit\n"
        llvm_code += str(self.function.current_block)
        llvm_code += f"\n}}\n"
        return llvm_code


def main():
    builder = CodeBuilder()

    # Allocate memory for variables
    ptr0 = builder.alloca("%ptr0", i32_ptr)
    ptr1 = builder.alloca("%ptr1", i32_ptr)

    # Store values in those allocated spaces
    builder.store("5", ptr0, i32)
    builder.store("10", ptr1, i32)

    # Load values into registers
    reg0 = builder.load(ptr0, i32)
    reg1 = builder.load(ptr1, i32)

    # Add the two registers
    reg2 = builder.add(reg0, reg1, i32)

    # Branch to exit block
    builder.br("exit")

    # Return the sum
    builder.ret(reg2)

    # Convert to LLVM IR
    llvm_code = builder.convert()
    print(llvm_code)


if __name__ == "__main__":
    main()