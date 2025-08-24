# Updated complex_plugin.py - plugins handle their own file outputs

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
        
        # Write complexity report
        if context.base_name:
            report_path = context.get_output_path(f"{context.base_name}_complexity.txt")
            self._write_complexity_report(metrics, report_path, messages)
        
        messages.info(f"Code complexity: {metrics['cyclomatic_complexity']}")
        return metrics
    
    def _write_complexity_report(self, metrics, filepath, messages):
        try:
            with open(filepath, 'w') as f:
                f.write("Code Complexity Analysis Report\n")
                f.write("=" * 30 + "\n\n")
                
                f.write(f"Cyclomatic Complexity: {metrics['cyclomatic_complexity']}\n")
                f.write(f"Lines of Code: {metrics['lines_of_code']}\n")
                f.write(f"Number of Procedures: {metrics['num_procedures']}\n")
                f.write(f"Maximum Nesting Depth: {metrics['max_nesting_depth']}\n\n")
                
                # Add interpretation
                f.write("Interpretation:\n")
                cc = metrics['cyclomatic_complexity']
                if cc <= 5:
                    f.write("• Low complexity - Easy to test and maintain\n")
                elif cc <= 10:
                    f.write("• Moderate complexity - Reasonably complex\n")
                elif cc <= 20:
                    f.write("• High complexity - Complex, difficult to test\n")
                else:
                    f.write("• Very high complexity - Extremely complex, error-prone\n")
                
                depth = metrics['max_nesting_depth']
                if depth <= 2:
                    f.write("• Good nesting depth - Easy to follow\n")
                elif depth <= 4:
                    f.write("• Moderate nesting depth - Still manageable\n")
                else:
                    f.write("• Deep nesting - Consider refactoring\n")
            
            messages.info(f"Complexity report saved: {os.path.basename(filepath)}")
        except Exception as e:
            messages.error(f"Failed to write complexity report: {e}")


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


# Function-based plugin examples with file output
@plugin_function(
    name="ast_printer", 
    description="Pretty prints the AST structure",
    dependencies=[]
)
def print_ast(ast, context, messages):
    """Print AST structure for debugging"""
    printer = ASTPrinter()
    ast_str = printer.print_ast(ast)
    
    # Write AST structure to file
    if context.base_name:
        ast_path = context.get_output_path(f"{context.base_name}_ast.txt")
        try:
            with open(ast_path, 'w') as f:
                f.write("Abstract Syntax Tree Structure\n")
                f.write("=" * 31 + "\n\n")
                f.write(ast_str)
            messages.info(f"AST structure saved: {os.path.basename(ast_path)}")
        except Exception as e:
            messages.error(f"Failed to write AST file: {e}")
    
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
        hints.append("  → Consider removing unused variables to improve code clarity")
        messages.warning(f"Found {len(unused)} unused variable(s)")
    
    # Check complexity
    complexity = complexity_results.get("cyclomatic_complexity", 0)
    if complexity > 10:
        hints.append(f"High cyclomatic complexity ({complexity}). Consider refactoring.")
        hints.append("  → Break down complex procedures into smaller ones")
        messages.warning(f"High code complexity: {complexity}")
    
    # Check nesting depth
    max_depth = complexity_results.get("max_nesting_depth", 0)
    if max_depth > 3:
        hints.append(f"Deep nesting detected (depth: {max_depth}). Consider extracting procedures.")
        hints.append("  → Use early returns or extract nested logic into procedures")
    
    # Check procedure count
    num_procedures = complexity_results.get("num_procedures", 0)
    if num_procedures == 0 and complexity > 5:
        hints.append("No procedures defined. Consider breaking code into procedures for better organization.")
    
    # Write optimization hints to file
    if context.base_name:
        hints_path = context.get_output_path(f"{context.base_name}_optimization_hints.txt")
        try:
            with open(hints_path, 'w') as f:
                f.write("Optimization Hints Report\n")
                f.write("=" * 24 + "\n\n")
                
                if hints:
                    f.write("Suggestions for improvement:\n\n")
                    for i, hint in enumerate(hints, 1):
                        f.write(f"{i}. {hint}\n")
                else:
                    f.write("No optimization suggestions found.\n")
                    f.write("Your code appears to be well-structured!\n")
                
                f.write(f"\n\nCode Statistics:\n")
                f.write(f"• Variables declared: {len(declared)}\n")
                f.write(f"• Variables used: {len(used)}\n")
                f.write(f"• Cyclomatic complexity: {complexity}\n")
                f.write(f"• Maximum nesting depth: {max_depth}\n")
                f.write(f"• Number of procedures: {num_procedures}\n")
            
            messages.info(f"Optimization hints saved: {os.path.basename(hints_path)}")
        except Exception as e:
            messages.error(f"Failed to write optimization hints: {e}")
    
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
    
    # Program overview
    doc.append("## Program Overview")
    doc.append(f"This document describes a PL/0 program compiled from `{context.source_filename or 'source file'}`.\n")
    
    # Variables section
    variables = static_results.get("declared_variables", [])
    if variables:
        doc.append("## Variables")
        doc.append("The following integer variables are declared in this program:")
        doc.append("")
        for var in sorted(variables):
            doc.append(f"- **`{var}`**: Integer variable")
        doc.append(f"\nTotal variables: {len(variables)}\n")
    
    # Procedures section
    procedures = static_results.get("procedures", [])
    if procedures:
        doc.append("## Procedures")
        doc.append("The following user-defined procedures are available:")
        doc.append("")
        for proc in sorted(procedures):
            doc.append(f"- **`{proc}()`**: User-defined procedure (no parameters)")
        doc.append(f"\nTotal procedures: {len(procedures)}\n")
    
    # Statistics section
    doc.append("## Program Statistics")
    doc.append(f"- Variables declared: {len(variables)}")
    doc.append(f"- Procedures defined: {len(procedures)}")
    
    # Add complexity info if available
    complexity_results = context.plugin_results.get("complexity_analyzer", {})
    if complexity_results:
        doc.append(f"- Lines of code: {complexity_results.get('lines_of_code', 0)}")
        doc.append(f"- Cyclomatic complexity: {complexity_results.get('cyclomatic_complexity', 0)}")
        doc.append(f"- Maximum nesting depth: {complexity_results.get('max_nesting_depth', 0)}")
    
    # Language features section
    doc.append("\n## PL/0 Language Features Used")
    features_used = []
    
    if variables:
        features_used.append("- Variable declarations (`var`)")
    if procedures:
        features_used.append("- Procedure definitions (`procedure`)")
    
    # We could analyze AST for more features, but this is a basic example
    if features_used:
        doc.extend(features_used)
    else:
        doc.append("- Basic program structure")
    
    # Write documentation to file
    documentation = "\n".join(doc)
    
    if context.base_name:
        doc_path = context.get_output_path(f"{context.base_name}_documentation.md")
        try:
            with open(doc_path, 'w') as f:
                f.write(documentation)
            messages.info(f"Program documentation saved: {os.path.basename(doc_path)}")
        except Exception as e:
            messages.error(f"Failed to write documentation: {e}")
    
    context.generated_outputs["documentation"] = documentation
    
    messages.info("Generated program documentation")
    return {"generated": True, "sections": 4}
