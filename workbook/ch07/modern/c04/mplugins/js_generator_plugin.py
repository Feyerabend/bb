# js_generator.py
# External plugin for generating JavaScript code from PL/0 AST

class JavaScriptGeneratorPlugin(Plugin):
    """Generates modern JavaScript code from PL/0 programs"""
    
    def __init__(self):
        super().__init__(
            "javascript_generator", 
            "Generates ES6+ JavaScript code with async I/O", 
            "1.0"
        )
        self.dependencies = ["static_analysis"]
    
    def run(self, ast, context, messages):
        generator = JavaScriptCodeGenerator(messages)
        js_code = generator.generate(ast)
        context.generated_outputs["javascript_code"] = js_code
        
        messages.info("Generated JavaScript code")
        return {
            "generated": True, 
            "lines": len(js_code.split('\n')),
            "language": "javascript",
            "features": ["es6", "async_io", "modules"]
        }


class JavaScriptCodeGenerator(Visitor):
    """Generates modern JavaScript with ES6+ features"""
    
    def __init__(self, messages: MessageCollector):
        self.messages = messages
        self.code_lines = []
        self.indent_level = 0
        self.procedures = set()
        self.global_vars = set()
        self.in_procedure = False
    
    def generate(self, ast: ASTNode) -> str:
        # Collect procedures first
        self._collect_procedures(ast)
        
        # Generate header
        self.code_lines = [
            "// Generated JavaScript code from PL/0 program",
            "// Requires Node.js for readline functionality",
            "",
            "const readline = require('readline');",
            "",
            "const rl = readline.createInterface({",
            "    input: process.stdin,",
            "    output: process.stdout",
            "});",
            "",
            "// Utility function for input",
            "const readInt = () => new Promise((resolve) => {",
            "    rl.question('Enter integer: ', (answer) => {",
            "        const num = parseInt(answer);",
            "        resolve(isNaN(num) ? 0 : num);",
            "    });",
            "});",
            "",
            "// Global variables",
        ]
        
        # Generate code
        ast.accept(self)
        
        # Close readline interface
        self.code_lines.extend([
            "",
            "// Cleanup",
            "process.on('exit', () => rl.close());",
            "process.on('SIGINT', () => process.exit(0));"
        ])
        
        return "\n".join(self.code_lines)
    
    def _collect_procedures(self, node):
        """Collect procedure names"""
        if isinstance(node, BlockNode):
            for proc_name, _ in node.procedures:
                self.procedures.add(proc_name)
        
        # Recursively check child nodes
        if hasattr(node, '__dict__'):
            for attr in node.__dict__.values():
                if isinstance(attr, ASTNode):
                    self._collect_procedures(attr)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, tuple) and len(item) == 2:
                            self._collect_procedures(item[1])
                        elif isinstance(item, ASTNode):
                            self._collect_procedures(item)
    
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
                for var in sorted(node.variables):
                    self._add_line(f"let {var} = 0;")
                self._add_line()
            
            # Generate procedure definitions
            for proc_name, proc_body in node.procedures:
                if proc_body.variables:
                    # Procedure with local variables - use async
                    self._add_line(f"async function {proc_name}() {{")
                else:
                    # Simple procedure - can be sync
                    self._add_line(f"function {proc_name}() {{")
                
                self.indent_level += 1
                
                # Local variables
                if proc_body.variables:
                    self._add_line("// Local variables")
                    for var in sorted(proc_body.variables):
                        self._add_line(f"let {var} = 0;")
                    self._add_line()
                
                self.in_procedure = True
                proc_body.accept(self)
                self.in_procedure = False
                
                self.indent_level -= 1
                self._add_line("}")
                self._add_line()
            
            # Main execution function
            self._add_line("async function main() {")
            self.indent_level += 1
            node.statement.accept(self)
            self._add_line("rl.close();")
            self.indent_level -= 1
            self._add_line("}")
            self._add_line()
            self._add_line("// Run the program")
            self._add_line("main().catch(console.error);")
            
        else:  # Inside procedure
            # Local variables already handled in main visit_block
            node.statement.accept(self)
    
    def visit_assign(self, node: AssignNode):
        expr = node.expression.accept(self)
        self._add_line(f"{node.var_name} = {expr};")
    
    def visit_call(self, node: CallNode):
        if self._has_io_operations(node):
            self._add_line(f"await {node.proc_name}();")
        else:
            self._add_line(f"{node.proc_name}();")
    
    def visit_read(self, node: ReadNode):
        self._add_line(f"{node.var_name} = await readInt();")
    
    def visit_write(self, node: WriteNode):
        expr = node.expression.accept(self)
        self._add_line(f"console.log({expr});")
    
    def visit_compound(self, node: CompoundNode):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node: NestedBlockNode):
        self._add_line("// Begin nested block")
        self._add_line("{")
        self.indent_level += 1
        
        if node.variables:
            self._add_line("// Local variables in nested scope")
            for var in node.variables:
                self._add_line(f"let {var} = 0;")
            self._add_line()
        
        for stmt in node.statements:
            stmt.accept(self)
        
        self.indent_level -= 1
        self._add_line("}")
        self._add_line("// End nested block")
    
    def visit_if(self, node: IfNode):
        condition = node.condition.accept(self)
        self._add_line(f"if ({condition}) {{")
        self.indent_level += 1
        node.then_statement.accept(self)
        self.indent_level -= 1
        self._add_line("}")
    
    def visit_while(self, node: WhileNode):
        condition = node.condition.accept(self)
        self._add_line(f"while ({condition}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._add_line("}")
    
    def visit_operation(self, node: OperationNode):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # JavaScript operator mapping
        op_map = {
            "+": "+", "-": "-", "*": "*", "/": "/",  # Use regular division
            "<": "<", ">": ">", "=": "===", "<=": "<=", ">=": ">="
        }
        
        js_op = op_map.get(node.operator, node.operator)
        
        # For division, floor the result to match PL/0 integer semantics
        if node.operator == "/":
            return f"Math.floor({left} / {right})"
        
        return f"({left} {js_op} {right})"
    
    def visit_variable(self, node: VariableNode):
        return node.name
    
    def visit_number(self, node: NumberNode):
        return str(node.value)
    
    def _has_io_operations(self, node):
        """Check if a node tree contains I/O operations that require async"""
        # For now, assume all procedures might have I/O
        # In a more sophisticated version, we could analyse the procedure body
        return True