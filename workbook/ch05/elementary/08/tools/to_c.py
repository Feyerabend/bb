from collections import defaultdict

class TACToCTranspiler:
    def __init__(self):
        self.globals = set()
        self.functions = defaultdict(list)
        self.current_function = None
        self.entry_point = "main"
        self.call_graph = defaultdict(set)

    def transpile(self, tac_instructions):
        # Process instructions and build functions
        for instr in tac_instructions:
            if instr["op"] == "LABEL":
                name = instr["result"]
                if name == "main":
                    self.current_function = self.entry_point
                else:
                    self.current_function = name
            else:
                if self.current_function:
                    self.functions[self.current_function].append(instr)
                    if instr["op"] == "=" and not instr["result"].startswith('t'):
                        self.globals.add(instr["result"])
                    if instr["op"] == "CALL":
                        self.call_graph[self.current_function].add(instr["arg1"])

        # Check for recursion
        self._check_recursion()

        # Generate C code
        output = ["#include <stdio.h>\n\n"]
        
        # Global variables
        if self.globals:
            output.append("// Global variables\n")
            output.extend(f"int {var};\n" for var in self.globals)
            output.append("\n")
        
        # Function prototypes
        output.append("// Function prototypes\n")
        for func in self.functions:
            output.append(f"void {func}();\n")
        output.append("\n")
        
        # Function definitions
        for func, instructions in self.functions.items():
            output.append(f"void {func}() {{\n")
            temps = {instr["result"] for instr in instructions 
                    if "result" in instr and instr["result"].startswith('t')}
            if temps:
                output.append(f"    int {', '.join(temps)};\n")
            for instr in instructions:
                output.append(f"    {self._translate(instr)}")
            output.append("}\n\n")
        
        # Main function
        output.append(f"int main() {{\n")
        output.append(f"    {self.entry_point}();\n")
        output.append("    return 0;\n}\n")
        
        return ''.join(output)

    def _check_recursion(self):
        for func, callees in self.call_graph.items():
            if func in callees:
                raise ValueError(f"Recursive call detected in {func}")

    def _translate(self, instr):
        op = instr["op"]
        if op == "LOAD":
            return f"{instr['result']} = {instr['arg1']};\n"
        elif op in {"+", "-", "*", "/"}:
            return f"{instr['result']} = {instr['arg1']} {op} {instr['arg2']};\n"
        elif op == "CALL":
            return f"{instr['arg1']}();\n"
        elif op == "IF_NOT":
            return f"if (!{instr['arg1']}) goto {instr['result']};\n"
        elif op == "GOTO":
            return f"goto {instr['result']};\n"
        elif op == "=":
            return f"{instr['result']} = {instr['arg1']};\n"
        elif op == "RETURN":
            return "return;\n"
        else:
            return f"/* Unknown operation: {op} */\n"

# Test with sample TAC
tac = [
    {"op": "LABEL", "result": "main"},
    {"op": "LOAD", "arg1": "5", "result": "t0"},
    {"op": "=", "arg1": "t0", "result": "x"},
    {"op": "CALL", "arg1": "print_result"},
    {"op": "RETURN"},
    {"op": "LABEL", "result": "print_result"},
    {"op": "LOAD", "arg1": "x", "result": "t1"},
    {"op": "+", "arg1": "t1", "arg2": "1", "result": "t2"},
    {"op": "=", "arg1": "t2", "result": "x"},
    {"op": "RETURN"},
]

transpiler = TACToCTranspiler()
print(transpiler.transpile(tac))
