import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM

def example_mutex_protection():
    vm = ToyVM()
    
    worker_instructions = [
        ("PUSH", 0),
        ("STORE", "i"),
        ("LOAD", "i"),
        ("PUSH", 100),
        ("SUB",),
        ("JUMP_IF", 14),
        ("LOAD", "lock"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "counter"),
        ("ATOMIC_GET",),
        ("PUSH", 1),
        ("ADD",),
        ("LOAD", "counter"),
        ("GLOBAL_STORE", "counter"),
        ("LOAD", "lock"),
        ("LOCK_RELEASE",),
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
        ("LOCK_CREATE",),
        ("GLOBAL_STORE", "lock"),
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
        ("JUMP_IF", 19),
        ("PRINT", "Test PASSED - Mutex protected counter"),
        ("JUMP", 20),
        ("PRINT", "Test FAILED - Mutex failed"),
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Mutex Protection ===")
    example_mutex_protection()
