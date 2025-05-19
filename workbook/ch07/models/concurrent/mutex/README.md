
## Mutex

A mutex, short for mutual exclusion, is a fundamental synchronisation primitive used in concurrent
programming to prevent multiple threads from accessing a shared resource simultaneously in a way
that leads to race conditions or data inconsistency. The core idea is simple but powerful: at any
given time, only one thread can "own" a mutex and thus gain access to the protected section of code
or resource. All other threads attempting to acquire the mutex must wait until it becomes available.

The historical origin of the concept can be traced back to the earliest days of multitasking operating
systems in the 1960s and 1970s, as developers realised that concurrent execution--particularly in
multiprocessor systems--could easily result in corrupted state when two processes attempted to modify
the same memory region or perform non-atomic operations. The term "mutual exclusion" and early
theoretical formulations such as Dekker's and Peterson's algorithms arose during this time to formalise
how competing processes could cooperate without interference. These early approaches were purely
software-based and worked only in restricted environments. Later, hardware-level atomic instructions
such as test-and-set, compare-and-swap, and fetch-and-add enabled more robust and portable implementations
of mutexes in operating systems and runtime libraries.

In practice, mutexes are ubiquitous in systems programming (e.g. C, C++, Rust) and application-level
concurrency frameworks (e.g. Java’s synchronised, Python’s threading.Lock, or Go’s sync.Mutex). They
are used whenever one needs to protect critical sections--regions of code that must be executed atomically
with respect to some shared resource, such as writing to a file, modifying a shared counter, or managing
a queue.

Using a mutex involves two key operations: `lock()` (or `acquire()`) and `unlock()` (or `release()`).
When a thread locks a mutex, it either gains access to the resource if the mutex was free, or is blocked
(or delayed) if another thread currently holds the lock. Once the thread finishes working with the
resource, it must unlock the mutex so that other waiting threads can proceed. Failing to release the
mutex leads to deadlock or starvation.

To demonstrate this in general, consider a simple Python example using threading.Lock:

```python
from threading import Lock, Thread

counter = 0
lock = Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

threads = [Thread(target=increment) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()

print(counter)  # should be 400000 if all increments were synchronised correctly
```

Without the lock, race conditions may cause unpredictable results--some increments could be lost due
to thread interleaving. The with lock: ensures only one thread modifies counter at a time.


