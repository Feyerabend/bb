
class RISCVM:
    def __init__(self):
        self.registers = [0] * 32  # 32 registers (x0 to x31)
        self.pc = 0                # program counter
        self.running = True        # VM status flag
        self.labels = {}           # label-to-index mapping

    def execute(self, program):
        self._preprocess_labels(program)

        while self.running and self.pc < len(program):
            instruction = program[self.pc]
            self.execute_instruction(instruction)
            # self.print_registers()  # register values after each instruction
            self.pc += 1

    # map to line numbers
    def _preprocess_labels(self, program):
        for i, line in enumerate(program):
            if ':' in line:
                label = line.strip().split(':')[0]
                self.labels[label] = i

    def execute_instruction(self, instruction):
        parts = instruction.split()
        
        # skip label lines
        if ':' in parts[0]:
            return

        opcode = parts[0]
        handler = self.get_opcode_handler(opcode)
        if handler:
            handler(parts)
        else:
            raise ValueError(f"Unknown instruction: {opcode}")

    def get_opcode_handler(self, opcode):
        handlers = {
            'ADDI': self.addi,
            'SLE': self.sle,
            'BEQ': self.beq,
            'MUL': self.mul,
            'SUB': self.sub,
            'J': self.j,
            'PRINT': self.print_value,
            'HALT': self.halt
        }
        return handlers.get(opcode)

    def parse_operand(self, operand):
        operand = operand.strip(',')  # no trailing commas
        if operand.startswith('x'):
            return int(operand[1:])  # extract register index
        return int(operand)  # immediate value

    def addi(self, parts):
        """ ADDI: rd = rs1 + imm """
        rd = self.parse_operand(parts[1])
        rs1 = self.parse_operand(parts[2])
        imm = int(parts[3])
        self.registers[rd] = self.registers[rs1] + imm

    def sle(self, parts):
        """ SLE: rd = (rs1 > 0) ? 1 : 0 (check if n > 0) """
        rd = self.parse_operand(parts[1])
        rs1 = self.parse_operand(parts[2])
        self.registers[rd] = 1 if self.registers[rs1] > 0 else 0

    def beq(self, parts):
        """ BEQ: if (rs1 == rs2) jump to label """
        rs1 = self.parse_operand(parts[1])
        rs2 = self.parse_operand(parts[2])
        label = parts[3]
        if self.registers[rs1] == self.registers[rs2]:
            self.pc = self.labels[label]  # set program counter to label index

    def mul(self, parts):
        """ MUL: rd = rs1 * rs2 """
        rd = self.parse_operand(parts[1])
        rs1 = self.parse_operand(parts[2])
        rs2 = self.parse_operand(parts[3])
        self.registers[rd] = self.registers[rs1] * self.registers[rs2]

    def sub(self, parts):
        """ SUB: rd = rs1 - imm """
        rd = self.parse_operand(parts[1])
        rs1 = self.parse_operand(parts[2])
        imm = int(parts[3])
        self.registers[rd] = self.registers[rs1] - imm

    def j(self, parts):
        """ J: jump to label """
        label = parts[1]
        self.pc = self.labels[label]  # program counter -> label index

    def print_value(self, parts):
        """ PRINT: Print value in register rd """
        rd = self.parse_operand(parts[1])
        print(self.registers[rd])

    def halt(self, _=None):
        """ HALT: Stop execution """
        self.running = False

    def print_registers(self):
        """ Print all registers for debugging in a human-readable format """
        print("Registers:", self.registers[1:])  # skip x0 (always 0)
        print("-" * 40)


program = [
    "ADDI x1, x0, 5",  # n = 5
    "ADDI x2, x0, 1",  # result = 1
    "loop:",           # label for loop start
    "SLE x4, x1, x0",  # if (n > 0)
    "BEQ x4, x0, end", # if false, jump to end
    "MUL x2, x2, x1",  # result *= n
    "SUB x1, x1, 1",   # n -= 1
    "J loop",          # jump back to loop
    "end:",            # label for end
    "PRINT x2",        # print result
    "HALT"             # halt program
]

vm = RISCVM()
vm.execute(program)
