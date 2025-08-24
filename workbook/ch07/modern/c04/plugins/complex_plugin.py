# Example plugin file: complex_plugin.py
# This demonstrates both class-based and function-based plugins

# Class-based plugin example
class ComplexityAnalyzerPlugin(Plugin):
    """Analyzes code complexity metrics"""
    
    def __init__(self):
        super().__init__(
            "complexity_analyzer", 
            "Analyzes cyclomatic complexity and other metrics",
            "1.0"
        )
        self.dependencies = ["static_analysis"]
    
    def run(self, ast, context, messages):
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze(ast)
        messages.info(f"Code complexity: {metrics['cyclomatic_complexity']}")
        return metrics


class ComplexityAnalyzer(Visitor):
    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity
        self.lines_of_code = 0
        self.num_procedures = 0
        self.max_nesting_depth = 0
        self.current_nesting_depth = 0
    
    def analyze(self, ast):
        ast.accept(self)
        return {
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "lines_of_code": self.lines_of_code,
            "num_procedures": self.num_procedures,
            "max_nesting_depth": self.max_nesting_depth
        }
    
    def visit_block(self, node):
        self.num_procedures += len(node.procedures)
        for _, proc_body in node.procedures:
            proc_body.accept(self)
        node.statement.accept(self)
    
    def visit_if(self, node):
        self.cyclomatic_complexity += 1
        self.current_nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_nesting_depth)
        node.condition.accept(self)
        node.then_statement.accept(self)
        self.current_nesting_depth -= 1
    
    def visit_while(self, node):
        self.cyclomatic_complexity += 1
        self.current_nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_nesting_depth)
        node.condition.accept(self)
        node.body.accept(self)
        self.current_nesting_depth -= 1
    
    def visit_assign(self, node):
        self.lines_of_code += 1
        node.expression.accept(self)
    
    def visit_call(self, node):
        self.lines_of_code += 1
    
    def visit_read(self, node):
        self.lines_of_code += 1
    
    def visit_write(self, node):
        self.lines_of_code += 1
        node.expression.accept(self)
    
    def visit_compound(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_operation(self, node):
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_number(self, node):
        pass


# Function-based plugin examples
@plugin_function(
    name="ast_printer", 
    description="Pretty prints the AST structure",
    dependencies=[]
)
def print_ast(ast, context, messages):
    """Print AST structure for debugging"""
    printer = ASTPrinter()
    ast_str = printer.print_ast(ast)
    context.generated_outputs["ast_structure"] = ast_str
    messages.info("Generated AST structure dump")
    return {"generated": True}


class ASTPrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.output = []
    
    def print_ast(self, node):
        self.output = []
        self.indent = 0
        node.accept(self)
        return "\n".join(self.output)
    
    def _add_line(self, text):
        self.output.append("  " * self.indent + text)
    
    def visit_block(self, node):
        self._add_line("Block:")
        self.indent += 1
        if node.variables:
            self._add_line(f"Variables: {', '.join(node.variables)}")
        if node.procedures:
            self._add_line("Procedures:")
            self.indent += 1
            for name, body in node.procedures:
                self._add_line(f"Procedure '{name}':")
                self.indent += 1
                body.accept(self)
                self.indent -= 1
            self.indent -= 1
        self._add_line("Statement:")
        self.indent += 1
        node.statement.accept(self)
        self.indent -= 1
        self.indent -= 1
    
    def visit_assign(self, node):
        self._add_line(f"Assignment: {node.var_name} :=")
        self.indent += 1
        node.expression.accept(self)
        self.indent -= 1
    
    def visit_call(self, node):
        self._add_line(f"Call: {node.proc_name}")
    
    def visit_read(self, node):
        self._add_line(f"Read: {node.var_name}")
    
    def visit_write(self, node):
        self._add_line("Write:")
        self.indent += 1
        node.expression.accept(self)
        self.indent -= 1
    
    def visit_compound(self, node):
        self._add_line("Compound:")
        self.indent += 1
        for stmt in node.statements:
            stmt.accept(self)
        self.indent -= 1
    
    def visit_nested_block(self, node):
        self._add_line("Nested Block:")
        self.indent += 1
        if node.variables:
            self._add_line(f"Local Variables: {', '.join(node.variables)}")
        for stmt in node.statements:
            stmt.accept(self)
        self.indent -= 1
    
    def visit_if(self, node):
        self._add_line("If:")
        self.indent += 1
        self._add_line("Condition:")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
        self._add_line("Then:")
        self.indent += 1
        node.then_statement.accept(self)
        self.indent -= 1
        self.indent -= 1
    
    def visit_while(self, node):
        self._add_line("While:")
        self.indent += 1
        self._add_line("Condition:")
        self.indent += 1
        node.condition.accept(self)
        self.indent -= 1
        self._add_line("Body:")
        self.indent += 1
        node.body.accept(self)
        self.indent -= 1
        self.indent -= 1
    
    def visit_operation(self, node):
        self._add_line(f"Operation: {node.operator}")
        self.indent += 1
        self._add_line("Left:")
        self.indent += 1
        node.left.accept(self)
        self.indent -= 1
        self._add_line("Right:")
        self.indent += 1
        node.right.accept(self)
        self.indent -= 1
        self.indent -= 1
    
    def visit_variable(self, node):
        self._add_line(f"Variable: {node.name}")
    
    def visit_number(self, node):
        self._add_line(f"Number: {node.value}")


@plugin_function(
    name="optimization_hints",
    description="Provides optimization suggestions",
    dependencies=["static_analysis", "complexity_analyzer"]
)
def analyze_optimizations(ast, context, messages):
    """Analyze code and suggest optimizations"""
    
    # Get results from other plugins
    static_results = context.plugin_results.get("static_analysis", {})
    complexity_results = context.plugin_results.get("complexity_analyzer", {})
    
    hints = []
    
    # Check for unused variables
    declared = set(static_results.get("declared_variables", []))
    used = set(static_results.get("used_variables", []))
    unused = declared - used
    
    if unused:
        hints.append(f"Unused variables detected: {', '.join(unused)}")
        messages.warning(f"Found {len(unused)} unused variable(s)")
    
    # Check complexity
    complexity = complexity_results.get("cyclomatic_complexity", 0)
    if complexity > 10:
        hints.append(f"High cyclomatic complexity ({complexity}). Consider refactoring.")
        messages.warning(f"High code complexity: {complexity}")
    
    # Check nesting depth
    max_depth = complexity_results.get("max_nesting_depth", 0)
    if max_depth > 3:
        hints.append(f"Deep nesting detected (depth: {max_depth}). Consider extracting procedures.")
    
    context.generated_outputs["optimization_hints"] = "\n".join(hints) if hints else "No optimization suggestions."
    
    return {
        "hints_count": len(hints),
        "unused_variables": len(unused),
        "needs_refactoring": complexity > 10 or max_depth > 3
    }


@plugin_function(
    name="documentation_generator",
    description="Generates documentation for PL/0 programs",
    dependencies=["static_analysis"]
)
def generate_documentation(ast, context, messages):
    """Generate program documentation"""
    
    static_results = context.plugin_results.get("static_analysis", {})
    
    doc = ["# PL/0 Program Documentation\n"]
    
    # Variables section
    variables = static_results.get("declared_variables", [])
    if variables:
        doc.append("## Variables")
        for var in sorted(variables):
            doc.append(f"- `{var}`: Integer variable")
        doc.append("")
    
    # Procedures section
    procedures = static_results.get("procedures", [])
    if procedures:
        doc.append("## Procedures")
        for proc in sorted(procedures):
            doc.append(f"- `{proc}()`: User-defined procedure")
        doc.append("")
    
    # Statistics section
    doc.append("## Statistics")
    doc.append(f"- Variables declared: {len(variables)}")
    doc.append(f"- Procedures defined: {len(procedures)}")
    
    # Add complexity info if available
    complexity_results = context.plugin_results.get("complexity_analyzer", {})
    if complexity_results:
        doc.append(f"- Lines of code: {complexity_results.get('lines_of_code', 0)}")
        doc.append(f"- Cyclomatic complexity: {complexity_results.get('cyclomatic_complexity', 0)}")
        doc.append(f"- Maximum nesting depth: {complexity_results.get('max_nesting_depth', 0)}")
    
    documentation = "\n".join(doc)
    context.generated_outputs["documentation"] = documentation
    
    messages.info("Generated program documentation")
    return {"generated": True, "sections": 3}
