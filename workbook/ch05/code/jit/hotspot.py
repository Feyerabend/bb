from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Any, Optional # Dict, Callable, Union
#import struct
import unittest
#import sys
from contextlib import contextmanager
from io import StringIO
import time

class VMError(Exception):
    pass

class StackUnderflowError(VMError):
    pass

class InvalidInstructionError(VMError):
    pass

class MemoryError(VMError):
    pass

class OpCode(Enum):
    PUSH = 0x01
    POP = 0x02
    DUP = 0x03
    SWAP = 0x04
    ROT = 0x05
    ADD = 0x10
    SUB = 0x11
    MUL = 0x12
    DIV = 0x13
    MOD = 0x14
    NEG = 0x15
    AND = 0x20
    OR = 0x21
    XOR = 0x22
    NOT = 0x23
    EQ = 0x30
    NE = 0x31
    LT = 0x32
    LE = 0x33
    GT = 0x34
    GE = 0x35
    JUMP = 0x40
    JUMP_IF_ZERO = 0x41
    JUMP_IF_NOT_ZERO = 0x42
    CALL = 0x43
    RET = 0x44
    LOAD = 0x50
    STORE = 0x51
    LOAD_LOCAL = 0x52
    STORE_LOCAL = 0x53
    PRINT = 0x60
    PRINT_CHAR = 0x61
    INPUT = 0x62
    HALT = 0x70
    NOP = 0x71
    TRACE = 0x80
    BREAKPOINT = 0x81

@dataclass
class Instruction:
    opcode: OpCode
    operands: List[Any]
    address: int = 0
    
    def __str__(self):
        if self.operands:
            return f"{self.opcode.name} {', '.join(map(str, self.operands))}"
        return self.opcode.name
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        expected_operands = {
            OpCode.PUSH: 1,
            OpCode.POP: 0,
            OpCode.DUP: 0,
            OpCode.SWAP: 0,
            OpCode.ROT: 0,
            OpCode.ADD: 0,
            OpCode.SUB: 0,
            OpCode.MUL: 0,
            OpCode.DIV: 0,
            OpCode.MOD: 0,
            OpCode.NEG: 0,
            OpCode.AND: 0,
            OpCode.OR: 0,
            OpCode.XOR: 0,
            OpCode.NOT: 0,
            OpCode.EQ: 0,
            OpCode.NE: 0,
            OpCode.LT: 0,
            OpCode.LE: 0,
            OpCode.GT: 0,
            OpCode.GE: 0,
            OpCode.JUMP: 1,
            OpCode.JUMP_IF_ZERO: 1,
            OpCode.JUMP_IF_NOT_ZERO: 1,
            OpCode.CALL: 1,
            OpCode.RET: 0,
            OpCode.LOAD: 1,
            OpCode.STORE: 1,
            OpCode.LOAD_LOCAL: 1,
            OpCode.STORE_LOCAL: 1,
            OpCode.PRINT: 0,
            OpCode.PRINT_CHAR: 0,
            OpCode.INPUT: 0,
            OpCode.HALT: 0,
            OpCode.NOP: 0,
            OpCode.TRACE: 0,
            OpCode.BREAKPOINT: 0,
        }
        expected = expected_operands.get(self.opcode, 0)
        if len(self.operands) != expected:
            raise InvalidInstructionError(
                f"Instruction {self.opcode.name} expects {expected} operands, got {len(self.operands)}"
            )

class InstructionHandler(ABC):
    @abstractmethod
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        pass
    
    @abstractmethod
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        pass
    
    def _check_stack_size(self, vm: 'HotspotVM', required: int, operation: str):
        if len(vm.stack) < required:
            raise StackUnderflowError(f"Stack underflow in {operation}: need {required}, have {len(vm.stack)}")

class StackHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        opcode = vm.current_instruction.opcode
        if opcode == OpCode.PUSH:
            vm.stack.append(operands[0])
        elif opcode == OpCode.POP:
            self._check_stack_size(vm, 1, "POP")
            vm.stack.pop()
        elif opcode == OpCode.DUP:
            self._check_stack_size(vm, 1, "DUP")
            vm.stack.append(vm.stack[-1])
        elif opcode == OpCode.SWAP:
            self._check_stack_size(vm, 2, "SWAP")
            vm.stack[-1], vm.stack[-2] = vm.stack[-2], vm.stack[-1]
        elif opcode == OpCode.ROT:
            self._check_stack_size(vm, 3, "ROT")
            c = vm.stack.pop()
            b = vm.stack.pop()
            a = vm.stack.pop()
            vm.stack.extend([b, c, a])
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        opcode = vm.current_instruction.opcode
        if opcode == OpCode.PUSH:
            return [f"    stack.append({repr(operands[0])})"]
        elif opcode == OpCode.POP:
            return ["    if not stack: raise StackUnderflowError('POP')",
                   "    stack.pop()"]
        elif opcode == OpCode.DUP:
            return ["    if not stack: raise StackUnderflowError('DUP')",
                   "    stack.append(stack[-1])"]
        elif opcode == OpCode.SWAP:
            return ["    if len(stack) < 2: raise StackUnderflowError('SWAP')",
                   "    stack[-1], stack[-2] = stack[-2], stack[-1]"]
        elif opcode == OpCode.ROT:
            return ["    if len(stack) < 3: raise StackUnderflowError('ROT')",
                   "    c, b, a = stack.pop(), stack.pop(), stack.pop()",
                   "    stack.extend([b, c, a])"]

class ArithmeticHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        opcode = vm.current_instruction.opcode
        if opcode == OpCode.NEG:
            self._check_stack_size(vm, 1, "NEG")
            vm.stack[-1] = -vm.stack[-1]
            return None
        self._check_stack_size(vm, 2, opcode.name)
        b = vm.stack.pop()
        a = vm.stack.pop()
        try:
            if opcode == OpCode.ADD:
                result = a + b
            elif opcode == OpCode.SUB:
                result = a - b
            elif opcode == OpCode.MUL:
                result = a * b
            elif opcode == OpCode.DIV:
                if b == 0:
                    raise VMError("Division by zero")
                result = a / b
            elif opcode == OpCode.MOD:
                if b == 0:
                    raise VMError("Modulo by zero")
                result = a % b
        except (TypeError, ZeroDivisionError) as e:
            raise VMError(f"Arithmetic error in {opcode.name}: {e}")
        vm.stack.append(result)
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        opcode = vm.current_instruction.opcode
        if opcode == OpCode.NEG:
            return ["    if not stack: raise StackUnderflowError('NEG')",
                   "    stack[-1] = -stack[-1]"]
        op_map = {
            OpCode.ADD: "+", OpCode.SUB: "-", OpCode.MUL: "*", OpCode.DIV: "/", OpCode.MOD: "%"
        }
        op = op_map[opcode]
        lines = ["    if len(stack) < 2: raise StackUnderflowError('" + opcode.name + "')",
                "    b = stack.pop()",
                "    a = stack.pop()"]
        if opcode in [OpCode.DIV, OpCode.MOD]:
            lines.append("    if b == 0: raise VMError('" + opcode.name.lower() + " by zero')")
        lines.append(f"    stack.append(a {op} b)")
        return lines

class ComparisonHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        self._check_stack_size(vm, 2, vm.current_instruction.opcode.name)
        b = vm.stack.pop()
        a = vm.stack.pop()
        opcode = vm.current_instruction.opcode
        if opcode == OpCode.EQ:
            result = 1 if a == b else 0
        elif opcode == OpCode.NE:
            result = 1 if a != b else 0
        elif opcode == OpCode.LT:
            result = 1 if a < b else 0
        elif opcode == OpCode.LE:
            result = 1 if a <= b else 0
        elif opcode == OpCode.GT:
            result = 1 if a > b else 0
        elif opcode == OpCode.GE:
            result = 1 if a >= b else 0
        vm.stack.append(result)
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        op_map = {
            OpCode.EQ: "==", OpCode.NE: "!=", OpCode.LT: "<", OpCode.LE: "<=",
            OpCode.GT: ">", OpCode.GE: ">="
        }
        op = op_map[vm.current_instruction.opcode]
        return [
            "    if len(stack) < 2: raise StackUnderflowError('" + vm.current_instruction.opcode.name + "')",
            "    b = stack.pop()",
            "    a = stack.pop()",
            f"    stack.append(1 if a {op} b else 0)"
        ]

class ControlFlowHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        opcode = vm.current_instruction.opcode

        if opcode == OpCode.JUMP:
            target = operands[0]
            if not (0 <= target < len(vm.instructions)):
                raise VMError(f"Jump target {target} out of bounds")
            return target

        elif opcode == OpCode.JUMP_IF_ZERO:
            self._check_stack_size(vm, 1, "JUMP_IF_ZERO")
            if vm.stack.pop() == 0:
                target = operands[0]
                if not (0 <= target < len(vm.instructions)):
                    raise VMError(f"Jump target {target} out of bounds")
                return target

        elif opcode == OpCode.JUMP_IF_NOT_ZERO:
            self._check_stack_size(vm, 1, "JUMP_IF_NOT_ZERO")
            if vm.stack.pop() != 0:
                target = operands[0]
                if not (0 <= target < len(vm.instructions)):
                    raise VMError(f"Jump target {target} out of bounds")
                return target

        elif opcode == OpCode.CALL:
            target = operands[0]
            if not (0 <= target < len(vm.instructions)):
                raise VMError(f"Call target {target} out of bounds")
            vm.call_stack.append(vm.pc + 1)
            return target

        elif opcode == OpCode.RET:
            if not vm.call_stack:
                raise VMError("Return with empty call stack")
            return vm.call_stack.pop()
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        return ["    # Control flow - falling back to interpreter",
               f"    return {vm.pc}  # Exit JIT region"]

class IOHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        opcode = vm.current_instruction.opcode

        if opcode == OpCode.PRINT:
            self._check_stack_size(vm, 1, "PRINT")
            value = vm.stack.pop()
            print(f"Output: {value}")

        elif opcode == OpCode.PRINT_CHAR:
            self._check_stack_size(vm, 1, "PRINT_CHAR")
            char_code = vm.stack.pop()
            if not isinstance(char_code, int) or not (0 <= char_code <= 127):
                raise VMError(f"Invalid character code: {char_code}")
            print(chr(char_code), end='')

        elif opcode == OpCode.INPUT:
            try:
                value = input("Input: ")
                if not value:
                    vm.stack.append("")
                    return None
                try:
                    if '.' in value:
                        vm.stack.append(float(value))
                    else:
                        vm.stack.append(int(value))
                except ValueError:
                    vm.stack.append(value)
            except EOFError:
                vm.stack.append("")
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        opcode = vm.current_instruction.opcode

        if opcode == OpCode.PRINT:
            return ["    if not stack: raise StackUnderflowError('PRINT')",
                   "    print(f'Output: {stack.pop()}')"]

        elif opcode == OpCode.PRINT_CHAR:
            return ["    if not stack: raise StackUnderflowError('PRINT_CHAR')",
                   "    char_code = stack.pop()",
                   "    if not (0 <= char_code <= 127): raise VMError('Invalid char code')",
                   "    print(chr(char_code), end='')"]
        else:
            return ["    # I/O operation - not JIT compiled"]

class MemoryHandler(InstructionHandler):
    def execute(self, vm: 'HotspotVM', operands: List[Any]) -> Optional[int]:
        opcode = vm.current_instruction.opcode

        if opcode == OpCode.LOAD:
            address = operands[0]
            if address < 0:
                raise MemoryError(f"Invalid memory address: {address}")
            vm.stack.append(vm.memory.get(address, 0))

        elif opcode == OpCode.STORE:
            address = operands[0]
            if address < 0:
                raise MemoryError(f"Invalid memory address: {address}")
            self._check_stack_size(vm, 1, "STORE")
            value = vm.stack.pop()
            vm.memory[address] = value

        elif opcode == OpCode.LOAD_LOCAL:
            index = operands[0]
            if index < 0:
                raise MemoryError(f"Invalid local index: {index}")
            while index >= len(vm.locals):
                vm.locals.append(0)
            vm.stack.append(vm.locals[index])

        elif opcode == OpCode.STORE_LOCAL:
            index = operands[0]
            if index < 0:
                raise MemoryError(f"Invalid local index: {index}")
            self._check_stack_size(vm, 1, "STORE_LOCAL")
            value = vm.stack.pop()
            while index >= len(vm.locals):
                vm.locals.append(0)
            vm.locals[index] = value
        return None
    
    def compile(self, vm: 'HotspotVM', operands: List[Any]) -> List[str]:
        opcode = vm.current_instruction.opcode

        if opcode == OpCode.LOAD:
            return [f"    if {operands[0]} < 0: raise MemoryError('Invalid address')",
                   f"    stack.append(vm.memory.get({operands[0]}, 0))"]

        elif opcode == OpCode.STORE:
            return [f"    if {operands[0]} < 0: raise MemoryError('Invalid address')",
                   "    if not stack: raise StackUnderflowError('STORE')",
                   f"    vm.memory[{operands[0]}] = stack.pop()"]

        elif opcode == OpCode.LOAD_LOCAL:
            return [f"    if {operands[0]} < 0: raise MemoryError('Invalid local index')",
                   f"    while {operands[0]} >= len(vm.locals): vm.locals.append(0)",
                   f"    stack.append(vm.locals[{operands[0]}])"]

        elif opcode == OpCode.STORE_LOCAL:
            return [f"    if {operands[0]} < 0: raise MemoryError('Invalid local index')",
                   "    if not stack: raise StackUnderflowError('STORE_LOCAL')",
                   f"    while {operands[0]} >= len(vm.locals): vm.locals.append(0)",
                   f"    vm.locals[{operands[0]}] = stack.pop()"]

class HotspotVM:
    def __init__(self, hotspot_threshold=3):
        self.stack = []
        self.call_stack = []
        self.memory = {}
        self.locals = []
        self.pc = 0
        self.instructions = []
        self.jit_cache = {}
        self.exec_count = {}
        self.hotspot_threshold = hotspot_threshold
        self.compiled_regions = set()
        self.current_instruction = None
        self.handlers = {}
        self._register_handlers()
        self.debug = False
        self.trace = False
        self.max_instructions = 20000  # Increased for debugging
        self.instruction_count = 0
        self.max_stack_size = 1000
        self.max_call_depth = 100
    
    def _register_handlers(self):
        stack_handler = StackHandler()
        arith_handler = ArithmeticHandler()
        comp_handler = ComparisonHandler()
        control_handler = ControlFlowHandler()
        io_handler = IOHandler()
        memory_handler = MemoryHandler()
        for op in [OpCode.PUSH, OpCode.POP, OpCode.DUP, OpCode.SWAP, OpCode.ROT]:
            self.handlers[op] = stack_handler
        for op in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD, OpCode.NEG]:
            self.handlers[op] = arith_handler
        for op in [OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE]:
            self.handlers[op] = comp_handler
        for op in [OpCode.JUMP, OpCode.JUMP_IF_ZERO, OpCode.JUMP_IF_NOT_ZERO, OpCode.CALL, OpCode.RET]:
            self.handlers[op] = control_handler
        for op in [OpCode.PRINT, OpCode.PRINT_CHAR, OpCode.INPUT]:
            self.handlers[op] = io_handler
        for op in [OpCode.LOAD, OpCode.STORE, OpCode.LOAD_LOCAL, OpCode.STORE_LOCAL]:
            self.handlers[op] = memory_handler
    
    def reset(self):
        self.stack.clear()
        self.call_stack.clear()
        self.memory.clear()
        self.locals.clear()
        self.pc = 0
        self.instruction_count = 0
        self.exec_count.clear()
        self.jit_cache.clear()
        self.compiled_regions.clear()
    
    def load_program(self, instructions: List[Instruction]):
        if not instructions:
            raise ValueError("Cannot load empty program")
        self.instructions = instructions
        self.pc = 0
        for i, instruction in enumerate(self.instructions):
            instruction.address = i
    
    def _validate_state(self):
        if len(self.stack) > self.max_stack_size:
            raise VMError(f"Stack overflow: {len(self.stack)} > {self.max_stack_size}")
        if len(self.call_stack) > self.max_call_depth:
            raise VMError(f"Call stack overflow: {len(self.call_stack)} > {self.max_call_depth}")
        if self.instruction_count > self.max_instructions:
            raise VMError(f"Execution limit exceeded: {self.instruction_count} instructions")
    
    def run(self):
        if not self.instructions:
            raise ValueError("No program loaded")
        try:
            while self.pc < len(self.instructions):
                self._validate_state()
                self.instruction_count += 1
                if self.instructions[self.pc].opcode == OpCode.HALT:
                    if self.debug:
                        print("HALT instruction encountered")
                    break
                if self.pc in self.jit_cache:
                    if self.debug:
                        print(f"Executing JIT-compiled code at PC {self.pc}")
                    try:
                        new_pc = self.jit_cache[self.pc]()
                        if not isinstance(new_pc, int) or not (0 <= new_pc <= len(self.instructions)):
                            raise VMError(f"JIT function returned invalid PC: {new_pc}")
                        self.pc = new_pc
                        continue
                    except Exception as e:
                        if self.debug:
                            print(f"JIT execution failed: {e}, falling back to interpreter")
                        del self.jit_cache[self.pc]
                self.exec_count[self.pc] = self.exec_count.get(self.pc, 0) + 1
                if (self.exec_count[self.pc] >= self.hotspot_threshold and 
                    self.pc not in self.compiled_regions):
                    region = self.detect_compilation_region(self.pc)
                    if region:
                        self.jit_compile_region(region)
                        continue
                instruction = self.instructions[self.pc]
                self.current_instruction = instruction
                if self.trace:
                    print(f"PC:{self.pc:3d} {instruction} | Stack: {self.stack}")
                if instruction.opcode in self.handlers:
                    new_pc = self.handlers[instruction.opcode].execute(self, instruction.operands)
                    if new_pc is not None:
                        if not (0 <= new_pc <= len(self.instructions)):
                            raise VMError(f"Invalid PC from instruction: {new_pc}")
                        self.pc = new_pc
                    else:
                        self.pc += 1
                elif instruction.opcode == OpCode.NOP:
                    self.pc += 1
                else:
                    raise InvalidInstructionError(f"Unknown opcode: {instruction.opcode}")
        except VMError:
            raise
        except Exception as e:
            raise VMError(f"Unexpected error during execution at PC {self.pc}: {e}")
    
    def detect_compilation_region(self, start_pc):
        region_end = start_pc
        max_scan = min(start_pc + 20, len(self.instructions))
        non_compilable_ops = {OpCode.JUMP, OpCode.JUMP_IF_ZERO, OpCode.JUMP_IF_NOT_ZERO, 
                             OpCode.CALL, OpCode.RET, OpCode.HALT, OpCode.INPUT}
        for i in range(start_pc, max_scan):
            if i >= len(self.instructions):
                break
            instruction = self.instructions[i]
            if instruction.opcode in non_compilable_ops:
                break
            region_end = i + 1
        if region_end - start_pc >= 3:
            return (start_pc, region_end)
        return None
    
    def jit_compile_region(self, region):
        start_pc, end_pc = region
        if self.debug:
            print(f"JIT compiling region: PC {start_pc} to {end_pc-1}")
            print(f"Stack before JIT compilation: {self.stack}")
        for pc in range(start_pc, end_pc):
            self.compiled_regions.add(pc)
        try:
            code_lines = [
                "def jit_func():",
                "    stack = vm.stack",
                "    memory = vm.memory",
                "    locals = vm.locals"
            ]
            for pc in range(start_pc, end_pc):
                instruction = self.instructions[pc]
                self.current_instruction = instruction
                if instruction.opcode in self.handlers:
                    handler_lines = self.handlers[instruction.opcode].compile(self, instruction.operands)
                    code_lines.extend(handler_lines)
                else:
                    code_lines.append(f"    # Unknown instruction: {instruction}")
            code_lines.append(f"    if vm.debug: print(f'Stack after JIT region {start_pc}-{end_pc-1}: {{stack}}')")
            code_lines.append(f"    return {end_pc}")
            code_str = "\n".join(code_lines)
            if self.debug:
                print("Generated JIT code:")
                print(code_str)
                print("-" * 40)
            local_env = {}
            global_env = {
                "vm": self, 
                "print": print,
                "StackUnderflowError": StackUnderflowError,
                "VMError": VMError,
                "MemoryError": MemoryError
            }
            exec(code_str, global_env, local_env)
            self.jit_cache[start_pc] = local_env["jit_func"]
        except (SyntaxError, TypeError, NameError) as e:
            if self.debug:
                print(f"JIT compilation failed: {e}")
            for pc in range(start_pc, end_pc):
                self.compiled_regions.discard(pc)

class Assembler:
    @staticmethod
    def assemble(source_lines: List[str]) -> List[Instruction]:
        instructions = []
        labels = {}
        processed_lines = []
        for line in source_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '#' in line:
                    line = line[:line.index('#')].strip()
                if line:
                    processed_lines.append(line)
        instruction_count = 0
        for line in processed_lines:
            if line.endswith(':'):
                label = line[:-1].strip()
                if label in labels:
                    raise ValueError(f"Duplicate label: {label}")
                labels[label] = instruction_count
            else:
                instruction_count += 1
        for line in processed_lines:
            if line.endswith(':'):
                continue
            parts = line.split()
            if not parts:
                continue
            opcode_name = parts[0].upper()
            try:
                opcode = OpCode[opcode_name]
            except KeyError:
                raise ValueError(f"Unknown opcode: {opcode_name}")
            operands = []
            for operand_str in parts[1:]:
                operand_str = operand_str.strip(',')
                if operand_str in labels:
                    operands.append(labels[operand_str])
                else:
                    try:
                        if '.' in operand_str:
                            operands.append(float(operand_str))
                        else:
                            operands.append(int(operand_str))
                    except ValueError:
                        if operand_str.startswith('"') and operand_str.endswith('"'):
                            operands.append(operand_str[1:-1])
                        else:
                            operands.append(operand_str)
            instructions.append(Instruction(opcode, operands))
        return instructions

class Disassembler:
    @staticmethod
    def disassemble(instructions: List[Instruction]) -> str:
        lines = []
        for i, instruction in enumerate(instructions):
            address = f"{i:3d}: "
            if instruction.operands:
                operand_str = ", ".join(str(op) for op in instruction.operands)
                line = f"{address}{instruction.opcode.name} {operand_str}"
            else:
                line = f"{address}{instruction.opcode.name}"
            lines.append(line)
        return "\n".join(lines)

class VMProfiler:
    def __init__(self, vm: HotspotVM):
        self.vm = vm
        self.start_time = None
        self.execution_times = {}
        self.hotspots = []
    
    def start_profiling(self):
        self.start_time = time.time()
        self.vm.trace = True
    
    def stop_profiling(self):
        if self.start_time is None:
            return "No profiling session active"
        total_time = time.time() - self.start_time
        sorted_counts = sorted(self.vm.exec_count.items(), key=lambda x: x[1], reverse=True)
        self.hotspots = sorted_counts[:10]
        report = f"VM Execution Profile\n"
        report += f"{'='*50}\n"
        report += f"Total execution time: {total_time:.4f} seconds\n"
        report += f"Instructions executed: {self.vm.instruction_count}\n"
        report += f"JIT regions compiled: {len(self.vm.jit_cache)}\n"
        report += f"\nTop Hotspots:\n"
        report += f"{'PC':<5} {'Count':<8} {'Instruction':<30}\n"
        report += f"{'-'*50}\n"
        for pc, count in self.hotspots:
            if pc < len(self.vm.instructions):
                instr = self.vm.instructions[pc]
                report += f"{pc:<5} {count:<8} {str(instr):<30}\n"
        return report

def create_fibonacci_program(n: int) -> List[Instruction]:
    return Assembler.assemble([
        f"PUSH {n}",
        "STORE_LOCAL 0",
        "PUSH 0",
        "STORE_LOCAL 1",
        "PUSH 1",
        "STORE_LOCAL 2",
        "PUSH 2",
        "STORE_LOCAL 3",
        "loop:",
        "LOAD_LOCAL 3",
        "LOAD_LOCAL 0",
        "GE",
        "JUMP_IF_NOT_ZERO done",
        "LOAD_LOCAL 1",
        "LOAD_LOCAL 2",
        "ADD",
        "STORE_LOCAL 1",
        "LOAD_LOCAL 2",
        "STORE_LOCAL 2",
        "LOAD_LOCAL 3",
        "PUSH 1",
        "ADD",
        "STORE_LOCAL 3",
        "JUMP loop",
        "done:",
        "LOAD_LOCAL 2",
        "PRINT",
        "LOAD_LOCAL 2",
        "HALT"
    ])

def create_factorial_program(n: int) -> List[Instruction]:
    return Assembler.assemble([
        f"PUSH {n}",
        "STORE_LOCAL 0",
        "PUSH 1",
        "STORE_LOCAL 1",
        "loop:",
        "LOAD_LOCAL 0",
        "PUSH 0",
        "LE",
        "JUMP_IF_NOT_ZERO done",
        "LOAD_LOCAL 1",
        "LOAD_LOCAL 0",
        "MUL",
        "STORE_LOCAL 1",
        "LOAD_LOCAL 0",
        "PUSH 1",
        "SUB",
        "STORE_LOCAL 0",
        "JUMP loop",
        "done:",
        "LOAD_LOCAL 1",
        "PRINT",
        "LOAD_LOCAL 1",
        "HALT"
    ])

class TestHotspotVM(unittest.TestCase):
    def setUp(self):
        self.vm = HotspotVM()
    
    def test_basic_stack_operations(self):
        instructions = [
            Instruction(OpCode.PUSH, [42]),
            Instruction(OpCode.DUP, []),
            Instruction(OpCode.PUSH, [10]),
            Instruction(OpCode.SWAP, []),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [42, 10, 42])
    
    def test_arithmetic_operations(self):
        instructions = [
            Instruction(OpCode.PUSH, [10]),
            Instruction(OpCode.PUSH, [5]),
            Instruction(OpCode.ADD, []),
            Instruction(OpCode.PUSH, [3]),
            Instruction(OpCode.MUL, []),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [45])
    
    def test_comparison_operations(self):
        instructions = [
            Instruction(OpCode.PUSH, [10]),
            Instruction(OpCode.PUSH, [5]),
            Instruction(OpCode.GT, []),
            Instruction(OpCode.PUSH, [3]),
            Instruction(OpCode.PUSH, [3]),
            Instruction(OpCode.EQ, []),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [1, 1])
    
    def test_control_flow(self):
        instructions = [
            Instruction(OpCode.PUSH, [1]),
            Instruction(OpCode.JUMP_IF_NOT_ZERO, [4]),
            Instruction(OpCode.PUSH, [999]),
            Instruction(OpCode.HALT, []),
            Instruction(OpCode.PUSH, [42]),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [42])
    
    def test_memory_operations(self):
        instructions = [
            Instruction(OpCode.PUSH, [100]),
            Instruction(OpCode.STORE, [10]),
            Instruction(OpCode.LOAD, [10]),
            Instruction(OpCode.PUSH, [200]),
            Instruction(OpCode.STORE_LOCAL, [0]),
            Instruction(OpCode.LOAD_LOCAL, [0]),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [100, 200])
        self.assertEqual(self.vm.memory[10], 100)
        self.assertEqual(self.vm.locals[0], 200)
    
    def test_jit_compilation(self):
        instructions = [
            Instruction(OpCode.PUSH, [3]),        # 0: counter = 3
            Instruction(OpCode.STORE_LOCAL, [0]), # 1: store counter
            Instruction(OpCode.PUSH, [0]),        # 2: sum = 0
            Instruction(OpCode.STORE_LOCAL, [1]), # 3: store sum
            Instruction(OpCode.LOAD_LOCAL, [0]),  # 4: load counter
            Instruction(OpCode.PUSH, [0]),        # 5: push 0
            Instruction(OpCode.LE, []),           # 6: counter <= 0?
            Instruction(OpCode.JUMP_IF_NOT_ZERO, [17]), # 7: jump to end if true
            Instruction(OpCode.LOAD_LOCAL, [1]),  # 8: load sum
            Instruction(OpCode.LOAD_LOCAL, [0]),  # 9: load counter
            Instruction(OpCode.ADD, []),          # 10: sum += counter
            Instruction(OpCode.STORE_LOCAL, [1]), # 11: store sum
            Instruction(OpCode.LOAD_LOCAL, [0]),  # 12: load counter
            Instruction(OpCode.PUSH, [1]),        # 13: push 1
            Instruction(OpCode.SUB, []),          # 14: counter -= 1
            Instruction(OpCode.STORE_LOCAL, [0]), # 15: store counter
            Instruction(OpCode.JUMP, [4]),        # 16: loop back
            Instruction(OpCode.LOAD_LOCAL, [1]),  # 17: load sum
            Instruction(OpCode.HALT, [])          # 18: end
        ]
        self.vm.hotspot_threshold = 3
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertGreater(len(self.vm.exec_count), 0)
        self.assertEqual(self.vm.stack, [6])  # 3 + 2 + 1 = 6
    
    def test_assembler(self):
        source = [
            "PUSH 10",
            "PUSH 20",
            "ADD",
            "HALT"
        ]
        instructions = Assembler.assemble(source)
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [30])
    
    def test_error_handling(self):
        instructions = [
            Instruction(OpCode.POP, []),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        with self.assertRaises(StackUnderflowError):
            self.vm.run()
        self.vm.reset()
        instructions = [
            Instruction(OpCode.PUSH, [10]),
            Instruction(OpCode.PUSH, [0]),
            Instruction(OpCode.DIV, []),
            Instruction(OpCode.HALT, [])
        ]
        self.vm.load_program(instructions)
        with self.assertRaises(VMError):
            self.vm.run()
    
    def test_factorial(self):
        n = 5
        expected_result = 120
        instructions = create_factorial_program(n)
        self.vm.load_program(instructions)
        self.vm.run()
        self.assertEqual(self.vm.stack, [expected_result])

def main():
    print("HotspotVM - JIT-Compiled Stack-Based Virtual Machine")
    print("=" * 55)
    vm = HotspotVM(hotspot_threshold=5)
    vm.debug = True
    print("\n1. Simple Arithmetic:")
    program1 = Assembler.assemble([
        "PUSH 15",
        "PUSH 25",
        "ADD",
        "PUSH 2",
        "MUL",
        "PRINT",
        "HALT"
    ])
    vm.load_program(program1)
    vm.run()
    print("\n2. Fibonacci Calculation (n=10):")
    vm.reset()
    fib_program = create_fibonacci_program(10)
    vm.load_program(fib_program)
    profiler = VMProfiler(vm)
    profiler.start_profiling()
    vm.run()
    print(profiler.stop_profiling())
    print("\n3. JIT Compilation Demo (Sum 1 to 10):")
    vm.reset()
    vm.hotspot_threshold = 3
    hot_loop = Assembler.assemble([
        "PUSH 10",
        "STORE_LOCAL 0",
        "PUSH 0",
        "STORE_LOCAL 1",
        "loop:",
        "LOAD_LOCAL 0",
        "PUSH 0",
        "LE",
        "JUMP_IF_NOT_ZERO done",
        "LOAD_LOCAL 1",
        "LOAD_LOCAL 0",
        "ADD",
        "STORE_LOCAL 1",
        "LOAD_LOCAL 0",
        "PUSH 1",
        "SUB",
        "STORE_LOCAL 0",
        "JUMP loop",
        "done:",
        "LOAD_LOCAL 1",
        "PRINT",
        "LOAD_LOCAL 1",
        "HALT"
    ])
    vm.load_program(hot_loop)
    vm.run()
    print(f"\nJIT Statistics:")
    print(f"- Regions compiled: {len(vm.jit_cache)}")
    print(f"- Instructions executed: {vm.instruction_count}")
    print(f"- Hotspots detected: {len([c for c in vm.exec_count.values() if c >= vm.hotspot_threshold])}")

if __name__ == "__main__":
    print("Running tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    print("\n" + "="*60)
    main()


