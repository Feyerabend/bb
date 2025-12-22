import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM


def example_dining_philosophers():
    vm = ToyVM()
    
    philosopher_instructions = [
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} is thinking"),
        ("PUSH", 10),
        ("SLEEP",),
        ("LOAD", "left_fork_idx"),
        ("LOAD", "right_fork_idx"),
        ("SUB",),
        ("JUMP_IF", 12),
        ("LOAD", "right_fork"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} picked up right fork"),
        ("LOAD", "left_fork"),
        ("LOCK_ACQUIRE",),
        ("JUMP", 16),
        ("LOAD", "left_fork"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} picked up left fork"),
        ("LOAD", "right_fork"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} picked up right fork and is eating"),
        ("PUSH", 50),
        ("SLEEP",),
        ("LOAD", "meals_counter"),
        ("ATOMIC_INCREMENT",),
        ("POP",),
        ("LOAD", "right_fork"),
        ("LOCK_RELEASE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} put down right fork"),
        ("LOAD", "left_fork"),
        ("LOCK_RELEASE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} put down left fork and is done eating"),
    ]

    main_instructions = [
        ("PUSH", 5),
        ("STORE", "num_forks"),
        ("PUSH", 0),
        ("STORE", "fork_idx"),
        ("PUSH", 0),
        ("ATOMIC_CREATE",),
        ("GLOBAL_STORE", "meals_counter"),
        ("LOAD", "fork_idx"),
        ("LOAD", "num_forks"),
        ("SUB",),
        ("JUMP_IF", 19),             # Jump if fork_idx >= num_forks
        ("LOCK_CREATE",),
        ("LOAD", "fork_idx"),
        ("GLOBAL_STORE", "fork_"),
        ("LOAD", "fork_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "fork_idx"),
        ("JUMP", 7),
        ("PUSH", 5),
        ("STORE", "num_philosophers"),
        ("PUSH", 0),
        ("STORE", "phil_idx"),
        ("LOAD", "phil_idx"),
        ("LOAD", "num_philosophers"),
        ("SUB",),
        ("JUMP_IF", 49),             # Jump if phil_idx >= num_philosophers
        ("LOAD", "phil_idx"),
        ("GLOBAL_STORE", "philosopher_id"),
        ("LOAD", "phil_idx"),
        ("GLOBAL_STORE", "left_fork_idx"),
        ("LOAD", "left_fork_idx"),
        ("GLOBAL_STORE", "left_fork"),
        ("LOAD", "phil_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("LOAD", "num_forks"),
        ("MUL", "mod"),
        ("GLOBAL_STORE", "right_fork_idx"),
        ("LOAD", "right_fork_idx"),
        ("GLOBAL_STORE", "right_fork"),
        ("PUSH", 0),
        ("THREAD_CREATE", [philosopher_instructions]),
        ("POP",),
        ("LOAD", "phil_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "phil_idx"),
        ("JUMP", 23),
        ("PUSH", 300),
        ("SLEEP",),
        ("LOAD", "meals_counter"),
        ("ATOMIC_GET",),
        ("DUP",),
        ("PRINT", "Total meals eaten: {}"),
        ("PUSH", 0),
        ("SUB",),
        ("JUMP_IF", 60),             # Jump if meals_counter <= 0
        ("PRINT", "Test PASSED - Philosophers ate without deadlock"),
        ("JUMP", 61),
        ("PRINT", "Test FAILED - No meals recorded (possible deadlock)"),
        ("PRINT", "Dining philosophers simulation complete"),
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Dining Philosophers Problem ===")
    example_dining_philosophers()