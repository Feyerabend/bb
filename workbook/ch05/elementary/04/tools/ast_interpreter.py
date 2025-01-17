import sys
import json

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.constants = {}
        self.procedures = {}
        self.environment_stack = [{}]

    def print_env(self):
        for i, env in enumerate(self.environment_stack):
            print(f"Env {i}: {env}")

    def execute(self):
        self._execute_node(self.ast)

    def _current_environment(self):
        return self.environment_stack[-1]

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
        self.environment_stack.append({}) # new scope for block
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
        for child in node.get("children", []):
            self._execute_node(child)

    def _handle_assignment(self, node):
        var_name = node["value"]
        value = self._evaluate_expression(node["children"][0])
        self._set_variable(var_name, value)

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

        while self._execute_node(condition_node):
            self._execute_node(body_node)

    def _handle_if(self, node):
        condition = self._execute_node(node["children"][0])
        if condition:
            self._execute_node(node["children"][1])

    def _handle_call(self, node):
        proc_name = node["value"]
        if proc_name not in self.procedures:
            raise ValueError(f"Procedure {proc_name} not found")
        current_environment = self._current_environment()
        new_environment = current_environment.copy()
        self.environment_stack.append(new_environment)
        try:
            proc_node = self.procedures[proc_name]
            self._execute_node(proc_node["children"][0])  # one proc, start at BLOCK
        except:
            try:
                self._execute_node(proc_node["children"]) # else ..
            except:
                pass
        finally:
            for var_name in current_environment.keys():
                if var_name in new_environment:
                    current_environment[var_name] = new_environment[var_name]
            self.print_env()
            self.environment_stack.pop()

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
        for env in reversed(self.environment_stack):
            if var_name in env:
                env[var_name] = value
                return
        self._current_environment()[var_name] = value

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

