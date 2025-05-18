import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM

def example_atomic_counter():
    vm = ToyVM()
    
    worker_instructions = [
        ("PUSH", 0),              # PC 0: Initialize i = 0
        ("STORE", "i"),           # PC 1: Store i
        ("LOAD", "i"),            # PC 2: Load i
        ("PUSH", 100),            # PC 3: Push 100
        ("SUB",),                 # PC 4: Compute i - 100
        ("JUMP_IF", 13),          # PC 5: Jump to PC 13 if i >= 100
        ("LOAD", "counter"),      # PC 6: Load counter
        ("ATOMIC_INCREMENT",),    # PC 7: Atomically increment counter
        ("LOAD", "counter"),      # PC 8: Load counter for debug
        ("ATOMIC_GET",),          # PC 9: Get counter value
        ("PRINT", "Worker increment to {}"), # PC 10: Debug print
        ("POP",),                 # PC 11: Pop counter value
        ("POP",),                 # PC 12: Pop extra counter value
        ("LOAD", "i"),            # PC 13: Load i
        ("PUSH", 1),              # PC 14: Push 1
        ("ADD",),                 # PC 15: i += 1
        ("STORE", "i"),           # PC 16: Store i
        ("JUMP", 2),              # PC 17: Loop back
        ("NOP",),                 # PC 18: Loop exit
    ]

    main_instructions = [
        ("PUSH", 0),              # PC 0: Push 0
        ("ATOMIC_CREATE",),       # PC 1: Create atomic counter
        ("GLOBAL_STORE", "counter"), # PC 2: Store to counter
        ("PUSH", 0),              # PC 3: Create thread 0
        ("THREAD_CREATE", [worker_instructions]), # PC 4
        ("PUSH", 0),              # PC 5: Create thread 1
        ("THREAD_CREATE", [worker_instructions]), # PC 6
        ("LOAD", "thread-0"),     # PC 7: Join thread-0
        ("THREAD_JOIN",),         # PC 8
        ("LOAD", "thread-1"),     # PC 9: Join thread-1
        ("THREAD_JOIN",),         # PC 10
        ("LOAD", "counter"),      # PC 11: Load counter
        ("ATOMIC_GET",),          # PC 12: Get counter value
        ("DUP",),                 # PC 13: Duplicate for print
        ("PRINT", "Final counter value: {}"), # PC 14: Print value
        ("PUSH", 200),            # PC 15: Push 200
        ("SUB",),                 # PC 16: counter - 200
        ("JUMP_IF", 18),          # PC 17: Jump to 18 if counter == 200
        ("PRINT", "Test PASSED - Atomic counter correct"), # PC 18
        ("JUMP", 20),             # PC 19: Skip failure
        ("PRINT", "Test FAILED - Atomic counter incorrect"), # PC 20
        ("POP",),                 # PC 21: Clear stack
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Atomic Counter ===")
    example_atomic_counter()