import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

from vm import ToyVM

def example_producer_consumer():
    vm = ToyVM()
    
    producer_instructions = [
        ("PUSH", 0),
        ("STORE", "i"),
        ("LOAD", "i"),
        ("PUSH", 5),
        ("SUB",),
        ("JUMP_IF", 10),
        ("LOAD", "queue"),
        ("LOAD", "id"),
        ("QUEUE_SEND",),
        ("LOAD", "i"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "i"),
        ("JUMP", 2),
    ]

    consumer_instructions = [
        ("PUSH", 0),
        ("STORE", "count"),
        ("LOAD", "queue"),
        ("QUEUE_RECEIVE",),
        ("LOAD", "id"),
        ("PRINT", "Consumer {} received message"),
        ("LOAD", "count"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "count"),
        ("LOAD", "count"),
        ("PUSH", 5),
        ("SUB",),
        ("JUMP_IF", 14),
        ("JUMP", 2),
    ]

    main_instructions = [
        ("QUEUE_CREATE",),
        ("GLOBAL_STORE", "queue"),
        ("PUSH", 0),
        ("GLOBAL_STORE", "id"),
        ("PUSH", 0),
        ("THREAD_CREATE", [producer_instructions]),
        ("PUSH", 1),
        ("GLOBAL_STORE", "id"),
        ("PUSH", 0),
        ("THREAD_CREATE", [producer_instructions]),
        ("PUSH", 0),
        ("GLOBAL_STORE", "id"),
        ("PUSH", 0),
        ("THREAD_CREATE", [consumer_instructions]),
        ("PUSH", 1),
        ("GLOBAL_STORE", "id"),
        ("PUSH", 0),
        ("THREAD_CREATE", [consumer_instructions]),
        ("PUSH", 200),
        ("SLEEP",),
        ("PRINT", "Producer-Consumer simulation complete"),
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True)

if __name__ == "__main__":
    print("\n=== Example: Producer-Consumer Pattern ===")
    example_producer_consumer()