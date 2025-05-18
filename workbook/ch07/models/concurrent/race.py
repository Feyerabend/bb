import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM

def example_counter_race_condition():
    vm = ToyVM()
    
    worker_instructions = [
        ("PUSH", 0),              # PC 0: Initialize i = 0
        ("STORE", "i"),           # PC 1: Store i
        ("LOAD", "i"),            # PC 2: Load i
        ("PUSH", 100),            # PC 3: Push 100
        ("SUB",),                 # PC 4: Compute i - 100
        ("JUMP_IF", 17),          # PC 5: Jump to PC 17 if i >= 100
        ("LOAD", "counter_value"),# PC 6: Load counter value
        ("PUSH", 1),              # PC 7: Push 1
        ("ADD",),                 # PC 8: Increment
        ("GLOBAL_STORE", "counter_value"), # PC 9: Store back
        ("PUSH", 1),              # PC 10: Small delay
        ("SLEEP",),               # PC 11: Sleep 1ms
        ("LOAD", "i"),            # PC 12: Load i
        ("PUSH", 1),              # PC 13: Push 1
        ("ADD",),                 # PC 14: i += 1
        ("STORE", "i"),           # PC 15: Store i
        ("JUMP", 2),              # PC 16: Loop back
        ("NOP",),                 # PC 17: Loop exit
    ]

    main_instructions = [
        ("PUSH", 0),              # PC 0: Initialize counter
        ("GLOBAL_STORE", "counter_value"),
        ("PUSH", 0),              # PC 2: Create thread 0
        ("THREAD_CREATE", [worker_instructions]),
        ("PUSH", 0),              # PC 4: Create thread 1
        ("THREAD_CREATE", [worker_instructions]),
        ("LOAD", "thread-0"),     # PC 6: Join thread-0
        ("THREAD_JOIN",),
        ("LOAD", "thread-1"),     # PC 8: Join thread-1
        ("THREAD_JOIN",),
        ("LOAD", "counter_value"),# PC 10: Print final value
        ("DUP",),                 # PC 11: Duplicate for print
        ("PRINT", "Final counter value: {}"),
        ("PUSH", 200),            # PC 13: Check if correct
        ("SUB",),                 # PC 14: counter_value - 200
        ("JUMP_IF", 16),          # PC 15: Jump to 16 if counter_value == 200
        ("PRINT", "Test PASSED - No race condition (unlikely)"),
        ("JUMP", 19),             # PC 17: Skip failure message
        ("PRINT", "Test FAILED - Race condition detected"), # PC 18
        ("POP",),                 # PC 19: Clear stack
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Counter Race Condition ===")
    example_counter_race_condition()
