class Interpreter:
    def __init__(self):
        self.dictionary_stack = {}  # This will store our named procedures
        self.operand_stack = []     # Stack to hold values and intermediate results

    def def_procedure(self, name, procedure):
        """Defines a procedure by storing it in the dictionary."""
        self.dictionary_stack[name] = procedure
    
    def execute(self, token):
        """Executes a token."""
        if isinstance(token, int):  # Push numbers directly onto the operand stack
            self.operand_stack.append(token)
        
        elif isinstance(token, str):  # It might be a command or a procedure name
            # Check if it's a built-in function
            if hasattr(self, token):
                getattr(self, token)()  # Invoke the operation
            
            # Check if it's a defined procedure
            elif token in self.dictionary_stack:
                procedure = self.dictionary_stack[token]
                self.execute_procedure(procedure)
            else:
                raise ValueError(f"Unknown command or undefined name: {token}")
    
    def execute_procedure(self, procedure):
        """Executes a procedure (a list of tokens)."""
        for token in procedure:
            self.execute(token)
    
    def square(self):
        """Custom square function that squares the top of the operand stack."""
        value = self.operand_stack.pop()
        self.operand_stack.append(value * value)

# Setting up the interpreter and defining a procedure
interpreter = Interpreter()

# Define a procedure "square" as a list of tokens. We'll mimic the square function here
# Define a new name "my_square" in the dictionary that runs the "square" method
interpreter.def_procedure("my_square", ["square"])

# Push a number onto the operand stack and call our custom procedure
interpreter.operand_stack.append(5)
interpreter.execute("my_square")  # This should square the number 5

# The operand stack should now contain the result of 5 squared
print("Operand Stack:", interpreter.operand_stack)  # Expected output: Operand Stack: [25]
