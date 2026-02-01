from math_add_lib import math_add_library
from math_multiply_lib import math_multiply_library
from math_max_lib import math_max_library
from loader import LibraryLoader
from vm import VirtualMachine

# Init the library loader
loader = LibraryLoader()

# Load our simple math libraries
loader.add_library("add", math_add_library)
loader.add_library("multiply", math_multiply_library)
loader.add_library("max", math_max_library)

# Example 1: Simple addition
print("=" * 50)
print("Example 1: Using the 'add' library")
print("=" * 50)
program1 = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "10"}},
    {"type": "assignment", "dest": "arg1", "rhs": {"type": "term", "value": "25"}},
    {"type": "call", "identifier": "add", "arg_count": 2},
    {"type": "print", "value": "result"},  # Should print 35
    {"type": "halt"},
]

vm1 = VirtualMachine(program1)
loader.link_library(vm1, "add")  # Link the add library
vm1.run()

# Example 2: Chaining operations (add then multiply)
print("\n" + "=" * 50)
print("Example 2: Chaining 'add' and 'multiply' libraries")
print("=" * 50)
program2 = [
    {"type": "label", "identifier": "start"},
    # First: 5 + 3 = 8
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "5"}},
    {"type": "assignment", "dest": "arg1", "rhs": {"type": "term", "value": "3"}},
    {"type": "call", "identifier": "add", "arg_count": 2},
    {"type": "assignment", "dest": "sum_result", "rhs": {"type": "term", "value": "result"}},
    
    # Then: 8 * 4 = 32
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "sum_result"}},
    {"type": "assignment", "dest": "arg1", "rhs": {"type": "term", "value": "4"}},
    {"type": "call", "identifier": "multiply", "arg_count": 2},
    {"type": "print", "value": "result"},  # Should print 32
    {"type": "halt"},
]

vm2 = VirtualMachine(program2)
loader.link_library(vm2, "add")
loader.link_library(vm2, "multiply")
vm2.run()

# Example 3: Using max to find the larger of two numbers
print("\n" + "=" * 50)
print("Example 3: Using the 'max' library")
print("=" * 50)
program3 = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "42"}},
    {"type": "assignment", "dest": "arg1", "rhs": {"type": "term", "value": "17"}},
    {"type": "call", "identifier": "max", "arg_count": 2},
    {"type": "print", "value": "result"},  # Should print 42
    {"type": "halt"},
]

vm3 = VirtualMachine(program3)
loader.link_library(vm3, "max")
vm3.run()

# Example 4: Demonstrating selective linking
# Only link what you need!
print("\n" + "=" * 50)
print("Example 4: Selective linking (only 'multiply')")
print("=" * 50)
program4 = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "7"}},
    {"type": "assignment", "dest": "arg1", "rhs": {"type": "term", "value": "6"}},
    {"type": "call", "identifier": "multiply", "arg_count": 2},
    {"type": "print", "value": "result"},  # Should print 42
    {"type": "halt"},
]

vm4 = VirtualMachine(program4)
# Notice: We only link 'multiply', not 'add' or 'max'
loader.link_library(vm4, "multiply")
vm4.run()

print("\n" + "=" * 50)
print("Key Concept: Libraries are loaded once, linked as needed")
print("=" * 50)
