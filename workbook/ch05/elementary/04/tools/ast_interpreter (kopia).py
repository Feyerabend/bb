import sys
import json

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.constants = {}
        self.procedures = {}
        self.environment_stack = [{}]  # Stack of environments for variable scopes

    def execute(self):
        self._execute_node(self.ast)

    def _current_environment(self):
        return self.environment_stack[-1]  # Always access the current environment at the top of the stack

    def _execute_node(self, node):
        method_name = f"_handle_{node['type'].lower()}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"Unknown node type: {node['type']}")
        return method(node)

    def _handle_program(self, node):
        for child in node.get("children", []):
            self._execute_node(child)

    def _handle_block(self, node):
        self.environment_stack.append({})  # New scope for the block
        try:
            for child in node.get("children", []):
                self._execute_node(child)
        finally:
            self.environment_stack.pop()

    def _handle_const_decl(self, node):
        for child in node.get("children", []):
            const_name = node["value"]
            const_value = self._execute_node(child)
            self.constants[const_name] = const_value

    def _handle_var_decl(self, node):
        env = self._current_environment()
        env[node["value"]] = 0

    def _handle_proc_decl(self, node):
        self.procedures[node["value"]] = node

    def _handle_begin(self, node):
        self.environment_stack.append({})  # New scope for BEGIN
        try:
            for child in node.get("children", []):
                self._execute_node(child)
        finally:
            self.environment_stack.pop()

    def _handle_assignment(self, node):
        var_name = node["value"]
        value = self._evaluate_expression(node["children"][0])
        
        # Debugging before setting the variable
        print(f"Handling assignment: {var_name} = {value}")
        
        self._set_variable(var_name, value)
        
        # Debugging after setting the variable
        print(f"After assignment: {var_name} = {value}")

    def _handle_expression(self, node):
        return self._evaluate_expression(node["children"][0])

    def _handle_operator(self, node):
        left = self._evaluate_expression(node["children"][0])
        right = self._evaluate_expression(node["children"][1])

        if node["value"] == "+":
            return left + right
        elif node["value"] == "-":
            return left - right
        elif node["value"] == "*":
            return left * right
        elif node["value"] == "/":
            return left // right
        else:
            raise ValueError(f"Unsupported operator: {node['value']}")

    def _handle_condition(self, node):
        left = self._evaluate_expression(node["children"][0])
        right = self._evaluate_expression(node["children"][1])

        print(f"Condition: {left} {node['value']} {right}")

        if node["value"] == "=":
            return left == right
        elif node["value"] == "#":
            return left != right
        elif node["value"] == "<":
            return left < right
        elif node["value"] == "<=":
            return left <= right
        elif node["value"] == ">":
            return left > right
        elif node["value"] == ">=":
            return left >= right
        else:
            raise ValueError(f"Unsupported condition operator: {node['value']}")

    def _handle_while(self, node):
        condition_node = node["children"][0]
        body_node = node["children"][1]

        print("Entering while loop")  # Debug: Log loop entry
        while self._execute_node(condition_node):
            self._execute_node(body_node)
        print(f"Loop variables: {self.environment_stack[-1]}")  # Debug: Print current variables

    def _handle_if(self, node):
        condition = self._execute_node(node["children"][0])
        print(f"Evaluating IF condition: {condition}")
        if condition:
            print("Condition is TRUE, executing IF body")
            self._execute_node(node["children"][1])
        else:
            print("Condition is FALSE, skipping IF body")

    def _handle_call(self, node):
        proc_name = node["value"]
        if proc_name not in self.procedures:
            raise ValueError(f"Procedure {proc_name} not found")

        # Get a reference to the current environment (global environment)
        current_environment = self._current_environment()

        # Create a shallow copy of the current environment for the procedure
        new_environment = current_environment.copy()

        # Push the new environment onto the stack for the procedure
        self.environment_stack.append(new_environment)
        print(f"Calling procedure {proc_name} with environment: {new_environment}")  # Debugging

        try:
            # Execute the procedure
            self._execute_node(self.procedures[proc_name])

            # Synchronize changes back to the outer (global) scope
            # Update the global environment with any changes made in the procedure's environment
            for var_name, value in new_environment.items():
                current_environment[var_name] = value

        finally:
            # Remove the procedure's environment
            self.environment_stack.pop()
            print(f"Returning from procedure {proc_name}, environment restored to: {self._current_environment()}")  # Debugging    

    def _handle_number(self, node):
        return int(node["value"])

    def _handle_identifier(self, node):
        var_name = node["value"]
        for env in reversed(self.environment_stack):
            if var_name in env:
                return env[var_name]
        if var_name in self.constants:
            return self.constants[var_name]
        raise ValueError(f"Undefined variable: {var_name}")

    def _set_variable(self, var_name, value):
        # Print the environment stack before setting the variable
        print(f"Before setting variable: {var_name} = {value}")
        print("Current environment stack:")
        for i, env in enumerate(self.environment_stack):
            print(f"Env {i}: {env}")

        # Iterate over environments from top to bottom (most recent to global)
        for env in reversed(self.environment_stack):
            if var_name in env:
                env[var_name] = value
                print(f"Set {var_name} = {value} in environment: {env}")
                return

        # If not found in any local environment, set it in the global environment
        self._current_environment()[var_name] = value
        print(f"Set {var_name} = {value} in global environment: {self._current_environment()}")

    def _evaluate_expression(self, node):
        if node["type"] == "NUMBER":
            return int(node["value"])
        elif node["type"] == "IDENTIFIER":
            return self._handle_identifier(node)
        elif node["type"] == "TERM":
            left = self._evaluate_expression(node["children"][0])
            right = self._evaluate_expression(node["children"][1])
            if node["value"] == "*":
                return left * right
            elif node["value"] == "/":
                return left // right
        elif node["type"] == "OPERATOR":
            left = self._evaluate_expression(node["children"][0])
            right = self._evaluate_expression(node["children"][1])
            if node["value"] == "+":
                return left + right
            elif node["value"] == "-":
                return left - right
        elif node["type"] == "EXPRESSION":
            return self._evaluate_expression(node["children"][0])
        else:
            raise ValueError(f"Unsupported expression type: {node['type']}")

if __name__ == "__main__":
    input_file = sys.argv[1]

    try:
        with open(input_file, "r") as file:
            ast = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from the file '{input_file}': {e}")
        sys.exit(1)

    interpreter = Interpreter(ast)
    interpreter.execute()

    print("Variables output:")
    print(interpreter.environment_stack[0])  # Print global environment