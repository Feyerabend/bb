"""
This virtual machine implements a simple stack-based architecture with support
for basic concurrency primitives:
- Threads (create, join)
- Locks (acquire, release)
- Semaphores (acquire, release)
- Message passing (send, receive)
- Atomic operations

Instructions are simple opcodes with optional arguments.
"""

import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple


class Thread:
    def __init__(self, vm, name: str, instructions: List[Tuple], start_pc: int = 0):
        self.vm = vm
        self.name = name
        self.instructions = instructions
        self.pc = start_pc  # Program counter
        self.stack = []     # Execution stack
        self.variables = {} # Local variables
        self.running = True
        self.waiting = False
        self.wait_condition: Optional[Callable[[], bool]] = None
        self.joined_by = []  # Threads waiting for this thread to complete
    
    def step(self):
        if not self.running or self.waiting:
            return False
        
        if self.pc >= len(self.instructions):
            self.running = False
            # Wake up any threads waiting on this one
            for thread_name in self.joined_by:
                thread = self.vm.threads.get(thread_name)
                if thread and thread.waiting:
                    thread.waiting = False
            return False
        
        # Check if wait condition is satisfied
        if self.wait_condition and self.wait_condition():
            self.waiting = False
            self.wait_condition = None
        
        if not self.waiting:
            instruction = self.instructions[self.pc]
            opcode = instruction[0]
            args = instruction[1:] if len(instruction) > 1 else []
            
            self.vm.execute_instruction(self, opcode, args)
            self.pc += 1
            return True
        
        return False


class Lock:
    def __init__(self, name: str):
        self.name = name
        self.locked = False
        self.owner = None
        self.waiting_threads = []
    
    def acquire(self, thread_name: str) -> bool:
        if not self.locked:
            self.locked = True
            self.owner = thread_name
            return True
        return False
    
    def release(self, thread_name: str) -> bool:
        if self.locked and self.owner == thread_name:
            # Wake up one waiting thread if any
            if self.waiting_threads:
                next_thread = self.waiting_threads.pop(0)
                self.locked = True
                self.owner = next_thread
                return (True, next_thread)
            else:
                self.locked = False
                self.owner = None
                return (True, None)
        return (False, None)


class Semaphore:
    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count
        self.waiting_threads = []
    
    def acquire(self, thread_name: str) -> bool:
        if self.count > 0:
            self.count -= 1
            return True
        return False
    
    def release(self) -> Optional[str]:
        if self.waiting_threads:
            next_thread = self.waiting_threads.pop(0)
            return next_thread
        else:
            self.count += 1
            return None


class MessageQueue:
    def __init__(self, name: str):
        self.name = name
        self.messages = deque()
        self.waiting_receivers = []
    
    def send(self, message: Any) -> Optional[str]:
        if self.waiting_receivers:
            receiver = self.waiting_receivers.pop(0)
            return (receiver, message)
        else:
            self.messages.append(message)
            return None
    
    def receive(self, thread_name: str) -> Tuple[bool, Any]:
        if self.messages:
            message = self.messages.popleft()
            return (True, message)
        return (False, None)


class AtomicCounter:
    def __init__(self, name: str, initial_value: int = 0):
        self.name = name
        self.value = initial_value
    
    def increment(self) -> int:
        self.value += 1
        return self.value
    
    def decrement(self) -> int:
        self.value -= 1
        return self.value
    

class ToyVM:
    def __init__(self):
        self.threads: Dict[str, Thread] = {}
        self.locks: Dict[str, Lock] = {}
        self.semaphores: Dict[str, Semaphore] = {}
        self.message_queues: Dict[str, MessageQueue] = {}
        self.atomic_counters: Dict[str, AtomicCounter] = {}
        self.globals = {}  # Global variables
        self.next_thread_id = 0
        self.running = False
        self.scheduler_type = "round_robin"  # Can be "round_robin" or "random"
    
    def create_thread(self, instructions: List[Tuple], name: str = None) -> str:
        if name is None:
            name = f"thread-{self.next_thread_id}"
            self.next_thread_id += 1
        
        thread = Thread(self, name, instructions)
        self.threads[name] = thread
        return name
    
    def create_lock(self, name: str = None) -> str:
        if name is None:
            name = f"lock-{len(self.locks)}"
        
        lock = Lock(name)
        self.locks[name] = lock
        return name
    
    def create_semaphore(self, count: int, name: str = None) -> str:
        if name is None:
            name = f"semaphore-{len(self.semaphores)}"
        
        semaphore = Semaphore(name, count)
        self.semaphores[name] = semaphore
        return name
    
    def create_message_queue(self, name: str = None) -> str:
        if name is None:
            name = f"queue-{len(self.message_queues)}"
        
        queue = MessageQueue(name)
        self.message_queues[name] = queue
        return name
    
    def create_atomic_counter(self, initial_value: int = 0, name: str = None) -> str:
        if name is None:
            name = f"counter-{len(self.atomic_counters)}"
        
        counter = AtomicCounter(name, initial_value)
        self.atomic_counters[name] = counter
        return name
    
    def run(self, max_steps: int = 1000, debug: bool = False):
        self.running = True
        step_count = 0
        
        active_threads = list(self.threads.keys())
        
        while self.running and step_count < max_steps:
            step_count += 1
            
            # Check if any threads are still running
            active_threads = [t for t in active_threads if self.threads[t].running]
            if not active_threads:
                break
            
            # Select next thread to run based on scheduling strategy
            if self.scheduler_type == "round_robin":
                thread_name = active_threads[0]
                active_threads = active_threads[1:] + [thread_name]
            else:  # random scheduling
                thread_name = random.choice(active_threads)
            
            thread = self.threads[thread_name]
            
            if debug:
                print(f"Step {step_count}: Running thread {thread_name} at PC {thread.pc}")
                if thread.pc < len(thread.instructions):
                    print(f"  Instruction: {thread.instructions[thread.pc]}")
                print(f"  Stack: {thread.stack}")
                print(f"  Variables: {thread.variables}")
            
            # Execute one step of the thread
            thread.step()
            
            # Short sleep to simulate concurrent execution
            time.sleep(0.01)
        
        self.running = False
        
        if debug:
            if step_count >= max_steps:
                print(f"Stopped after {max_steps} steps")
            else:
                print(f"All threads completed after {step_count} steps")
        
        return step_count

    def execute_instruction(self, thread: Thread, opcode: str, args: List[Any]):

        # Stack operations
        if opcode == "PUSH":
            thread.stack.append(args[0])
        elif opcode == "POP":
            if thread.stack:
                thread.stack.pop()
        elif opcode == "DUP":
            if thread.stack:
                thread.stack.append(thread.stack[-1])
        
        # Arithmetic operations
        elif opcode == "ADD":
            if len(thread.stack) >= 2:
                b = thread.stack.pop()
                a = thread.stack.pop()
                thread.stack.append(a + b)
        elif opcode == "SUB":
            if len(thread.stack) >= 2:
                b = thread.stack.pop()
                a = thread.stack.pop()
                thread.stack.append(a - b)
        elif opcode == "MUL":
            if len(thread.stack) >= 2:
                b = thread.stack.pop()
                a = thread.stack.pop()
                thread.stack.append(a * b)
        elif opcode == "DIV":
            if len(thread.stack) >= 2:
                b = thread.stack.pop()
                a = thread.stack.pop()
                if b != 0:
                    thread.stack.append(a // b)
        
        # Variable operations
        elif opcode == "LOAD":
            var_name = args[0]
            if var_name in thread.variables:
                thread.stack.append(thread.variables[var_name])
            elif var_name in self.globals:
                thread.stack.append(self.globals[var_name])
        elif opcode == "STORE":
            var_name = args[0]
            if thread.stack:
                value = thread.stack.pop()
                thread.variables[var_name] = value
        elif opcode == "GLOBAL_STORE":
            var_name = args[0]
            if thread.stack:
                value = thread.stack.pop()
                self.globals[var_name] = value
        
        # Control flow
        elif opcode == "JUMP":
            target = args[0]
            thread.pc = target - 1  # -1 because pc will be incremented after
        elif opcode == "JUMP_IF":
            condition = thread.stack.pop() if thread.stack else False
            target = args[0]
            if condition:
                thread.pc = target - 1
        elif opcode == "PRINT":
            if args:
                message = args[0]
                if thread.stack and "{}" in message:
                    value = thread.stack[-1]
                    message = message.replace("{}", str(value))
                print(f"[{thread.name}] {message}")
            elif thread.stack:
                print(f"[{thread.name}] {thread.stack[-1]}")
        
        # Thread operations
        elif opcode == "THREAD_CREATE":
            if len(thread.stack) >= 1:
                instructions_index = thread.stack.pop()
                new_thread_instructions = args[0][instructions_index]
                new_thread_name = self.create_thread(new_thread_instructions)
                thread.stack.append(new_thread_name)
        elif opcode == "THREAD_JOIN":
            if thread.stack:
                other_thread_name = thread.stack.pop()
                other_thread = self.threads.get(other_thread_name)
                if other_thread and other_thread.running:
                    other_thread.joined_by.append(thread.name)
                    thread.waiting = True
                    thread.wait_condition = lambda: not other_thread.running
        
        # Lock operations
        elif opcode == "LOCK_CREATE":
            lock_name = self.create_lock()
            thread.stack.append(lock_name)
        elif opcode == "LOCK_ACQUIRE":
            if thread.stack:
                lock_name = thread.stack[-1]  # Peek
                lock = self.locks.get(lock_name)
                if lock:
                    if lock.acquire(thread.name):
                        thread.stack.pop()  # Success, remove lock name
                    else:
                        # Failed to acquire, wait
                        lock.waiting_threads.append(thread.name)
                        thread.waiting = True
                        thread.wait_condition = lambda: lock.owner == thread.name
        elif opcode == "LOCK_RELEASE":
            if thread.stack:
                lock_name = thread.stack.pop()
                lock = self.locks.get(lock_name)
                if lock:
                    result, next_thread = lock.release(thread.name)
                    if result and next_thread:
                        next_thread_obj = self.threads.get(next_thread)
                        if next_thread_obj:
                            next_thread_obj.waiting = False
        
        # Semaphore operations
        elif opcode == "SEMAPHORE_CREATE":
            if thread.stack:
                count = thread.stack.pop()
                sem_name = self.create_semaphore(count)
                thread.stack.append(sem_name)
        elif opcode == "SEMAPHORE_ACQUIRE":
            if thread.stack:
                sem_name = thread.stack[-1]  # Peek
                sem = self.semaphores.get(sem_name)
                if sem:
                    if sem.acquire(thread.name):
                        thread.stack.pop()  # Success, remove semaphore name
                    else:
                        # Failed to acquire, wait
                        sem.waiting_threads.append(thread.name)
                        thread.waiting = True
                        # This condition will be checked after a semaphore is released
        elif opcode == "SEMAPHORE_RELEASE":
            if thread.stack:
                sem_name = thread.stack.pop()
                sem = self.semaphores.get(sem_name)
                if sem:
                    next_thread = sem.release()
                    if next_thread:
                        next_thread_obj = self.threads.get(next_thread)
                        if next_thread_obj:
                            next_thread_obj.waiting = False
        
        # Message queue operations
        elif opcode == "QUEUE_CREATE":
            queue_name = self.create_message_queue()
            thread.stack.append(queue_name)
        elif opcode == "QUEUE_SEND":
            if len(thread.stack) >= 2:
                message = thread.stack.pop()
                queue_name = thread.stack.pop()
                queue = self.message_queues.get(queue_name)
                if queue:
                    result = queue.send(message)
                    if result:
                        receiver_name, _ = result
                        receiver = self.threads.get(receiver_name)
                        if receiver:
                            receiver.waiting = False
                            receiver.stack.append(message)
        elif opcode == "QUEUE_RECEIVE":
            if thread.stack:
                queue_name = thread.stack[-1]  # Peek
                queue = self.message_queues.get(queue_name)
                if queue:
                    success, message = queue.receive(thread.name)
                    if success:
                        thread.stack.pop()  # Remove queue name
                        thread.stack.append(message)  # Push received message
                    else:
                        # No message available, wait
                        queue.waiting_receivers.append(thread.name)
                        thread.waiting = True
                        # This condition will be checked when a message is sent
        
        # Atomic counter operations
        elif opcode == "ATOMIC_CREATE":
            if thread.stack:
                initial_value = thread.stack.pop()
                counter_name = self.create_atomic_counter(initial_value)
                thread.stack.append(counter_name)
        elif opcode == "ATOMIC_INCREMENT":
            if thread.stack:
                counter_name = thread.stack.pop()
                counter = self.atomic_counters.get(counter_name)
                if counter:
                    new_value = counter.increment()
                    thread.stack.append(new_value)
        elif opcode == "ATOMIC_DECREMENT":
            if thread.stack:
                counter_name = thread.stack.pop()
                counter = self.atomic_counters.get(counter_name)
                if counter:
                    new_value = counter.decrement()
                    thread.stack.append(new_value)
        
        # Sleep operation
        elif opcode == "SLEEP":
            if thread.stack:
                duration = thread.stack.pop()
                time.sleep(duration / 1000)  # Convert to seconds
        
        # No operation
        elif opcode == "NOP":
            pass
        
        else:
            print(f"Unknown opcode: {opcode}")



def example_counter_race_condition():
    """Example demonstrating a race condition with a shared counter."""
    vm = ToyVM()
    
    # Instructions for incrementing a counter
    increment_instructions = [
        ("LOAD", "counter"),           # Load counter value
        ("PUSH", 1),                   # Push 1
        ("ADD",),                      # Add 1 to counter
        ("GLOBAL_STORE", "counter"),   # Store updated value
    ]
    
    # Create main program
    main_instructions = [
        ("PUSH", 0),                   # Initial counter value
        ("GLOBAL_STORE", "counter"),   # Store in global variable
        
        # Create 5 threads to increment the counter
        ("PUSH", 5),                   # Number of threads
        ("STORE", "num_threads"),      # Store in variable
        
        # Loop to create threads
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # num_threads - 0
        ("JUMP_IF", 14),               # If result is 0, jump to join section
        
        ("PUSH", 0),                   # Thread instructions index (0 = increment_instructions)
        ("THREAD_CREATE", [increment_instructions]),  # Create thread
        ("POP",),                      # Discard thread name
        
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "num_threads"),      # Store updated count
        ("JUMP", 5),                   # Jump back to loop condition
        
        # Print final result
        ("PUSH", 100),                 # Sleep to ensure threads complete
        ("SLEEP",),                    # Sleep
        ("LOAD", "counter"),           # Load counter value
        ("PRINT", "Final counter value: {}"),  # Print result
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_mutex_protection():
    """Example demonstrating mutex protection for a shared counter."""
    vm = ToyVM()
    
    # Instructions for safely incrementing a counter using a mutex
    safe_increment_instructions = [
        ("LOAD", "mutex"),             # Load mutex name
        ("LOCK_ACQUIRE",),             # Acquire lock (blocks until acquired)
        
        ("LOAD", "counter"),           # Load counter value
        ("PUSH", 1),                   # Push 1
        ("ADD",),                      # Add 1 to counter
        ("GLOBAL_STORE", "counter"),   # Store updated value
        
        ("LOAD", "mutex"),             # Load mutex name
        ("LOCK_RELEASE",),             # Release lock
    ]
    
    # Create main program
    main_instructions = [
        ("PUSH", 0),                   # Initial counter value
        ("GLOBAL_STORE", "counter"),   # Store in global variable
        
        ("LOCK_CREATE",),              # Create a mutex
        ("GLOBAL_STORE", "mutex"),     # Store mutex name
        
        # Create 5 threads to increment the counter
        ("PUSH", 5),                   # Number of threads
        ("STORE", "num_threads"),      # Store in variable
        
        # Loop to create threads
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # num_threads - 0
        ("JUMP_IF", 14),               # If result is 0, jump to join section
        
        ("PUSH", 0),                   # Thread instructions index (0 = safe_increment_instructions)
        ("THREAD_CREATE", [safe_increment_instructions]),  # Create thread
        ("POP",),                      # Discard thread name
        
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "num_threads"),      # Store updated count
        ("JUMP", 7),                   # Jump back to loop condition
        
        # Print final result
        ("PUSH", 100),                 # Sleep to ensure threads complete
        ("SLEEP",),                    # Sleep
        ("LOAD", "counter"),           # Load counter value
        ("PRINT", "Final counter value with mutex: {}"),  # Print result
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_producer_consumer():
    """Example demonstrating a producer-consumer pattern with a message queue."""
    vm = ToyVM()
    
    # Producer instructions
    producer_instructions = [
        ("LOAD", "queue"),             # Load queue name
        ("PUSH", 5),                   # Number of items to produce
        ("STORE", "count"),            # Store in variable
        
        # Loop to produce items
        ("LOAD", "count"),             # Load count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # count - 0
        ("JUMP_IF", 13),               # If result is 0, exit
        
        ("LOAD", "count"),             # Load current count as the item value
        ("PRINT", "Producing item: {}"),  # Print
        ("LOAD", "queue"),             # Load queue name
        ("LOAD", "count"),             # Load item value
        ("QUEUE_SEND",),               # Send to queue
        
        ("LOAD", "count"),             # Load count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "count"),            # Store updated count
        ("JUMP", 3),                   # Jump back to loop condition
        
        ("PRINT", "Producer finished"),
    ]
    
    # Consumer instructions
    consumer_instructions = [
        ("LOAD", "queue"),             # Load queue name
        ("PUSH", 5),                   # Number of items to consume
        ("STORE", "count"),            # Store in variable
        
        # Loop to consume items
        ("LOAD", "count"),             # Load count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # count - 0
        ("JUMP_IF", 10),               # If result is 0, exit
        
        ("LOAD", "queue"),             # Load queue name
        ("QUEUE_RECEIVE",),            # Receive from queue (blocks until available)
        ("PRINT", "Consumed item: {}"),  # Print received item
        
        ("LOAD", "count"),             # Load count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "count"),            # Store updated count
        ("JUMP", 3),                   # Jump back to loop condition
        
        ("PRINT", "Consumer finished"),
    ]
    

    main_instructions = [
        ("QUEUE_CREATE",),             # Create a message queue
        ("GLOBAL_STORE", "queue"),     # Store queue name
        
        # Create producer thread
        ("PUSH", 0),                   # Thread instructions index (0 = producer_instructions)
        ("THREAD_CREATE", [producer_instructions, consumer_instructions]),
        ("STORE", "producer"),         # Store producer thread name
        
        # Create consumer thread
        ("PUSH", 1),                   # Thread instructions index (1 = consumer_instructions)
        ("THREAD_CREATE", [producer_instructions, consumer_instructions]),
        ("STORE", "consumer"),         # Store consumer thread name
        
        # Wait for both threads to complete
        ("LOAD", "producer"),
        ("THREAD_JOIN",),
        
        ("LOAD", "consumer"),
        ("THREAD_JOIN",),
        
        ("PRINT", "All done!"),
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_semaphore():
    """Example demonstrating semaphore usage to limit concurrent access."""
    vm = ToyVM()
    
    # Worker thread instructions
    worker_instructions = [
        ("LOAD", "semaphore"),         # Load semaphore name
        ("SEMAPHORE_ACQUIRE",),        # Acquire semaphore (blocks if none available)
        
        ("LOAD", "worker_id"),         # Load worker ID
        ("PRINT", "Worker {} acquired semaphore"),
        
        ("PUSH", 50),                  # Sleep for 50ms to simulate work
        ("SLEEP",),
        
        ("LOAD", "worker_id"),         # Load worker ID
        ("PRINT", "Worker {} releasing semaphore"),
        
        ("LOAD", "semaphore"),         # Load semaphore name
        ("SEMAPHORE_RELEASE",),        # Release semaphore
    ]
    
    # Create main program
    main_instructions = [
        ("PUSH", 3),                   # Semaphore count (3 concurrent workers max)
        ("SEMAPHORE_CREATE",),         # Create semaphore
        ("GLOBAL_STORE", "semaphore"), # Store semaphore name
        
        # Create 6 worker threads
        ("PUSH", 6),                   # Number of workers
        ("STORE", "num_workers"),      # Store in variable
        ("PUSH", 1),                   # Start worker ID from 1
        ("STORE", "current_id"),       # Store in variable
        
        # Loop to create workers
        ("LOAD", "num_workers"),       # Load worker count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # num_workers - 0
        ("JUMP_IF", 15),               # If result is 0, exit
        
        ("LOAD", "current_id"),        # Load current worker ID
        ("GLOBAL_STORE", "worker_id"), # Store as global for the worker to access
        
        ("PUSH", 0),                   # Thread instructions index (0 = worker_instructions)
        ("THREAD_CREATE", [worker_instructions]),  # Create thread
        ("POP",),                      # Discard thread name
        
        ("LOAD", "current_id"),        # Load current ID
        ("PUSH", 1),                   # Push 1
        ("ADD",),                      # Increment
        ("STORE", "current_id"),       # Store updated ID
        
        ("LOAD", "num_workers"),       # Load worker count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "num_workers"),      # Store updated count
        ("JUMP", 7),                   # Jump back to loop condition
        
        ("PUSH", 300),                 # Sleep for 300ms to wait for workers
        ("SLEEP",),
        ("PRINT", "Main thread finished"),
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_atomic_counter():
    """Example demonstrating atomic counter usage."""
    vm = ToyVM()
    
    # Thread instructions for incrementing atomic counter
    increment_atomic_instructions = [
        ("LOAD", "counter"),           # Load counter name
        ("ATOMIC_INCREMENT",),         # Atomically increment
        ("PRINT", "Incremented to: {}"),
    ]
    
    # Create main program
    main_instructions = [
        ("PUSH", 0),                   # Initial counter value
        ("ATOMIC_CREATE",),            # Create atomic counter
        ("GLOBAL_STORE", "counter"),   # Store counter name
        
        # Create 5 threads to increment the counter
        ("PUSH", 5),                   # Number of threads
        ("STORE", "num_threads"),      # Store in variable
        
        # Loop to create threads
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 0),                   # Push 0 for comparison
        ("SUB",),                      # num_threads - 0
        ("JUMP_IF", 14),               # If result is 0, jump to join section
        
        ("PUSH", 0),                   # Thread instructions index (0 = increment_atomic_instructions)
        ("THREAD_CREATE", [increment_atomic_instructions]),  # Create thread
        ("POP",),                      # Discard thread name
        
        ("LOAD", "num_threads"),       # Load thread count
        ("PUSH", 1),                   # Push 1
        ("SUB",),                      # Decrement
        ("STORE", "num_threads"),      # Store updated count
        ("JUMP", 7),                   # Jump back to loop condition
        
        # Print final result
        ("PUSH", 100),                 # Sleep to ensure threads complete
        ("SLEEP",),                    # Sleep
        ("LOAD", "counter"),           # Load counter name
        ("ATOMIC_INCREMENT",),         # One final increment from main thread
        ("PRINT", "Final atomic counter value: {}"),  # Print result
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_dining_philosophers():
    """Example demonstrating the dining philosophers problem."""
    vm = ToyVM()
    
    # Each philosopher needs two forks to eat
    # We'll use locks to represent forks
    
    # Philosopher instructions
    philosopher_instructions = [
        # Parameters: philosopher_id, left_fork, right_fork
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} is thinking"),
        
        # Try to pick up left fork
        ("LOAD", "left_fork"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} picked up left fork"),
        
        # Try to pick up right fork
        ("LOAD", "right_fork"),
        ("LOCK_ACQUIRE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} picked up right fork and is eating"),
        
        # Eat for a while
        ("PUSH", 50),
        ("SLEEP",),
        
        # Put down right fork
        ("LOAD", "right_fork"),
        ("LOCK_RELEASE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} put down right fork"),
        
        # Put down left fork
        ("LOAD", "left_fork"),
        ("LOCK_RELEASE",),
        ("LOAD", "philosopher_id"),
        ("PRINT", "Philosopher {} put down left fork and is done eating"),
    ]

    main_instructions = [
        # Create 5 forks (locks)
        ("PUSH", 5),
        ("STORE", "num_forks"),
        ("PUSH", 0),
        ("STORE", "fork_idx"),
        
        # Loop to create forks
        ("LOAD", "fork_idx"),
        ("LOAD", "num_forks"),
        ("SUB",),
        ("JUMP_IF", 13),  # Jump to philosophers creation if done
        
        ("LOCK_CREATE",),
        ("LOAD", "fork_idx"),
        ("GLOBAL_STORE", "fork_"),  # Will be fork_0, fork_1, etc.
        
        ("LOAD", "fork_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "fork_idx"),
        ("JUMP", 4),  # Jump back to loop condition
        
        # Create 5 philosophers
        ("PUSH", 5),
        ("STORE", "num_philosophers"),
        ("PUSH", 0),
        ("STORE", "phil_idx"),
        
        # Loop to create philosophers
        ("LOAD", "phil_idx"),
        ("LOAD", "num_philosophers"),
        ("SUB",),
        ("JUMP_IF", 36),  # Jump to end if done
        
        # Set philosopher ID
        ("LOAD", "phil_idx"),
        ("GLOBAL_STORE", "philosopher_id"),
        
        # Determine left and right forks
        # Left fork is the philosopher's ID
        ("LOAD", "phil_idx"),
        ("GLOBAL_STORE", "fork_idx"),
        ("LOAD", "fork_idx"),
        ("GLOBAL_STORE", "left_fork"),
        
        # Right fork is (ID + 1) % num_forks
        ("LOAD", "phil_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("LOAD", "num_forks"),
        ("MUL", "mod"),  # Simulate modulo
        ("GLOBAL_STORE", "fork_idx"),
        ("LOAD", "fork_idx"),
        ("GLOBAL_STORE", "right_fork"),
        
        # Create philosopher thread
        ("PUSH", 0),
        ("THREAD_CREATE", [philosopher_instructions]),
        ("POP",),
        
        # Increment philosopher index
        ("LOAD", "phil_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "phil_idx"),
        ("JUMP", 17),  # Jump back to loop condition
        
        # Wait for a while and then exit
        ("PUSH", 300),
        ("SLEEP",),
        ("PRINT", "Dining philosophers simulation complete"),
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_readers_writers():
    """Example demonstrating the readers-writers problem."""
    vm = ToyVM()
    
    # Reader instructions
    reader_instructions = [
        # Parameters: reader_id
        ("LOAD", "reader_id"),
        ("PRINT", "Reader {} is trying to read"),
        
        # Acquire reader semaphore
        ("LOAD", "reader_sem"),
        ("SEMAPHORE_ACQUIRE",),
        
        # Increment reader count
        ("LOAD", "reader_count"),
        ("ATOMIC_INCREMENT",),
        ("STORE", "count"),
        
        # If this is the first reader, acquire the write lock
        ("LOAD", "count"),
        ("PUSH", 1),
        ("SUB",),
        ("JUMP_IF", 13),  # Skip if not first reader
        
        ("LOAD", "write_lock"),
        ("LOCK_ACQUIRE",),
        
        # Release reader semaphore
        ("LOAD", "reader_sem"),
        ("SEMAPHORE_RELEASE",),
        
        # Read for a while
        ("LOAD", "reader_id"),
        ("PRINT", "Reader {} is reading"),
        ("PUSH", 50),
        ("SLEEP",),
        
        # Acquire reader semaphore again to update count
        ("LOAD", "reader_sem"),
        ("SEMAPHORE_ACQUIRE",),
        
        # Decrement reader count
        ("LOAD", "reader_count"),
        ("ATOMIC_DECREMENT",),
        ("STORE", "count"),
        
        # If this is the last reader, release the write lock
        ("LOAD", "count"),
        ("PUSH", 0),
        ("SUB",),
        ("JUMP_IF", 31),  # Skip if not last reader
        
        ("LOAD", "write_lock"),
        ("LOCK_RELEASE",),
        
        # Release reader semaphore
        ("LOAD", "reader_sem"),
        ("SEMAPHORE_RELEASE",),
        
        ("LOAD", "reader_id"),
        ("PRINT", "Reader {} is done reading"),
    ]
    
    # Writer instructions
    writer_instructions = [
        # Parameters: writer_id
        ("LOAD", "writer_id"),
        ("PRINT", "Writer {} is trying to write"),
        
        # Acquire write lock
        ("LOAD", "write_lock"),
        ("LOCK_ACQUIRE",),
        
        # Write for a while
        ("LOAD", "writer_id"),
        ("PRINT", "Writer {} is writing"),
        ("PUSH", 80),
        ("SLEEP",),
        
        # Release write lock
        ("LOAD", "write_lock"),
        ("LOCK_RELEASE",),
        
        ("LOAD", "writer_id"),
        ("PRINT", "Writer {} is done writing"),
    ]
    
    # Create main program
    main_instructions = [
        # Create necessary synchronization primitives
        ("LOCK_CREATE",),
        ("GLOBAL_STORE", "write_lock"),
        
        ("PUSH", 1),
        ("SEMAPHORE_CREATE",),
        ("GLOBAL_STORE", "reader_sem"),
        
        ("PUSH", 0),
        ("ATOMIC_CREATE",),
        ("GLOBAL_STORE", "reader_count"),
        
        # Create 3 readers
        ("PUSH", 3),
        ("STORE", "num_readers"),
        ("PUSH", 1),
        ("STORE", "reader_idx"),
        
        # Loop to create readers
        ("LOAD", "reader_idx"),
        ("LOAD", "num_readers"),
        ("SUB",),
        ("JUMP_IF", 22),  # Jump to writers creation if done
        
        # Set reader ID
        ("LOAD", "reader_idx"),
        ("GLOBAL_STORE", "reader_id"),
        
        # Create reader thread
        ("PUSH", 0),
        ("THREAD_CREATE", [reader_instructions, writer_instructions]),
        ("POP",),
        
        # Increment reader index
        ("LOAD", "reader_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "reader_idx"),
        ("JUMP", 13),  # Jump back to loop condition
        
        # Create 2 writers
        ("PUSH", 2),
        ("STORE", "num_writers"),
        ("PUSH", 1),
        ("STORE", "writer_idx"),
        
        # Loop to create writers
        ("LOAD", "writer_idx"),
        ("LOAD", "num_writers"),
        ("SUB",),
        ("JUMP_IF", 39),  # Jump to end if done
        
        # Set writer ID
        ("LOAD", "writer_idx"),
        ("GLOBAL_STORE", "writer_id"),
        
        # Create writer thread
        ("PUSH", 1),
        ("THREAD_CREATE", [reader_instructions, writer_instructions]),
        ("POP",),
        
        # Increment writer index
        ("LOAD", "writer_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "writer_idx"),
        ("JUMP", 30),  # Jump back to loop condition
        
        # Wait for a while and then exit
        ("PUSH", 500),
        ("SLEEP",),
        ("PRINT", "Readers-writers simulation complete"),
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)


def example_barrier_synchronization():
    """Example demonstrating barrier synchronization."""
    vm = ToyVM()
    
    # Worker thread instructions
    worker_instructions = [
        # Parameters: worker_id, num_workers
        # Each worker does some work, then waits at a barrier for all workers to complete
        # Then they all proceed to the next phase together
        
        # Phase 1
        ("LOAD", "worker_id"),
        ("PRINT", "Worker {} starting phase 1"),
        
        # Simulate some work
        ("PUSH", 30),
        ("SLEEP",),
        
        ("LOAD", "worker_id"),
        ("PRINT", "Worker {} completed phase 1, waiting at barrier"),
        
        # Increment the barrier counter
        ("LOAD", "barrier_counter"),
        ("ATOMIC_INCREMENT",),
        ("STORE", "count"),
        
        # Check if all workers have arrived
        ("LOAD", "count"),
        ("LOAD", "num_workers"),
        ("SUB",),
        ("JUMP_IF", 15),  # If equal, we're the last one
        
        # Not the last one, wait for barrier to be released
        ("LOAD", "barrier_sem"),
        ("SEMAPHORE_ACQUIRE",),
        ("JUMP", 18),  # Jump to phase 2
        
        # Last worker to arrive releases the barrier
        ("PUSH", 1),
        ("STORE", "i"),
        
        # Loop to release all waiting workers
        ("LOAD", "i"),
        ("LOAD", "num_workers"),
        ("PUSH", 1),
        ("SUB",),  # num_workers - 1 (exclude self)
        ("SUB",),
        ("JUMP_IF", 27),  # Jump to self-release if done
        
        ("LOAD", "barrier_sem"),
        ("SEMAPHORE_RELEASE",),
        
        ("LOAD", "i"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "i"),
        ("JUMP", 16),  # Jump back to release loop
        
        # Phase 2
        ("LOAD", "worker_id"),
        ("PRINT", "Worker {} starting phase 2"),
        
        # Simulate more work
        ("PUSH", 30),
        ("SLEEP",),
        
        ("LOAD", "worker_id"),
        ("PRINT", "Worker {} completed all phases"),
    ]
    
    main_instructions = [
        # Create synchronization primitives
        ("PUSH", 0),
        ("ATOMIC_CREATE",),
        ("GLOBAL_STORE", "barrier_counter"),
        
        ("PUSH", 0),
        ("SEMAPHORE_CREATE",),
        ("GLOBAL_STORE", "barrier_sem"),
        
        # Number of workers
        ("PUSH", 5),
        ("GLOBAL_STORE", "num_workers"),
        
        # Create workers
        ("PUSH", 5),
        ("STORE", "worker_count"),
        ("PUSH", 1),
        ("STORE", "worker_idx"),
        
        # Loop to create workers
        ("LOAD", "worker_idx"),
        ("LOAD", "worker_count"),
        ("SUB",),
        ("JUMP_IF", 24),  # Jump to end if done
        
        # Set worker ID
        ("LOAD", "worker_idx"),
        ("GLOBAL_STORE", "worker_id"),
        
        # Create worker thread
        ("PUSH", 0),
        ("THREAD_CREATE", [worker_instructions]),
        ("POP",),
        
        # Increment worker index
        ("LOAD", "worker_idx"),
        ("PUSH", 1),
        ("ADD",),
        ("STORE", "worker_idx"),
        ("JUMP", 15),  # Jump back to loop condition
        
        # Wait for a while and then exit
        ("PUSH", 300),
        ("SLEEP",),
        ("PRINT", "Barrier synchronization simulation complete"),
    ]
    
    vm.create_thread(main_instructions, "main")
    vm.run(debug=True)



if __name__ == "__main__":
    print("\n=== Example: Counter Race Condition ===")
    example_counter_race_condition()
    
#    print("\n=== Example: Mutex Protection ===")
#    example_mutex_protection()
    
#    print("\n=== Example: Producer-Consumer Pattern ===")
#    example_producer_consumer()
    
#    print("\n=== Example: Semaphore Usage ===")
#    example_semaphore()
    
#    print("\n=== Example: Atomic Counter ===")
#    example_atomic_counter()
    
#    print("\n=== Example: Dining Philosophers Problem ===")
#    example_dining_philosophers()
    
#    print("\n=== Example: Readers-Writers Problem ===")
#    example_readers_writers()
    
#    print("\n=== Example: Barrier Synchronization ===")
#    example_barrier_synchronization()