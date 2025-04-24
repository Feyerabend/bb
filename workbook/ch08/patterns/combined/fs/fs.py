from typing import Dict, List, Optional, Union, Any, Callable
from abc import ABC, abstractmethod

# > composite pattern
# FileSystemNode is the abstract Component class
class FileSystemNode(ABC):
    """Abstract base class for file system nodes (Component in Composite pattern)"""
    def __init__(self, name: str):
        self.name = name
        self.metadata = {
            "created": 0,
            "modified": 0,
            "permissions": "rw-r--r--"
        }
    
    @abstractmethod
    def get_type(self) -> str:
        """Return type of node"""
        pass
    
    @abstractmethod
    def accept(self, visitor: 'FileSystemVisitor') -> Any:
        """Accept a visitor (Visitor pattern)"""
        pass


# File is a Leaf in the Composite pattern
class File(FileSystemNode):
    """Represents a file in the file system (Leaf in Composite pattern)"""
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self.content = content
        self.metadata["size"] = len(content)
        self.metadata["permissions"] = "rw-r--r--"
    
    def get_type(self) -> str:
        return "file"
    
    def read(self) -> str:
        """Read the file content"""
        return self.content
    
    def write(self, content: str) -> None:
        """Write content to the file"""
        self.content = content
        self.metadata["size"] = len(content)
        self.metadata["modified"] += 1
    
    def append(self, content: str) -> None:
        """Append content to the file"""
        self.content += content
        self.metadata["size"] = len(self.content)
        self.metadata["modified"] += 1
    
    def accept(self, visitor: 'FileSystemVisitor') -> Any:
        """Accept a visitor"""
        return visitor.visit_file(self)


# Directory is a Composite in the Composite pattern
class Directory(FileSystemNode):
    """Represents a directory in the file system (Composite in Composite pattern)"""
    def __init__(self, name: str, parent: Optional['Directory'] = None):
        super().__init__(name)
        self.parent = parent
        self.children: Dict[str, Union[File, 'Directory']] = {}
        self.metadata["permissions"] = "rwxr-xr-x"
    
    def get_type(self) -> str:
        return "directory"
    
    def add_child(self, name: str, node: Union[File, 'Directory']) -> None:
        """Add a child node (file or directory) to this directory"""
        self.children[name] = node
        self.metadata["modified"] += 1
    
    def remove_child(self, name: str) -> None:
        """Remove a child node by name"""
        if name in self.children:
            del self.children[name]
            self.metadata["modified"] += 1
    
    def get_child(self, name: str) -> Optional[Union[File, 'Directory']]:
        """Get a child node by name"""
        return self.children.get(name)
    
    def list_children(self) -> List[str]:
        """List all children names"""
        return list(self.children.keys())
    
    def accept(self, visitor: 'FileSystemVisitor') -> Any:
        """Accept a visitor"""
        return visitor.visit_directory(self)


# > visitor pattern
class FileSystemVisitor(ABC):
    """Abstract visitor for file system nodes"""
    @abstractmethod
    def visit_file(self, file: File) -> Any:
        pass
    
    @abstractmethod
    def visit_directory(self, directory: Directory) -> Any:
        pass


class FindVisitor(FileSystemVisitor):
    """Visitor that finds nodes matching a pattern"""
    def __init__(self, name_pattern: str = None):
        self.name_pattern = name_pattern
        self.results = []
        self.current_path = ""
    
    def visit_file(self, file: File) -> None:
        """Visit a file node"""
        if self.name_pattern is None or self.name_pattern in file.name:
            self.results.append(f"{self.current_path}/{file.name}" if self.current_path else file.name)
    
    def visit_directory(self, directory: Directory) -> None:
        """Visit a directory node and its children"""
        if self.name_pattern is None or self.name_pattern in directory.name:
            self.results.append(f"{self.current_path}/{directory.name}" if self.current_path else directory.name)
        
        old_path = self.current_path
        self.current_path = f"{self.current_path}/{directory.name}" if self.current_path else directory.name
        
        for child_name, child in directory.children.items():
            child.accept(self)
        
        # restore path when going back up the tree
        self.current_path = old_path


class StatVisitor(FileSystemVisitor):
    """Visitor that collects node statistics"""
    def visit_file(self, file: File) -> Dict[str, Any]:
        """Visit a file node"""
        result = file.metadata.copy()
        result["name"] = file.name
        result["type"] = file.get_type()
        result["size"] = len(file.content)
        return result
    
    def visit_directory(self, directory: Directory) -> Dict[str, Any]:
        """Visit a directory node"""
        result = directory.metadata.copy()
        result["name"] = directory.name
        result["type"] = directory.get_type()
        return result

# > strategy pattern
# for path resolution
class PathStrategy(ABC):
    """Strategy for path resolution"""
    @abstractmethod
    def resolve_path(self, path: str, current_directory: Directory, root: Directory) -> List[str]:
        """Resolve a path to path components"""
        pass


class StandardPathStrategy(PathStrategy):
    """Standard path resolution strategy"""
    def resolve_path(self, path: str, current_directory: Directory, root: Directory) -> List[str]:
        """
        Resolve a path to path components
        
        Args:
            path: Path to resolve
            current_directory: Current working directory
            root: Root directory
            
        Returns:
            A tuple of (start_node, path_components)
        """
        if not path:
            return (current_directory, [])
            
        if path == "/":
            return (root, [])
            
        # remove trailing slash if present
        if path.endswith("/"):
            path = path[:-1]
            
        # absolute paths
        if path.startswith("/"):
            start_node = root
            path = path[1:]
        else:
            start_node = current_directory
            
        # split by '/' and filter empty parts
        path_components = [part for part in path.split("/") if part]
        
        return (start_node, path_components)


# > factory pattern
class FileSystemNodeFactory:
    """Factory for creating file system nodes"""
    @staticmethod
    def create_file(name: str, content: str = "") -> File:
        """Create a file"""
        return File(name, content)
    
    @staticmethod
    def create_directory(name: str, parent: Optional[Directory] = None) -> Directory:
        """Create a directory"""
        return Directory(name, parent)


# > command pattern
class Command(ABC):
    """Abstract command class"""
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command"""
        pass


class MkdirCommand(Command):
    """Command to create a directory"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> None:
        """Execute the command"""
        path_strategy = StandardPathStrategy()
        start_node, path_components = path_strategy.resolve_path(
            self.path, self.file_system.current_directory, self.file_system.root
        )
        
        if not path_components:
            raise ValueError("Cannot create directory with empty name")
        
        current = start_node
        
        # navigate to parent directory and create intermediate directories
        for i, part in enumerate(path_components[:-1]):
            if part == "..":
                if current.parent is not None:
                    current = current.parent
                continue
            elif part == ".":
                continue
                
            if part not in current.children:
                # create intermediate directories if they don't exist
                new_dir = FileSystemNodeFactory.create_directory(part, current)
                current.add_child(part, new_dir)
                current = new_dir
            else:
                child = current.children[part]
                if not isinstance(child, Directory):
                    raise NotADirectoryError(f"{'/'.join(path_components[:i+1])} is not a directory")
                current = child
                
        # create final directory
        final_name = path_components[-1]
        if final_name in current.children:
            raise FileExistsError(f"Directory {self.path} already exists")
            
        new_dir = FileSystemNodeFactory.create_directory(final_name, current)
        current.add_child(final_name, new_dir)


class CdCommand(Command):
    """Command to change directory"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> None:
        """Execute the command"""
        if self.path == "/":
            self.file_system.current_directory = self.file_system.root
            return
            
        node = self.file_system.get_node_at_path(self.path)
        
        if node is None:
            raise FileNotFoundError(f"Directory {self.path} not found")
            
        if not isinstance(node, Directory):
            raise NotADirectoryError(f"{self.path} is not a directory")
            
        self.file_system.current_directory = node


class LsCommand(Command):
    """Command to list directory contents"""
    def __init__(self, file_system: 'FileSystem', path: str = ""):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> List[str]:
        """Execute the command"""
        target = self.file_system.current_directory
        
        if self.path:
            target = self.file_system.get_node_at_path(self.path)
            
        if target is None:
            raise FileNotFoundError(f"Directory {self.path} not found")
            
        if not isinstance(target, Directory):
            raise NotADirectoryError(f"{self.path} is not a directory")
            
        return target.list_children()


class CreateFileCommand(Command):
    """Command to create a file"""
    def __init__(self, file_system: 'FileSystem', path: str, content: str = ""):
        self.file_system = file_system
        self.path = path
        self.content = content
    
    def execute(self) -> None:
        """Execute the command"""
        path_strategy = StandardPathStrategy()
        start_node, path_components = path_strategy.resolve_path(
            self.path, self.file_system.current_directory, self.file_system.root
        )
        
        if not path_components:
            raise ValueError("Cannot create file with empty name")
        
        current = start_node
        
        # navigate to parent directory
        for i, part in enumerate(path_components[:-1]):
            if part == "..":
                if current.parent is not None:
                    current = current.parent
                continue
            elif part == ".":
                continue
                
            if part not in current.children:
                # create intermediate directories
                new_dir = FileSystemNodeFactory.create_directory(part, current)
                current.add_child(part, new_dir)
                current = new_dir
            else:
                child = current.children[part]
                if not isinstance(child, Directory):
                    raise NotADirectoryError(f"{'/'.join(path_components[:i+1])} is not a directory")
                current = child
                
        # create file
        final_name = path_components[-1]
        if final_name in current.children:
            raise FileExistsError(f"File {self.path} already exists")
            
        new_file = FileSystemNodeFactory.create_file(final_name, self.content)
        current.add_child(final_name, new_file)


class ReadFileCommand(Command):
    """Command to read a file"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> str:
        """Execute the command"""
        node = self.file_system.get_node_at_path(self.path)
        
        if node is None:
            raise FileNotFoundError(f"File {self.path} not found")
            
        if isinstance(node, Directory):
            raise IsADirectoryError(f"{self.path} is a directory, not a file")
            
        return node.read()


class WriteFileCommand(Command):
    """Command to write to a file"""
    def __init__(self, file_system: 'FileSystem', path: str, content: str):
        self.file_system = file_system
        self.path = path
        self.content = content
    
    def execute(self) -> None:
        """Execute the command"""
        node = self.file_system.get_node_at_path(self.path)
        
        if node is None:
            # create the file if it doesn't exist
            create_cmd = CreateFileCommand(self.file_system, self.path, self.content)
            try:
                create_cmd.execute()
            except (FileExistsError, NotADirectoryError) as e:
                raise e
        elif isinstance(node, Directory):
            raise IsADirectoryError(f"{self.path} is a directory, not a file")
        else:
            node.write(self.content)


class DeleteCommand(Command):
    """Command to delete a file or directory"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> None:
        """Execute the command"""
        # can't delete root!
        if self.path == "/" or self.path == "":
            raise PermissionError("Cannot delete the root directory")
            
        path_strategy = StandardPathStrategy()
        start_node, path_components = path_strategy.resolve_path(
            self.path, self.file_system.current_directory, self.file_system.root
        )
        
        if not path_components:
            raise ValueError("Invalid path")
            
        # get parent directory
        if len(path_components) == 1:
            parent = start_node
            node_name = path_components[0]
        else:
            # traverse to parent
            current = start_node
            for part in path_components[:-1]:
                if part == "..":
                    if current.parent is not None:
                        current = current.parent
                    continue
                elif part == ".":
                    continue
                
                if part not in current.children:
                    raise FileNotFoundError(f"Parent directory for {self.path} not found")
                
                child = current.children[part]
                if not isinstance(child, Directory):
                    raise NotADirectoryError(f"Part of path {part} is not a directory")
                
                current = child
            
            parent = current
            node_name = path_components[-1]
                
        if node_name not in parent.children:
            raise FileNotFoundError(f"{self.path} not found")
            
        # remove node
        parent.remove_child(node_name)


class FindCommand(Command):
    """Command to find files/directories matching a pattern"""
    def __init__(self, file_system: 'FileSystem', path: str, name_pattern: str = None):
        self.file_system = file_system
        self.path = path
        self.name_pattern = name_pattern
    
    def execute(self) -> List[str]:
        """Execute the command"""
        start_node = self.file_system.get_node_at_path(self.path)
        if start_node is None:
            raise FileNotFoundError(f"Directory {self.path} not found")
            
        if not isinstance(start_node, Directory):
            raise NotADirectoryError(f"{self.path} is not a directory")
            
        # use visitor pattern to find matching nodes
        visitor = FindVisitor(self.name_pattern)
        start_node.accept(visitor)
        
        return visitor.results


class PwdCommand(Command):
    """Command to print working directory"""
    def __init__(self, file_system: 'FileSystem'):
        self.file_system = file_system
    
    def execute(self) -> str:
        """Execute the command"""
        path_components = []
        current = self.file_system.current_directory
        
        while current != self.file_system.root:
            path_components.append(current.name)
            current = current.parent
            
        if not path_components:
            return "/"
        else:
            return "/" + "/".join(reversed(path_components))


class TouchCommand(Command):
    """Command to create an empty file or update timestamps"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> None:
        """Execute the command"""
        node = self.file_system.get_node_at_path(self.path)
        
        if node is None:
            # create file if it doesn't exist
            create_cmd = CreateFileCommand(self.file_system, self.path, "")
            try:
                create_cmd.execute()
            except NotADirectoryError as e:
                raise e
        elif isinstance(node, Directory):
            raise IsADirectoryError(f"{self.path} is a directory")
        else:
            # update timestamps only
            node.metadata["modified"] += 1


class ChmodCommand(Command):
    """Command to change permissions"""
    def __init__(self, file_system: 'FileSystem', path: str, permissions: str):
        self.file_system = file_system
        self.path = path
        self.permissions = permissions
    
    def execute(self) -> None:
        """Execute the command"""
        # validate permissions format (simplified)
        if not (len(self.permissions) == 9 and 
                all(c in "rwx-" for c in self.permissions)):
            raise ValueError("Invalid permissions format. Should be like 'rw-r--r--'")
            
        node = self.file_system.get_node_at_path(self.path)
        if node is None:
            raise FileNotFoundError(f"{self.path} not found")
            
        node.metadata["permissions"] = self.permissions


class StatCommand(Command):
    """Command to get file/directory metadata"""
    def __init__(self, file_system: 'FileSystem', path: str):
        self.file_system = file_system
        self.path = path
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command"""
        node = self.file_system.get_node_at_path(self.path)
        if node is None:
            raise FileNotFoundError(f"{self.path} not found")
            
        # use visitor pattern to get statistics
        visitor = StatVisitor()
        return node.accept(visitor)


# > singleton pattern
# for FileSystem
class Singleton(type):
    """Metaclass for implementing the Singleton pattern"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FileSystem(metaclass=Singleton):
    """File system implementation with design patterns"""
    def __init__(self):
        """Initialize the file system"""
        self.root = FileSystemNodeFactory.create_directory("root", None)
        self.current_directory = self.root
        self._initialize_standard_directories()
        self.path_strategy = StandardPathStrategy()
    
    def _initialize_standard_directories(self) -> None:
        """Create standard directories like /bin, /etc, /home"""
        standard_dirs = ["bin", "etc", "home", "tmp", "var"]
        for dir_name in standard_dirs:
            self.mkdir(dir_name)
    
    def execute_command(self, command: Command) -> Any:
        """Execute a command"""
        return command.execute()
    
    def get_node_at_path(self, path: str) -> Optional[Union[File, Directory]]:
        """Get the node (file or directory) at the specified path"""
        start_node, path_components = self.path_strategy.resolve_path(
            path, self.current_directory, self.root
        )
        
        # empty path components means current directory or root
        if not path_components:
            return start_node
            
        # navigate through path components
        current = start_node
        for part in path_components:
            if part == "..":
                if current.parent is not None:
                    current = current.parent
            elif part == ".":
                continue
            else:
                if part not in current.children:
                    return None
                    
                current = current.children[part]
                
                # if we hit file before the end of the path, it's an error
                if isinstance(current, File) and part != path_components[-1]:
                    return None
                    
        return current
    
    # convenience methods that use the Command pattern internally
    def mkdir(self, path: str) -> None:
        """Create a new directory"""
        command = MkdirCommand(self, path)
        self.execute_command(command)
    
    def cd(self, path: str) -> None:
        """Change current directory"""
        command = CdCommand(self, path)
        self.execute_command(command)
    
    def ls(self, path: str = "") -> List[str]:
        """List contents of a directory"""
        command = LsCommand(self, path)
        return self.execute_command(command)
    
    def create_file(self, path: str, content: str = "") -> None:
        """Create a new file"""
        command = CreateFileCommand(self, path, content)
        self.execute_command(command)
    
    def read_file(self, path: str) -> str:
        """Read file content"""
        command = ReadFileCommand(self, path)
        return self.execute_command(command)
    
    def write_file(self, path: str, content: str) -> None:
        """Write content to a file"""
        command = WriteFileCommand(self, path, content)
        self.execute_command(command)
    
    def delete(self, path: str) -> None:
        """Delete a file or directory"""
        command = DeleteCommand(self, path)
        self.execute_command(command)
    
    def append_to_file(self, path: str, content: str) -> None:
        """Append content to a file"""
        # first read existing content ..
        try:
            existing_content = self.read_file(path)
            # .. then write combined content
            self.write_file(path, existing_content + content)
        except FileNotFoundError:
            # if file doesn't exist, create it
            self.create_file(path, content)
    
    def find(self, path: str, name_pattern: str = None) -> List[str]:
        """Find files/directories matching a pattern"""
        command = FindCommand(self, path, name_pattern)
        return self.execute_command(command)
    
    def pwd(self) -> str:
        """Get current working directory path"""
        command = PwdCommand(self)
        return self.execute_command(command)
    
    def touch(self, path: str) -> None:
        """Create an empty file or update timestamps if file exists"""
        command = TouchCommand(self, path)
        self.execute_command(command)
    
    def chmod(self, path: str, permissions: str) -> None:
        """Change file/directory permissions"""
        command = ChmodCommand(self, path, permissions)
        self.execute_command(command)
    
    def stat(self, path: str) -> Dict[str, Any]:
        """Get file/directory metadata"""
        command = StatCommand(self, path)
        return self.execute_command(command)
    
    def rename(self, src_path: str, dst_path: str) -> None:
        """Rename or move a file or directory"""
        # method is more complex, so we'll implement it directly
        # can't rename/move root
        if src_path == "/" or src_path == "":
            raise PermissionError("Cannot rename or move the root directory")
            
        src_node = self.get_node_at_path(src_path)
        if src_node is None:
            raise FileNotFoundError(f"{src_path} not found")
            
        # check if destination exists
        dst_node = self.get_node_at_path(dst_path)
        if dst_node is not None:
            raise FileExistsError(f"{dst_path} already exists")
            
        # get source parent and path components
        src_start, src_components = self.path_strategy.resolve_path(
            src_path, self.current_directory, self.root
        )
        
        # get destination parent and path components
        dst_start, dst_components = self.path_strategy.resolve_path(
            dst_path, self.current_directory, self.root
        )
        
        # navigate to source parent
        src_parent = src_start
        for part in src_components[:-1]:
            if part == "..":
                if src_parent.parent is not None:
                    src_parent = src_parent.parent
                continue
            elif part == ".":
                continue
            else:
                src_parent = src_parent.children[part]
        
        src_name = src_components[-1]
        
        # navigate or create destination parent
        dst_parent = dst_start
        for i, part in enumerate(dst_components[:-1]):
            if part == "..":
                if dst_parent.parent is not None:
                    dst_parent = dst_parent.parent
                continue
            elif part == ".":
                continue
            else:
                if part not in dst_parent.children:
                    # create intermediate directories
                    new_dir = FileSystemNodeFactory.create_directory(part, dst_parent)
                    dst_parent.add_child(part, new_dir)
                    dst_parent = new_dir
                else:
                    child = dst_parent.children[part]
                    if not isinstance(child, Directory):
                        raise NotADirectoryError(f"Part of destination path is not a directory")
                    dst_parent = child
        
        dst_name = dst_components[-1]
        
        # move node
        src_node.name = dst_name
        if isinstance(src_node, Directory):
            src_node.parent = dst_parent
            
        dst_parent.add_child(dst_name, src_node)
        src_parent.remove_child(src_name)
    
    def copy(self, src_path: str, dst_path: str) -> None:
        """Copy a file or directory"""
        # method uses a recursive helper, so we'll implement it directly
        src_node = self.get_node_at_path(src_path)
        if src_node is None:
            raise FileNotFoundError(f"{src_path} not found")
            
        # check if destination exists
        dst_node = self.get_node_at_path(dst_path)
        if dst_node is not None:
            raise FileExistsError(f"{dst_path} already exists")
            
        # get destination parent and path components
        dst_start, dst_components = self.path_strategy.resolve_path(
            dst_path, self.current_directory, self.root
        )
        
        # navigate or create destination parent
        dst_parent = dst_start
        for i, part in enumerate(dst_components[:-1]):
            if part == "..":
                if dst_parent.parent is not None:
                    dst_parent = dst_parent.parent
                continue
            elif part == ".":
                continue
            else:
                if part not in dst_parent.children:
                    # create intermediate directories
                    new_dir = FileSystemNodeFactory.create_directory(part, dst_parent)
                    dst_parent.add_child(part, new_dir)
                    dst_parent = new_dir
                else:
                    child = dst_parent.children[part]
                    if not isinstance(child, Directory):
                        raise NotADirectoryError(f"Part of destination path is not a directory")
                    dst_parent = child
        
        dst_name = dst_components[-1]
        
        # copy node
        if isinstance(src_node, File):
            new_file = FileSystemNodeFactory.create_file(dst_name, src_node.content)
            dst_parent.add_child(dst_name, new_file)
        else:  # directory
            # create new directory
            new_dir = FileSystemNodeFactory.create_directory(dst_name, dst_parent)
            dst_parent.add_child(dst_name, new_dir)
            
            # recursively copy children
            for child_name, child_node in src_node.children.items():
                if isinstance(child_node, File):
                    new_child = FileSystemNodeFactory.create_file(child_name, child_node.content)
                    new_dir.add_child(child_name, new_child)
                else:  # directory
                    self._copy_directory_recursive(child_node, new_dir, child_name)
    
    def _copy_directory_recursive(self, src_dir: Directory, dst_parent: Directory, dst_name: str) -> None:
        """Helper method for recursive directory copying"""
        new_dir = FileSystemNodeFactory.create_directory(dst_name, dst_parent)
        dst_parent.add_child(dst_name, new_dir)
        
        for child_name, child_node in src_dir.children.items():
            if isinstance(child_node, File):
                new_child = FileSystemNodeFactory.create_file(child_name, child_node.content)
                new_dir.add_child(child_name, new_child)
            else:  # directory
                self._copy_directory_recursive(child_node, new_dir, child_name)


# command interface for the file system
def run_command_interface():
    fs = FileSystem()
    print("Welcome to the File System (fs)")
    print("Type 'help' for available commands or 'exit' to quit")
    
    while True:
        # get current directory for prompt
        current_path = fs.pwd()
        command = input(f"{current_path}> ").strip()
        
        if not command:
            continue
            
        # split command and arguments
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            if cmd == "exit" or cmd == "quit" or cmd == "bye":
                print("Goodbye!")
                break
                
            elif cmd == "help":
                print("Available commands:")
                print("  mkdir <path>               - Create a directory")
                print("  cd <path>                  - Change directory")
                print("  ls [path]                  - List directory contents")
                print("  cat <path>                 - Display file contents")
                print("  touch <path>               - Create empty file or update timestamp")
                print("  write <path> <content>     - Write content to file")
                print("  append <path> <content>    - Append content to file")
                print("  rm <path>                  - Delete file or directory")
                print("  find <path> [pattern]      - Find files/dirs matching pattern")
                print("  pwd                        - Print working directory")
                print("  chmod <path> <permissions> - Change permissions")
                print("  stat <path>                - Show file/directory info")
                print("  mv <src> <dst>             - Move/rename file or directory")
                print("  cp <src> <dst>             - Copy file or directory")
                print("  help                       - Show this help")
                print("  exit/quit/bye              - Exit the program")
                
            elif cmd == "mkdir":
                if not args:
                    print("Error: mkdir requires a path argument")
                else:
                    fs.mkdir(args[0])
                    print(f"Created directory: {args[0]}")
                    
            elif cmd == "cd":
                if not args:
                    print("Error: cd requires a path argument")
                else:
                    fs.cd(args[0])
                    
            elif cmd == "ls":
                path = args[0] if args else ""
                items = fs.ls(path)
                if items:
                    for item in items:
                        node = fs.get_node_at_path(f"{path}/{item}" if path else item)
                        if isinstance(node, Directory):
                            print(f"{item}/")
                        else:
                            print(item)
                else:
                    print("(empty directory)")
                    
            elif cmd == "cat":
                if not args:
                    print("Error: cat requires a file path")
                else:
                    content = fs.read_file(args[0])
                    print(content)
                    
            elif cmd == "touch":
                if not args:
                    print("Error: touch requires a path argument")
                else:
                    fs.touch(args[0])
                    print(f"Touched: {args[0]}")
                    
            elif cmd == "write":
                if len(args) < 2:
                    print("Error: write requires a file path and content")
                else:
                    path = args[0]
                    content = " ".join(args[1:])
                    fs.write_file(path, content)
                    print(f"Wrote to file: {path}")
                    
            elif cmd == "append":
                if len(args) < 2:
                    print("Error: append requires a file path and content")
                else:
                    path = args[0]
                    content = " ".join(args[1:])
                    fs.append_to_file(path, content)
                    print(f"Appended to file: {path}")
                    
            elif cmd == "rm":
                if not args:
                    print("Error: rm requires a path argument")
                else:
                    fs.delete(args[0])
                    print(f"Deleted: {args[0]}")
                    
            elif cmd == "find":
                if not args:
                    print("Error: find requires a path argument")
                else:
                    pattern = args[1] if len(args) > 1 else None
                    results = fs.find(args[0], pattern)
                    if results:
                        for result in results:
                            print(result)
                    else:
                        print("No matching files found")
                        
            elif cmd == "pwd":
                print(fs.pwd())
                
            elif cmd == "chmod":
                if len(args) < 2:
                    print("Error: chmod requires a path and permissions")
                else:
                    fs.chmod(args[0], args[1])
                    print(f"Changed permissions for {args[0]}")
                    
            elif cmd == "stat":
                if not args:
                    print("Error: stat requires a path argument")
                else:
                    info = fs.stat(args[0])
                    for key, value in info.items():
                        print(f"{key}: {value}")
                        
            elif cmd == "mv":
                if len(args) < 2:
                    print("Error: mv requires source and destination paths")
                else:
                    fs.rename(args[0], args[1])
                    print(f"Moved/renamed: {args[0]} → {args[1]}")
                    
            elif cmd == "cp":
                if len(args) < 2:
                    print("Error: cp requires source and destination paths")
                else:
                    fs.copy(args[0], args[1])
                    print(f"Copied: {args[0]} → {args[1]}")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Run automated demo first
    fs = FileSystem()
    
    print("-- prepopulate demo --")
    # Create some directories and files
    fs.mkdir("/home/user")
    fs.cd("/home/user")
    
    # Create some files
    fs.create_file("hello.txt", "Hello, World!")
    fs.create_file("notes.md", "# My Notes\n\nThis is a markdown file.")
    
    # Create a project directory with some code
    fs.mkdir("project")
    fs.cd("project")
    fs.create_file("main.py", "def main():\n    print('Hello from the virtual file system!')\n\nif __name__ == '__main__':\n    main()")
    
    # List files in the current directory
    print(f"Files in {fs.pwd()}: {fs.ls()}")
    
    # Read file content
    print("Content of main.py:")
    print(fs.read_file("main.py"))
    
    # Go back to home directory for interactive session
    fs.cd("/")
    
    print("The file system has been pre-populated with some files in /home/user/")
    print("\n-- end demo --\n")

    # Start interactive command line interface
    run_command_interface()
