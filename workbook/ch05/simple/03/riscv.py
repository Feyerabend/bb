#!/usr/bin/env python3
"""
RISC-V RV32I Assembler and Virtual Machine
Implements some core instructions from the base integer instruction set
"""

import struct
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Instruction:
    """Represents a decoded RISC-V instruction"""
    opcode: str
    rd: int = 0
    rs1: int = 0
    rs2: int = 0
    imm: int = 0
    funct3: int = 0
    funct7: int = 0


class RISCVAssembler:
    """Two-pass assembler for RISC-V assembly code"""
    
    # ABI register name mappings
    REG_MAP = {
        'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
        't0': 5, 't1': 6, 't2': 7,
        's0': 8, 'fp': 8, 's1': 9,
        'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
        's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
        's8': 24, 's9': 25, 's10': 26, 's11': 27,
        't3': 28, 't4': 29, 't5': 30, 't6': 31
    }
    
    def __init__(self):
        self.labels: Dict[str, int] = {}
        self.instructions: List[Instruction] = []
        self.source_map: List[int] = []  # Maps instruction index to source line
        
    def parse_register(self, reg: str) -> int:
        """Parse register name (x0-x31 or ABI names)"""
        reg = reg.strip().lower().rstrip(',')
        
        if reg in self.REG_MAP:
            return self.REG_MAP[reg]
        
        if reg.startswith('x'):
            return int(reg[1:])
        
        raise ValueError(f"Invalid register: {reg}")
    
    def parse_immediate(self, imm: str) -> int:
        """Parse immediate value (decimal or hex)"""
        imm = imm.strip().rstrip(',')
        if imm.startswith('0x'):
            return int(imm, 16)
        return int(imm)
    
    def parse_offset(self, operand: str) -> Tuple[int, int]:
        """Parse offset(register) format -> (offset, register)"""
        if '(' in operand:
            offset, reg = operand.split('(')
            reg = reg.rstrip(')')
            return self.parse_immediate(offset), self.parse_register(reg)
        else:
            # Just a register, offset = 0
            return 0, self.parse_register(operand)
    
    def assemble(self, source: str) -> List[Instruction]:
        """Assemble RISC-V assembly code into instruction list"""
        lines = source.strip().split('\n')
        
        # First pass: collect labels
        addr = 0
        for line_num, line in enumerate(lines):
            # Remove comments
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # Check for label
            if ':' in line:
                label = line.split(':')[0].strip()
                self.labels[label] = addr
                # Check if there's an instruction on the same line
                rest = line.split(':', 1)[1].strip()
                if rest:
                    addr += 4
                    self.source_map.append(line_num)
            else:
                addr += 4
                self.source_map.append(line_num)
        
        # Second pass: assemble instructions
        addr = 0
        for line in lines:
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            # Skip label-only lines
            if ':' in line:
                rest = line.split(':', 1)[1].strip()
                if not rest:
                    continue
                line = rest
            
            instr = self.parse_instruction(line, addr)
            self.instructions.append(instr)
            addr += 4
        
        return self.instructions
    
    def parse_instruction(self, line: str, addr: int) -> Instruction:
        """Parse a single instruction"""
        parts = line.replace(',', ' ').split()
        op = parts[0].upper()
        
        # R-type: op rd, rs1, rs2
        if op in ['ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA', 'SLT', 'SLTU']:
            return Instruction(op, 
                             rd=self.parse_register(parts[1]),
                             rs1=self.parse_register(parts[2]),
                             rs2=self.parse_register(parts[3]))
        
        # M extension (multiply/divide)
        if op in ['MUL', 'MULH', 'MULHSU', 'MULHU', 'DIV', 'DIVU', 'REM', 'REMU']:
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             rs1=self.parse_register(parts[2]),
                             rs2=self.parse_register(parts[3]))
        
        # I-type arithmetic: op rd, rs1, imm
        if op in ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU']:
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             rs1=self.parse_register(parts[2]),
                             imm=self.parse_immediate(parts[3]))
        
        # I-type shifts: op rd, rs1, shamt
        if op in ['SLLI', 'SRLI', 'SRAI']:
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             rs1=self.parse_register(parts[2]),
                             imm=self.parse_immediate(parts[3]) & 0x1F)
        
        # Load: op rd, offset(rs1)
        if op in ['LB', 'LH', 'LW', 'LBU', 'LHU']:
            offset, base = self.parse_offset(parts[2])
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             rs1=base,
                             imm=offset)
        
        # Store: op rs2, offset(rs1)
        if op in ['SB', 'SH', 'SW']:
            offset, base = self.parse_offset(parts[2])
            return Instruction(op,
                             rs1=base,
                             rs2=self.parse_register(parts[1]),
                             imm=offset)
        
        # Branch: op rs1, rs2, label
        if op in ['BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']:
            target = parts[3]
            if target in self.labels:
                offset = self.labels[target] - addr
            else:
                offset = self.parse_immediate(target)
            return Instruction(op,
                             rs1=self.parse_register(parts[1]),
                             rs2=self.parse_register(parts[2]),
                             imm=offset)
        
        # JAL: jal rd, label
        if op == 'JAL':
            target = parts[2] if len(parts) > 2 else parts[1]
            rd = self.parse_register(parts[1]) if len(parts) > 2 else 1  # default ra
            
            if target in self.labels:
                offset = self.labels[target] - addr
            else:
                offset = self.parse_immediate(target)
            return Instruction(op, rd=rd, imm=offset)
        
        # JALR: jalr rd, rs1, offset
        if op == 'JALR':
            rd = self.parse_register(parts[1])
            if len(parts) > 3:
                offset, base = self.parse_offset(parts[2])
            else:
                offset, base = 0, self.parse_register(parts[2])
            return Instruction(op, rd=rd, rs1=base, imm=offset)
        
        # LUI: lui rd, imm
        if op == 'LUI':
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             imm=self.parse_immediate(parts[2]))
        
        # AUIPC: auipc rd, imm
        if op == 'AUIPC':
            return Instruction(op,
                             rd=self.parse_register(parts[1]),
                             imm=self.parse_immediate(parts[2]))
        
        # ECALL, EBREAK
        if op in ['ECALL', 'EBREAK']:
            return Instruction(op)
        
        # Pseudo-instructions
        if op == 'NOP':
            return Instruction('ADDI', rd=0, rs1=0, imm=0)
        
        if op == 'MV':  # mv rd, rs -> addi rd, rs, 0
            return Instruction('ADDI',
                             rd=self.parse_register(parts[1]),
                             rs1=self.parse_register(parts[2]),
                             imm=0)
        
        if op == 'LI':  # li rd, imm -> addi rd, x0, imm
            return Instruction('ADDI',
                             rd=self.parse_register(parts[1]),
                             rs1=0,
                             imm=self.parse_immediate(parts[2]))
        
        if op == 'J':  # j label -> jal x0, label
            target = parts[1]
            if target in self.labels:
                offset = self.labels[target] - addr
            else:
                offset = self.parse_immediate(target)
            return Instruction('JAL', rd=0, imm=offset)
        
        if op == 'RET':  # ret -> jalr x0, ra, 0
            return Instruction('JALR', rd=0, rs1=1, imm=0)
        
        raise ValueError(f"Unknown instruction: {op}")


class RISCVVM:
    """RISC-V Virtual Machine (RV32I + M extension)"""
    
    def __init__(self, mem_size: int = 65536):
        self.regs = [0] * 32  # 32 general-purpose registers
        self.pc = 0           # Program counter
        self.memory = bytearray(mem_size)  # Main memory
        self.running = True
        self.output = []
        
    def reset(self):
        """Reset VM state"""
        self.regs = [0] * 32
        self.pc = 0
        self.memory = bytearray(len(self.memory))
        self.running = True
        self.output = []
    
    def read_mem(self, addr: int, size: int, signed: bool = False) -> int:
        """Read from memory (size in bytes: 1, 2, or 4)"""
        if addr < 0 or addr + size > len(self.memory):
            raise ValueError(f"Memory access out of bounds: {addr}")
        
        if size == 1:
            val = self.memory[addr]
            if signed and val & 0x80:
                val |= 0xFFFFFF00
        elif size == 2:
            val = struct.unpack_from('<H', self.memory, addr)[0]
            if signed and val & 0x8000:
                val |= 0xFFFF0000
        else:  # size == 4
            val = struct.unpack_from('<I', self.memory, addr)[0]
        
        return val
    
    def write_mem(self, addr: int, val: int, size: int):
        """Write to memory (size in bytes: 1, 2, or 4)"""
        if addr < 0 or addr + size > len(self.memory):
            raise ValueError(f"Memory access out of bounds: {addr}")
        
        if size == 1:
            self.memory[addr] = val & 0xFF
        elif size == 2:
            struct.pack_into('<H', self.memory, addr, val & 0xFFFF)
        else:  # size == 4
            struct.pack_into('<I', self.memory, addr, val & 0xFFFFFFFF)
    
    def sign_extend(self, val: int, bits: int) -> int:
        """Sign extend a value"""
        if val & (1 << (bits - 1)):
            return val | (~((1 << bits) - 1))
        return val
    
    def to_i32(self, val: int) -> int:
        """Convert to signed 32-bit integer"""
        val = val & 0xFFFFFFFF
        if val & 0x80000000:
            return val - 0x100000000
        return val
    
    def to_u32(self, val: int) -> int:
        """Convert to unsigned 32-bit integer"""
        return val & 0xFFFFFFFF
    
    def execute(self, instructions: List[Instruction], debug: bool = False):
        """Execute a list of instructions"""
        self.pc = 0
        self.running = True
        
        max_cycles = 100000
        cycles = 0
        
        while self.running and cycles < max_cycles:
            if self.pc < 0 or self.pc // 4 >= len(instructions):
                break
            
            instr = instructions[self.pc // 4]
            
            if debug:
                print(f"PC={self.pc:04x} {instr.opcode} ", end='')
            
            self.execute_instruction(instr)
            
            if debug:
                self.print_regs()
            
            cycles += 1
        
        if cycles >= max_cycles:
            print(f"Warning: Max cycles ({max_cycles}) reached")
    
    def execute_instruction(self, instr: Instruction):
        """Execute a single instruction"""
        op = instr.opcode
        
        # Ensure x0 is always 0
        self.regs[0] = 0
        
        # R-type ALU operations
        if op == 'ADD':
            self.regs[instr.rd] = self.to_i32(self.regs[instr.rs1] + self.regs[instr.rs2])
            self.pc += 4
        elif op == 'SUB':
            self.regs[instr.rd] = self.to_i32(self.regs[instr.rs1] - self.regs[instr.rs2])
            self.pc += 4
        elif op == 'AND':
            self.regs[instr.rd] = self.regs[instr.rs1] & self.regs[instr.rs2]
            self.pc += 4
        elif op == 'OR':
            self.regs[instr.rd] = self.regs[instr.rs1] | self.regs[instr.rs2]
            self.pc += 4
        elif op == 'XOR':
            self.regs[instr.rd] = self.regs[instr.rs1] ^ self.regs[instr.rs2]
            self.pc += 4
        elif op == 'SLL':
            self.regs[instr.rd] = self.to_u32(self.regs[instr.rs1] << (self.regs[instr.rs2] & 0x1F))
            self.pc += 4
        elif op == 'SRL':
            self.regs[instr.rd] = self.to_u32(self.regs[instr.rs1]) >> (self.regs[instr.rs2] & 0x1F)
            self.pc += 4
        elif op == 'SRA':
            self.regs[instr.rd] = self.to_i32(self.to_i32(self.regs[instr.rs1]) >> (self.regs[instr.rs2] & 0x1F))
            self.pc += 4
        elif op == 'SLT':
            self.regs[instr.rd] = 1 if self.to_i32(self.regs[instr.rs1]) < self.to_i32(self.regs[instr.rs2]) else 0
            self.pc += 4
        elif op == 'SLTU':
            self.regs[instr.rd] = 1 if self.to_u32(self.regs[instr.rs1]) < self.to_u32(self.regs[instr.rs2]) else 0
            self.pc += 4
        
        # M extension
        elif op == 'MUL':
            self.regs[instr.rd] = self.to_i32(self.regs[instr.rs1] * self.regs[instr.rs2])
            self.pc += 4
        elif op == 'DIV':
            rs1, rs2 = self.to_i32(self.regs[instr.rs1]), self.to_i32(self.regs[instr.rs2])
            self.regs[instr.rd] = self.to_i32(rs1 // rs2) if rs2 != 0 else -1
            self.pc += 4
        elif op == 'REM':
            rs1, rs2 = self.to_i32(self.regs[instr.rs1]), self.to_i32(self.regs[instr.rs2])
            self.regs[instr.rd] = self.to_i32(rs1 % rs2) if rs2 != 0 else rs1
            self.pc += 4
        
        # I-type ALU operations
        elif op == 'ADDI':
            self.regs[instr.rd] = self.to_i32(self.regs[instr.rs1] + instr.imm)
            self.pc += 4
        elif op == 'ANDI':
            self.regs[instr.rd] = self.regs[instr.rs1] & instr.imm
            self.pc += 4
        elif op == 'ORI':
            self.regs[instr.rd] = self.regs[instr.rs1] | instr.imm
            self.pc += 4
        elif op == 'XORI':
            self.regs[instr.rd] = self.regs[instr.rs1] ^ instr.imm
            self.pc += 4
        elif op == 'SLTI':
            self.regs[instr.rd] = 1 if self.to_i32(self.regs[instr.rs1]) < instr.imm else 0
            self.pc += 4
        elif op == 'SLTIU':
            self.regs[instr.rd] = 1 if self.to_u32(self.regs[instr.rs1]) < self.to_u32(instr.imm) else 0
            self.pc += 4
        elif op == 'SLLI':
            self.regs[instr.rd] = self.to_u32(self.regs[instr.rs1] << instr.imm)
            self.pc += 4
        elif op == 'SRLI':
            self.regs[instr.rd] = self.to_u32(self.regs[instr.rs1]) >> instr.imm
            self.pc += 4
        elif op == 'SRAI':
            self.regs[instr.rd] = self.to_i32(self.to_i32(self.regs[instr.rs1]) >> instr.imm)
            self.pc += 4
        
        # Load operations
        elif op == 'LB':
            addr = self.regs[instr.rs1] + instr.imm
            self.regs[instr.rd] = self.to_i32(self.read_mem(addr, 1, signed=True))
            self.pc += 4
        elif op == 'LH':
            addr = self.regs[instr.rs1] + instr.imm
            self.regs[instr.rd] = self.to_i32(self.read_mem(addr, 2, signed=True))
            self.pc += 4
        elif op == 'LW':
            addr = self.regs[instr.rs1] + instr.imm
            self.regs[instr.rd] = self.to_i32(self.read_mem(addr, 4))
            self.pc += 4
        elif op == 'LBU':
            addr = self.regs[instr.rs1] + instr.imm
            self.regs[instr.rd] = self.read_mem(addr, 1, signed=False)
            self.pc += 4
        elif op == 'LHU':
            addr = self.regs[instr.rs1] + instr.imm
            self.regs[instr.rd] = self.read_mem(addr, 2, signed=False)
            self.pc += 4
        
        # Store operations
        elif op == 'SB':
            addr = self.regs[instr.rs1] + instr.imm
            self.write_mem(addr, self.regs[instr.rs2], 1)
            self.pc += 4
        elif op == 'SH':
            addr = self.regs[instr.rs1] + instr.imm
            self.write_mem(addr, self.regs[instr.rs2], 2)
            self.pc += 4
        elif op == 'SW':
            addr = self.regs[instr.rs1] + instr.imm
            self.write_mem(addr, self.regs[instr.rs2], 4)
            self.pc += 4
        
        # Branch operations
        elif op == 'BEQ':
            if self.regs[instr.rs1] == self.regs[instr.rs2]:
                self.pc += instr.imm
            else:
                self.pc += 4
        elif op == 'BNE':
            if self.regs[instr.rs1] != self.regs[instr.rs2]:
                self.pc += instr.imm
            else:
                self.pc += 4
        elif op == 'BLT':
            if self.to_i32(self.regs[instr.rs1]) < self.to_i32(self.regs[instr.rs2]):
                self.pc += instr.imm
            else:
                self.pc += 4
        elif op == 'BGE':
            if self.to_i32(self.regs[instr.rs1]) >= self.to_i32(self.regs[instr.rs2]):
                self.pc += instr.imm
            else:
                self.pc += 4
        elif op == 'BLTU':
            if self.to_u32(self.regs[instr.rs1]) < self.to_u32(self.regs[instr.rs2]):
                self.pc += instr.imm
            else:
                self.pc += 4
        elif op == 'BGEU':
            if self.to_u32(self.regs[instr.rs1]) >= self.to_u32(self.regs[instr.rs2]):
                self.pc += instr.imm
            else:
                self.pc += 4
        
        # Jump operations
        elif op == 'JAL':
            self.regs[instr.rd] = self.pc + 4
            self.pc += instr.imm
        elif op == 'JALR':
            temp = self.pc + 4
            self.pc = (self.regs[instr.rs1] + instr.imm) & ~1
            self.regs[instr.rd] = temp
        
        # Upper immediate
        elif op == 'LUI':
            self.regs[instr.rd] = instr.imm << 12
            self.pc += 4
        elif op == 'AUIPC':
            self.regs[instr.rd] = self.pc + (instr.imm << 12)
            self.pc += 4
        
        # System calls
        elif op == 'ECALL':
            self.handle_syscall()
            self.pc += 4
        elif op == 'EBREAK':
            print("EBREAK encountered")
            self.running = False
        
        else:
            raise ValueError(f"Unknown opcode: {op}")
        
        # x0 is hardwired to 0
        self.regs[0] = 0
    
    def handle_syscall(self):
        """Handle system calls (simplified)"""
        syscall_num = self.regs[17]  # a7
        
        if syscall_num == 1:  # Print integer
            val = self.to_i32(self.regs[10])  # a0
            print(val)
            self.output.append(str(val))
        elif syscall_num == 4:  # Print string
            addr = self.regs[10]  # a0
            chars = []
            while True:
                ch = self.memory[addr]
                if ch == 0:
                    break
                chars.append(chr(ch))
                addr += 1
            text = ''.join(chars)
            print(text, end='')
            self.output.append(text)
        elif syscall_num == 10:  # Exit
            self.running = False
        elif syscall_num == 11:  # Print character
            ch = chr(self.regs[10] & 0xFF)
            print(ch, end='')
            self.output.append(ch)
    
    def print_regs(self):
        """Print register state"""
        names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2',
                's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',
                'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7',
                's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']
        
        for i in range(0, 32, 4):
            line = []
            for j in range(4):
                if i + j < 32:
                    val = self.to_i32(self.regs[i + j])
                    line.append(f"{names[i+j]:4s}={val:6d}")
            print("  ".join(line))


# Example programs
FACTORIAL = """
# Calculate 5! (factorial)
    li a0, 5           # n = 5
    li a1, 1           # result = 1
loop:
    beq a0, zero, done # if n == 0, done
    mul a1, a1, a0     # result *= n
    addi a0, a0, -1    # n--
    j loop
done:
    li a7, 1           # syscall: print int
    mv a0, a1          # move result to a0
    ecall
    li a7, 10          # syscall: exit
    ecall
"""

FIBONACCI = """
# Fibonacci sequence (first 10 numbers)
    li t0, 0           # fib(n-2)
    li t1, 1           # fib(n-1)
    li t2, 10          # counter
loop:
    beq t2, zero, done
    add t3, t0, t1     # fib(n) = fib(n-1) + fib(n-2)
    
    li a7, 1           # print
    mv a0, t3
    ecall
    
    mv t0, t1          # shift values
    mv t1, t3
    addi t2, t2, -1
    j loop
done:
    li a7, 10
    ecall
"""

ARRAY_SUM = """
# Sum array elements
    li t0, 1000        # array base address
    li t1, 5           # array size
    
    # Initialize array
    li t2, 10
    sw t2, 0(t0)
    li t2, 20
    sw t2, 4(t0)
    li t2, 30
    sw t2, 8(t0)
    li t2, 40
    sw t2, 12(t0)
    li t2, 50
    sw t2, 16(t0)
    
    # Sum array
    li t3, 0           # sum = 0
    li t4, 0           # i = 0
sum_loop:
    beq t4, t1, print_result
    slli t5, t4, 2     # offset = i * 4
    add t5, t0, t5     # address = base + offset
    lw t6, 0(t5)       # load element
    add t3, t3, t6     # sum += element
    addi t4, t4, 1     # i++
    j sum_loop
    
print_result:
    li a7, 1
    mv a0, t3
    ecall
    li a7, 10
    ecall
"""


def main():
    """Main function - runs example programs"""
    examples = [
        ("Factorial", FACTORIAL),
        ("Fibonacci", FIBONACCI),
        ("Array Sum", ARRAY_SUM)
    ]
    
    for name, code in examples:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        
        # Assemble
        asm = RISCVAssembler()
        instructions = asm.assemble(code)
        print(f"Assembled {len(instructions)} instructions")
        
        # Execute
        vm = RISCVVM()
        vm.execute(instructions)
        
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
