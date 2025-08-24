# Updated optimal_plugin.py - plugins handle their own file outputs

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
        
        # Write optimization report to file
        if context.base_name:
            report_path = context.get_output_path(f"{context.base_name}_optimizations.txt")
            self._write_optimization_report(optimizations, report_path, messages)
        
        return optimizations
    
    def _write_optimization_report(self, optimizations, filepath, messages):
        try:
            total_optimizations = sum(optimizations.values())
            
            with open(filepath, 'w') as f:
                f.write("Optimization Analysis Report\n")
                f.write("=" * 28 + "\n\n")
                f.write(f"Total opportunities found: {total_optimizations}\n\n")
                
                if optimizations["constant_folding"] > 0:
                    f.write(f"Constant folding opportunities: {optimizations['constant_folding']}\n")
                    f.write("• Operations like '5 + 3' can be computed at compile time\n")
                    f.write("• This reduces runtime computation and improves performance\n")
                    f.write("• Example: Replace '2 + 3' with '5'\n\n")
                
                if optimizations["algebraic_simplification"] > 0:
                    f.write(f"Algebraic simplifications: {optimizations['algebraic_simplification']}\n")
                    f.write("• Operations like 'x + 0', 'x * 1', 'x - 0' can be simplified\n")
                    f.write("• Examples:\n")
                    f.write("  - 'x + 0' → 'x'\n")
                    f.write("  - 'x * 1' → 'x'\n")
                    f.write("  - 'x * 0' → '0'\n")
                    f.write("  - '0 + x' → 'x'\n\n")
                
                if optimizations["dead_code"] > 0:
                    f.write(f"Dead code blocks: {optimizations['dead_code']}\n")
                    f.write("• Unreachable code after constant condition evaluation\n")
                    f.write("• Example: 'if 0 = 1 then ...' can be eliminated\n")
                    f.write("• This reduces code size and improves clarity\n\n")
                
                if optimizations["strength_reduction"] > 0:
                    f.write(f"Strength reduction opportunities: {optimizations['strength_reduction']}\n")
                    f.write("• Expensive operations can be replaced with cheaper ones\n")
                    f.write("• Examples:\n")
                    f.write("  - 'x * 2' → 'x + x' (addition is faster than multiplication)\n")
                    f.write("  - Powers of 2 multiplication can use bit shifts (in assembly)\n\n")
                
                if total_optimizations == 0:
                    f.write("The code is already well-optimized!\n")
                    f.write("No obvious optimization patterns were detected.\n")
                else:
                    f.write("Recommendations:\n")
                    f.write("• These optimizations can be applied automatically by a compiler\n")
                    f.write("• Manual optimization may improve code readability\n")
                    f.write("• Consider using a modern optimizing compiler\n")
            
            messages.info(f"Optimization report saved: {os.path.basename(filepath)}")
        except Exception as e:
            messages.error(f"Failed to write optimization report: {e}")


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
    
    # Write peephole analysis to file
    if context.base_name:
        report_path = context.get_output_path(f"{context.base_name}_peephole.txt")
        try:
            with open(report_path, 'w') as f:
                f.write("Peephole Optimization Report\n")
                f.write("=" * 27 + "\n\n")
                f.write(f"Total patterns found: {total_patterns}\n\n")
                
                if patterns["redundant_assignments"] > 0:
                    f.write(f"Redundant assignments: {patterns['redundant_assignments']}\n")
                    f.write("• Variables assigned and then immediately reassigned\n")
                    f.write("• Example: x := 5; x := 7; (first assignment is redundant)\n")
                    f.write("• This wastes computation cycles\n\n")
                
                if patterns["unnecessary_operations"] > 0:
                    f.write(f"Unnecessary operations: {patterns['unnecessary_operations']}\n")
                    f.write("• Operations that don't change the result\n")
                    f.write("• These can be eliminated to improve performance\n\n")
                
                if total_patterns == 0:
                    f.write("No peephole optimization patterns detected.\n")
                    f.write("The code has efficient local instruction sequences.\n")
                else:
                    f.write("Peephole optimization benefits:\n")
                    f.write("• Reduces instruction count\n")
                    f.write("• Improves execution speed\n")
                    f.write("• Can be applied automatically by compilers\n")
                    f.write("• Works on small windows of instructions\n")
            
            messages.info(f"Peephole analysis saved: {os.path.basename(report_path)}")
        except Exception as e:
            messages.error(f"Failed to write peephole report: {e}")
    
    context.generated_outputs["peephole_analysis"] = f"Found {total_patterns} patterns"
    
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


@plugin_function(
    name="control_flow_analyzer",
    description="Analyzes control flow patterns and complexity",
    dependencies=["static_analysis"]
)
def analyze_control_flow(ast, context, messages):
    """Analyze control flow patterns in the program"""
    
    analyzer = ControlFlowAnalyzer()
    flow_info = analyzer.analyze(ast)
    
    # Write control flow analysis to file
    if context.base_name:
        report_path = context.get_output_path(f"{context.base_name}_control_flow.txt")
        try:
            with open(report_path, 'w') as f:
                f.write("Control Flow Analysis Report\n")
                f.write("=" * 28 + "\n\n")
                
                f.write(f"Control Flow Statistics:\n")
                f.write(f"• If statements: {flow_info['if_count']}\n")
                f.write(f"• While loops: {flow_info['while_count']}\n")
                f.write(f"• Procedure calls: {flow_info['call_count']}\n")
                f.write(f"• Assignment statements: {flow_info['assign_count']}\n")
                f.write(f"• I/O operations: {flow_info['io_count']}\n\n")
                
                f.write(f"Flow Complexity:\n")
                f.write(f"• Maximum nesting level: {flow_info['max_nesting']}\n")
                f.write(f"• Total decision points: {flow_info['decision_points']}\n")
                f.write(f"• Branching factor: {flow_info['branching_factor']:.2f}\n\n")
                
                # Provide analysis
                if flow_info['max_nesting'] > 4:
                    f.write("⚠ Warning: Deep nesting detected\n")
                    f.write("  Consider refactoring to reduce complexity\n\n")
                
                if flow_info['decision_points'] > 10:
                    f.write("⚠ Warning: High number of decision points\n")
                    f.write("  This may make testing difficult\n\n")
                
                if flow_info['while_count'] > 3:
                    f.write("ℹ Info: Multiple loops detected\n")
                    f.write("  Ensure proper termination conditions\n\n")
                
                f.write("Control Flow Patterns:\n")
                if flow_info['nested_loops']:
                    f.write("• Contains nested loops\n")
                if flow_info['conditional_in_loop']:
                    f.write("• Contains conditionals inside loops\n")
                if flow_info['loop_in_conditional']:
                    f.write("• Contains loops inside conditionals\n")
                
                if not any([flow_info['nested_loops'], flow_info['conditional_in_loop'], 
                           flow_info['loop_in_conditional']]):
                    f.write("• Simple, linear control flow\n")
            
            messages.info(f"Control flow analysis saved: {os.path.basename(report_path)}")
        except Exception as e:
            messages.error(f"Failed to write control flow report: {e}")
    
    messages.info(f"Control flow analysis completed - {flow_info['decision_points']} decision points")
    return flow_info


class ControlFlowAnalyzer(Visitor):
    """Analyzes control flow patterns in the AST"""
    
    def __init__(self):
        self.if_count = 0
        self.while_count = 0
        self.call_count = 0
        self.assign_count = 0
        self.read_count = 0
        self.write_count = 0
        self.current_nesting = 0
        self.max_nesting = 0
        self.in_loop = False
        self.in_conditional = False
        self.nested_loops = False
        self.conditional_in_loop = False
        self.loop_in_conditional = False
    
    def analyze(self, ast):
        ast.accept(self)
        return {
            "if_count": self.if_count,
            "while_count": self.while_count,
            "call_count": self.call_count,
            "assign_count": self.assign_count,
            "io_count": self.read_count + self.write_count,
            "max_nesting": self.max_nesting,
            "decision_points": self.if_count + self.while_count,
            "branching_factor": (self.if_count + self.while_count) / max(1, self.assign_count + self.call_count),
            "nested_loops": self.nested_loops,
            "conditional_in_loop": self.conditional_in_loop,
            "loop_in_conditional": self.loop_in_conditional
        }
    
    def visit_block(self, node):
        for _, proc_body in node.procedures:
            proc_body.accept(self)
        node.statement.accept(self)
    
    def visit_assign(self, node):
        self.assign_count += 1
        node.expression.accept(self)
    
    def visit_call(self, node):
        self.call_count += 1
    
    def visit_read(self, node):
        self.read_count += 1
    
    def visit_write(self, node):
        self.write_count += 1
        node.expression.accept(self)
    
    def visit_compound(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node):
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if(self, node):
        self.if_count += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        
        if self.in_loop:
            self.conditional_in_loop = True
        
        old_in_conditional = self.in_conditional
        self.in_conditional = True
        
        node.condition.accept(self)
        node.then_statement.accept(self)
        
        self.in_conditional = old_in_conditional
        self.current_nesting -= 1
    
    def visit_while(self, node):
        self.while_count += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        
        if self.in_loop:
            self.nested_loops = True
        
        if self.in_conditional:
            self.loop_in_conditional = True
        
        old_in_loop = self.in_loop
        self.in_loop = True
        
        node.condition.accept(self)
        node.body.accept(self)
        
        self.in_loop = old_in_loop
        self.current_nesting -= 1
    
    def visit_operation(self, node):
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node):
        pass
    
    def visit_number(self, node):
        pass
