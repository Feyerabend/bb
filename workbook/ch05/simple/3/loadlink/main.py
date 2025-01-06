
from factorial_library import factorial_library
from fibonacci_library import fibonacci_library
from loader import LibraryLoader
from vm import VirtualMachine

# init, loading
loader = LibraryLoader()
loader.add_library("factorial", factorial_library)
loader.add_library("fibonacci", fibonacci_library)

'''
# test factorial
program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "5"}},
    {"type": "call", "identifier": "factorial", "arg_count": 1},
    {"type": "print", "value": "result"},
    {"type": "halt"},
]
'''
# test fibonacci
program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "5"}},
    {"type": "call", "identifier": "fibonacci", "arg_count": 1},
    {"type": "print", "value": "result"},
    {"type": "halt"},
]

# load libraries dynamically into the Virtual Machine
vm = VirtualMachine(program)
loader.link_library(vm, "factorial")  # link factorial
loader.link_library(vm, "fibonacci")  # link Fibonacci

print("\nRunning the program with linked libraries:")
vm.run()
