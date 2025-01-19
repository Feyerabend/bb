import sys
import json

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.indentation = 0
        self.code = []
        self.scopes = [{}]  # Stack of scopes, starting with the global scope

    def _indent(self):
        return "    " * self.indentation  # 4 spaces for indentation

    def generate_code(self):
        self._process_node(self.ast)
        return "\n".join(self.code)

    def _process_node(self, node):
        method_name = f"_handle_{node['type'].lower()}"
        method = getattr(self, method_name, None)
        if method is None:
            raise ValueError(f"Syntax Error: Unknown node type '{node['type']}'")
        return method(node)

    def _handle_program(self, node):
        for child in node.get("children", []):
            self._process_node(child)

    def _handle_block(self, node):
        block_name = node.get("value", "noname")
        self.code.append(f"{self._indent()}# Block: {block_name}")
        #self.indentation += 1  # Increase indentation for the block
        for child in node.get("children", []):
            self._process_node(child)
        #self.indentation -= 1  # Decrease indentation after block is processed

    def _handle_const_decl(self, node):
        const_name = node["value"]
        const_value = self._process_node(node["children"][0])
        self.code.append(f"{self._indent()}{const_name} = {const_value}  # const")

    def _handle_var_decl(self, node):
        var_name = node["value"]
        # Check if the variable is already in the current scope
        if var_name in self.scopes[-1]:
            raise ValueError(f"Variable '{var_name}' already declared in the current scope")
        self.scopes[-1][var_name] = 'local'
        self.code.append(f"{self._indent()}{var_name} = None  # var")

    def _handle_assignment(self, node):
        var_name = node["value"]
        value = self._process_node(node["children"][0])

        # Check if the variable is local or global
        if var_name not in self.scopes[-1]:
            # If the variable is not in the current scope, it must be global
            self.code.append(f"{self._indent()}global {var_name}")
        self.code.append(f"{self._indent()}{var_name} = {value}")

    def _handle_while(self, node):
        condition = self._process_node(node["children"][0])
        self.code.append(f"{self._indent()}while {condition}:")
        self.indentation += 1  # Increase indentation for the body of the while loop
        self._process_node(node["children"][1])
        self.indentation -= 1  # Decrease indentation after the while body

    def _handle_if(self, node):
        condition = self._process_node(node["children"][0])
        self.code.append(f"{self._indent()}if {condition}:")
        self.indentation += 1  # Increase indentation for the if block
        self._process_node(node["children"][1])
        self.indentation -= 1  # Decrease indentation after the if block

    def _handle_expression(self, node):
        return self._process_node(node["children"][0])

    def _handle_operator(self, node):
        left = self._process_node(node["children"][0])
        right = self._process_node(node["children"][1])
        return f"({left} {node['value']} {right})"

    def _handle_condition(self, node):
        left = self._process_node(node["children"][0])
        right = self._process_node(node["children"][1])
        operator = {
            "=": "==",
            "#": "!=",
            "<": "<",
            "<=": "<=",
            ">": ">",
            ">=": ">="
        }.get(node["value"], None)
        if operator is None:
            raise ValueError(f"Unsupported condition operator: {node['value']}")
        return f"({left} {operator} {right})"

    def _handle_number(self, node):
        return node["value"]

    def _handle_identifier(self, node):
        return node["value"]

    def _handle_proc_decl(self, node):
        proc_name = node["value"]
        self.code.append(f"{self._indent()}def {proc_name}():")
        self.scopes.append({})  # New local scope for the procedure
        self.indentation += 1  # Increase indentation for the function body
        for child in node.get("children", []):
            self._process_node(child)
        self.indentation -= 1  # Decrease indentation after function body
        self.scopes.pop()  # Exit the local scope

    def _handle_term(self, node):
        if node["type"] == "NUMBER":
            return node["value"]
        elif node["type"] == "IDENTIFIER":
            return node["value"]
        elif node["type"] == "OPERATOR":
            left = self._process_node(node["children"][0])
            right = self._process_node(node["children"][1])
            if node["value"] == "+":
                return f"({left} + {right})"
            elif node["value"] == "-":
                return f"({left} - {right})"
            elif node["value"] == "*":
                return f"({left} * {right})"
            elif node["value"] == "/":
                return f"({left} // {right})"
        return None

    def _handle_call(self, node):
        proc_name = node["value"]
        self.code.append(f"{self._indent()}{proc_name}()")  # Procedure call in Python

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

    generator = CodeGenerator(ast)
    generated_code = generator.generate_code()
    print(generated_code)