#!/usr/bin/env python3
"""
Test VM Engine - A minimal but functional virtual machine for test execution
"""

import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


class ValueType(Enum):
    INT = "int"
    STRING = "string"
    BOOL = "bool"
    RESULT = "result"


@dataclass
class Value:
    type: ValueType
    data: Any
    
    def __str__(self):
        if self.type == ValueType.STRING:
            return f'"{self.data}"'
        return str(self.data)
    
    def __eq__(self, other):
        if isinstance(other, Value):
            return self.type == other.type and self.data == other.data
        return False


@dataclass
class Instruction:
    opcode: str
    args: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.opcode} {' '.join(self.args)}"


class TestVMError(Exception):
    pass


class TestVM:
    def __init__(self):
        self.reset()
        
        # Mock function registry - easily extensible
        self.functions = {
            'add': lambda x, y: Value(ValueType.INT, x.data + y.data),
            'multiply': lambda x, y: Value(ValueType.INT, x.data * y.data),
            'concat': lambda x, y: Value(ValueType.STRING, x.data + y.data),
            'subtract': lambda x, y: Value(ValueType.INT, x.data - y.data),
            'divide': lambda x, y: Value(ValueType.INT, x.data // y.data if y.data != 0 else 0),
            'length': lambda x: Value(ValueType.INT, len(str(x.data))),
            'equals': lambda x, y: Value(ValueType.BOOL, x.data == y.data),
        }
        
    def reset(self):
        """Reset VM state"""
        self.stack: List[Value] = []
        self.variables: Dict[str, Value] = {}
        self.labels: Dict[str, int] = {}
        self.logs: List[str] = []
        self.pc = 0  # program counter
        self.failed = False
        self.passed = False
        self.last_assertion_failed = False
        self.fail_message = ""
        
    def push(self, value: Value):
        """Push value onto stack"""
        self.stack.append(value)
        
    def pop(self) -> Value:
        """Pop value from stack"""
        if not self.stack:
            raise TestVMError("Stack underflow")
        return self.stack.pop()
        
    def peek(self) -> Value:
        """Peek at top of stack without removing"""
        if not self.stack:
            raise TestVMError("Stack is empty")
        return self.stack[-1]
        
    def get_variable(self, name: str) -> Value:
        """Get variable value"""
        if name not in self.variables:
            raise TestVMError(f"Variable '{name}' not found")
        return self.variables[name]
        
    def set_variable(self, name: str, value: Value):
        """Set variable value"""
        self.variables[name] = value
        
    def log(self, message: str):
        """Add message to log"""
        self.logs.append(message)
        print(f"LOG: {message}")
        
    def parse_value(self, type_str: str, value_str: str) -> Value:
        """Parse a value from string representation"""
        if type_str == "int":
            return Value(ValueType.INT, int(value_str))
        elif type_str == "string":
            # Remove quotes if present
            if value_str.startswith('"') and value_str.endswith('"'):
                value_str = value_str[1:-1]
            return Value(ValueType.STRING, value_str)
        elif type_str == "bool":
            return Value(ValueType.BOOL, value_str.lower() == "true")
        else:
            raise TestVMError(f"Unknown type: {type_str}")
            
    def parse_expected_value(self, value_str: str) -> Value:
        """Parse expected value, inferring type"""
        # Try int first
        try:
            return Value(ValueType.INT, int(value_str))
        except ValueError:
            pass
            
        # Try bool
        if value_str.lower() in ["true", "false"]:
            return Value(ValueType.BOOL, value_str.lower() == "true")
            
        # Default to string
        if value_str.startswith('"') and value_str.endswith('"'):
            value_str = value_str[1:-1]
        return Value(ValueType.STRING, value_str)
        
    def execute_instruction(self, instruction: Instruction) -> bool:
        """Execute a single instruction. Returns False to stop execution."""
        opcode = instruction.opcode
        args = instruction.args
        
        try:
            if opcode == "LOAD_INPUT":
                # LOAD_INPUT <type> <value>
                value = self.parse_value(args[0], args[1])
                self.push(value)
                
            elif opcode == "LOAD_VAR":
                # LOAD_VAR <name>
                value = self.get_variable(args[0])
                self.push(value)
                
            elif opcode == "STORE_VAR":
                # STORE_VAR <name>
                value = self.pop()
                self.set_variable(args[0], value)
                
            elif opcode == "CLEAR_CONTEXT":
                # CLEAR_CONTEXT
                self.stack.clear()
                self.variables.clear()
                
            elif opcode == "CALL_FUNC":
                # CALL_FUNC <name>
                func_name = args[0]
                if func_name not in self.functions:
                    raise TestVMError(f"Function '{func_name}' not found")
                    
                func = self.functions[func_name]
                
                # Get function signature to determine argument count
                import inspect
                sig = inspect.signature(func)
                arg_count = len(sig.parameters)
                
                # Pop arguments from stack
                func_args = []
                for _ in range(arg_count):
                    func_args.append(self.pop())
                func_args.reverse()  # Arguments were pushed in order
                
                # Call function and store result
                result = func(*func_args)
                self.set_variable("result", result)
                # Also push result back onto stack for chaining
                self.push(result)
                
            elif opcode == "CALL_PROC":
                # CALL_PROC <name> - similar to CALL_FUNC but no return value
                print(f"Calling procedure: {args[0]}")
                
            elif opcode == "WAIT_UNTIL":
                # WAIT_UNTIL <condition> <timeout>
                # For now, just simulate a wait
                timeout = float(args[1]) if len(args) > 1 else 1.0
                print(f"Waiting for condition '{args[0]}' (timeout: {timeout}s)")
                time.sleep(min(timeout, 0.1))  # Quick simulation
                
            elif opcode == "ASSERT_EQ":
                # ASSERT_EQ <var/result> <expected>
                self.last_assertion_failed = False
                if args[0] == "result":
                    actual = self.get_variable("result")
                else:
                    actual = self.get_variable(args[0])
                    
                expected = self.parse_expected_value(args[1])
                
                if actual != expected:
                    self.last_assertion_failed = True
                    self.fail_message = f"Assertion failed: expected {expected}, got {actual}"
                    
            elif opcode == "ASSERT_NE":
                # ASSERT_NE <var/result> <unexpected>
                self.last_assertion_failed = False
                if args[0] == "result":
                    actual = self.get_variable("result")
                else:
                    actual = self.get_variable(args[0])
                    
                unexpected = self.parse_expected_value(args[1])
                
                if actual == unexpected:
                    self.last_assertion_failed = True
                    self.fail_message = f"Assertion failed: expected not {unexpected}, but got {actual}"
                    
            elif opcode == "ASSERT_TRUE":
                # ASSERT_TRUE <var/result>
                self.last_assertion_failed = False
                if args[0] == "result":
                    actual = self.get_variable("result")
                else:
                    actual = self.get_variable(args[0])
                    
                if actual.type != ValueType.BOOL or not actual.data:
                    self.last_assertion_failed = True
                    self.fail_message = f"Assertion failed: expected true, got {actual}"
                    
            elif opcode == "ASSERT_FALSE":
                # ASSERT_FALSE <var/result>
                self.last_assertion_failed = False
                if args[0] == "result":
                    actual = self.get_variable("result")
                else:
                    actual = self.get_variable(args[0])
                    
                if actual.type != ValueType.BOOL or actual.data:
                    self.last_assertion_failed = True
                    self.fail_message = f"Assertion failed: expected false, got {actual}"
                    
            elif opcode == "JUMP":
                # JUMP <label>
                label = args[0]
                if label in self.labels:
                    self.pc = self.labels[label] - 1  # -1 because pc will be incremented
                else:
                    raise TestVMError(f"Label '{label}' not found")
                    
            elif opcode == "JUMP_IF_FAIL":
                # JUMP_IF_FAIL <label>
                if self.last_assertion_failed:
                    label = args[0]
                    if label in self.labels:
                        self.pc = self.labels[label] - 1
                    else:
                        raise TestVMError(f"Label '{label}' not found")
                        
            elif opcode == "LABEL":
                # LABEL <name> - handled in preprocessing
                pass
                
            elif opcode == "LOG":
                # LOG <message>
                message = " ".join(args)  # Join all args as message
                # Remove quotes if the message is quoted
                if message.startswith('"') and message.endswith('"'):
                    message = message[1:-1]
                self.log(message)
                
            elif opcode == "FAIL":
                # FAIL <message>
                self.failed = True
                self.fail_message = " ".join(args)
                return False
                
            elif opcode == "PASS":
                # PASS
                self.passed = True
                return False
                
            else:
                raise TestVMError(f"Unknown instruction: {opcode}")
                
        except Exception as e:
            self.failed = True
            self.fail_message = f"Runtime error: {str(e)}"
            return False
            
        return True
        
    def parse_program(self, source: str) -> List[Instruction]:
        """Parse source code into instructions"""
        instructions = []
        
        for line_num, line in enumerate(source.strip().split('\n'), 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Parse instruction
            parts = line.split()
            if not parts:
                continue
                
            opcode = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            instructions.append(Instruction(opcode, args))
            
        return instructions
        
    def collect_labels(self, instructions: List[Instruction]):
        """Collect all labels and their positions"""
        self.labels.clear()
        for i, instruction in enumerate(instructions):
            if instruction.opcode == "LABEL":
                label_name = instruction.args[0]
                self.labels[label_name] = i
                
    def execute_program(self, source: str) -> bool:
        """Execute a complete program"""
        self.reset()
        
        try:
            instructions = self.parse_program(source)
            self.collect_labels(instructions)
            
            self.pc = 0
            while self.pc < len(instructions) and not self.failed and not self.passed:
                instruction = instructions[self.pc]
                
                if not self.execute_instruction(instruction):
                    break
                    
                self.pc += 1
                
            return not self.failed or self.passed
            
        except Exception as e:
            self.failed = True
            self.fail_message = f"Parse error: {str(e)}"
            return False
            
    def print_results(self):
        """Print test execution results"""
        print("\n" + "="*50)
        
        if self.passed:
            print("✓ TEST PASSED")
        elif self.failed or self.last_assertion_failed:
            print("✗ TEST FAILED")
            if self.fail_message:
                print(f"Reason: {self.fail_message}")
        else:
            print("- TEST INCOMPLETE")
            
        if self.logs:
            print(f"\nLogs ({len(self.logs)} entries):")
            for i, log in enumerate(self.logs, 1):
                print(f"  {i}. {log}")
                
        print("="*50)


def main():
    """Run example programs"""
    vm = TestVM()
    
    print("Test VM Engine (Python) - Running Examples")
    print("="*50)
    
    # Example 1: Basic arithmetic test
    test1 = """
    # Test basic addition
    LOAD_INPUT int 2
    LOAD_INPUT int 3
    CALL_FUNC add
    ASSERT_EQ result 5
    LOG "Addition test completed successfully"
    PASS
    """
    
    print("\nExample 1: Testing add(2, 3) == 5")
    print("Program:")
    for line in test1.strip().split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {line.strip()}")
    
    vm.execute_program(test1)
    vm.print_results()
    
    # Example 2: Test with failure and control flow
    test2 = """
    # Test multiplication with expected failure
    LOAD_INPUT int 5
    LOAD_INPUT int 3
    CALL_FUNC multiply
    LOG "Testing multiplication"
    ASSERT_EQ result 14
    JUMP_IF_FAIL failure
    LOG "This should not be reached"
    PASS
    
    LABEL failure
    LOG "Test failed as expected - result was not 14"
    FAIL "Wrong result for multiplication"
    """
    
    print("\nExample 2: Testing multiply(5, 3) == 14 (should fail)")
    print("Program:")
    for line in test2.strip().split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {line.strip()}")
    
    vm.execute_program(test2)
    vm.print_results()
    
    # Example 3: String operations
    test3 = """
    # Test string concatenation
    LOAD_INPUT string Hello
    LOAD_INPUT string " World"
    CALL_FUNC concat
    STORE_VAR greeting
    LOAD_VAR greeting
    CALL_FUNC length
    ASSERT_EQ result 11
    LOG String operations completed
    PASS
    """
    
    print("\nExample 3: String concatenation and length")
    print("Program:")
    for line in test3.strip().split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {line.strip()}")
    
    vm.execute_program(test3)
    vm.print_results()


if __name__ == "__main__":
    main()
