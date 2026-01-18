
## Simple OS

This code implements a simple operating system simulation with several components:

1. *Process Management*:
   - `Process` class represents processes with PID, name, priority, state, etc.
   - `ProcessManager` handles process creation, termination, and tracking
   - `Scheduler` with different scheduling strategies (Round Robin and Priority)
   - Process states: READY, RUNNING, BLOCKED, TERMINATED

2. *Memory Management*:
   - `MemoryManager` with allocation strategies (First Fit and Best Fit)
   - Tracks free and allocated memory blocks
   - Handles memory allocation and deallocation for processes

3. *File System*:
   - Hierarchical structure with `Directory` and `File` classes
   - Supports basic operations: mkdir, cd, ls, create/read/write files
   - Path navigation and current directory tracking

4. *Shell Interface*:
   - Interactive command-line interface
   - Implements common commands (ls, cd, mkdir, etc.)
   - Process-related commands (run, kill, ps)
   - System configuration commands (setsched, setmem)

5. *Kernel*:
   - Coordinates all components
   - Observer pattern for system monitoring
   - Bootstraps the system with initial processes

6. *Asynchronous Execution*:
   - Uses Python's asyncio for concurrent process execution
   - Cooperative multitasking through async/await

The system demonstrates core OS concepts:
- Process scheduling and state management
- Memory allocation strategies
- File system organization
- System monitoring
- User interaction via shell

To run it, simply execute the script. You'll get an interactive shell where you can try commands like:
- `ls`, `mkdir test`, `cd test`
- `run process1` (creates a new process)
- `ps` (view processes)
- `free` (view memory usage)
- `setsched priority` (change scheduler)
- `exit` (quit)

..
