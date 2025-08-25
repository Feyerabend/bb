# python_generator.py
# External plugin for generating Python code from PL/0 AST

class PythonGeneratorPlugin(Plugin):
    """Generates Python code from PL/0 programs"""
    
    def __init__(self):
        super().__init__(
            "python_generator", 
            "Generates Python code with modern idioms", 
            "1.0"
        )
        self.dependencies = ["static_analysis"]
    
    def run(self, ast, context, messages):
        generator = PythonCodeGenerator(messages)
        python_code = generator.generate(ast)
        context.generated_outputs["python_code"] = python_code
        
        messages.info("Generated Python code")
        return {
            "generated": True, 
            "lines": len(python_code.split('\n')),
            "language": "python"
        }


class PythonCodeGenerator(Visitor):
    """Generates clean, idiomatic Python code"""
    
    def __init__(self, messages: MessageCollector):
        self.messages = messages
        self.code_lines = []
        self.indent_level = 0
        self.procedures = set()
        self.global_vars = set()
        self.in_procedure = False
        self.procedure_vars = {}  # Track variables per procedure
    
    def generate(self, ast: ASTNode) -> str:
        # First pass: collect procedures and global variables
        self._collect_info(ast)
        
        # Generate header
        self.code_lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Generated Python code from PL/0 program",
            "This code maintains the semantics of the original PL/0 program",
            '"""',
            "",
            "import sys",
            ""
        ]
        
        # Generate code
        ast.accept(self)
        
        return "\n".join(self.code_lines)
    
    def _collect_info(self, node):
        """Collect information about procedures and variables"""
        if isinstance(node, BlockNode):
            if not self.in_procedure:  # Global scope
                self.global_vars.update(node.variables)
            
            for proc_name, proc_body in node.procedures:
                self.procedures.add(proc_name)
                # Collect procedure variables
                proc_vars = set()
                self._collect_proc_vars(proc_body, proc_vars)
                self.procedure_vars[proc_name] = proc_vars
                
        elif hasattr(node, '__dict__'):
            for attr in node.__dict__.values():
                if isinstance(attr, ASTNode):
                    self._collect_info(attr)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, (ASTNode, tuple)):
                            if isinstance(item, tuple) and len(item) == 2:
                                self._collect_info(item[1])  # procedure body
                            elif isinstance(item, ASTNode):
                                self._collect_info(item)
    
    def _collect_proc_vars(self, node, var_set):
        """Collect variables used in a procedure"""
        if isinstance(node, BlockNode):
            var_set.update(node.variables)
            for _, proc_body in node.procedures:
                self._collect_proc_vars(proc_body, var_set)
            self._collect_proc_vars(node.statement, var_set)
        elif hasattr(node, '__dict__'):
            for attr in node.__dict__.values():
                if isinstance(attr, ASTNode):
                    self._collect_proc_vars(attr, var_set)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, ASTNode):
                            self._collect_proc_vars(item, var_set)
    
    def _add_line(self, line: str = ""):
        """Add a line of code with proper indentation"""
        if line.strip():
            self.code_lines.append("    " * self.indent_level + line)
        else:
            self.code_lines.append("")
    
    def visit_block(self, node: BlockNode):
        if not self.in_procedure:  # Main program
            # Initialize global variables
            if node.variables:
                self._add_line("# Global variables")
                for var in sorted(node.variables):
                    self._add_line(f"{var} = 0")
                self._add_line()
            
            # Generate procedure definitions
            for proc_name, proc_body in node.procedures:
                self._add_line(f"def {proc_name}():")
                self.indent_level += 1
                
                # Add global declarations for variables used in procedure
                proc_vars = self.procedure_vars.get(proc_name, set())
                global_refs = proc_vars.intersection(self.global_vars)
                if global_refs:
                    global_stmt = "global " + ", ".join(sorted(global_refs))
                    self._add_line(global_stmt)
                    self._add_line()
                
                # Generate local variables if any
                if proc_body.variables:
                    self._add_line("# Local variables")
                    for var in sorted(proc_body.variables):
                        self._add_line(f"{var} = 0")
                    self._add_line()
                
                self.in_procedure = True
                proc_body.accept(self)
                self.in_procedure = False
                
                self.indent_level -= 1
                self._add_line()
            
            # Main execution
            self._add_line("def main():")
            self.indent_level += 1
            
            # Add global declarations if needed
            if self.global_vars:
                global_stmt = "global " + ", ".join(sorted(self.global_vars))
                self._add_line(global_stmt)
                self._add_line()
            
            node.statement.accept(self)
            self.indent_level -= 1
            self._add_line()
            self._add_line('if __name__ == "__main__":')
            self.indent_level += 1
            self._add_line("main()")
            self.indent_level -= 1
            
        else:  # Inside procedure
            # Local variables
            for var in node.variables:
                self._add_line(f"{var} = 0")
            if node.variables:
                self._add_line()
            
            node.statement.accept(self)
    
    def visit_assign(self, node: AssignNode):
        expr = node.expression.accept(self)
        self._add_line(f"{node.var_name} = {expr}")
    
    def visit_call(self, node: CallNode):
        self._add_line(f"{node.proc_name}()")
    
    def visit_read(self, node: ReadNode):
        self._add_line("try:")
        self.indent_level += 1
        self._add_line(f'{node.var_name} = int(input("Enter integer: "))')
        self.indent_level -= 1
        self._add_line("except ValueError:")
        self.indent_level += 1
        self._add_line("print('Invalid input! Using 0.')")
        self._add_line(f"{node.var_name} = 0")
        self.indent_level -= 1
    
    def visit_write(self, node: WriteNode):
        expr = node.expression.accept(self)
        self._add_line(f"print({expr})")
    
    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node: NestedBlockNode):
        self._add_line("# Begin nested block")
        if node.variables:
            self._add_line("# Local variables in nested scope")
            for var in node.variables:
                self._add_line(f"{var} = 0")
            self._add_line()
        
        for stmt in node.statements:
            stmt.accept(self)
        self._add_line("# End nested block")
    
    def visit_if(self, node: IfNode):
        condition = node.condition.accept(self)
        self._add_line(f"if {condition}:")
        self.indent_level += 1
        node.then_statement.accept(self)
        self.indent_level -= 1
    
    def visit_while(self, node: WhileNode):
        condition = node.condition.accept(self)
        self._add_line(f"while {condition}:")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
    
    def visit_operation(self, node: OperationNode):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # Python operator mapping
        op_map = {
            "+": "+", "-": "-", "*": "*", "/": "//",  # Integer division
            "<": "<", ">": ">", "=": "==", "<=": "<=", ">=": ">="
        }
        
        python_op = op_map.get(node.operator, node.operator)
        return f"({left} {python_op} {right})"
    
    def visit_variable(self, node: VariableNode):
        return node.name
    
    def visit_number(self, node: NumberNode):
        return str(node.value)
