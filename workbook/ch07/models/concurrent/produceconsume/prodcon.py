import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

# Thread, Lock, Semaphore, MessageQueue, AtomicCounter classes (unchanged)
class Thread:
    def __init__(self, vm, name: str, instructions: List[Tuple], start_pc: int = 0, priority: int = 0):
        self.vm = vm
        self.name = name
        self.instructions = instructions
        self.pc = start_pc
        self.stack = []
        self.variables = {}
        self.running = True
        self.waiting = False
        self.wait_condition: Optional[Callable[[], bool]] = None
        self.joined_by = []
        self.priority = priority
        self.last_scheduled = time.time()

    def step(self):
        if not self.running or self.waiting:
            return False
        if self.pc >= len(self.instructions):
            self.running = False
            for thread_name in self.joined_by:
                thread = self.vm.threads.get(thread_name)
                if thread and thread.waiting:
                    thread.waiting = False
                    thread.wait_condition = None
            return False
        if self.wait_condition and self.wait_condition():
            self.waiting = False
            self.wait_condition = None
        instruction = self.instructions[self.pc]
        opcode = instruction[0]
        args = instruction[1:] if len(instruction) > 1 else []
        self.vm.execute_instruction(self, opcode, args)
        self.pc += 1
        self.last_scheduled = time.time()
        return True

class Lock:
    def __init__(self, name: str):
        self.name = name
        self.locked = False
        self.owner = None
        self.waiting_threads = deque()

    def acquire(self, thread_name: str) -> bool:
        if not self.locked:
            self.locked = True
            self.owner = thread_name
            return True
        self.waiting_threads.append(thread_name)
        return False

    def release(self, thread_name: str) -> Tuple[bool, Optional[str]]:
        if self.locked and self.owner == thread_name:
            if self.waiting_threads:
                next_thread = self.waiting_threads.popleft()
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
        self.waiting_threads = deque()

    def acquire(self, thread_name: str) -> bool:
        if self.count > 0:
            self.count -= 1
            return True
        self.waiting_threads.append(thread_name)
        return False

    def release(self) -> Optional[str]:
        if self.waiting_threads:
            next_thread = self.waiting_threads.popleft()
            return next_thread
        self.count += 1
        return None

class MessageQueue:
    def __init__(self, name: str):
        self.name = name
        self.messages = deque()
        self.waiting_receivers = deque()

    def send(self, message: Any) -> Optional[Tuple[str, Any]]:
        if self.waiting_receivers:
            receiver = self.waiting_receivers.popleft()
            return (receiver, message)
        self.messages.append(message)
        return None

    def receive(self, thread_name: str) -> Tuple[bool, Any]:
        if self.messages:
            return (True, self.messages.popleft())
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

    def get(self) -> int:
        return self.value

class ToyVM:
    def __init__(self):
        self.threads: Dict[str, Thread] = {}
        self.locks: Dict[str, Lock] = {}
        self.semaphores: Dict[str, Semaphore] = {}
        self.message_queues: Dict[str, MessageQueue] = {}
        self.atomic_counters: Dict[str, AtomicCounter] = {}
        self.globals = {}
        self.next_thread_id = 0
        self.running = False
        self.scheduler_type = "round_robin"
        self.step_interval = 0.01
        self.active_threads = deque()

    def create_thread(self, instructions: List[Tuple], name: str = None, priority: int = 0) -> str:
        if name is None:
            name = f"thread-{self.next_thread_id}"
            self.next_thread_id += 1
        thread = Thread(self, name, instructions, priority=priority)
        self.threads[name] = thread
        self.active_threads.append(name)
        print(f"[DEBUG] Created thread {name}")
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

    def detect_deadlock(self) -> bool:
        if not self.threads:
            return False
        all_waiting = all(t.waiting or not t.running for t in self.threads.values())
        if all_waiting:
            for thread in self.threads.values():
                if thread.waiting and thread.wait_condition and thread.wait_condition():
                    return False
            return True
        return False

    def get_thread_state(self, thread: Thread) -> str:
        if not thread.running:
            return "terminated"
        if thread.waiting:
            if thread.wait_condition:
                try:
                    can_proceed = thread.wait_condition()
                    return f"waiting (condition: {can_proceed})"
                except:
                    return "waiting (condition error)"
            return "waiting"
        return "runnable"

    def run(self, max_steps: int = 50000, debug: bool = False):
        self.running = True
        step_count = 0
        while self.running and step_count < max_steps:
            step_count += 1
            runnable_threads = [t for t in self.active_threads if self.threads[t].running and not self.threads[t].waiting]
            self.active_threads = deque([t for t in self.active_threads if self.threads[t].running])
            if not runnable_threads:
                for t in self.active_threads:
                    thread = self.threads[t]
                    if thread.waiting and thread.wait_condition and thread.wait_condition():
                        runnable_threads.append(t)
                        thread.waiting = False
                        thread.wait_condition = None
            if not runnable_threads:
                if not self.active_threads:
                    break
            if self.detect_deadlock():
                if debug:
                    print("Deadlock detected!")
                    self.print_thread_states(debug)
                self.running = False
                break
            thread_name = self.select_thread(runnable_threads)
            if thread_name is None:
                continue
            thread = self.threads[thread_name]
            if debug:
                print(f"Step {step_count}: Running thread {thread_name} (priority {thread.priority}) at PC {thread.pc}")
                if thread.pc < len(thread.instructions):
                    print(f"  Instruction: {thread.instructions[thread.pc]}")
                print(f"  Stack: {thread.stack}")
                print(f"  Variables: {thread.variables}")
                print(f"  State: {self.get_thread_state(thread)}")
            thread.step()
            time.sleep(self.step_interval)
        self.running = False
        if debug:
            if step_count >= max_steps:
                print(f"Stopped after {max_steps} steps - possible incomplete execution")
                self.print_thread_states(debug)
            else:
                print(f"All threads completed after {step_count} steps")
        return step_count

    def select_thread(self, active_threads: List[str]) -> str:
        if not active_threads:
            return None
        if self.scheduler_type == "priority":
            candidates = [
                (t, self.threads[t].priority, -self.threads[t].last_scheduled)
                for t in active_threads
            ]
            selected = max(candidates, key=lambda x: (x[1], x[2]))[0]
        elif self.scheduler_type == "round_robin":
            if active_threads:
                selected = active_threads[0]
                if selected in self.active_threads:
                    while self.active_threads and self.active_threads[0] != selected:
                        self.active_threads.rotate(-1)
                    if self.active_threads:
                        self.active_threads.rotate(-1)
            else:
                selected = None
        else:
            selected = random.choice(active_threads)
        if selected:
            print(f"[DEBUG] Selected thread {selected}")
        return selected

    def print_thread_states(self, debug: bool):
        if not debug:
            return
        print("\nThread States:")
        for name, thread in self.threads.items():
            state = self.get_thread_state(thread)
            print(f"  {name}: {state}, PC: {thread.pc}, Stack: {thread.stack}")
            if thread.waiting and thread.wait_condition:
                print(f"    Waiting on condition: {thread.wait_condition.__name__ if hasattr(thread.wait_condition, '__name__') else 'anonymous'}")

    def execute_instruction(self, thread: Thread, opcode: str, args: List[Any]):
        try:
            if opcode == "PUSH":
                thread.stack.append(args[0])
            elif opcode == "POP":
                if thread.stack:
                    thread.stack.pop()
                else:
                    raise RuntimeError("Stack underflow on POP")
            elif opcode == "DUP":
                if thread.stack:
                    thread.stack.append(thread.stack[-1])
                else:
                    raise RuntimeError("Stack underflow on DUP")
            elif opcode == "ADD":
                if len(thread.stack) >= 2:
                    b = thread.stack.pop()
                    a = thread.stack.pop()
                    thread.stack.append(a + b)
                else:
                    raise RuntimeError("Stack underflow on ADD")
            elif opcode == "SUB":
                if len(thread.stack) >= 2:
                    b = thread.stack.pop()
                    a = thread.stack.pop()
                    thread.stack.append(a - b)
                else:
                    raise RuntimeError("Stack underflow on SUB")
            elif opcode == "MUL":
                if len(thread.stack) >= 2:
                    b = thread.stack.pop()
                    a = thread.stack.pop()
                    if args and args[0] == "mod":
                        thread.stack.append(a % b)
                    else:
                        thread.stack.append(a * b)
                else:
                    raise RuntimeError("Stack underflow on MUL")
            elif opcode == "DIV":
                if len(thread.stack) >= 2:
                    b = thread.stack.pop()
                    a = thread.stack.pop()
                    if b != 0:
                        thread.stack.append(a // b)
                    else:
                        raise RuntimeError("Division by zero")
                else:
                    raise RuntimeError("Stack underflow on DIV")
            elif opcode == "LOAD":
                var_name = args[0]
                if var_name in thread.variables:
                    thread.stack.append(thread.variables[var_name])
                elif var_name in self.globals:
                    thread.stack.append(self.globals[var_name])
                else:
                    raise KeyError(f"Variable {var_name} not found")
            elif opcode == "STORE":
                var_name = args[0]
                if thread.stack:
                    thread.variables[var_name] = thread.stack.pop()
                else:
                    raise RuntimeError("Stack underflow on STORE")
            elif opcode == "GLOBAL_STORE":
                var_name = args[0]
                if thread.stack:
                    self.globals[var_name] = thread.stack.pop()
                else:
                    raise RuntimeError("Stack underflow on GLOBAL_STORE")
            elif opcode == "JUMP":
                thread.pc = args[0] - 1
            elif opcode == "JUMP_IF":
                if thread.stack:
                    condition = thread.stack.pop()
                    if condition >= 0:
                        thread.pc = args[0] - 1
                else:
                    raise RuntimeError("Stack underflow on JUMP_IF")
            elif opcode == "PRINT":
                if args:
                    message = args[0]
                    if thread.stack and "{}" in message:
                        value = thread.stack[-1]
                        message = message.replace("{}", str(value))
                    print(f"[{thread.name}] {message}")
                elif thread.stack:
                    print(f"[{thread.name}] {thread.stack[-1]}")
            elif opcode == "THREAD_CREATE":
                if len(thread.stack) >= 1:
                    instructions_index = thread.stack.pop()
                    new_thread_instructions = args[0][instructions_index]
                    new_thread_name = self.create_thread(new_thread_instructions, priority=thread.priority + 1)
                    thread.stack.append(new_thread_name)
                else:
                    raise RuntimeError("Stack underflow on THREAD_CREATE")
            elif opcode == "THREAD_JOIN":
                if thread.stack:
                    other_thread_name = thread.stack.pop()
                    other_thread = self.threads.get(other_thread_name)
                    if other_thread and other_thread.running:
                        other_thread.joined_by.append(thread.name)
                        thread.waiting = True
                        thread.wait_condition = lambda: not other_thread.running
                else:
                    raise RuntimeError("Stack underflow on THREAD_JOIN")
            elif opcode == "LOCK_CREATE":
                lock_name = self.create_lock()
                thread.stack.append(lock_name)
            elif opcode == "LOCK_ACQUIRE":
                if thread.stack:
                    lock_name = thread.stack.pop()
                    lock = self.locks.get(lock_name)
                    if lock:
                        if lock.acquire(thread.name):
                            pass
                        else:
                            thread.waiting = True
                            thread.wait_condition = lambda: lock.owner == thread.name or not lock.locked
                    else:
                        raise KeyError(f"Lock {lock_name} not found")
                else:
                    raise RuntimeError("Stack underflow on LOCK_ACQUIRE")
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
                                next_thread_obj.wait_condition = None
                    else:
                        raise KeyError(f"Lock {lock_name} not found")
                else:
                    raise RuntimeError("Stack underflow on LOCK_RELEASE")
            elif opcode == "SEMAPHORE_CREATE":
                if thread.stack:
                    count = thread.stack.pop()
                    sem_name = self.create_semaphore(count)
                    thread.stack.append(sem_name)
                else:
                    raise RuntimeError("Stack underflow on SEMAPHORE_CREATE")
            elif opcode == "SEMAPHORE_ACQUIRE":
                if thread.stack:
                    sem_name = thread.stack.pop()
                    sem = self.semaphores.get(sem_name)
                    if sem:
                        if sem.acquire(thread.name):
                            pass
                        else:
                            thread.waiting = True
                            thread.wait_condition = lambda: sem.count > 0 or thread.name in sem.waiting_threads
                    else:
                        raise KeyError(f"Semaphore {sem_name} not found")
                else:
                    raise RuntimeError("Stack underflow on SEMAPHORE_ACQUIRE")
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
                                next_thread_obj.wait_condition = None
                    else:
                        raise KeyError(f"Semaphore {sem_name} not found")
                else:
                    raise RuntimeError("Stack underflow on SEMAPHORE_RELEASE")
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
                            receiver_name, msg = result
                            receiver = self.threads.get(receiver_name)
                            if receiver:
                                receiver.waiting = False
                                receiver.wait_condition = None
                                receiver.stack.append(msg)
                    else:
                        raise KeyError(f"Queue {queue_name} not found")
                else:
                    raise RuntimeError("Stack underflow on QUEUE_SEND")
            elif opcode == "QUEUE_RECEIVE":
                if thread.stack:
                    queue_name = thread.stack.pop()
                    queue = self.message_queues.get(queue_name)
                    if queue:
                        success, message = queue.receive(thread.name)
                        if success:
                            thread.stack.append(message)
                        else:
                            queue.waiting_receivers.append(thread.name)
                            thread.waiting = True
                            thread.wait_condition = lambda: len(queue.messages) > 0 or thread.name in queue.waiting_receivers
                    else:
                        raise KeyError(f"Queue {queue_name} not found")
                else:
                    raise RuntimeError("Stack underflow on QUEUE_RECEIVE")
            elif opcode == "ATOMIC_CREATE":
                if thread.stack:
                    initial_value = thread.stack.pop()
                    counter_name = self.create_atomic_counter(initial_value)
                    thread.stack.append(counter_name)
                else:
                    raise RuntimeError("Stack underflow on ATOMIC_CREATE")
            elif opcode == "ATOMIC_INCREMENT":
                if thread.stack:
                    counter_name = thread.stack.pop()
                    counter = self.atomic_counters.get(counter_name)
                    if counter:
                        thread.stack.append(counter.increment())
                    else:
                        raise KeyError(f"Atomic counter {counter_name} not found")
                else:
                    raise RuntimeError("Stack underflow on ATOMIC_INCREMENT")
            elif opcode == "ATOMIC_DECREMENT":
                if thread.stack:
                    counter_name = thread.stack.pop()
                    counter = self.atomic_counters.get(counter_name)
                    if counter:
                        thread.stack.append(counter.decrement())
                    else:
                        raise KeyError(f"Atomic counter {counter_name} not found")
                else:
                    raise RuntimeError("Stack underflow on ATOMIC_DECREMENT")
            elif opcode == "ATOMIC_GET":
                if thread.stack:
                    counter_name = thread.stack.pop()
                    counter = self.atomic_counters.get(counter_name)
                    if counter:
                        thread.stack.append(counter.get())
                    else:
                        raise KeyError(f"Atomic counter {counter_name} not found")
                else:
                    raise RuntimeError("Stack underflow on ATOMIC_GET")
            elif opcode == "SLEEP":
                if thread.stack:
                    duration = thread.stack.pop()
                    time.sleep(duration / 1000)
                else:
                    raise RuntimeError("Stack underflow on SLEEP")
            elif opcode == "NOP":
                pass
            else:
                raise ValueError(f"[{thread.name}] Unknown opcode: {opcode}")
        except Exception as e:
            print(f"[{thread.name}] Error executing {opcode}: {str(e)}")
            thread.running = False

def producer_consumer_example():

    BUFFER_SIZE = 5  # Size of the bounded buffer
    NUM_PRODUCERS = 2
    NUM_CONSUMERS = 3
    NUM_ITEMS_PER_PRODUCER = 8  # Each producer creates this many items
    
    vm = ToyVM()
    vm.step_interval = 0.01  # Speed up or slow down execution for debugging
    
    producer_instructions = [
        # Initialize producer variables
        ["PUSH", "producer"],
        ["PRINT", "Starting {} thread..."],
        ["PUSH", NUM_ITEMS_PER_PRODUCER],
        ["STORE", "items_to_produce"],
        
        # Create loop for producing items
        ["LOAD", "items_to_produce"],
        ["PUSH", 0],
        ["SUB"],  # Check if items_to_produce <= 0
        ["JUMP_IF", 17],  # Exit if done
        
        # Acquire the semaphore for empty slots
        ["LOAD", "empty_sem"],
        ["SEMAPHORE_ACQUIRE"],
        
        # Acquire the buffer lock
        ["LOAD", "buffer_lock"],
        ["LOCK_ACQUIRE"],
        
        # Produce an item (use atomic counter to get unique IDs)
        ["LOAD", "item_counter"],
        ["ATOMIC_INCREMENT"],
        ["STORE", "item"],
        ["LOAD", "item"],
        ["PRINT", "Produced item {}"],
        
        # Add to buffer (push to message queue)
        ["LOAD", "buffer_queue"],
        ["LOAD", "item"],
        ["QUEUE_SEND"],
        
        # Release buffer lock
        ["LOAD", "buffer_lock"],
        ["LOCK_RELEASE"],
        
        # Signal that a filled slot is available
        ["LOAD", "filled_sem"],
        ["SEMAPHORE_RELEASE"],
        
        # Decrement counter and loop
        ["LOAD", "items_to_produce"],
        ["PUSH", 1],
        ["SUB"],
        ["STORE", "items_to_produce"],
        ["PUSH", 100],  # Sleep a bit
        ["SLEEP"],
        ["JUMP", 4],  # Jump back to check loop condition
        
        # Exit
        ["PRINT", "Producer finished"],
    ]
    
    consumer_instructions = [
        # Init consumer variables
        ["PUSH", "consumer"],
        ["PRINT", "Starting {} thread..."],
        
        # Create a loop for consuming items
        # We'll use a shared counter to ensure all items are consumed exactly once
        ["PUSH", True],  # Loop control flag
        ["STORE", "keep_running"],
        
        # Check if we should continue running
        ["LOAD", "keep_running"],
        ["JUMP_IF", 19],  # Exit if keep_running is false
        
        # Acquire the semaphore for filled slots
        ["LOAD", "filled_sem"],
        ["SEMAPHORE_ACQUIRE"],
        
        # Acquire the buffer lock
        ["LOAD", "buffer_lock"],
        ["LOCK_ACQUIRE"],
        
        # Take item from buffer
        ["LOAD", "buffer_queue"],
        ["QUEUE_RECEIVE"],
        ["STORE", "item"],
        ["LOAD", "item"],
        ["PRINT", "Consumed item {}"],
        
        # Release buffer lock
        ["LOAD", "buffer_lock"],
        ["LOCK_RELEASE"],
        
        # Signal that an empty slot is available
        ["LOAD", "empty_sem"],
        ["SEMAPHORE_RELEASE"],
        
        # Increment shared consumed counter
        ["LOAD", "consumed_counter"],
        ["ATOMIC_INCREMENT"],
        ["STORE", "my_consumed_count"],
        
        # Check if we've consumed all items
        ["LOAD", "my_consumed_count"],
        ["LOAD", "total_items"],
        ["SUB"],  # my_consumed_count - total_items
        ["PUSH", 0],
        ["SUB"],  # Check if my_consumed_count >= total_items
        ["JUMP_IF", 41],  # If true, we need to terminate
        
        # Continue consuming
        ["PUSH", 150],  # Sleep a bit longer than producer
        ["SLEEP"],
        ["JUMP", 6],  # Jump back to check loop condition
        
        # Set termination flag
        ["PUSH", False],
        ["STORE", "keep_running"],
        ["JUMP", 6],  # Jump back to exit loop
        
        # Exit
        ["PRINT", "Consumer finished - all items consumed"],
    ]
    
    # Create a lock for buffer access
    buffer_lock = vm.create_lock("buffer_lock")
    vm.globals["buffer_lock"] = buffer_lock
    
    # Create semaphores for buffer capacity control
    # - empty_sem counts available slots (starts at BUFFER_SIZE)
    # - filled_sem counts filled slots (starts at 0)
    empty_sem = vm.create_semaphore(BUFFER_SIZE, "empty_sem")
    vm.globals["empty_sem"] = empty_sem
    filled_sem = vm.create_semaphore(0, "filled_sem")
    vm.globals["filled_sem"] = filled_sem
    
    # Create message queue for the buffer
    buffer_queue = vm.create_message_queue("buffer_queue")
    vm.globals["buffer_queue"] = buffer_queue
    
    # Create atomic counter for item IDs
    item_counter = vm.create_atomic_counter(1, "item_counter")
    vm.globals["item_counter"] = item_counter
    
    # Create an atomic counter to track total consumed items
    consumed_counter = vm.create_atomic_counter(0, "consumed_counter")
    vm.globals["consumed_counter"] = consumed_counter
    
    # Set target for total items to be produced and consumed
    total_items = NUM_ITEMS_PER_PRODUCER * NUM_PRODUCERS
    vm.globals["total_items"] = total_items
    
    # Create producer threads
    producer_threads = []
    for i in range(NUM_PRODUCERS):
        producer_name = vm.create_thread(producer_instructions, f"Producer-{i+1}")
        producer_threads.append(producer_name)
    
    # Create consumer threads
    consumer_threads = []
    for i in range(NUM_CONSUMERS):
        consumer_name = vm.create_thread(consumer_instructions, f"Consumer-{i+1}")
        consumer_threads.append(consumer_name)
    
    return vm, producer_threads, consumer_threads

def main():
    print("Creating producer-consumer example...")
    vm, producer_threads, consumer_threads = producer_consumer_example()
    
    print("\nStarting simulation with:")
    print(f"- Buffer size: 5")
    print(f"- Producers: 2")
    print(f"- Consumers: 3")
    print(f"- Items per producer: 8")
    print(f"- Total items: 16")
    print("\nRunning simulation...")
    
    steps = vm.run(10000, debug=True)
    
    print(f"\nSimulation completed in {steps} steps.")
    
    print("\nFinal thread states:")
    vm.print_thread_states(debug=True)

if __name__ == "__main__":
    main()