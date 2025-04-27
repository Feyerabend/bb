from typing import Dict, Any, List, Optional, Callable

# ============================
# Shared RAM Simulation
# ============================
class SharedRAM:
    """Simulates shared memory with call stack and parameters"""
    def __init__(self):
        self.memory: Dict[int, Any] = {}  # Shared memory
        self.call_stack: List[Dict] = []  # Stack for saving context
        self.param_stack: List[Any] = []  # Stack for function parameters
        self.output_buffer: List[str] = []  # Log output
    
    def push_params(self, *args):
        """Push parameters onto the shared RAM stack"""
        self.param_stack.extend(args)
        
    def pop_params(self, count=1):
        """Pop parameters from the shared RAM stack"""
        if len(self.param_stack) < count:
            raise ValueError("Not enough parameters on stack")
        return [self.param_stack.pop() for _ in range(count)]
        
    def log(self, message: str):
        """Log messages into the output buffer"""
        self.output_buffer.append(message)

# ============================
# Bank Simulation (ROM Bank)
# ============================
class Bank:
    """Represents a ROM bank with functions"""
    def __init__(self, name: str):
        self.name = name
        self.functions: Dict[int, Callable] = {}  # Function ID -> Function

    def register(self, fid: int):
        """Decorator to register functions in the bank"""
        def decorator(func: Callable):
            self.functions[fid] = func
            return func
        return decorator

# ============================
# Bank Manager & Bank Switching Logic
# ============================
class BankManager:
    """Handles bank switching and function execution across banks"""
    def __init__(self):
        self.banks: Dict[str, Bank] = {}  # Banks indexed by name
        self.ram = SharedRAM()  # Shared memory across banks
        self.current_bank: Optional[str] = None  # Current active bank
    
    def add_bank(self, bank: Bank):
        """Add a bank to the system"""
        self.banks[bank.name] = bank
        
    def call(self, target_bank: str, fid: int, *args):
        """Execute a function from a target bank, simulate bank switching"""
        if target_bank not in self.banks:
            raise ValueError(f"Bank {target_bank} not found")
        
        # Save current context (bank and return address)
        if self.current_bank:
            self.ram.call_stack.append({
                'bank': self.current_bank,
                'return_pc': 0  # Simulated return address (could be program counter)
            })
        
        # Simulate bank switching
        self.current_bank = target_bank
        self.ram.push_params(*args)  # Push parameters into shared memory
        
        try:
            # Execute the function from the target bank via function ID
            result = self.banks[target_bank].functions[fid](self)
            self.ram.log(f"{target_bank}: Function {fid} completed")
            return result
        except Exception as e:
            self.ram.log(f"ERROR in {target_bank}: {str(e)}")
            raise
        finally:
            # Return to the calling bank (simulated)
            if self.ram.call_stack and self.current_bank == target_bank:
                self.ret()

    def ret(self, value: Any = None):
        """Simulate returning to the calling bank"""
        if not self.ram.call_stack:
            raise RuntimeError("Nothing to return to")
        
        context = self.ram.call_stack.pop()
        self.current_bank = context['bank']
        if value is not None:
            self.ram.push_params(value)
        self.ram.log(f"Returned to {self.current_bank}")

# ============================
# Example Banks (Fixed)
# ============================
def create_math_bank():
    bank = Bank("MATH")
    
    @bank.register(1)
    def add(manager):
        a, b = manager.ram.pop_params(2)
        result = a + b
        manager.ram.push_params(result)
        manager.ram.log(f"ADD: {a} + {b} = {result}")
        return result
        
    @bank.register(2)
    def multiply(manager):
        a, b = manager.ram.pop_params(2)
        result = a * b
        manager.ram.push_params(result)
        manager.ram.log(f"MULT: {a} * {b} = {result}")
        return result
        
    return bank

def create_string_bank():
    bank = Bank("STRINGS")
    
    @bank.register(1)
    def concat(manager):
        s1, s2 = manager.ram.pop_params(2)
        result = s1 + s2
        manager.ram.push_params(result)
        manager.ram.log(f"CONCAT: '{s1}' + '{s2}' = '{result}'")
        return result
        
    @bank.register(2)
    def reverse(manager):
        s, = manager.ram.pop_params(1)
        result = s[::-1]
        manager.ram.push_params(result)
        manager.ram.log(f"REVERSE: '{s}' -> '{result}'")
        return result
        
    return bank

def create_main_bank():
    bank = Bank("MAIN")
    
    @bank.register(0)
    def main(manager):
        manager.ram.log("MAIN: Starting program")
        
        # Call functions from other banks
        manager.call("MATH", 1, 5, 3)  # Math operations
        manager.call("MATH", 2, 4, 6)
        
        manager.call("STRINGS", 1, "Hello", "World")  # String operations
        manager.call("STRINGS", 2, "Python")
        
        manager.ram.log("MAIN: Program complete")
        return 0
        
    return bank

# ============================
# Simulation Function (Fixed)
# ============================
def run_simulation():
    manager = BankManager()
    
    # Add banks to the manager
    manager.add_bank(create_main_bank())
    manager.add_bank(create_math_bank())
    manager.add_bank(create_string_bank())
    
    # Start execution in the MAIN bank
    manager.current_bank = "MAIN"
    try:
        manager.call("MAIN", 0)  # Start the MAIN bank function
    except Exception as e:
        print(f"Simulation ended with error: {e}")
    
    # Print execution log
    print("\nExecution Log:")
    print("\n".join(manager.ram.output_buffer))
    
    # Print final state
    print("\nFinal State:")
    print(f"Current Bank: {manager.current_bank}")
    print(f"Param Stack: {manager.ram.param_stack}")
    print(f"Call Stack Depth: {len(manager.ram.call_stack)}")

if __name__ == "__main__":
    run_simulation()