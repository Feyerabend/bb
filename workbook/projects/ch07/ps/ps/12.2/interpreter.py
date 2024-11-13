
class OperandStack:

    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            raise ValueError("Operand stack underflow")
        return self.stack.pop()

    def top(self): # = peek
        if not self.stack:
            raise ValueError("Operand stack underflow")
        return self.stack[-1]

    def clear(self):
        self.stack.clear()

    def __len__(self):
        return len(self.stack)

    def __repr__(self):
        return repr(self.stack)


# add: __str__ to check define
class DictionaryStack:

    def __init__(self):
        self.stack = [{}]

    def define(self, name, value):
        """Defines a variable or procedure in the current (topmost) dictionary scope."""
        self.stack[-1][name] = value

    def lookup(self, name):
        """Looks up a name in the stack, searching from the top (most recent) scope."""
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        raise KeyError(f"Undefined name: {name}")

    def push_scope(self):
        """Pushes a new dictionary (scope) onto the stack."""
        self.stack.append({})

    def pop_scope(self):
        """Pops the top dictionary (scope) from the stack. Raises an error if only one scope exists."""
        if len(self.stack) <= 1:
            raise ValueError("Cannot pop the global scope")
        self.stack.pop()

    def __len__(self):
        return len(self.stack)

    def __repr__(self):
        return repr(self.stack)


class Interpreter:
    def __init__(self, operand_stack, dictionary_stack):
        self.operand_stack = operand_stack
        self.dictionary_stack = dictionary_stack

    def add(self):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        self.operand_stack.push(a + b)

    def sub(self):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        self.operand_stack.push(a - b)

    def mul(self):
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        self.operand_stack.push(a * b)

    def div(self):
        b = self.operand_stack.pop()
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        a = self.operand_stack.pop()
        self.operand_stack.push(a / b)

    def dup(self):
        self.operand_stack.push(self.operand_stack.top())

    def exch(self): # aka: swap
        b = self.operand_stack.pop()
        a = self.operand_stack.pop()
        self.operand_stack.push(b)
        self.operand_stack.push(a)

    def pop(self):
        self.operand_stack.pop()

# procedures

    def define_procedure(self, name, commands):
        self.dictionary_stack.define(name, commands)

    def execute_procedure(self, procedure_name):
        """Executes a procedure by fetching it from the dictionary stack and interpreting each command."""
        commands = self.dictionary_stack.lookup(procedure_name)
        if not isinstance(commands, list):
            raise ValueError(f"{procedure_name} is not a procedure")
        for command in commands:
            self.execute(command)

# control

    def if_(self):
        """Executes a procedure if the top operand is true (non-zero)."""
        proc = self.operand_stack.pop()
        condition = self.operand_stack.pop()
        if condition:
            self.execute(proc)

    def ifelse(self):
        """Executes one of two procedures based on a condition."""
        else_proc = self.operand_stack.pop()
        if_proc = self.operand_stack.pop()
        condition = self.operand_stack.pop()
        if condition:
            self.execute(if_proc)
        else:
            self.execute(else_proc)


    def repeat(self):
        """Repeats a procedure a specified number of times."""
        proc = self.operand_stack.pop()
        count = int(self.operand_stack.pop())
        for _ in range(count):
            self.execute(proc)

    def is_number(self, value):
        """Check if value is a number, whether as a string, a float, or inside a single-item list."""
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        if isinstance(value, str):
            if value.isdigit() or (value[0] == '-' and value[1:].isdigit()):
                return int(value)
            try:
                return float(value)
            except ValueError:
                return None  # not a number
        return None

# main exec

    def execute(self, token):
        # Number handling
        number = self.is_number(token)
        if number is not None:
            self.operand_stack.push(number)
    
        # Literal name or command handling
        elif isinstance(token, str):
            if token.startswith('/'):  # Literal name, so push as-is
                self.operand_stack.push(token)
        
            elif token == "def":  # Handle the "def" command specifically
                # Expecting: <name> <value> def
                value = self.operand_stack.pop()
                name = self.operand_stack.pop()
            
                if not isinstance(name, str) or not name.startswith('/'):
                    raise ValueError("Expected a literal name starting with '/' for def")

                # Define without the leading '/' in the dictionary
                self.dictionary_stack.define(name[1:], value)

            else:  # Check dictionary for variable/procedure or an operation
                try:
                    value = self.dictionary_stack.lookup(token)
                    if isinstance(value, list):  # Procedure / block
                        self.execute_procedure(value)
                    else:  # Defined value, push to operand stack
                        self.operand_stack.push(value)
                except KeyError:
                    if hasattr(self, token):  # Invoke interpreter operation if exists
                        getattr(self, token)()
                    else:
                        raise ValueError(f"Unknown command or undefined name: {token}")

        # Block handling
        elif isinstance(token, list):  # Array or Block
            if token and token[0] == '{' and token[-1] == '}':  # Block
                block_content = token[1:-1]  # Remove the braces
                self.operand_stack.push(block_content)
            else:
                self.operand_stack.push(token)
    
        else:
            raise TypeError(f"Unsupported token type: {type(token)}")



