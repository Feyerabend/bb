import os
import sys
import csv
import getopt
import time
from enum import Enum, unique

TRUE = 1
FALSE = 0

@unique
class OP(Enum):
    ADD =       0
    AND =       1
    CALL =      2
    DIV =       3
    EMIT =      4
    EQ =        5
    GT =        6
    GQ =        7
    HALT =      8
    JP =        9
    JPNZ =      10
    JPZ =       11
    LD =        12
    LDARG =     13
    LOAD =      14
    LT =        15
    LQ =        16
    MOD =       17
    MUL =       18
    NEQ =       19
    NOP =       20
    OR =        21
    PRINT =     22
    PRNT =      23
    RET =       24
    RLOAD =     25
    RSTORE =    26
    SET =       27
    ST =        28
    STARG =     29
    STORE =     30
    SUB =       31
    UMIN =      32
    XOR =       33

ary = [
    0,      # ADD
    0,      # AND
    1,      # CALL addr
    0,      # DIV
    0,      # EMIT
    0,      # EQ
    0,      # GT
    0,      # GQ
    0,      # HALT
    1,      # JP addr
    1,      # JPNZ addr
    1,      # JPZ addr
    1,      # LD local_reg
    1,      # LDARG arg_reg
    1,      # LOAD global_reg
    0,      # LT
    0,      # LQ
    0,      # MOD
    0,      # MUL
    0,      # NEQ
    0,      # NOP
    0,      # OR
    0,      # PRINT
    0,      # PRNT
    0,      # RET
    0,      # RLOAD
    0,      # RSTORE
    1,      # SET number
    1,      # ST local_reg
    1,      # STARG arg_reg
    1,      # STORE global_reg
    0,      # SUB
    0,      # UMIN
    0]      # XOR

class Diagnostics:
    def __init__(self):
        self.operation_count = {op.value: 0 for op in OP}
        self.execution_times = {op.value: 0 for op in OP}
        self.error_count = {
            'division_by_zero': 0,
            'invalid_operation': 0,
        }

    def log_operation(self, op):
        """Log the execution of an operation."""
        self.operation_count[op] += 1

    def record_execution_time(self, op, start_time):
        """Record the execution time for an operation."""
        execution_time = time.time() - start_time
        self.execution_times[op] += execution_time

    def increment_error(self, error_type):
        """Increment the error count."""
        if error_type in self.error_count:
            self.error_count[error_type] += 1

    def print_diagnostics(self):
        """Print a summary of diagnostics after the VM run."""
        print("\n=== Diagnostic Summary ===")
        print("Operation Counts:")
        for op, count in self.operation_count.items():
            if count > 0:
                print(f"{OP(op).name}: {count}")

        print("\nExecution Times:")
        for op, time_taken in self.execution_times.items():
            if time_taken > 0:
                print(f"{OP(op).name}: {time_taken:.6f} seconds")

        print("\nError Counts:")
        for error, count in self.error_count.items():
            print(f"{error.replace('_', ' ').title()}: {count}")

        print("==========================\n")

class VM:
    def __init__(self, code, start, arrs, args, vars,
                 diagnostics,
                 singlestep=False, breakpoints=None, trace=False):
        self.stack = []
        self.sp = -1
        self.fp = 0

        self.arrs = [0 for _ in range(arrs)]  # "arrays"
        self.args = [0 for _ in range(args)]  # passed to routines/procedures
        self.vars = [0 for _ in range(vars)]  # global variables

        self.pc = start  # where to start
        self.code = code

        self.trace = trace #
        self.breakpoints = set(breakpoints if breakpoints else [])
        self.singlestep = singlestep
        self.running = True #
        self.param = 'pos' # pc operator/operand stack

        self.diagnostics = diagnostics  # Reference to the Diagnostics object

    def pop(self):
        if not self.stack:
            raise Exception("Runtime error: stack is empty")
        self.sp -= 1
        value = int(self.stack.pop())
        return value

    def push(self, value):
        self.sp += 1
        self.stack.append(int(value))

    def nextcode(self):
        if self.pc < 0 or self.pc > len(self.code) - 1:
            raise Exception("Runtime error: program counter out of range (%d)" % self.pc)
        acode = self.code[self.pc]
        self.pc += 1
        return acode

    def run(self):
        while True:
            op = self.nextcode()
            start_time = time.time()

            # debug control
            if self.pc in self.breakpoints:
                print(f"> breakpoint at {self.pc}")
                self.singlestep = True
            if self.singlestep:
                command = input("> (c)ontinue, (s)tep, (b)reakpoints, (t)race, (n)o trace, (q)uit: ").strip().lower()
                if command == 'c':
                    self.singlestep = False
                elif command == 's':
                    pass
                elif command == 'b':
                    print(f"> breakpoints: {self.breakpoints}")
                    pass
                elif command == 't':
                    self.trace = True
                    self.param = input(">> (p)c, (s)tack, (o)perand, (a)rrays, a(r)guments, (v)ariables: ").strip().lower()
                    if not self.param:
                        self.param = 'pos'
                elif command == 'n':
                    self.trace = False
                elif command == 'q':
                    return
            if self.trace:
                print(self.pline(self.pc, op, self.stack))

            if op is None:
                break

            if op == OP.ADD.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a + b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.AND.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a & b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.CALL.value:
                self.diagnostics.log_operation(op)
                addr = self.nextcode()
                self.push(self.fp)
                self.push(self.pc)
                self.fp = self.sp
                self.pc = addr
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.DIV.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if b == 0:
                    raise Exception("Runtime error: division by zero.")
                c = a // b  # divmod?
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.EMIT.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                print(chr(v), end='')
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.EQ.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a == b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.GT.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a > b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.GQ.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a >= b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.HALT.value:
                break

            elif op == OP.JP.value:
                self.diagnostics.log_operation(op)
                next = self.nextcode()
                if next < 0 or next > len(self.code) - 1:
                    raise Exception("Runtime error: program counter out of range (%d)" % next)
                self.pc = next
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.JPNZ.value:
                self.diagnostics.log_operation(op)
                addr = self.nextcode()
                v = self.pop()
                if addr < 0 or addr > len(self.code) - 1:
                    raise Exception("Runtime error: program counter out of range (%d)" % addr)
                if v != 0:
                    self.pc = addr
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.JPZ.value:
                self.diagnostics.log_operation(op)
                addr = self.nextcode()
                v = self.pop()
                if addr < 0 or addr > len(self.code) - 1:
                    raise Exception("Runtime error: program counter out of range (%d)" % addr)
                if v == 0:
                    self.pc = addr
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.LD.value:
                self.diagnostics.log_operation(op)
                offset = self.nextcode()
                next = self.fp + offset
                if next > len(self.vars) - 1:
                    raise Exception("Runtime error: memory address out of ranges (%d)" % next)
                v = self.vars[next]
                self.push(v)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.LDARG.value:
                self.diagnostics.log_operation(op)
                addr = self.nextcode()
                if addr < 0 or addr > len(self.args) - 1:
                    raise Exception("Runtime error: loading from argument address out of range (%d)" % addr)
                v = self.args[addr]
                self.push(v)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.LOAD.value:
                self.diagnostics.log_operation(op)
                addr = self.nextcode()
                if addr < 0 or addr > len(self.vars) - 1:
                    raise Exception("Runtime error: loading from variable address out of range (%d)" % addr)
                v = self.vars[addr]
                self.push(v)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.LT.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a < b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.LQ.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a <= b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.MOD.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a % b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.MUL.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a * b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.NEQ.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                if a != b:
                    c = TRUE
                else:
                    c = FALSE
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.NOP.value:
                pass

            elif op == OP.OR.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a | b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.PRINT.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                print(int(v))
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.PRNT.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                print(int(v), end='')
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.RET.value:
                self.diagnostics.log_operation(op)
                self.sp = self.fp
                self.pc = self.pop()
                self.fp = self.pop()
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.RLOAD.value:
                self.diagnostics.log_operation(op)
                a = self.pop()
                if a < 0 or a > len(self.arrs) - 1:
                    raise Exception("Runtime error: storing value in array out of range (%d)" % a)
                v = self.arrs[a]
                self.push(v)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.RSTORE.value:
                self.diagnostics.log_operation(op)
                a = self.pop()
                b = self.pop()
                if a < 0 or a > len(self.arrs) - 1:
                    raise Exception("Runtime error: storing value in array out of range (%d)" % a)
                self.arrs[a] = b
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.SET.value:
                self.diagnostics.log_operation(op)
                v = self.nextcode()
                self.push(v)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.ST.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                offset = self.nextcode()
                next = self.fp + offset
                if next > len(self.vars) - 1:
                    raise Exception("Runtime error: not enough memory reserved for variables (%d)" % next)
                self.vars[next] = v
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.STARG.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                addr = self.nextcode()
                if addr < 0 or addr > len(self.args) - 1:
                    raise Exception("Runtime error: storing argument out of range (%d)" % addr)
                self.args[addr] = v
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.STORE.value:
                self.diagnostics.log_operation(op)
                v = self.pop()
                addr = self.nextcode()
                if addr < 0 or addr > len(self.vars) - 1:
                    raise Exception("Runtime error: variable storing address out of range (%d)" % addr)
                self.vars[addr] = v
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.SUB.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a - b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.UMIN.value:
                self.diagnostics.log_operation(op)
                a = self.pop()
                self.push(int(-a))
                self.diagnostics.record_execution_time(op, start_time)

            elif op == OP.XOR.value:
                self.diagnostics.log_operation(op)
                b = self.pop()
                a = self.pop()
                c = a ^ b
                self.push(c)
                self.diagnostics.record_execution_time(op, start_time)

            else:
                break  # for undefined operations, exit loop

        # after the run, print diagnostics
        self.diagnostics.print_diagnostics()

        return

    # truncate long arrays .. cut off at target_sequence 0,0,0,0,0
    def truncatearr(self, arr):
        target_sequence = [0, 0, 0, 0, 0] # arbitrary choice!
        target_length = len(target_sequence)
        for i in range(len(arr) - target_length + 1):
            if arr[i:i + target_length] == target_sequence:
                return arr[:i]
        return arr

    # current line with environmental items
    def pline(self, pc, op, stack):
        string = '> '
        if 'p' in self.param:
            string += f' pc={pc} '
        if 'o' in self.param:
            if ary[op] == 1:
                string += f' op=\'{OP(op).name} {self.code[pc]}\' '
            else:
                string += f' op=\'{OP(op).name}\' '
        if 's' in self.param:
            string += f' stack={stack} '
        if 'f' in self.param:
            string += f' frame={self.fp} '
        if 'a' in self.param:
            string += f' arrs={self.truncatearr(self.arrs)} '
        if 'r' in self.param:
            string += f' args={self.truncatearr(self.args)} '
        if 'v' in self.param:
            string += f' vars={self.truncatearr(self.vars)} '
        return string


class Runner:
    def __init__(self):
        self.ARRS = 2048
        self.ARGS = 2048
        self.VARS = 2048

    # get the bytecode and setup the code
    def load(self, file):
        self.file = file

        # read tokens from file
        input = []
        with open(self.file, 'r') as f:
            csvf = csv.reader(f, delimiter=',')
            input.extend(csvf)
        f.close()
        nums = input.pop(0)
        self.start = int(nums.pop(0))
        code = [int(i) for i in nums]
        self.code = code

    def run(self, singlestep, breakpoints, trace):
        diagnostics = Diagnostics()
        # set up vm
        vm = VM(self.code, self.start, self.ARRS, self.ARGS, self.VARS,
                diagnostics,
                singlestep, breakpoints, trace)
        vm.run()


def main(argv):
    singlestep = False
    breakpoints = []
    trace = False
    inputfile = None

    try:
        opts, args = getopt.getopt(argv, "s:b:t:i:", ["singlestep=", "breakpoints=", "trace=", "input="])
    except getopt.GetoptError:
        print('Usage: dvm.py --singlestep <true/false> --breakpoints <list_of_numbers> --trace <true/false> --input <file>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-s", "--singlestep"):
            if arg.lower() == 'true' or arg.lower() == 't':
                singlestep = True
            elif arg.lower() == 'false' or arg.lower() == 'f':
                singlestep = False
            else:
                print("Invalid value for --singlestep. Use 'true' or 'false'.")
                sys.exit(2)
        elif opt in ("-b", "--breakpoints"):
            try:
                breakpoints = [int(x) for x in arg.strip('[]').split(',')]
            except ValueError:
                print("Invalid format for --breakpoints. Use a list of numbers like '[14,16]'.")
                sys.exit(2)
        elif opt in ("-t", "--trace"):
            if arg.lower() == 'true' or arg.lower() == 't':
                trace = True
            elif arg.lower() == 'false' or arg.lower() == 'f':
                trace = False
            else:
                print("Invalid value for --trace. Use 'true' or 'false'.")
                sys.exit(2)
        elif opt in ("-i", "--input"):
            if arg.endswith('.b'):
                inputfile = arg
            else:
                print("Invalid format for --input. The file must end with '.b'.")
                sys.exit(2)

    r = Runner()
    print("loading ..")
    r.load(inputfile)
    print("running ..")
    r.run(singlestep, breakpoints, trace)
    print("done.")

if __name__ == "__main__":
    main(sys.argv[1:])