import asyncio
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List, Optional
from collections import deque
import shlex
import sys
from abc import ABC, abstractmethod


class ProcessState(Enum):
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    TERMINATED = auto()


@dataclass
class Process:
    pid: int
    name: str
    priority: int = 0
    state: ProcessState = ProcessState.READY
    memory_start: int = 0
    memory_size: int = 0
    code: Callable = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    async def execute(self):
        if self.code:
            await self.code(self)


class SchedulingStrategy(ABC):
    @abstractmethod
    async def schedule(self, ready_queue: deque, blocked_queue: deque) -> Optional[Process]:
        pass


class RoundRobinScheduler(SchedulingStrategy):
    async def schedule(self, ready_queue: deque, blocked_queue: deque) -> Optional[Process]:
        if not ready_queue:
            return None
        return ready_queue.popleft()


class PriorityScheduler(SchedulingStrategy):
    async def schedule(self, ready_queue: deque, blocked_queue: deque) -> Optional[Process]:
        if not ready_queue:
            return None
        highest_priority = max(ready_queue, key=lambda p: p.priority)
        ready_queue.remove(highest_priority)
        return highest_priority


class Scheduler:
    def __init__(self, strategy: SchedulingStrategy = None):
        self.ready_queue = deque()
        self.blocked_queue = deque()
        self.current_process = None
        self.strategy = strategy or RoundRobinScheduler()
        
    def set_strategy(self, strategy: SchedulingStrategy):
        self.strategy = strategy
        
    def add_process(self, process: Process):
        self.ready_queue.append(process)
        
    def unblock_process(self, pid: int):
        for i, process in enumerate(self.blocked_queue):
            if process.pid == pid:
                process.state = ProcessState.READY
                self.ready_queue.append(process)
                self.blocked_queue.remove(process)
                return True
        return False
        
    async def schedule(self):
        while self.ready_queue:
            self.current_process = await self.strategy.schedule(self.ready_queue, self.blocked_queue)
            if not self.current_process:
                break
                
            self.current_process.state = ProcessState.RUNNING
            print(f"[Scheduler] Running {self.current_process.name} (PID: {self.current_process.pid})")
            
            try:
                await self.current_process.execute()
            except Exception as e:
                print(f"Process error: {e}")
            
            if self.current_process.state == ProcessState.READY:
                self.ready_queue.append(self.current_process)
            elif self.current_process.state == ProcessState.BLOCKED:
                self.blocked_queue.append(self.current_process)
            elif self.current_process.state == ProcessState.RUNNING:
                self.current_process.state = ProcessState.READY
                self.ready_queue.append(self.current_process)
            else:  # TERMINATED
                print(f"[Scheduler] Process {self.current_process.name} terminated")


class MemoryAllocationStrategy(ABC):
    @abstractmethod
    def allocate(self, free_blocks: List[tuple], size: int) -> Optional[tuple]:
        pass


class FirstFitAllocator(MemoryAllocationStrategy):
    def allocate(self, free_blocks: List[tuple], size: int) -> Optional[tuple]:
        for i, (start, block_size) in enumerate(free_blocks):
            if block_size >= size:
                return i, start, size
        return None


class BestFitAllocator(MemoryAllocationStrategy):
    def allocate(self, free_blocks: List[tuple], size: int) -> Optional[tuple]:
        best_fit = None
        best_index = None
        best_waste = float('inf')
        
        for i, (start, block_size) in enumerate(free_blocks):
            if block_size >= size:
                waste = block_size - size
                if waste < best_waste:
                    best_waste = waste
                    best_fit = (start, size)
                    best_index = i
                    
        if best_fit:
            return best_index, best_fit[0], best_fit[1]
        return None


class MemoryManager:
    def __init__(self, total_memory: int, allocator: MemoryAllocationStrategy = None):
        self.total_memory = total_memory
        self.free_blocks = [(0, total_memory)]
        self.allocated_blocks = {}
        self.allocator = allocator or FirstFitAllocator()
    
    def set_allocator(self, allocator: MemoryAllocationStrategy):
        self.allocator = allocator
    
    def allocate(self, pid: int, size: int) -> int:
        result = self.allocator.allocate(self.free_blocks, size)
        if not result:
            raise MemoryError(f"Not enough memory to allocate {size} units")
            
        i, start, allocated_size = result
        self.allocated_blocks[pid] = (start, allocated_size)
        
        block_start, block_size = self.free_blocks[i]
        if block_size > allocated_size:
            self.free_blocks[i] = (block_start + allocated_size, block_size - allocated_size)
        else:
            self.free_blocks.pop(i)
        
        return start
    
    def free(self, pid: int):
        if pid in self.allocated_blocks:
            start, size = self.allocated_blocks.pop(pid)
            self.free_blocks.append((start, size))
            self._merge_free_blocks()
    
    def _merge_free_blocks(self):
        if not self.free_blocks:
            return
            
        self.free_blocks.sort(key=lambda block: block[0])
        merged = []
        current = self.free_blocks[0]
        
        for next_block in self.free_blocks[1:]:
            curr_start, curr_size = current
            next_start, next_size = next_block
            
            if curr_start + curr_size == next_start:
                current = (curr_start, curr_size + next_size)
            else:
                merged.append(current)
                current = next_block
        
        merged.append(current)
        self.free_blocks = merged


class FileSystemNode(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def is_directory(self) -> bool:
        pass


class File(FileSystemNode):
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self.content = content
    
    def is_directory(self) -> bool:
        return False


class Directory(FileSystemNode):
    def __init__(self, name: str, parent: 'Directory' = None):
        super().__init__(name)
        self.parent = parent
        self.children = {}
    
    def is_directory(self) -> bool:
        return True


class FileSystem:
    def __init__(self):
        self.root = Directory("root")
        self.current_directory = self.root
        
    def mkdir(self, name: str):
        if name in self.current_directory.children:
            raise FileExistsError(f"Directory {name} already exists")
        
        self.current_directory.children[name] = Directory(name, self.current_directory)
    
    def cd(self, path: str):
        if path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
        elif path == "/":
            self.current_directory = self.root
        elif path in self.current_directory.children:
            node = self.current_directory.children[path]
            if node.is_directory():
                self.current_directory = node
            else:
                raise NotADirectoryError(f"{path} is not a directory")
        else:
            raise FileNotFoundError(f"Directory {path} not found")
    
    def ls(self) -> List[str]:
        return list(self.current_directory.children.keys())
    
    def create_file(self, name: str, content: str = ""):
        if name in self.current_directory.children:
            raise FileExistsError(f"File {name} already exists")
        
        self.current_directory.children[name] = File(name, content)
    
    def read_file(self, name: str) -> str:
        if name not in self.current_directory.children:
            raise FileNotFoundError(f"File {name} not found")
        
        file = self.current_directory.children[name]
        if file.is_directory():
            raise IsADirectoryError(f"{name} is a directory, not a file")
        
        return file.content
    
    def write_file(self, name: str, content: str):
        if name not in self.current_directory.children:
            self.create_file(name, content)
        else:
            file = self.current_directory.children[name]
            if file.is_directory():
                raise IsADirectoryError(f"{name} is a directory, not a file")
            file.content = content
    
    def delete(self, name: str):
        if name not in self.current_directory.children:
            raise FileNotFoundError(f"{name} not found")
        
        del self.current_directory.children[name]
    
    def get_path(self) -> str:
        if self.current_directory == self.root:
            return "/"
        
        path = []
        current = self.current_directory
        while current != self.root:
            path.insert(0, current.name)
            current = current.parent
        
        return "/" + "/".join(path)


class Command(ABC):
    @abstractmethod
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        pass


class LSCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        files = kernel.file_system.ls()
        if files:
            print("\n".join(files))
        return True


class CDCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args:
            return True
        
        kernel.file_system.cd(args[0])
        return True


class MkdirCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args:
            print("Usage: mkdir <directory>")
            return True
        
        kernel.file_system.mkdir(args[0])
        return True


class CatCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args:
            print("Usage: cat <file>")
            return True
        
        content = kernel.file_system.read_file(args[0])
        print(content)
        return True


class EchoCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args:
            return True
        
        if len(args) >= 2 and args[-2] == ">":
            filename = args[-1]
            content = " ".join(args[:-2])
            kernel.file_system.write_file(filename, content)
        else:
            print(" ".join(args))
        return True


class PSCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        processes = kernel.process_manager.list_processes()
        print("PID\tState\t\tName")
        print("-" * 30)
        for proc in processes:
            print(f"{proc.pid}\t{proc.state.name}\t{proc.name}")
        return True


class FreeCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        mem = kernel.memory_manager
        free = sum(size for _, size in mem.free_blocks)
        used = mem.total_memory - free
        
        print(f"Total memory: {mem.total_memory} units")
        print(f"Used memory: {used} units ({used/mem.total_memory:.1%})")
        print(f"Free memory: {free} units ({free/mem.total_memory:.1%})")
        return True


class HelpCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        print("Available commands:")
        cmds = {
            "ls": "Lists files and directories in the current directory.",
            "cd": "Changes the current working directory to the specified path.",
            "mkdir": "Creates a new directory with the given name.",
            "cat": "Displays the contents of a specified file.",
            "echo": "Prints text to console or redirects it to a file.",
            "ps": "Lists all processes with their PID, state, and name.",
            "free": "Shows memory usage including total, used, and free memory.",
            "help": "Displays all available commands and their descriptions.",
            "exit": "Terminates the shell and exits the operating system.",
            "run": "Creates and starts a new process with the given name.",
            "kill": "Terminates a process with the specified PID.",
            "setsched": "Changes scheduling between Round Robin and Priority-based.",
            "setmem": "Switches memory allocation between First Fit and Best Fit."
        }
        for cmd, desc in cmds.items():
            print(f"  {cmd:<8} - {desc}")
        return True


class ExitCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        print("Goodbye!")
        return False


class RunCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args:
            print("Usage: run <process_name>")
            return True
            
        process_name = args[0]
        
        async def simple_process(process):
            print(f"Process {process.name} started")
            for i in range(5):
                print(f"{process.name}: Working... ({i+1}/5)")
                await asyncio.sleep(1)
            print(f"{process.name}: Work complete!")
            process.state = ProcessState.TERMINATED
            
        try:
            process = kernel.process_manager.create_process(process_name, simple_process)
            print(f"Started process {process_name} with PID {process.pid}")
        except Exception as e:
            print(f"Failed to start process: {e}")
        return True


class KillCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args or not args[0].isdigit():
            print("Usage: kill <pid>")
            return True
            
        pid = int(args[0])
        
        try:
            kernel.process_manager.terminate_process(pid)
            print(f"Process with PID {pid} terminated")
        except ValueError as e:
            print(f"Error: {e}")
        return True


class SetSchedulerCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args or args[0] not in ["rr", "priority"]:
            print("Usage: setsched <rr|priority>")
            return True
            
        if args[0] == "rr":
            kernel.process_manager.scheduler.set_strategy(RoundRobinScheduler())
            print("Scheduler set to Round Robin")
        else:
            kernel.process_manager.scheduler.set_strategy(PriorityScheduler())
            print("Scheduler set to Priority-based")
        return True


class SetMemAllocCommand(Command):
    async def execute(self, args: List[str], kernel: 'Kernel') -> bool:
        if not args or args[0] not in ["firstfit", "bestfit"]:
            print("Usage: setmem <firstfit|bestfit>")
            return True
            
        if args[0] == "firstfit":
            kernel.memory_manager.set_allocator(FirstFitAllocator())
            print("Memory allocator set to First Fit")
        else:
            kernel.memory_manager.set_allocator(BestFitAllocator())
            print("Memory allocator set to Best Fit")
        return True


class Shell:
    def __init__(self, kernel: 'Kernel'):
        self.kernel = kernel
        self.running = True
        self.commands = {
            "ls": LSCommand(),
            "cd": CDCommand(),
            "mkdir": MkdirCommand(),
            "cat": CatCommand(),
            "echo": EchoCommand(),
            "ps": PSCommand(),
            "free": FreeCommand(),
            "help": HelpCommand(),
            "exit": ExitCommand(),
            "run": RunCommand(),
            "kill": KillCommand(),
            "setsched": SetSchedulerCommand(),
            "setmem": SetMemAllocCommand(),
        }
    
    async def run(self):
        print("Simple OS Shell. Type 'help' for commands.")
        while self.running:
            try:
                cwd = self.kernel.file_system.get_path()
                cmd = input(f"{cwd}> ")
                if cmd.strip():
                    self.running = await self.execute(cmd)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the shell")
            except EOFError:
                self.running = False
    
    async def execute(self, cmd_line: str) -> bool:
        try:
            args = shlex.split(cmd_line)
            cmd = args[0]
            
            if cmd in self.commands:
                return await self.commands[cmd].execute(args[1:], self.kernel)
            else:
                print(f"Command not found: {cmd}")
                return True
        except Exception as e:
            print(f"Error: {e}")
            return True


class ProcessManager:
    def __init__(self, memory_manager: MemoryManager):
        self.next_pid = 1
        self.processes = {}
        self.memory_manager = memory_manager
        self.scheduler = Scheduler()
    
    def create_process(self, name: str, code: Callable, memory_size: int = 64, priority: int = 0) -> Process:
        pid = self.next_pid
        self.next_pid += 1
        
        memory_start = self.memory_manager.allocate(pid, memory_size)
        
        process = Process(
            pid=pid,
            name=name,
            priority=priority,
            memory_start=memory_start,
            memory_size=memory_size,
            code=code
        )
        
        self.processes[pid] = process
        self.scheduler.add_process(process)
        
        return process
    
    def terminate_process(self, pid: int):
        if pid not in self.processes:
            raise ValueError(f"Process {pid} not found")
        
        process = self.processes[pid]
        process.state = ProcessState.TERMINATED
        
        self.memory_manager.free(pid)
        del self.processes[pid]
    
    def list_processes(self) -> List[Process]:
        return list(self.processes.values())
    
    async def start_scheduler(self):
        return await self.scheduler.schedule()


class KernelObserver(ABC):
    @abstractmethod
    async def update(self, event: str, data: Any = None):
        pass


class SystemMonitor(KernelObserver):
    def __init__(self):
        self.stats = {"uptime": 0, "process_count": 0}
    
    async def update(self, event: str, data: Any = None):
        if event == "tick":
            self.stats["uptime"] += 1
        elif event == "process_created":
            self.stats["process_count"] += 1
        elif event == "process_terminated":
            self.stats["process_count"] -= 1


class Kernel:
    def __init__(self, memory_size: int = 1024):
        self.memory_manager = MemoryManager(memory_size)
        self.process_manager = ProcessManager(self.memory_manager)
        self.file_system = FileSystem()
        self.observers = []
        self.shell = None
        
    def register_observer(self, observer: KernelObserver):
        self.observers.append(observer)
        
    async def notify_observers(self, event: str, data: Any = None):
        for observer in self.observers:
            await observer.update(event, data)
        
    async def bootstrap(self):
        print("Booting Simple OS...")
        
        system_monitor = SystemMonitor()
        self.register_observer(system_monitor)
        
        await self._create_init_process()
        await self._create_system_processes()
        
        self.shell = Shell(self)
        await self.shell.run()
    
    async def _create_init_process(self):
        async def init_code(process):
            print("Init process running")
            while True:
                await self.notify_observers("tick")
                await asyncio.sleep(5)
        
        self.process_manager.create_process("init", init_code)
        await self.notify_observers("process_created", {"name": "init"})
    
    async def _create_system_processes(self):
        async def system_monitor(process):
            while True:
                process.context["uptime"] = process.context.get("uptime", 0) + 1
                await asyncio.sleep(1)
                
        self.process_manager.create_process("system_monitor", system_monitor)
        await self.notify_observers("process_created", {"name": "system_monitor"})
        
        async def user_process(process):
            print(f"User process {process.name} started")
            for i in range(5):
                print(f"{process.name}: Working... ({i+1}/5)")
                await asyncio.sleep(0.5)
            print(f"{process.name}: Work complete!")
            process.state = ProcessState.TERMINATED
            
        self.process_manager.create_process("user_process", user_process)
        await self.notify_observers("process_created", {"name": "user_process"})


async def main():
    kernel = Kernel()
    await kernel.bootstrap()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
