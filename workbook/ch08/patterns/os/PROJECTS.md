## OS Simulation Projects*  

### A. Multi-threaded Process Scheduler
- *Goal*: Extend the OS scheduler to handle threads.  
- *Tasks*:  
  - Add thread states (`READY`, `RUNNING`, `WAITING`).  
  - Implement thread synchronization (mutexes/semaphores).  
  - Simulate thread context switching.  

### B. Virtual Memory & Paging Simulation
- *Goal*: Add virtual memory to the OS.  
- *Tasks*:  
  - Simulate *page tables* and *TLB (Translation Lookaside Buffer)*.  
  - Implement *page replacement algorithms* (FIFO, LRU).  
  - Handle *page faults* gracefully.  

### C. File System with Permissions & Symbolic Links
- *Goal*: Extend the file system to support Unix-like permissions.  
- *Tasks*:  
  - Add `chmod`, `chown` commands.  
  - Support symbolic/hard links.  
  - Simulate `inodes` for file metadata.  
