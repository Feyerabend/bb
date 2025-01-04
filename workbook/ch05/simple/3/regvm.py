
class REGVM:
    def __init__(self):
        self.pc = 0
        self.registers = { }
        self.flags = { 'Z': 0, 'N': 0 }
        self.memory = []
        self.stack = []
        self.label_map = { }
        self.program_lines = []

    def load_program(self, program):
        self.program_lines = program
        self._build_label_map()

    def _build_label_map(self):
        line_number = 0
        for index, instruction in enumerate(self.program_lines):
            if instruction.endswith(':'):
                label = instruction[:-1]  # no colon
                self.label_map[label] = index
            else:
                line_number += 1

    def fetch(self):
        while self.pc < len(self.memory):
            instruction = self.memory[self.pc]
            self.pc += 1
            if instruction.endswith(':'):
                continue  # skip labels
            else:
                return instruction
        return None

    def decode_and_execute(self, instruction):
        if not instruction:
            return False

        parts = instruction.split()
        opcode = parts[0]
        args = parts[1:]

        # all registers in args should be initialized to 0
        for arg in args:
            if arg.isalpha() and arg not in self.registers:
                self.registers[arg] = 0

        if opcode == 'MOV':
            fst = args[0]  # destination register
            snd = args[1]  # source (could be a register or an immediate value)

            # dynamically init destination register
            if fst not in self.registers:
                self.registers[fst] = 0

            # source as immediate value or register
            if snd.isdigit():  # if source is immediate value
                self.registers[fst] = int(snd)
            else:  # if source is register
                if snd not in self.registers:
                    # dynamically init source register to 0 if it doesn't exist
                    self.registers[snd] = 0
                self.registers[fst] = self.registers[snd]

        elif opcode == 'ADD':
            fst = args[0]
            snd = args[1]

            if fst not in self.registers:
                self.registers[fst] = 0

            if snd.isdigit():
                self.registers[fst] += int(snd)
            else:
                if snd not in self.registers:
                    self.registers[snd] = 0
                self.registers[fst] += self.registers[snd]
            self.update_flags(self.registers[fst])

        elif opcode == 'SUB':
            fst = args[0]
            snd = args[1]
            
            if snd.isalpha():
                self.registers[fst] -= self.registers.get(snd, 0)
            else:
                self.registers[fst] -= int(snd)
            self.update_flags(self.registers[fst])
            
        elif opcode == 'MUL':
            fst = args[0]
            snd = args[1]
            if snd.isalpha():
                self.registers[fst] *= self.registers[snd]
            else:
                self.registers[fst] *= int(snd)
            self.update_flags(self.registers[fst])

        elif opcode == 'DIV':
            fst = args[0]
            snd = args[1]

            if snd.isalpha():
                divisor = self.registers.get(snd, 0)
            else:
                divisor = int(snd)

            if divisor == 0:
                print(f"Error: Division by zero when trying to divide {fst} by {snd}")
                # or, e.g. send an exception ..
                self.registers[fst] = 0
            else:
                if snd.isalpha():
                    self.registers[fst] //= self.registers[snd]
                else:
                    self.registers[fst] //= int(snd)
            self.update_flags(self.registers[fst])

        elif opcode == 'CMP':
            fst = args[0]
            snd = args[1]
            
            if snd.isdigit():
                snd_value = int(snd)
            else:
                snd_value = self.registers.get(snd, 0)
            
            if self.registers[fst] == snd_value:
                self.flags['Z'] = 1
            else:
                self.flags['Z'] = 0

        elif opcode == 'JMP':
            fst = args[0]
            if fst in self.label_map:
                self.pc = self.label_map[fst]

        elif opcode == 'JL':
            fst = args[0]  # label
            reg1 = args[1]
            reg2 = args[2]

            if reg1.isalpha() and reg2.isalpha():
                if reg1 in self.registers and reg2 in self.registers:
                    if self.registers[reg1] < self.registers[reg2]:
                        if fst in self.label_map:
                            self.pc = self.label_map[fst]
                else:
                    raise KeyError(f"JL failed because registers {reg1} or {reg2} do not exist.")
            else:
                print("Error: JL expects two register names.")

        elif opcode == 'JG':
            fst = args[0]
            reg1 = args[1]
            reg2 = args[2]

            if reg1.isalpha() and reg2.isalpha():
                if reg1 in self.registers and reg2 in self.registers:
                    if self.registers[reg1] > self.registers[reg2]:
                        if fst in self.label_map:
                            self.pc = self.label_map[fst]
                else:
                    raise KeyError(f"JG failed because registers {reg1} or {reg2} do not exist.")
            else:
                print("Error: JG expects two register names.")

        elif opcode == 'JZ':
            fst = args[0]
            if self.flags['Z'] == 1 and fst in self.label_map:
                self.pc = self.label_map[fst]

        elif opcode == 'PRINT':
            fst = args[0]
            if fst not in self.registers:
                self.registers[fst] = 0  # optionally init 0
            print(f"Register {fst}: {self.registers[fst]}")

        elif opcode == 'CALL':
            func_name = args[0]
            self.stack.append(self.pc)  # current PC
            self.pc = self.label_map[func_name]  # jump function

        elif opcode == 'RETURN':
            if self.stack:
                self.pc = self.stack.pop()

        elif opcode == 'HALT':
            print("  HALT")
            return False

        else:
            raise ValueError(f"Unknown opcode: {opcode}")

        return True

    def update_flags(self, result):
        if result == 0:
            self.flags['Z'] = 1  # Zero flag
        else:
            self.flags['Z'] = 0

        if result < 0:
            self.flags['N'] = 1  # Negative flag
        else:
            self.flags['N'] = 0

        # overflow flag (for signed operations)
        # example overflow limits for 8-bit signed
        if result > 255 or result < -128:
            self.flags['O'] = 1
        else:
            self.flags['O'] = 0
    
    def run(self):
        while True:
            instruction = self.fetch()
            if not instruction or not self.decode_and_execute(instruction):
                break


program = [
    "MOV A 1",   # Init A
    "MOV B 5",   # Init B with 5
    "start:",    # Label for start
    "CALL factorial",  # Call factorial function
    "PRINT A",   # Print result in A
    "HALT",      # End program (HALT is a placeholder)

    # Function to calculate factorial
    "factorial:",  # Label for factorial function
    "CMP B 0",     # Compare B with 0
    "JZ end_fact", # If B is 0, jump to end_fact (return 1)
    "MUL A B",     # Multiply A by B
    "SUB B 1",     # Subtract 1 from B
    "CALL factorial", # Recursive call to factorial
    "end_fact:",   # End of factorial function
    "RETURN",      # Return from factorial function
]

'''
program = [
    "MOV t1, 5",      # Assign 5 to t1
    "MOV t2, 10",     # Assign 10 to t2
    "MOV t3, t1",     # Assign value of t1 to t3
    "MOV t4, t5",     # Assign value of t5 (should initialize t5 to 0) to t4
    "PRINT t1",       # Print t1 (should be 5)
    "PRINT t2",       # Print t2 (should be 10)
    "PRINT t3",       # Print t3 (should be 5)
    "PRINT t4",       # Print t4 (should be 0)
    "HALT"
]

program = [
    "MOV t1, 5",
    "MOV t2, 10",
    "MOV t3, t1",
    "ADD t3, t2",
    "MOV t4, t1",
    "MUL t4, t2",
    "MOV t5, t1 && t2",
    "MOV t6, t1 || t2",
    "start:",
    "CMP t1, t2",
    "JL less_than",
    "CMP t1, t2",
    "JG greater_than",
    "MOV t7, t1",
    "ADD t7, t2",
    "JMP end",
    "less_than:",
    "MOV t7, t2",
    "SUB t7, t1",
    "JMP end",
    "greater_than:",
    "MOV t7, t1",
    "SUB t7, t2",
    "CALL my_function",
    "JMP end",
    "my_function:",
    "MOV t8, t1",
    "MUL t8, t2",
    "RETURN",
    "end:",
    "PRINT t7",
    "PRINT t8",
    "HALT"

]
'''


vm = REGVM()
vm.load_program(program)
vm.memory = program
vm.run()


# task:
# convert:
# MOV t3, t1
# ADD t3, t2
# to the "ARM"
# ADD t3, t1, t2
# ..