
## File System

### 1. Composite Pattern  
- `FileSystemNode` (abstract base class) → Component  
- `File` → Leaf (no children)  
- `Directory` → Composite (holds child nodes)  
- Why? Treat files/directories uniformly (e.g., recursive traversal).  

### 2. Visitor Pattern  
- `FileSystemVisitor` (abstract) → Defines operations for nodes.  
- Concrete Visitors:  
  - `FindVisitor`: Searches files/dirs by name.  
  - `StatVisitor`: Collects metadata (size, permissions).  
- Why? Decouples operations from node logic (e.g., `accept()` calls `visit_file()`).  

### 3. Command Pattern  
- `Command` (abstract) → Standardizes operations (`execute()`).  
- Concrete Commands:  
  - `MkdirCommand`, `CdCommand`, `LsCommand`, etc.  
- Why? Encapsulates actions (e.g., file creation) for undo/redo or logging.  

### 4. Strategy Pattern  
- `PathStrategy` → Abstracts path resolution logic.  
- `StandardPathStrategy` → Handles Unix-like paths (`/`, `..`, `.`).  
- Why? Swappable path rules (e.g., add Windows support later).  

### 5. Factory Pattern  
- `FileSystemNodeFactory` → Centralizes creation of:  
  - Files (`create_file()`).  
  - Directories (`create_directory()`).  
- Why? Ensures consistent node creation.  

### 6. Singleton Pattern  
- `FileSystem` → Uses `Singleton` metaclass for a single instance.  
- Why? Global access to the root filesystem.  


### Tasks

1. Add a new command:  
   - Subclass `Command` (e.g., `ZipCommand` for compression).  

2. Support new path styles:  
   - Implement `PathStrategy` (e.g., `WindowsPathStrategy`).  

3. Add a visitor:  
   - Extend `FileSystemVisitor` (e.g., `EncryptVisitor` for file encryption).  


### Benefits
- Modularity: Patterns isolate concerns (e.g., traversal vs. commands).  
- Maintainability: Easy to add features (e.g., undo/redo via command history).  
- Educational: Demonstrates how real file systems abstract complexity.  
