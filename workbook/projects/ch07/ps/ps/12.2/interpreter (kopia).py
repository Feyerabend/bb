
class PostScriptObject:
    def execute(self, interpreter):
        pass

class Number(PostScriptObject):
    def __init__(self, value):
        self.value = value
    
    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Boolean(PostScriptObject):
    def __init__(self, value):
        self.value = value

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class String(PostScriptObject):
    def __init__(self, value):
        self.value = value

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Array(PostScriptObject):
    def __init__(self, elements):
        self.elements = elements

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Name(PostScriptObject):
    def __init__(self, name):
        self.name = name

    def execute(self, interpreter):
        value = interpreter.lookup(self.name)
        if isinstance(value, Procedure):
            interpreter.execution_stack.append(interpreter.current_object_stream)
            interpreter.current_object_stream = value.elements
        elif value is not None:
            value.execute(interpreter)
        else:
            raise NameError(f"Undefined name: {self.name}")

class Operator(PostScriptObject):
    def __init__(self, func):
        self.func = func

    def execute(self, interpreter):
        self.func(interpreter)

class Procedure(PostScriptObject):
    def __init__(self, elements):
        self.elements = elements

    def execute(self, interpreter):
        interpreter.execution_stack.append(interpreter.current_object_stream)
        interpreter.current_object_stream = self.elements


class Interpreter:
    def __init__(self):
        self.operand_stack = []
        self.execution_stack = []
        self.dictionary_stack = [{}]
        self.current_object_stream = []

    def lookup(self, name):
        for dictionary in reversed(self.dictionary_stack):
            if name in dictionary:
                return dictionary[name]
        return None

    def define(self, name, value):
        self.dictionary_stack[-1][name] = value

    def execute(self, objects):
        self.current_object_stream = objects
        while self.current_object_stream:
            obj = self.current_object_stream.pop(0)
            obj.execute(self)
        if self.execution_stack:
            self.current_object_stream = self.execution_stack.pop()


# Example usage:

# Define some basic operations
def add(interpreter):
    b = interpreter.operand_stack.pop().value
    a = interpreter.operand_stack.pop().value
    interpreter.operand_stack.append(Number(a + b))

def print_stack(interpreter):
    print("Stack:", [obj.value for obj in interpreter.operand_stack])

# Create interpreter instance
interpreter = Interpreter()

# Define some PostScript-like operators
interpreter.define("add", Operator(add))
interpreter.define("=", Operator(print_stack))

# Example: executing a sequence
objects = [
    Number(5),
    Number(3),
    Name("add"),
    Name("=")
]

interpreter.execute(objects)
