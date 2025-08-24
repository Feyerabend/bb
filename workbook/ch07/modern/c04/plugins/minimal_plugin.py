# simple_plugin.py
# minimal plugin example

@plugin_function(
    name="variable_counter",
    description="Counts the number of variables and their usage",
    version="1.0",
    dependencies=["static_analysis"]
)
def count_variables(ast, context, messages):
    """Count variables and their usage patterns"""
    
    # Get static analysis results
    static_results = context.plugin_results.get("static_analysis", {})
    
    declared_vars = static_results.get("declared_variables", [])
    used_vars = static_results.get("used_variables", [])
    undefined_vars = static_results.get("undefined_variables", [])
    
    # Create summary
    summary = {
        "total_declared": len(declared_vars),
        "total_used": len(used_vars),
        "total_undefined": len(undefined_vars),
        "usage_ratio": len(used_vars) / max(len(declared_vars), 1)
    }
    
    # Generate report
    report_lines = [
        "Variable Usage Report",
        "=" * 20,
        f"Variables declared: {summary['total_declared']}",
        f"Variables used: {summary['total_used']}",
        f"Undefined variables: {summary['total_undefined']}",
        f"Usage ratio: {summary['usage_ratio']:.2%}"
    ]
    
    if declared_vars:
        report_lines.extend([
            "",
            "Declared variables:",
            "- " + ", ".join(sorted(declared_vars))
        ])
    
    if undefined_vars:
        report_lines.extend([
            "",
            "Undefined variables (errors):",
            "- " + ", ".join(sorted(undefined_vars))
        ])
    
    context.generated_outputs["variable_report"] = "\n".join(report_lines)
    
    messages.info(f"Variable analysis complete: {summary['total_declared']} declared, {summary['total_used']} used")
    
    if summary['total_undefined'] > 0:
        messages.warning(f"Found {summary['total_undefined']} undefined variable(s)")
    
    return summary


@plugin_function(
    name="statement_counter", 
    description="Counts different types of statements",
    version="1.0"
)
def count_statements(ast, context, messages):
    """Count different types of statements in the program"""
    
    counter = StatementCounter()
    counts = counter.count(ast)
    
    # Generate summary
    total_statements = sum(counts.values())
    
    report_lines = [
        "Statement Count Report",
        "=" * 21,
        f"Total statements: {total_statements}"
    ]
    
    for stmt_type, count in sorted(counts.items()):
        if count > 0:
            percentage = (count / total_statements) * 100 if total_statements > 0 else 0
            report_lines.append(f"{stmt_type}: {count} ({percentage:.1f}%)")
    
    context.generated_outputs["statement_report"] = "\n".join(report_lines)
    
    messages.info(f"Found {total_statements} total statements")
    
    return {
        "total_statements": total_statements,
        "statement_breakdown": counts,
        "most_common": max(counts.items(), key=lambda x: x[1]) if counts else ("none", 0)
    }


class StatementCounter(Visitor):
    """Helper visitor to count different statement types"""
    
    def __init__(self):
        self.counts = {
            "assignments": 0,
            "procedure_calls": 0,
            "read_statements": 0,
            "write_statements": 0,
            "if_statements": 0,
            "while_statements": 0,
            "compound_statements": 0,
            "nested_blocks": 0
        }
    
    def count(self, ast):
        ast.accept(self)
        return self.counts
    
    def visit_block(self, node):
        for _, proc_body in node.procedures:
            proc_body.accept(self)
        node.statement.accept(self)
    
    def visit_assign(self, node):
        self.counts["assignments"] += 1
        node.expression.accept(self)
    
    def visit_call(self, node):
        self.counts["procedure_calls"] += 1
    
    def visit_read(self, node):
        self.counts["read_statements"] += 1
    
    def visit_write(self, node):
        self.counts["write_statements"] += 1
        node.expression.accept(self)
    
    def visit_compound(self, node):
        self.counts["compound_statements"] += 1
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node):
        self.counts["nested_blocks"] += 1
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if(self, node):
        self.counts["if_statements"] += 1
        node.condition.accept(self)
        node.then_statement.accept(self)
    
    def visit_while(self, node):
        self.counts["while_statements"] += 1
        node.condition.accept(self)
        node.body.accept(self)
    
    def visit_operation(self, node):
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_number(self, node):
        pass