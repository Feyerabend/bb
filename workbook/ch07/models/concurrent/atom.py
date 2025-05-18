import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM

def example_atomic_counter():
    vm = ToyVM()
    
    worker_instructions = [
        ("PUSH", 0),
        ("STORE", "i"),
        ("LOAD", "i"),
        ("PUSH", 100),
        ("SUB",),
        ("JUMP_IF", 8),
        ("LOAD", "counter"),
        ("ATOMIC_INCREMENT",),
        ("POP",),
        ("LOAD", "i"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "i"),
        ("JUMP", 2),
    ]

    main_instructions = [
        ("PUSH", 0),
        ("ATOMIC_CREATE",),
        ("GLOBAL_STORE", "counter"),
        ("PUSH", 0),
        ("THREAD_CREATE", [worker_instructions]),
        ("PUSH", 0),
        ("THREAD_CREATE", [worker_instructions]),
        ("PUSH", 100),
        ("SLEEP",),
        ("LOAD", "counter"),
        ("ATOMIC_GET",),
        ("PRINT", "Final counter value: {}"),
        ("LOAD", "counter"),
        ("ATOMIC_GET",),
        ("PUSH", 200),
        ("SUB",),
        ("JUMP_IF", 17),
        ("PRINT", "Test PASSED - Atomic counter correct"),
        ("JUMP", 18),
        ("PRINT", "Test FAILED - Atomic counter incorrect"),
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Atomic Counter ===")
    example_atomic_counter()