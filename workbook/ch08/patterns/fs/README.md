
## File System

### 1. Composite Pattern  
- `FileSystemNode` (abstract base class) acts as the Component.  
- `File` is a Leaf (no children).  
- `Directory` is a Composite (holds children: files or directories).  
- Enables uniform treatment of files/directories (e.g., recursive traversal).  

### 2. Visitor Pattern  
- `FileSystemVisitor` (abstract) defines operations for nodes.  
- Concrete visitors:  
  - `FindVisitor`: Searches for files/dirs matching a pattern.  
  - `StatVisitor`: Collects metadata (size, permissions).  
- Decouples operations from node classes (e.g., `accept()` calls `visit_file()`/`visit_directory()`).  

### 3. Strategy Pattern  
- `PathStrategy` abstracts path resolution logic.  
- `StandardPathStrategy` implements Unix-like path handling (`/`, `..`, `.`).  
- Allows swapping path resolution rules (e.g., Windows-style paths later).  

### 4. Command Pattern  
- `Command` (abstract) standardizes operations (e.g., `execute()`).  
- Concrete commands:  
  - `MkdirCommand`, `CdCommand`, `LsCommand`, etc.  
  - Encapsulates actions like file creation, deletion, or metadata updates.  
- Enables undo/redo or logging extensions.  

### 5. Factory Pattern  
- `FileSystemNodeFactory` centralizes creation of:  
  - Files (`create_file()`).  
  - Directories (`create_directory()`).  
- Simplifies object creation and ensures consistency.  

### 6. Singleton Pattern  
- `FileSystem` uses a metaclass (`Singleton`) to enforce a single instance.  
- Guarantees global access to the root filesystem.  


#### Benefits  
- Extensibility: New commands, visitors, or path strategies can be added without modifying core logic.
- Separation of Concerns: Each pattern isolates specific behaviors (e.g. traversal vs. operations).
- Reusability: Components like `FindVisitor` or `StandardPathStrategy` can be reused across projects.

