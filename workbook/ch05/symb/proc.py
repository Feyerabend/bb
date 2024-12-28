
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # List of dictionaries, each representing a scope

    def enter_scope(self):
        """Create a new scope and push it onto the scope stack."""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope by popping it from the scope stack."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            print("Error: Cannot exit global scope.")

    def add_symbol(self, name, value):
        """Add a symbol to the current scope."""
        self.scopes[-1][name] = value

    def get_symbol(self, name):
        """Retrieve a symbol's value from the current scope or outer scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None  # Symbol not found

    def display(self):
        """Display all symbols in the current scope."""
        for scope in self.scopes:
            for symbol, value in scope.items():
                print(f"{symbol}: {value}")

class ProceduralParser:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def parse_program(self, program):
        """Parse a simple procedural program."""
        for statement in program:
            if statement["type"] == "function":
                self.parse_function(statement)
            elif statement["type"] == "declaration":
                self.parse_declaration(statement)

    def parse_function(self, func):
        """Parse a function block."""
        print(f"Entering function: {func['name']}")
        self.symbol_table.enter_scope()

        # Add function parameters to the symbol table
        for param in func["params"]:
            self.symbol_table.add_symbol(param, None)  # Parameters have no initial value

        # Parse the function body
        for statement in func["body"]:
            self.parse_declaration(statement)

        # Display the symbol table state
        print("Symbol table state after function:")
        self.symbol_table.display()

        # Exit function scope
        self.symbol_table.exit_scope()

    def parse_declaration(self, decl):
        """Parse a variable declaration."""
        self.symbol_table.add_symbol(decl["name"], decl["value"])


# Test Procedural Language Parser
procedural_program = [
    {"type": "declaration", "name": "global_var", "value": 42},
    {"type": "function", "name": "foo", "params": ["a", "b"], "body": [
        {"type": "declaration", "name": "x", "value": 10},
        {"type": "declaration", "name": "y", "value": 20},
    ]},
    {"type": "function", "name": "bar", "params": [], "body": [
        {"type": "declaration", "name": "z", "value": 99},
    ]}
]

print("\n--- Procedural Language Parser ---")
parser = ProceduralParser()
parser.parse_program(procedural_program)