import time
import random
from collections import deque
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid

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

    def run(self, max_steps: int = 20000, debug: bool = False):
        self.running = True
        step_count = 0
        while self.running and step_count < max_steps:
            step_count += 1
            runnable_threads = [t for t in self.active_threads if self.threads[t].running and not self.threads[t].waiting]
            if not runnable_threads:
                for t in self.active_threads:
                    thread = self.threads[t]
                    if thread.waiting and thread.wait_condition and thread.wait_condition():
                        runnable_threads.append(t)
                        thread.waiting = False
                        thread.wait_condition = None
            if not runnable_threads:
                break
            if self.detect_deadlock():
                if debug:
                    print("Deadlock detected!")
                    self.print_thread_states(debug)
                self.running = False
                break
            thread_name = self.select_thread(runnable_threads)
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
            selected = self.active_threads[0]
            self.active_threads.rotate(-1)
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
        if opcode == "PUSH":
            thread.stack.append(args[0])
        elif opcode == "POP":
            if thread.stack:
                thread.stack.pop()
        elif opcode == "DUP":
            if thread.stack:
                thread.stack.append(thread.stack[-1])
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
                if args and args[0] == "mod":
                    thread.stack.append(a % b)
                else:
                    thread.stack.append(a * b)
        elif opcode == "DIV":
            if len(thread.stack) >= 2:
                b = thread.stack.pop()
                a = thread.stack.pop()
                if b != 0:
                    thread.stack.append(a // b)
        elif opcode == "LOAD":
            var_name = args[0]
            if var_name in thread.variables:
                thread.stack.append(thread.variables[var_name])
            elif var_name in self.globals:
                thread.stack.append(self.globals[var_name])
        elif opcode == "STORE":
            var_name = args[0]
            if thread.stack:
                thread.variables[var_name] = thread.stack.pop()
        elif opcode == "GLOBAL_STORE":
            var_name = args[0]
            if thread.stack:
                self.globals[var_name] = thread.stack.pop()
        elif opcode == "JUMP":
            thread.pc = args[0] - 1
        elif opcode == "JUMP_IF":
            condition = thread.stack.pop() if thread.stack else False
            if condition >= 0:
                thread.pc = args[0] - 1
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
        elif opcode == "THREAD_JOIN":
            if thread.stack:
                other_thread_name = thread.stack.pop()
                other_thread = self.threads.get(other_thread_name)
                if other_thread and other_thread.running:
                    other_thread.joined_by.append(thread.name)
                    thread.waiting = True
                    thread.wait_condition = lambda: not other_thread.running
        elif opcode == "LOCK_CREATE":
            lock_name = self.create_lock()
            thread.stack.append(lock_name)
        elif opcode == "LOCK_ACQUIRE":
            if thread.stack:
                lock_name = thread.stack[-1]
                lock = self.locks.get(lock_name)
                if lock:
                    if lock.acquire(thread.name):
                        thread.stack.pop()
                    else:
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
                            next_thread_obj.wait_condition = None
        elif opcode == "SEMAPHORE_CREATE":
            if thread.stack:
                count = thread.stack.pop()
                sem_name = self.create_semaphore(count)
                thread.stack.append(sem_name)
        elif opcode == "SEMAPHORE_ACQUIRE":
            if thread.stack:
                sem_name = thread.stack[-1]
                sem = self.semaphores.get(sem_name)
                if sem:
                    if sem.acquire(thread.name):
                        thread.stack.pop()
                    else:
                        thread.waiting = True
                        thread.wait_condition = lambda: sem.count > 0 or thread.name in sem.waiting_threads
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
        elif opcode == "QUEUE_RECEIVE":
            if thread.stack:
                queue_name = thread.stack[-1]
                queue = self.message_queues.get(queue_name)
                if queue:
                    success, message = queue.receive(thread.name)
                    if success:
                        thread.stack.pop()
                        thread.stack.append(message)
                    else:
                        queue.waiting_receivers.append(thread.name)
                        thread.waiting = True
                        thread.wait_condition = lambda: len(queue.messages) > 0 or thread.name in queue.waiting_receivers
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
                    thread.stack.append(counter.increment())
        elif opcode == "ATOMIC_DECREMENT":
            if thread.stack:
                counter_name = thread.stack.pop()
                counter = self.atomic_counters.get(counter_name)
                if counter:
                    thread.stack.append(counter.decrement())
        elif opcode == "ATOMIC_GET":
            if thread.stack:
                counter_name = thread.stack.pop()
                counter = self.atomic_counters.get(counter_name)
                if counter:
                    thread.stack.append(counter.get())
        elif opcode == "SLEEP":
            if thread.stack:
                duration = thread.stack.pop()
                time.sleep(duration / 1000)
        elif opcode == "NOP":
            pass
        else:
            print(f"[{thread.name}] Unknown opcode: {opcode}")

def example_atomic_counter():
    vm = ToyVM()
    
    worker_instructions = [
        ("PUSH", 0),              # PC 0: Initialize i = 0
        ("STORE", "i"),           # PC 1: Store i
        ("LOAD", "i"),            # PC 2: Load i
        ("PUSH", 100),            # PC 3: Push 100
        ("SUB",),                 # PC 4: Compute i - 100
        ("JUMP_IF", 17),          # PC 5: Jump to PC 17 if i >= 100
        ("LOAD", "counter"),      # PC 6: Load counter
        ("ATOMIC_INCREMENT",),    # PC 7: Atomically increment counter
        ("DUP",),                 # PC 8: Duplicate counter value
        ("PRINT", "Worker increment to {}"), # PC 9: Debug print
        ("POP",),                 # PC 10: Pop duplicated counter value
        ("POP",),                 # PC 11: Pop original counter value
        ("LOAD", "i"),            # PC 12: Load i
        ("PUSH", 1),              # PC 13: Push 1
        ("ADD",),                 # PC 14: i += 1
        ("STORE", "i"),           # PC 15: Store i
        ("JUMP", 2),              # PC 16: Loop back to PC 2
        ("NOP",),                 # PC 17: Loop exit
    ]

    main_instructions = [
        ("PUSH", 0),              # PC 0: Push 0
        ("ATOMIC_CREATE",),       # PC 1: Create atomic counter
        ("GLOBAL_STORE", "counter"), # PC 2: Store to counter
        ("PUSH", 0),              # PC 3: Create thread 0
        ("THREAD_CREATE", [worker_instructions]), # PC 4
        ("PUSH", 0),              # PC 5: Create thread 1
        ("THREAD_CREATE", [worker_instructions]), # PC 6
        ("LOAD", "thread-0"),     # PC 7: Load thread-0 name
        ("THREAD_JOIN",),         # PC 8: Join thread-0
        ("LOAD", "thread-1"),     # PC 9: Load thread-1 name
        ("THREAD_JOIN",),         # PC 10: Join thread-1
        ("LOAD", "counter"),      # PC 11: Load counter
        ("ATOMIC_GET",),          # PC 12: Get counter value
        ("DUP",),                 # PC 13: Duplicate for print
        ("PRINT", "Final counter value: {}"), # PC 14: Print value
        ("PUSH", 200),            # PC 15: Push 200
        ("SUB",),                 # PC 16: counter - 200
        ("JUMP_IF", 19),          # PC 17: Jump to 19 if counter == 200
        ("PRINT", "Test FAILED - Atomic counter incorrect"), # PC 18
        ("JUMP", 20),             # PC 19: Skip failure
        ("PRINT", "Test PASSED - Atomic counter correct"), # PC 20
    ]
    
    vm.create_thread(main_instructions, "main", priority=1)
    vm.run(debug=True, max_steps=50000)  # Keep increased max_steps for debugging

if __name__ == "__main__":
    print("\n=== Example: Atomic Counter ===")
    example_atomic_counter()