
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Start with the global scope.

    def enter_scope(self):
        """Create a new scope for function bodies."""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            print("Error: Cannot exit global scope.")

    def add_binding(self, name, value):
        """Add a binding for a variable or function."""
        self.scopes[-1][name] = value

    def get_binding(self, name):
        """Retrieve a binding from the current or outer scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None  # If not found

    def display(self):
        """Display all bindings in the current scope."""
        for scope in self.scopes:
            for name, value in scope.items():
                print(f"{name}: {value}")


class FunctionalParser:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def parse_program(self, program):
        """Parse a functional program, handling bindings and functions."""
        for statement in program:
            if statement["type"] == "binding":
                self.parse_binding(statement)
            elif statement["type"] == "function":
                self.parse_function(statement)

    def parse_binding(self, bind):
        """Parse a binding (variable or function assignment)."""
        self.symbol_table.add_binding(bind["name"], bind["value"])

    def parse_function(self, func):
        """Parse a function definition."""
        print(f"Defining function: {func['name']}")
        self.symbol_table.add_binding(func["name"], func)  # Store the function itself in the symbol table

    def parse_call(self, call):
        """Parse a function call."""
        func = self.symbol_table.get_binding(call["name"])
        if func:
            print(f"Calling function: {call['name']}")
            self.symbol_table.enter_scope()
            # Bind function parameters in the local scope
            for param, arg in zip(func["params"], call["args"]):
                self.symbol_table.add_binding(param, arg)
            # Simulate function body execution (not implemented here)
            print(f"Executing function body of {func['name']} with arguments: {call['args']}")
            self.symbol_table.exit_scope()
        else:
            print(f"Function {call['name']} not defined.")

    def display_symbol_table(self):
        """Display the symbol table at any point."""
        print("Symbol Table:")
        self.symbol_table.display()


# Test Functional Language Parser

functional_program = [
    {"type": "binding", "name": "x", "value": 42},
    {"type": "function", "name": "add", "params": ["a", "b"], "body": [
        {"type": "binding", "name": "result", "value": "a + b"},
    ]},
    {"type": "function", "name": "multiply", "params": ["a", "b"], "body": [
        {"type": "binding", "name": "result", "value": "a * b"},
    ]},
]

print("\n--- Functional Language Parser ---")
parser = FunctionalParser()

# Parse the program
parser.parse_program(functional_program)

# Display the symbol table after parsing
parser.display_symbol_table()

# Simulate a function call
call = {"name": "add", "args": [5, 10]}
parser.parse_call(call)

# Display the symbol table after a call
parser.display_symbol_table()