
## Simple OS


### Strategy Pattern

SchedulingStrategy for pluggable scheduling algorithms (Round Robin and Priority-based)

MemoryAllocationStrategy for different memory allocation strategies (First Fit and Best Fit)



### Command Pattern

Converted shell commands to proper Command classes

Each command is encapsulated in its own class with a standard interface


### Observer Pattern

KernelObserver interface and SystemMonitor implementation

Kernel can notify observers of system events like process creation, termination, and tick events


### Composite Pattern

Enhanced the file system with a proper FileSystemNode hierarchy

Both File and Directory extend from the same base class


### Dependency Injection


The Kernel [injects dependencies](./DEPENDENCY.md) into its components

Scheduler strategies and memory allocators are injectable
