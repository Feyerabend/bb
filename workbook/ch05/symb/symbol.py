class SymbolTable:
    def __init__(self):
        # start at an empty list for scopes, beginning with the global scope
        self.scopes = [{}]  # global scope at index 0

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            print("Cannot exit global scope")

    def insert(self, name, symbol_info):
        self.scopes[-1][name] = symbol_info

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # only for show and tell, not needed for the symbol table
    def print_table(self):
        for scope_index, scope in enumerate(self.scopes):
            print(f"Scope {scope_index + 1}:")
            for name, info in scope.items():
                print(f"  Name: {name}")
                for key, value in info.items():
                    print(f"    {key}: {value}")
            print()

# symbol information for variables and functions
def create_variable_entry(var_type, scope, attributes=None, location=None):
    return {
        'Type': var_type,
        'Scope': scope,
        'Attributes': attributes or [],
        'Location': location
    }

def create_function_entry(return_type, parameters, scope):
    return {
        'Return Type': return_type,
        'Parameters': parameters,
        'Scope': scope
    }

# symbol table for a simple program with a function and arithmetic
symbol_table = SymbolTable()

# insert function 'add' into global scope
symbol_table.insert('add', create_function_entry('int', [('int', 'a'), ('int', 'b')], 'global'))

# insert variable 'x' into local scope (function 'foo')
symbol_table.enter_scope()
symbol_table.insert('x', create_variable_entry('float', 'local (function foo)', ['const'], '0x100'))

# simulate the arithmetic operation: x = 5 + 3 (simple arithmetic, add constants)
symbol_table.insert('5', create_variable_entry('int', 'local (expression)', [], '0x200'))
symbol_table.insert('3', create_variable_entry('int', 'local (expression)', [], '0x201'))

symbol_table.print_table()
