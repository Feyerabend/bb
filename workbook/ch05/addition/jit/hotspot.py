from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol, runtime_checkable #Final, List



class VMError(Exception):
    """Base exception for all VM-related errors."""
    pass


class StackUnderflowError(VMError):
    pass


class InvalidInstructionError(VMError):
    pass


class MemoryAccessError(VMError):
    pass


class DivisionByZeroError(VMError):
    pass


class CallStackUnderflowError(VMError):
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


@dataclass(frozen=True)
class Instruction:
    opcode: OpCode
    operands: tuple[Any, ...] = field(default_factory=tuple)
    address: int = 0

    def __str__(self) -> str:
        if not self.operands:
            return self.opcode.name
        return f"{self.opcode.name} {' '.join(map(str, self.operands))}"

    def __post_init__(self) -> None:
        self._validate_operands_count()

    def _validate_operands_count(self) -> None:
        expected = {
            OpCode.PUSH: 1,
            OpCode.JUMP: 1,
            OpCode.JUMP_IF_ZERO: 1,
            OpCode.JUMP_IF_NOT_ZERO: 1,
            OpCode.CALL: 1,
            OpCode.LOAD: 1,
            OpCode.STORE: 1,
            OpCode.LOAD_LOCAL: 1,
            OpCode.STORE_LOCAL: 1,
        }.get(self.opcode, 0)

        if len(self.operands) != expected:
            raise InvalidInstructionError(
                f"{self.opcode.name} expects {expected} operand(s), got {len(self.operands)}"
            )




@runtime_checkable
class InstructionExecutor(Protocol):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        """Return new PC or None to continue with pc += 1"""


@runtime_checkable
class InstructionCompiler(Protocol):
    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        """Return list of python code lines (indented)"""


class InstructionHandler(ABC, InstructionExecutor, InstructionCompiler):
    """Base class for handlers that implement both execution and JIT compilation"""
    pass




class StackHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        stack = vm.stack
        match instr.opcode:
            case OpCode.PUSH:
                stack.append(instr.operands[0])
            case OpCode.POP:
                if not stack: raise StackUnderflowError("POP")
                stack.pop()
            case OpCode.DUP:
                if not stack: raise StackUnderflowError("DUP")
                stack.append(stack[-1])
            case OpCode.SWAP:
                if len(stack) < 2: raise StackUnderflowError("SWAP")
                stack[-1], stack[-2] = stack[-2], stack[-1]
            case OpCode.ROT:
                if len(stack) < 3: raise StackUnderflowError("ROT")
                c, b, a = stack.pop(), stack.pop(), stack.pop()
                stack.extend([b, c, a])
        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        match instr.opcode:
            case OpCode.PUSH:
                return [f"    stack.append({repr(instr.operands[0])})"]
            case OpCode.POP:
                return ["    if not stack: raise StackUnderflowError('POP')", "    stack.pop()"]
            case OpCode.DUP:
                return ["    if not stack: raise StackUnderflowError('DUP')", "    stack.append(stack[-1])"]
            case OpCode.SWAP:
                return ["    if len(stack) < 2: raise StackUnderflowError('SWAP')",
                        "    stack[-1], stack[-2] = stack[-2], stack[-1]"]
            case OpCode.ROT:
                return ["    if len(stack) < 3: raise StackUnderflowError('ROT')",
                        "    c, b, a = stack.pop(), stack.pop(), stack.pop()",
                        "    stack.extend([b, c, a])"]
        return []


class ArithmeticHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        stack = vm.stack
        if instr.opcode == OpCode.NEG:
            if not stack: raise StackUnderflowError("NEG")
            stack[-1] = -stack[-1]
            return None

        if len(stack) < 2: raise StackUnderflowError(instr.opcode.name)
        b = stack.pop()
        a = stack.pop()

        match instr.opcode:
            case OpCode.ADD: result = a + b
            case OpCode.SUB: result = a - b
            case OpCode.MUL: result = a * b
            case OpCode.DIV:
                if b == 0: raise DivisionByZeroError()
                result = a / b
            case OpCode.MOD:
                if b == 0: raise DivisionByZeroError()
                result = a % b
            case _:
                raise InvalidInstructionError(f"Unexpected arithmetic opcode: {instr.opcode}")
        stack.append(result)
        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        if instr.opcode == OpCode.NEG:
            return ["    if not stack: raise StackUnderflowError('NEG')", "    stack[-1] = -stack[-1]"]

        op_map = {OpCode.ADD: "+", OpCode.SUB: "-", OpCode.MUL: "*", OpCode.DIV: "/", OpCode.MOD: "%"}
        op = op_map[instr.opcode]

        lines = [
            f"    if len(stack) < 2: raise StackUnderflowError('{instr.opcode.name}')",
            "    b = stack.pop()",
            "    a = stack.pop()"
        ]
        if instr.opcode in (OpCode.DIV, OpCode.MOD):
            lines.append("    if b == 0: raise DivisionByZeroError()")
        lines.append(f"    stack.append(a {op} b)")
        return lines


class ComparisonHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        stack = vm.stack
        if len(stack) < 2: raise StackUnderflowError(instr.opcode.name)
        b = stack.pop()
        a = stack.pop()

        result = {
            OpCode.EQ: a == b,
            OpCode.NE: a != b,
            OpCode.LT: a < b,
            OpCode.LE: a <= b,
            OpCode.GT: a > b,
            OpCode.GE: a >= b,
        }[instr.opcode]

        stack.append(1 if result else 0)
        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        op_map = {
            OpCode.EQ: "==", OpCode.NE: "!=", OpCode.LT: "<",
            OpCode.LE: "<=", OpCode.GT: ">", OpCode.GE: ">="
        }
        op = op_map[instr.opcode]

        return [
            f"    if len(stack) < 2: raise StackUnderflowError('{instr.opcode.name}')",
            "    b = stack.pop()",
            "    a = stack.pop()",
            f"    stack.append(1 if a {op} b else 0)"
        ]


class ControlFlowHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        match instr.opcode:
            case OpCode.JUMP:
                target = instr.operands[0]
                if not (0 <= target < len(vm.instructions)):
                    raise VMError(f"Jump target out of bounds: {target}")
                return target

            case OpCode.JUMP_IF_ZERO:
                if not vm.stack: raise StackUnderflowError("JUMP_IF_ZERO")
                if vm.stack.pop() == 0:
                    target = instr.operands[0]
                    if not (0 <= target < len(vm.instructions)):
                        raise VMError(f"Jump target out of bounds: {target}")
                    return target

            case OpCode.JUMP_IF_NOT_ZERO:
                if not vm.stack: raise StackUnderflowError("JUMP_IF_NOT_ZERO")
                if vm.stack.pop() != 0:
                    target = instr.operands[0]
                    if not (0 <= target < len(vm.instructions)):
                        raise VMError(f"Jump target out of bounds: {target}")
                    return target

            case OpCode.CALL:
                target = instr.operands[0]
                if not (0 <= target < len(vm.instructions)):
                    raise VMError(f"Call target out of bounds: {target}")
                vm.call_stack.append(vm.pc + 1)
                return target

            case OpCode.RET:
                if not vm.call_stack:
                    raise CallStackUnderflowError("RET with empty call stack")
                return vm.call_stack.pop()

        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        # Control flow is usually not directly jittable in simple linear regions
        return [
            "    # Control flow instruction - cannot be fully JIT compiled in linear block",
            f"    return {vm.pc}  # force exit of current JIT region"
        ]


class MemoryHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        match instr.opcode:
            case OpCode.LOAD:
                addr = instr.operands[0]
                if addr < 0:
                    raise MemoryAccessError(f"Negative memory address: {addr}")
                vm.stack.append(vm.memory.get(addr, 0))

            case OpCode.STORE:
                addr = instr.operands[0]
                if addr < 0:
                    raise MemoryAccessError(f"Negative memory address: {addr}")
                if not vm.stack:
                    raise StackUnderflowError("STORE")
                vm.memory[addr] = vm.stack.pop()

            case OpCode.LOAD_LOCAL:
                idx = instr.operands[0]
                if idx < 0:
                    raise MemoryAccessError(f"Negative local index: {idx}")
                while idx >= len(vm.locals):
                    vm.locals.append(0)
                vm.stack.append(vm.locals[idx])

            case OpCode.STORE_LOCAL:
                idx = instr.operands[0]
                if idx < 0:
                    raise MemoryAccessError(f"Negative local index: {idx}")
                if not vm.stack:
                    raise StackUnderflowError("STORE_LOCAL")
                while idx >= len(vm.locals):
                    vm.locals.append(0)
                vm.locals[idx] = vm.stack.pop()

        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        match instr.opcode:
            case OpCode.LOAD:
                addr = instr.operands[0]
                return [
                    f"    if {addr} < 0: raise MemoryAccessError('Negative address')",
                    f"    stack.append(memory.get({addr}, 0))"
                ]
            case OpCode.STORE:
                addr = instr.operands[0]
                return [
                    f"    if {addr} < 0: raise MemoryAccessError('Negative address')",
                    "    if not stack: raise StackUnderflowError('STORE')",
                    f"    memory[{addr}] = stack.pop()"
                ]
            case OpCode.LOAD_LOCAL:
                idx = instr.operands[0]
                return [
                    f"    if {idx} < 0: raise MemoryAccessError('Negative local index')",
                    f"    while {idx} >= len(locals): locals.append(0)",
                    f"    stack.append(locals[{idx}])"
                ]
            case OpCode.STORE_LOCAL:
                idx = instr.operands[0]
                return [
                    f"    if {idx} < 0: raise MemoryAccessError('Negative local index')",
                    "    if not stack: raise StackUnderflowError('STORE_LOCAL')",
                    f"    while {idx} >= len(locals): locals.append(0)",
                    f"    locals[{idx}] = stack.pop()"
                ]
        return []


class IOHandler(InstructionHandler):
    def execute(self, vm: 'ExecutionEngine', instr: Instruction) -> Optional[int]:
        match instr.opcode:
            case OpCode.PRINT:
                if not vm.stack: raise StackUnderflowError("PRINT")
                print(f"Output: {vm.stack.pop()}")

            case OpCode.PRINT_CHAR:
                if not vm.stack: raise StackUnderflowError("PRINT_CHAR")
                code = vm.stack.pop()
                if not isinstance(code, int) or not (0 <= code <= 127):
                    raise VMError(f"Invalid char code: {code}")
                print(chr(code), end="")

            case OpCode.INPUT:
                try:
                    value = input("Input: ")
                    if value.strip() == "":
                        vm.stack.append("")
                    else:
                        try:
                            vm.stack.append(int(value))
                        except ValueError:
                            try:
                                vm.stack.append(float(value))
                            except ValueError:
                                vm.stack.append(value)
                except EOFError:
                    vm.stack.append("")

        return None

    def compile_to_python(self, vm: 'ExecutionEngine', instr: Instruction) -> list[str]:
        match instr.opcode:
            case OpCode.PRINT:
                return [
                    "    if not stack: raise StackUnderflowError('PRINT')",
                    "    print(f'Output: {{stack.pop()}}')"
                ]
            case OpCode.PRINT_CHAR:
                return [
                    "    if not stack: raise StackUnderflowError('PRINT_CHAR')",
                    "    code = stack.pop()",
                    "    if not isinstance(code, int) or not (0 <= code <= 127):",
                    "        raise VMError(f'Invalid char code: {{code}}')",
                    "    print(chr(code), end='')"
                ]
            case _:
                return ["    # I/O operation - not supported in JIT"]
        return []




class ExecutionEngine:
    def __init__(self, hotspot_threshold: int = 5):
        self.stack: list[Any] = []
        self.call_stack: list[int] = []
        self.memory: dict[int, Any] = {}
        self.locals: list[Any] = []
        self.pc: int = 0
        self.instructions: list[Instruction] = []
        self.hotspot_threshold = hotspot_threshold
        self.exec_count: dict[int, int] = {}
        self.jit_cache: dict[int, callable] = {}
        self.handlers: dict[OpCode, InstructionHandler] = {}

        self._register_handlers()

    def _register_handlers(self) -> None:
        self.handlers.update({op: StackHandler() for op in [
            OpCode.PUSH, OpCode.POP, OpCode.DUP, OpCode.SWAP, OpCode.ROT]})
        self.handlers.update({op: ArithmeticHandler() for op in [
            OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD, OpCode.NEG]})
        self.handlers.update({op: ComparisonHandler() for op in [
            OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE]})
        self.handlers.update({op: ControlFlowHandler() for op in [
            OpCode.JUMP, OpCode.JUMP_IF_ZERO, OpCode.JUMP_IF_NOT_ZERO, OpCode.CALL, OpCode.RET]})
        self.handlers.update({op: MemoryHandler() for op in [
            OpCode.LOAD, OpCode.STORE, OpCode.LOAD_LOCAL, OpCode.STORE_LOCAL]})
        self.handlers.update({op: IOHandler() for op in [
            OpCode.PRINT, OpCode.PRINT_CHAR, OpCode.INPUT]})

    def load(self, instructions: list[Instruction]) -> None:
        if not instructions:
            raise ValueError("Cannot load empty program")
        self.instructions = instructions
        self.pc = 0
        for i, instr in enumerate(self.instructions):
            object.__setattr__(instr, 'address', i)  # frozen dataclass workaround

    def run(self) -> None:
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]

            if instr.opcode == OpCode.HALT:
                break

            # JIT fast path
            if self.pc in self.jit_cache:
                self.pc = self.jit_cache[self.pc]()
                continue

            # Hotspot detection
            self.exec_count[self.pc] = self.exec_count.get(self.pc, 0) + 1
            if self.exec_count[self.pc] >= self.hotspot_threshold:
                region = self._try_detect_hot_region()
                if region:
                    self._jit_compile_region(region)
                    continue

            # Normal interpreter path
            handler = self.handlers.get(instr.opcode)
            if handler is None:
                raise InvalidInstructionError(f"No handler for opcode: {instr.opcode}")

            new_pc = handler.execute(self, instr)
            self.pc = new_pc if new_pc is not None else self.pc + 1

    def _try_detect_hot_region(self) -> Optional[tuple[int, int]]:
        start = self.pc
        end = start
        max_scan = min(start + 30, len(self.instructions))

        forbidden = {
            OpCode.JUMP, OpCode.JUMP_IF_ZERO, OpCode.JUMP_IF_NOT_ZERO,
            OpCode.CALL, OpCode.RET, OpCode.HALT, OpCode.INPUT
        }

        for i in range(start, max_scan):
            if self.instructions[i].opcode in forbidden:
                break
            end = i + 1

        if end - start >= 5:
            return start, end
        return None

    def _jit_compile_region(self, region: tuple[int, int]) -> None:
        start, end = region
        lines = [
            "def jit_block():",
            "    stack = self.stack",
            "    memory = self.memory",
            "    locals = self.locals"
        ]

        for i in range(start, end):
            instr = self.instructions[i]
            handler = self.handlers.get(instr.opcode)
            if handler:
                lines.extend(handler.compile_to_python(self, instr))

        lines.append(f"    return {end}")

        code = "\n".join(lines)
        local_env = {}
        try:
            exec(code, {"self": self}, local_env)
            self.jit_cache[start] = local_env["jit_block"]
        except Exception as e:
            print(f"JIT compilation failed for region {start}-{end-1}: {e}")




if __name__ == "__main__":
    vm = ExecutionEngine(hotspot_threshold=3)

    # simple test
    program = [
        Instruction(OpCode.PUSH, (8,)),
        Instruction(OpCode.PUSH, (5,)),
        Instruction(OpCode.ADD, ()),
        Instruction(OpCode.PRINT, ()),
        Instruction(OpCode.PUSH, (13,)),
        Instruction(OpCode.PRINT_CHAR, ()),
        Instruction(OpCode.HALT, ())
    ]

    vm.load(program)
    print("Running simple program..")
    vm.run()
    print("\nFinal stack:", vm.stack)
