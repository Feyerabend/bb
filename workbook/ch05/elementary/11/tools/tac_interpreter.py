
import sys

class TACVirtualMachine:
    def __init__(self):
        self.memory = {}  # variables and temporaries
        self.labels = {}  # maps labels to instruction indices
        self.program = []  # list of instructions
        self.pc = 0  # program counter
        self.call_stack = []  # stack to store return addresses

    def load_program(self, program):
        self.program = program
        self._parse_labels()

    def load_file(self, filename):
        program = []
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if line:  # ignore empty lines
                    program.append(line)
        return program

    def _parse_labels(self):
        for idx, instruction in enumerate(self.program):
            if isinstance(instruction, str) and instruction.endswith(':'):
                self.labels[instruction[:-1]] = idx

    def run(self):
        if "main" not in self.labels:
            raise ValueError("No 'main' label found in the program!")

        self.pc = self.labels["main"]  # start at 'main'

        while self.pc < len(self.program):
            instruction = self.program[self.pc]
            if instruction.startswith("HALT"): # (HALT not used)
                break  # stop execution
            self._execute(instruction)
            self.pc += 1

    def _execute(self, instruction):

        if isinstance(instruction, str):
            if instruction.endswith(':'):
                return  # Label, do nothing
            elif instruction.startswith('HALT'):
                self.pc = len(self.program)
            elif instruction.startswith('IF_NOT'):
                self._execute_if_not(instruction)
            elif instruction.startswith('GOTO'):
                self._execute_goto(instruction)
            elif instruction.startswith('CALL'):
                self._execute_call(instruction)
            elif instruction.startswith('RETURN'):
                self._execute_return()
            else:
                self._execute_operation(instruction)
        else:
            self._execute_operation(instruction)


    def _execute_operation(self, instruction):
        parts = instruction.split()
        if len(parts) < 2:
            return  # ignore empty or invalid instructions

        if len(parts) == 4 and parts[2] == "LOAD":
            # immediate "t66 = LOAD 3"
            dest = parts[0]
            src = parts[3]
            self.memory[dest] = int(src) if src.isdigit() else self.memory.get(src, 0)
            return

        if len(parts) == 3 and parts[1] == '=':
            # simple assignment "x = y"
            dest, src = parts[0], parts[2]
            self.memory[dest] = self.memory.get(src, 0)
            return

        if len(parts) == 5 and parts[1] == '=':
            # binary ops: "t0 = + t1 t2"
            dest, op, src1, src2 = parts[0], parts[2], parts[3], parts[4]
            val1, val2 = self.memory.get(src1, 0), self.memory.get(src2, 0)

            if op == '+':
                self.memory[dest] = val1 + val2
            elif op == '-':
                self.memory[dest] = val1 - val2
            elif op == '*':
                self.memory[dest] = val1 * val2
            elif op == '/':
                self.memory[dest] = val1 // val2  # integer division: val1 // val2 if val2 != 0 else 0  # avoid division by zero
            elif op == '>':
                self.memory[dest] = 1 if val1 > val2 else 0
            elif op == '<':
                self.memory[dest] = 1 if val1 < val2 else 0
            elif op == '!=':
                self.memory[dest] = 1 if val1 != val2 else 0
            elif op == '<=':
                self.memory[dest] = 1 if val1 <= val2 else 0
            else:
                raise ValueError(f"Unknown operation: {op}")
            return

        raise ValueError(f"Invalid instruction format: {instruction}")

    def _execute_if_not(self, instruction):
        parts = instruction.split()
        condition = self.memory.get(parts[1], 0)
        if not condition:
            self.pc = self.labels[parts[3]] - 1

    def _execute_goto(self, instruction):
        parts = instruction.split()
        self.pc = self.labels[parts[1]] - 1

    def _execute_call(self, instruction):
        parts = instruction.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid CALL instruction: {instruction}")

        func_label = parts[1]
        if func_label not in self.labels:
            raise ValueError(f"Undefined function label: {func_label}")

        self.call_stack.append(self.pc)  # return address
        self.pc = self.labels[func_label] - 1  # jump to function start

    def _execute_return(self):
        if not self.call_stack:
            raise ValueError("RETURN executed with an empty call stack!")

        self.pc = self.call_stack.pop()  # restore instruction pointer

def filter_temps(memory):
    return {k: v for k, v in memory.items() if not k.startswith('t') or not k[1:].isdigit()}

def filter_local_vars(memory):
    return {k: v for k, v in memory.items() if not k.endswith('.l')}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tac_interpreter.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print("Interpreting TAC code from:", input_file)
    vm = TACVirtualMachine()
    program = vm.load_file(input_file)
    vm.load_program(program)
    vm.run()

#   final_memory = filter_local_vars(filter_temps(vm.memory))
#   final_memory = filter_temps(vm.memory)
    final_memory = vm.memory

    if output_file:
        with open(output_file, 'w') as f:
            f.write(str(final_memory) + '\n')
    else:
        print("Final memory state:", final_memory)

if __name__ == "__main__":
    main()
