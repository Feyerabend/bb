
from typing import Dict, Any, List, Optional, Protocol #, Callable


class Command(Protocol):
    def execute(self, manager: "BankManager") -> Any:
        ...

class Memento:
    def __init__(self, bank: str, return_pc: int = 0):
        self.bank = bank
        self.return_pc = return_pc

class SharedRAM:
    def __init__(self):
        self.memory: Dict[int, Any] = {}
        self.call_stack: List[Memento] = []
        self.param_stack: List[Any] = []
        self.output_buffer: List[str] = []
        
    def push_params(self, *args):
        self.param_stack.extend(args)
        
    def pop_params(self, count=1):
        if len(self.param_stack) < count:
            raise ValueError("Not enough parameters on stack")
        return [self.param_stack.pop() for _ in range(count)]
        
    def log(self, message: str):
        self.output_buffer.append(message)

class Bank:
    def __init__(self, name: str):
        self.name = name
        self.commands: Dict[int, Command] = {}
        
    def register(self, fid: int):
        def decorator(cmd: Command):
            self.commands[fid] = cmd
            return cmd
        return decorator

class BankManager:
    def __init__(self):
        self.banks: Dict[str, Bank] = {}
        self.ram = SharedRAM()
        self.current_bank: Optional[str] = None
        
    def add_bank(self, bank: Bank):
        self.banks[bank.name] = bank
        
    def call(self, target_bank: str, fid: int, *args):
        if target_bank not in self.banks:
            raise ValueError(f"Bank {target_bank} not found")
            
        if self.current_bank:
            self.ram.call_stack.append(Memento(self.current_bank))
            
        self.current_bank = target_bank
        self.ram.push_params(*args)
        
        try:
            command = self.banks[target_bank].commands[fid]
            result = command.execute(self)
            self.ram.log(f"{target_bank}: Function {fid} completed")
            return result
        except Exception as e:
            self.ram.log(f"ERROR in {target_bank}: {str(e)}")
            raise
        finally:
            if self.ram.call_stack and self.current_bank == target_bank:
                self.ret()

    def ret(self, value: Any = None):
        if not self.ram.call_stack:
            raise RuntimeError("Nothing to return to")
            
        memento = self.ram.call_stack.pop()
        self.current_bank = memento.bank
        if value is not None:
            self.ram.push_params(value)
        self.ram.log(f"Returned to {self.current_bank}")



class AddCommand:
    def execute(self, manager: BankManager) -> Any:
        a, b = manager.ram.pop_params(2)
        result = a + b
        manager.ram.push_params(result)
        manager.ram.log(f"ADD: {a} + {b} = {result}")
        return result

class MultiplyCommand:
    def execute(self, manager: BankManager) -> Any:
        a, b = manager.ram.pop_params(2)
        result = a * b
        manager.ram.push_params(result)
        manager.ram.log(f"MULT: {a} * {b} = {result}")
        return result

class ConcatCommand:
    def execute(self, manager: BankManager) -> Any:
        s1, s2 = manager.ram.pop_params(2)
        result = s1 + s2
        manager.ram.push_params(result)
        manager.ram.log(f"CONCAT: '{s1}' + '{s2}' = '{result}'")
        return result

class ReverseCommand:
    def execute(self, manager: BankManager) -> Any:
        s, = manager.ram.pop_params(1)
        result = s[::-1]
        manager.ram.push_params(result)
        manager.ram.log(f"REVERSE: '{s}' -> '{result}'")
        return result

class MainCommand:
    def execute(self, manager: BankManager) -> Any:
        manager.ram.log("MAIN: Starting program")
        
        manager.call("MATH", 1, 5, 3)
        manager.call("MATH", 2, 4, 6)
        manager.call("STRINGS", 1, "Hello", "World")
        manager.call("STRINGS", 2, "Python")
        
        manager.ram.log("MAIN: Program complete")
        return 0



def create_math_bank():
    bank = Bank("MATH")
    bank.register(1)(AddCommand())
    bank.register(2)(MultiplyCommand())
    return bank

def create_string_bank():
    bank = Bank("STRINGS")
    bank.register(1)(ConcatCommand())
    bank.register(2)(ReverseCommand())
    return bank

def create_main_bank():
    bank = Bank("MAIN")
    bank.register(0)(MainCommand())
    return bank



def run_simulation():
    manager = BankManager()
    manager.add_bank(create_main_bank())
    manager.add_bank(create_math_bank())
    manager.add_bank(create_string_bank())
    
    manager.current_bank = "MAIN"
    try:
        manager.call("MAIN", 0)
    except Exception as e:
        print(f"Simulation ended with error: {e}")
    
    print("\nExecution Log:")
    print("\n".join(manager.ram.output_buffer))
    
    print("\nFinal State:")
    print(f"Current Bank: {manager.current_bank}")
    print(f"Param Stack: {manager.ram.param_stack}")
    print(f"Call Stack Depth: {len(manager.ram.call_stack)}")

if __name__ == "__main__":
    run_simulation()
