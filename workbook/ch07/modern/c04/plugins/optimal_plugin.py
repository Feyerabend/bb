# optimization_plugin.py
# Fixed version of the optimization plugin

class OptimizationPlugin(Plugin):
    """Performs constant folding and algebraic optimizations"""
    
    def __init__(self):
        super().__init__(
            "optimizer", 
            "Performs constant folding and algebraic optimizations", 
            "1.0"
        )
        self.dependencies = ["static_analysis"]
    
    def run(self, ast, context, messages):
        optimizer = OptimizationAnalyzer()
        
        # Analyze the AST for optimization opportunities
        optimizations = optimizer.analyze(ast)
        
        total_optimizations = sum(optimizations.values())
        
        if total_optimizations > 0:
            messages.info(f"Found {total_optimizations} optimization opportunities")
        else:
            messages.info("No obvious optimizations found")
        
        # Generate optimization report
        report_lines = [
            "Optimization Analysis Report",
            "=" * 28,
            f"Total opportunities found: {total_optimizations}",
            ""
        ]
        
        if optimizations["constant_folding"] > 0:
            report_lines.extend([
                f"Constant folding opportunities: {optimizations['constant_folding']}",
                "- Operations like '5 + 3' can be computed at compile time",
                ""
            ])
        
        if optimizations["algebraic_simplification"] > 0:
            report_lines.extend([
                f"Algebraic simplifications: {optimizations['algebraic_simplification']}",
                "- Operations like 'x + 0', 'x * 1', 'x - 0' can be simplified",
                ""
            ])
        
        if optimizations["dead_code"] > 0:
            report_lines.extend([
                f"Dead code blocks: {optimizations['dead_code']}",
                "- Unreachable code after constant condition evaluation",
                ""
            ])
        
        if optimizations["strength_reduction"] > 0:
            report_lines.extend([
                f"Strength reduction opportunities: {optimizations['strength_reduction']}",
                "- Expensive operations like 'x * 2' can become 'x + x'",
                ""
            ])
        
        if total_optimizations == 0:
            report_lines.append("The code is already well-optimized!")
        
        context.generated_outputs["optimization_analysis"] = "\n".join(report_lines)
        
        return optimizations


class OptimizationAnalyzer(Visitor):
    """Analyzes AST for optimization opportunities without modifying it"""
    
    def __init__(self):
        self.optimizations = {
            "constant_folding": 0,
            "algebraic_simplification": 0,
            "dead_code": 0,
            "strength_reduction": 0
        }
    
    def analyze(self, ast):
        ast.accept(self)
        return self.optimizations
    
    def visit_block(self, node):
        for _, proc_body in node.procedures:
            proc_body.accept(self)
        node.statement.accept(self)
    
    def visit_assign(self, node):
        node.expression.accept(self)
    
    def visit_call(self, node):
        pass
    
    def visit_read(self, node):
        pass
    
    def visit_write(self, node):
        node.expression.accept(self)
    
    def visit_compound(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if(self, node):
        # Check for constant conditions
        if self._is_constant_condition(node.condition):
            self.optimizations["dead_code"] += 1
        
        node.condition.accept(self)
        node.then_statement.accept(self)
    
    def visit_while(self, node):
        # Check for constant conditions
        if self._is_constant_condition(node.condition):
            self.optimizations["dead_code"] += 1
        
        node.condition.accept(self)
        node.body.accept(self)
    
    def visit_operation(self, node):
        # Check for constant folding opportunities
        if self._can_constant_fold(node):
            self.optimizations["constant_folding"] += 1
        
        # Check for algebraic simplifications
        if self._can_algebraic_simplify(node):
            self.optimizations["algebraic_simplification"] += 1
        
        # Check for strength reduction
        if self._can_strength_reduce(node):
            self.optimizations["strength_reduction"] += 1
        
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_number(self, node):
        pass
    
    def _is_constant_condition(self, node):
        """Check if a condition evaluates to a constant"""
        return (isinstance(node, OperationNode) and 
                isinstance(node.left, NumberNode) and 
                isinstance(node.right, NumberNode))
    
    def _can_constant_fold(self, node):
        """Check if operation can be constant folded"""
        return (isinstance(node, OperationNode) and
                isinstance(node.left, NumberNode) and 
                isinstance(node.right, NumberNode))
    
    def _can_algebraic_simplify(self, node):
        """Check for algebraic simplification opportunities"""
        if not isinstance(node, OperationNode):
            return False
        
        # x + 0, x - 0, x * 1, x / 1
        if isinstance(node.right, NumberNode):
            if node.operator in ["+", "-"] and node.right.value == 0:
                return True
            if node.operator == "*" and node.right.value == 1:
                return True
            if node.operator == "/" and node.right.value == 1:
                return True
        
        # 0 + x, 1 * x
        if isinstance(node.left, NumberNode):
            if node.operator == "+" and node.left.value == 0:
                return True
            if node.operator == "*" and node.left.value == 1:
                return True
        
        # x * 0, 0 * x
        if ((isinstance(node.left, NumberNode) and node.left.value == 0) or
            (isinstance(node.right, NumberNode) and node.right.value == 0)) and node.operator == "*":
            return True
        
        return False
    
    def _can_strength_reduce(self, node):
        """Check for strength reduction opportunities"""
        if not isinstance(node, OperationNode):
            return False
        
        # x * 2 or 2 * x (can become x + x)
        if node.operator == "*":
            if isinstance(node.right, NumberNode) and node.right.value == 2:
                return True
            if isinstance(node.left, NumberNode) and node.left.value == 2:
                return True
        
        return False


@plugin_function(
    name="peephole_optimizer",
    description="Identifies peephole optimization opportunities",
    dependencies=["static_analysis"]
)
def analyze_peephole_optimizations(ast, context, messages):
    """Look for peephole optimization patterns"""
    
    analyzer = PeepholeAnalyzer()
    patterns = analyzer.analyze(ast)
    
    total_patterns = sum(patterns.values())
    
    report_lines = [
        "Peephole Optimization Report",
        "=" * 27,
        f"Total patterns found: {total_patterns}",
        ""
    ]
    
    if patterns["redundant_assignments"] > 0:
        report_lines.extend([
            f"Redundant assignments: {patterns['redundant_assignments']}",
            "- Variables assigned and then immediately reassigned",
            ""
        ])
    
    if patterns["unnecessary_operations"] > 0:
        report_lines.extend([
            f"Unnecessary operations: {patterns['unnecessary_operations']}",
            "- Operations that don't change the result",
            ""
        ])
    
    if total_patterns == 0:
        report_lines.append("No peephole optimization patterns detected.")
    
    context.generated_outputs["peephole_analysis"] = "\n".join(report_lines)
    
    messages.info(f"Peephole analysis found {total_patterns} optimization patterns")
    
    return patterns


class PeepholeAnalyzer(Visitor):
    """Analyzes for peephole optimization patterns"""
    
    def __init__(self):
        self.patterns = {
            "redundant_assignments": 0,
            "unnecessary_operations": 0
        }
        self.recent_assignments = {}  # Track recent assignments
    
    def analyze(self, ast):
        ast.accept(self)
        return self.patterns
    
    def visit_block(self, node):
        for _, proc_body in node.procedures:
            proc_body.accept(self)
        node.statement.accept(self)
    
    def visit_assign(self, node):
        # Check for redundant assignment pattern
        if node.var_name in self.recent_assignments:
            self.patterns["redundant_assignments"] += 1
        
        self.recent_assignments[node.var_name] = True
        node.expression.accept(self)
    
    def visit_call(self, node):
        # Procedure calls can modify variables, so clear tracking
        self.recent_assignments.clear()
    
    def visit_read(self, node):
        # Reading modifies a variable
        self.recent_assignments[node.var_name] = True
    
    def visit_write(self, node):
        node.expression.accept(self)
    
    def visit_compound(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node):
        # Save current state
        old_assignments = self.recent_assignments.copy()
        
        for stmt in node.statements:
            stmt.accept(self)
        
        # Restore state (variables in nested block may shadow outer ones)
        self.recent_assignments = old_assignments
    
    def visit_if(self, node):
        node.condition.accept(self)
        # Clear assignment tracking since execution is conditional
        old_assignments = self.recent_assignments.copy()
        node.then_statement.accept(self)
        self.recent_assignments = old_assignments
    
    def visit_while(self, node):
        node.condition.accept(self)
        # Clear assignment tracking since loop execution varies
        old_assignments = self.recent_assignments.copy()
        node.body.accept(self)
        self.recent_assignments = old_assignments
    
    def visit_operation(self, node):
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_number(self, node):
        pass
