class TACGenerator:
    def __init__(self, symbol_table):
        self.temp_count = 0  # temporary vars
        self.label_count = 0  # labels (unique)
        self.instructions = []  # TAC instructions
        self.symbol_table = symbol_table  # symbol table for scope
        self.scope_stack = ["global"]  # stack to track current scope

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def enter_scope(self, scope_name):
        self.scope_stack.append(scope_name)

    def leave_scope(self):
        self.scope_stack.pop()

    def current_scope(self):
        return self.scope_stack[-1]


    # Resolve an identifier to its declaration in the current scope stack.
    # Checks the scopes from the innermost (top of the stack) outward.
    def resolve_identifier(self, identifier):
        for scope in reversed(self.scope_stack):
            if scope in self.symbol_table and identifier in self.symbol_table[scope]["scope"]:
                return f"{scope}_{identifier}"  # fully qualified name
        raise NameError(f"Identifier '{identifier}' not found in any accessible scope.")

    def generate(self, node): # TACs ..
        method = f"gen_{node['type'].lower()}"
        if hasattr(self, method): # python .. 
            return getattr(self, method)(node)
        else:
            raise NotImplementedError(f"No handler for node type {node['type']}")

    def gen_program(self, node):
        self.enter_scope("global")
        for child in node["children"]:
            self.generate(child)
        self.leave_scope()

    def gen_block(self, node):
        for child in node["children"]:
            self.generate(child)

    def gen_var_decl(self, node):
        # do not emit TAC instruction
        pass

    def gen_assignment(self, node):
        target = self.resolve_identifier(node["value"])
        expression = self.generate(node["children"][0])
        self.emit(f"{target} = {expression}")

    def gen_expression(self, node):
        if len(node["children"]) == 1:
            return self.generate(node["children"][0])
        elif len(node["children"]) == 2:
            left = self.generate(node["children"][0])
            right = self.generate(node["children"][1])
            temp = self.new_temp()
            op = node["value"]
            self.emit(f"{temp} = {left} {op} {right}")
            return temp

    def gen_identifier(self, node):
        return self.resolve_identifier(node["value"])

    def gen_number(self, node):
        return node["value"]

    def gen_while(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit(f"{start_label}:")
        condition = self.generate(node["children"][0])
        self.emit(f"if not {condition} goto {end_label}")
        self.generate(node["children"][1])  # loop body
        self.emit(f"goto {start_label}")
        self.emit(f"{end_label}:")

    def gen_proc_decl(self, node):
        proc_name = node["value"]
        self.emit(f"proc {proc_name}:")
        self.enter_scope(proc_name)
        self.generate(node["children"][0])  # procedure body
        self.leave_scope()
        self.emit(f"endproc")

    def gen_call(self, node):
        proc_name = node["value"]
        self.emit(f"call {proc_name}")

    def gen_if(self, node):
        condition = self.generate(node["children"][0])
        else_label = self.new_label()
        end_label = self.new_label()
        self.emit(f"if not {condition} goto {else_label}")
        self.generate(node["children"][1])  # true
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")
        if len(node["children"]) > 2:
            self.generate(node["children"][2])  # false -- do not have else? include?
        self.emit(f"{end_label}:")

# test
if __name__ == "__main__":

    symbol_table = {
        "global": {
            "scope": {
                "x": {"type": "variable"},
                "y": {"type": "variable"},
                "multiply": {
                    "type": "procedure",
                    "scope": {
                        "a": {"type": "variable"},
                        "b": {"type": "variable"},
                        "x": {"type": "variable"},
                        "y": {"type": "variable"}
                    }
                },
            }
        },# def
        "multiply": {
            "scope": {
                "a": {"type": "variable"},
                "b": {"type": "variable"},
                "x": {"type": "variable"},
                "y": {"type": "variable"}
            }
        },
    }

    ast = {
        "type": "PROGRAM",
        "value": "noname",
        "children": [
            {
                "type": "PROC_DECL",
                "value": "multiply",
                "children": [
                    {
                        "type": "BLOCK",
                        "children": [
                            {
                                "type": "ASSIGNMENT",
                                "value": "x",
                                "children": [
                                    {
                                        "type": "EXPRESSION",
                                        "value": "+",
                                        "children": [
                                            {"type": "IDENTIFIER", "value": "a"},
                                            {"type": "IDENTIFIER", "value": "b"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    generator = TACGenerator(symbol_table)
    generator.generate(ast)
    for instr in generator.instructions:
        print(instr)
