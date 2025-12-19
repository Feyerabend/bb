#!/usr/bin/env python3
"""
Line Editor with Command Pattern Implementation
Features:
- Edit, add, delete lines
- Save/load text files
- Undo/redo functionality
- Search/replace operations
"""
from abc import ABC, abstractmethod
import os
import re
from typing import Optional # List


class Command(ABC):
    
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass


class EditorBuffer:
    
    def __init__(self):
        self.lines = [""]
        self.filename = None
    
    def get_line(self, line_num: int) -> str:
        if 0 <= line_num < len(self.lines):
            return self.lines[line_num]
        return ""
    
    def set_line(self, line_num: int, text: str) -> None:
        if 0 <= line_num < len(self.lines):
            self.lines[line_num] = text
        elif line_num == len(self.lines):  # Append new line
            self.lines.append(text)
    
    def insert_line(self, line_num: int, text: str) -> None:
        if 0 <= line_num <= len(self.lines):
            self.lines.insert(line_num, text)
    
    def delete_line(self, line_num: int) -> str:
        if 0 <= line_num < len(self.lines):
            return self.lines.pop(line_num)
        return ""
    
    def line_count(self) -> int:
        return len(self.lines)
    
    def load_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r') as file:
                self.lines = file.read().splitlines()
                if not self.lines:  # empty files
                    self.lines = [""]
                self.filename = filename
                return True
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return False
    
    def save_file(self, filename: Optional[str] = None) -> bool:
        if filename:
            self.filename = filename
        
        if not self.filename:
            print("No filename specified")
            return False
        
        try:
            with open(self.filename, 'w') as file:
                file.write('\n'.join(self.lines))
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    def get_all_text(self) -> str:
        return '\n'.join(self.lines)


# Command classes
class InsertLineCommand(Command):
    
    def __init__(self, buffer: EditorBuffer, line_num: int, text: str):
        self.buffer = buffer
        self.line_num = line_num
        self.text = text
    
    def execute(self) -> None:
        self.buffer.insert_line(self.line_num, self.text)
    
    def undo(self) -> None:
        self.buffer.delete_line(self.line_num)


class DeleteLineCommand(Command):
    
    def __init__(self, buffer: EditorBuffer, line_num: int):
        self.buffer = buffer
        self.line_num = line_num
        self.deleted_text = None
    
    def execute(self) -> None:
        self.deleted_text = self.buffer.delete_line(self.line_num)
    
    def undo(self) -> None:
        if self.deleted_text is not None:
            self.buffer.insert_line(self.line_num, self.deleted_text)


class ModifyLineCommand(Command):
    
    def __init__(self, buffer: EditorBuffer, line_num: int, new_text: str):
        self.buffer = buffer
        self.line_num = line_num
        self.new_text = new_text
        self.old_text = None
    
    def execute(self) -> None:
        self.old_text = self.buffer.get_line(self.line_num)
        self.buffer.set_line(self.line_num, self.new_text)
    
    def undo(self) -> None:
        if self.old_text is not None:
            self.buffer.set_line(self.line_num, self.old_text)


class SearchReplaceCommand(Command):
    
    def __init__(self, buffer: EditorBuffer, search_str: str, replace_str: str, 
                 line_range: tuple = None, case_sensitive: bool = False):
        self.buffer = buffer
        self.search_str = search_str
        self.replace_str = replace_str
        self.line_range = line_range or (0, self.buffer.line_count())
        self.case_sensitive = case_sensitive
        self.modifications = []  # store (line_num, old_text) pairs
    
    def execute(self) -> None:
        start, end = self.line_range
        end = min(end, self.buffer.line_count())
        
        flags = 0 if self.case_sensitive else re.IGNORECASE
        
        for i in range(start, end):
            line = self.buffer.get_line(i)
            new_line = re.sub(self.search_str, self.replace_str, line, flags=flags)
            
            if new_line != line:
                self.modifications.append((i, line))
                self.buffer.set_line(i, new_line)
    
    def undo(self) -> None:
        for line_num, old_text in self.modifications:
            self.buffer.set_line(line_num, old_text)


class CommandHistory:
    
    def __init__(self):
        self.history = []
        self.position = -1
    
    def execute_command(self, command: Command) -> None:
        # remove any forward history if we're in the middle
        if self.position < len(self.history) - 1:
            self.history = self.history[:self.position + 1]
        
        command.execute()
        self.history.append(command)
        self.position += 1
    
    def undo(self) -> bool:
        if self.position >= 0:
            self.history[self.position].undo()
            self.position -= 1
            return True
        return False
    
    def redo(self) -> bool:
        if self.position < len(self.history) - 1:
            self.position += 1
            self.history[self.position].execute()
            return True
        return False
    
    def can_undo(self) -> bool:
        return self.position >= 0
    
    def can_redo(self) -> bool:
        return self.position < len(self.history) - 1


class LineEditor:
    
    def __init__(self):
        self.buffer = EditorBuffer()
        self.command_history = CommandHistory()
        self.running = True
        self.clipboard = ""
        self.current_line = 0
    
    def run(self) -> None:
        print("Line Editor started. Type 'help' for commands")
        
        while self.running:
            try:
                command = input(f"{self.current_line}> ").strip()
                if not command:
                    continue
                
                self.process_command(command)
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def process_command(self, command_str: str) -> None:
        parts = command_str.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "n" or cmd == "next":
            self.next_line()
        elif cmd == "p" or cmd == "prev":
            self.prev_line()
        elif cmd == "g" or cmd == "goto":
            try:
                line_num = int(args)
                self.goto_line(line_num)
            except ValueError:
                print("Invalid line number")
        
        elif cmd == "i" or cmd == "insert":
            self.insert_line(args)
        elif cmd == "a" or cmd == "append":
            self.append_line(args)
        elif cmd == "e" or cmd == "edit":
            self.edit_line(args)
        elif cmd == "d" or cmd == "delete":
            self.delete_line()
        elif cmd == "sr" or cmd == "replace":
            self.search_replace(args)
        
        elif cmd == "load":
            self.load_file(args)
        elif cmd == "save":
            self.save_file(args)
        
        elif cmd == "undo":
            self.undo()
        elif cmd == "redo":
            self.redo()
        
        elif cmd == "copy":
            self.copy_line()
        elif cmd == "paste":
            self.paste_line()
        
        elif cmd == "l" or cmd == "list":
            self.list_lines(args)
        elif cmd == "s" or cmd == "show":
            self.show_current_line()
        
        elif cmd == "help":
            self.show_help()
        elif cmd == "quit" or cmd == "exit":
            self.running = False
        else:
            print(f"Unknown command: {cmd}")
    
    def next_line(self) -> None:
        if self.current_line < self.buffer.line_count() - 1:
            self.current_line += 1
            self.show_current_line()
    
    def prev_line(self) -> None:
        if self.current_line > 0:
            self.current_line -= 1
            self.show_current_line()
    
    def goto_line(self, line_num: int) -> None:
        if 0 <= line_num < self.buffer.line_count():
            self.current_line = line_num
            self.show_current_line()
        else:
            print(f"Line number out of range (0-{self.buffer.line_count()-1})")
    
    def insert_line(self, text: str) -> None:
        command = InsertLineCommand(self.buffer, self.current_line, text)
        self.command_history.execute_command(command)
        self.next_line()
    
    def append_line(self, text: str) -> None:
        command = InsertLineCommand(self.buffer, self.current_line + 1, text)
        self.command_history.execute_command(command)
        self.next_line()
    
    def edit_line(self, text: str) -> None:
        if not text:
            # if no text provided, get interactively
            current = self.buffer.get_line(self.current_line)
            print(f"Current: {current}")
            text = input("New text: ")
            if not text:  # user cancelled
                return
        
        command = ModifyLineCommand(self.buffer, self.current_line, text)
        self.command_history.execute_command(command)
        self.show_current_line()
    
    def delete_line(self) -> None:
        if self.buffer.line_count() > 1:  # keep at least one line
            command = DeleteLineCommand(self.buffer, self.current_line)
            self.command_history.execute_command(command)
            
            # if we deleted the last line, move up
            if self.current_line >= self.buffer.line_count():
                self.current_line = self.buffer.line_count() - 1
            
            self.show_current_line()
        else:
            print("Cannot delete the only line")
    
    def search_replace(self, args: str) -> None:
        parts = args.split(' ')
        if len(parts) < 2:
            print("Usage: sr search_text replacement_text [i]")
            return
        
        search_str = parts[0]
        replace_str = parts[1]
        case_sensitive = 'i' not in parts[2:] if len(parts) > 2 else False
        
        command = SearchReplaceCommand(self.buffer, search_str, replace_str, 
                                     (0, self.buffer.line_count()), 
                                     case_sensitive=case_sensitive)
        self.command_history.execute_command(command)
        print("Search and replace completed")
    
    def load_file(self, filename: str) -> None:
        if not filename:
            filename = input("Enter filename to load: ")
        
        if os.path.exists(filename):
            if self.buffer.load_file(filename):
                self.current_line = 0
                print(f"Loaded {filename} ({self.buffer.line_count()} lines)")
        else:
            print(f"File not found: {filename}")
    
    def save_file(self, filename: str) -> None:
        if not filename and not self.buffer.filename:
            filename = input("Enter filename to save: ")
        
        if self.buffer.save_file(filename):
            print(f"Saved to {self.buffer.filename}")
    
    def undo(self) -> None:
        if self.command_history.undo():
            print("Undo successful")
            self.show_current_line()
        else:
            print("Nothing to undo")
    
    def redo(self) -> None:
        if self.command_history.redo():
            print("Redo successful")
            self.show_current_line()
        else:
            print("Nothing to redo")
    
    def copy_line(self) -> None:
        self.clipboard = self.buffer.get_line(self.current_line)
        print("Line copied to clipboard")
    
    def paste_line(self) -> None:
        if self.clipboard:
            command = InsertLineCommand(self.buffer, self.current_line + 1, self.clipboard)
            self.command_history.execute_command(command)
            self.current_line += 1
            self.show_current_line()
        else:
            print("Clipboard is empty")
    
    def list_lines(self, args: str) -> None:
        start = max(0, self.current_line - 3)
        end = min(self.buffer.line_count(), self.current_line + 4)
        
        if args:
            try:
                parts = args.split('-')
                if len(parts) == 1:
                    count = int(parts[0])
                    start = max(0, self.current_line)
                    end = min(self.buffer.line_count(), start + count)
                else:
                    start = max(0, int(parts[0]))
                    end = min(self.buffer.line_count(), int(parts[1]) + 1)
            except ValueError:
                print("Invalid range format. Use: list [start-end] or [count]")
        
        for i in range(start, end):
            marker = ">" if i == self.current_line else " "
            print(f"{marker} {i}: {self.buffer.get_line(i)}")
    
    def show_current_line(self) -> None:
        print(f"{self.current_line}: {self.buffer.get_line(self.current_line)}")
    
    def show_help(self) -> None:
        help_text = """
Line Editor Commands:
--------------------
Navigation:
  n, next          - Move to the next line
  p, prev          - Move to the previous line
  g, goto <line>   - Go to specified line number

Editing:
  i, insert <text> - Insert text at current line
  a, append <text> - Append text after current line
  e, edit [text]   - Edit current line (prompt if no text given)
  d, delete        - Delete current line
  sr <old> <new>   - Search and replace text (add 'i' for case insensitive)

File Operations:
  load <file>      - Load file
  save [file]      - Save to file (use current filename if not specified)

History:
  undo             - Undo last command
  redo             - Redo last undone command

Clipboard:
  copy             - Copy current line to clipboard
  paste            - Paste clipboard after current line

Display:
  l, list [range]  - List lines (default: around current)
  s, show          - Show current line

Misc:
  help             - Show this help
  quit, exit       - Exit the editor
"""
        print(help_text)


if __name__ == "__main__":
    editor = LineEditor()
    editor.run()
