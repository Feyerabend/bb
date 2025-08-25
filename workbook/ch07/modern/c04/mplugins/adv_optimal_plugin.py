# advanced_optimization.py
# Advanced optimization analysis (preparation for future AST transformations)

class AdvancedOptimizationPlugin(Plugin):
    """Advanced optimization analysis and transformation preparation"""
    
    def __init__(self):
        super().__init__(
            "advanced_optimizer", 
            "Advanced optimization analysis with control flow and data flow", 
            "1.0"
        )
        self.dependencies = ["static_analysis"]
    
    def run(self, ast, context, messages):
        analyzer = AdvancedOptimizer(messages)
        analysis = analyzer.analyze(ast)
        
        # Generate comprehensive optimization report
        report = self._generate_report(analysis)
        context.generated_outputs["advanced_optimization_report"] = report
        
        total_opportunities = sum(analysis["optimizations"].values())
        messages.info(f"Advanced analysis found {total_opportunities} optimization opportunities")
        
        return analysis
    
    def _generate_report(self, analysis):
        """Generate detailed optimization report"""
        lines = [
            "Advanced Optimization Analysis Report",
            "=" * 35,
            "",
            f"Control Flow Analysis:",
            f"  • Basic blocks: {analysis['control_flow']['basic_blocks']}",
            f"  • Loop nesting depth: {analysis['control_flow']['max_loop_depth']}",
            f"  • Conditional branches: {analysis['control_flow']['conditional_branches']}",
            f"  • Unreachable code blocks: {analysis['control_flow']['unreachable_blocks']}",
            "",
            f"Data Flow Analysis:",
            f"  • Variable definitions: {analysis['data_flow']['definitions']}",
            f"  • Variable uses: {analysis['data_flow']['uses']}",
            f"  • Live variables: {len(analysis['data_flow']['live_variables'])}",
            f"  • Dead assignments: {analysis['data_flow']['dead_assignments']}",
            "",
            f"Optimization Opportunities:",
        ]
        
        opts = analysis["optimizations"]
        for opt_type, count in opts.items():
            if count > 0:
                lines.append(f"  • {opt_type.replace('_', ' ').title()}: {count}")
        
        if analysis["transformation_hints"]:
            lines.extend([
                "",
                "Transformation Hints:",
            ])
            for hint in analysis["transformation_hints"]:
                lines.append(f"  • {hint}")
        
        return "\n".join(lines)


class AdvancedOptimizer(Visitor):
    """Advanced optimization analyzer with control and data flow analysis"""
    
    def __init__(self, messages: MessageCollector):
        self.messages = messages
        
        # Analysis results
        self.control_flow = {
            "basic_blocks": 0,
            "max_loop_depth": 0,
            "current_loop_depth": 0,
            "conditional_branches": 0,
            "unreachable_blocks": 0
        }
        
        self.data_flow = {
            "definitions": 0,  # Variable assignments
            "uses": 0,         # Variable uses
            "live_variables": set(),
            "dead_assignments": 0,
            "variable_states": {}  # Track variable state through program
        }
        
        self.optimizations = {
            "loop_invariant_code": 0,
            "common_subexpression": 0,
            "dead_code_elimination": 0,
            "constant_propagation": 0,
            "copy_propagation": 0,
            "loop_unrolling": 0,
            "tail_recursion": 0,
            "register_allocation": 0
        }
        
        self.transformation_hints = []
        self.expression_cache = {}  # For common subexpression detection
        self.current_scope_vars = set()
        self.loop_invariant_candidates = []
    
    def analyze(self, ast):
        """Perform comprehensive analysis"""
        ast.accept(self)
        
        # Post-analysis processing
        self._analyze_register_pressure()
        self._detect_optimization_patterns()
        
        return {
            "control_flow": self.control_flow,
            "data_flow": self.data_flow,
            "optimizations": self.optimizations,
            "transformation_hints": self.transformation_hints
        }
    
    def visit_block(self, node: BlockNode):
        """Analyze block structure"""
        self.control_flow["basic_blocks"] += 1
        
        # Track scope variables
        old_vars = self.current_scope_vars.copy()
        self.current_scope_vars.update(node.variables)
        
        # Analyze procedures
        for proc_name, proc_body in node.procedures:
            self.messages.debug(f"Analyzing procedure: {proc_name}")
            
            # Check for tail recursion opportunities
            if self._has_tail_recursion(proc_body, proc_name):
                self.optimizations["tail_recursion"] += 1
                self.transformation_hints.append(f"Procedure '{proc_name}' can be tail-call optimized")
            
            proc_body.accept(self)
        
        node.statement.accept(self)
        
        # Restore scope
        self.current_scope_vars = old_vars
    
    def visit_assign(self, node: AssignNode):
        """Analyze assignment for optimization opportunities"""
        self.data_flow["definitions"] += 1
        
        # Check for constant propagation
        expr_result = self._analyze_expression(node.expression)
        if expr_result["is_constant"]:
            self.optimizations["constant_propagation"] += 1
            self.transformation_hints.append(
                f"Variable '{node.var_name}' can be constant propagated"
            )
        
        # Check for copy propagation (x := y)
        if isinstance(node.expression, VariableNode):
            self.optimizations["copy_propagation"] += 1
            self.transformation_hints.append(
                f"Assignment '{node.var_name} := {node.expression.name}' is copy propagation candidate"
            )
        
        # Track variable state
        self.data_flow["variable_states"][node.var_name] = {
            "last_assignment": "current",
            "is_constant": expr_result["is_constant"],
            "expression": str(node.expression)
        }
        
        node.expression.accept(self)
    
    def visit_call(self, node: CallNode):
        """Analyze procedure calls"""
        # Procedure calls invalidate certain optimizations
        self.data_flow["variable_states"].clear()  # Conservative approach
    
    def visit_read(self, node: ReadNode):
        """Analyze input operations"""
        self.data_flow["definitions"] += 1
        
        # Input invalidates constant propagation for this variable
        if node.var_name in self.data_flow["variable_states"]:
            self.data_flow["variable_states"][node.var_name]["is_constant"] = False
    
    def visit_write(self, node: WriteNode):
        """Analyze output operations"""
        expr_result = self._analyze_expression(node.expression)
        node.expression.accept(self)
    
    def visit_compound(self, node: CompoundNode):
        """Analyze compound statements"""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node: NestedBlockNode):
        """Analyze nested blocks"""
        self.control_flow["basic_blocks"] += 1
        
        # New scope
        old_vars = self.current_scope_vars.copy()
        self.current_scope_vars.update(node.variables)
        
        for stmt in node.statements:
            stmt.accept(self)
        
        # Restore scope
        self.current_scope_vars = old_vars
    
    def visit_if(self, node: IfNode):
        """Analyze conditional statements"""
        self.control_flow["conditional_branches"] += 1
        
        # Analyze condition for constant folding
        cond_result = self._analyze_expression(node.condition)
        if cond_result["is_constant"]:
            self.optimizations["dead_code_elimination"] += 1
            self.transformation_hints.append("If statement has constant condition - can eliminate dead branch")
        
        node.condition.accept(self)
        
        # New basic block for then branch
        self.control_flow["basic_blocks"] += 1
        node.then_statement.accept(self)
    
    def visit_while(self, node: WhileNode):
        """Analyze loop structures"""
        self.control_flow["conditional_branches"] += 1
        self.control_flow["current_loop_depth"] += 1
        self.control_flow["max_loop_depth"] = max(
            self.control_flow["max_loop_depth"], 
            self.control_flow["current_loop_depth"]
        )
        
        # Analyze loop condition
        cond_result = self._analyze_expression(node.condition)
        
        # Check for loop invariant code
        old_invariant_candidates = self.loop_invariant_candidates.copy()
        
        # Analyze loop body
        self.control_flow["basic_blocks"] += 1  # Loop body is a basic block
        node.body.accept(self)
        
        # Check for loop unrolling opportunities
        if self._can_unroll_loop(node):
            self.optimizations["loop_unrolling"] += 1
            self.transformation_hints.append("Loop is candidate for unrolling")
        
        # Detect loop invariant code
        invariant_count = len(self.loop_invariant_candidates) - len(old_invariant_candidates)
        if invariant_count > 0:
            self.optimizations["loop_invariant_code"] += invariant_count
            self.transformation_hints.append(f"Found {invariant_count} loop invariant expressions")
        
        self.control_flow["current_loop_depth"] -= 1
        
        node.condition.accept(self)
    
    def visit_operation(self, node: OperationNode):
        """Analyze operations for optimization opportunities"""
        # Generate expression signature for common subexpression detection
        expr_sig = self._get_expression_signature(node)
        
        if expr_sig in self.expression_cache:
            self.optimizations["common_subexpression"] += 1
            self.transformation_hints.append(f"Common subexpression detected: {expr_sig}")
        else:
            self.expression_cache[expr_sig] = True
        
        # Check if this could be loop invariant
        if self.control_flow["current_loop_depth"] > 0:
            if self._is_loop_invariant_expression(node):
                self.loop_invariant_candidates.append(expr_sig)
        
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node: VariableNode):
        """Analyze variable usage"""
        self.data_flow["uses"] += 1
        self.data_flow["live_variables"].add(node.name)
    
    def visit_number(self, node: NumberNode):
        """Analyze number literals"""
        pass
    
    def _analyze_expression(self, expr):
        """Analyze expression properties"""
        if isinstance(expr, NumberNode):
            return {"is_constant": True, "value": expr.value}
        elif isinstance(expr, VariableNode):
            var_state = self.data_flow["variable_states"].get(expr.name, {})
            return {"is_constant": var_state.get("is_constant", False)}
        elif isinstance(expr, OperationNode):
            left_result = self._analyze_expression(expr.left)
            right_result = self._analyze_expression(expr.right)
            return {
                "is_constant": left_result.get("is_constant", False) and 
                              right_result.get("is_constant", False)
            }
        return {"is_constant": False}
    
    def _get_expression_signature(self, node):
        """Get a signature for expression comparison"""
        if isinstance(node, NumberNode):
            return f"NUM_{node.value}"
        elif isinstance(node, VariableNode):
            return f"VAR_{node.name}"
        elif isinstance(node, OperationNode):
            left_sig = self._get_expression_signature(node.left)
            right_sig = self._get_expression_signature(node.right)
            return f"OP_{node.operator}({left_sig},{right_sig})"
        return "UNKNOWN"
    
    def _is_loop_invariant_expression(self, node):
        """Check if expression is loop invariant"""
        if isinstance(node, NumberNode):
            return True
        elif isinstance(node, VariableNode):
            # Variable is loop invariant if not modified in current loop
            # This is a simplified check - real analysis would need def-use chains
            return node.name not in self.current_scope_vars
        elif isinstance(node, OperationNode):
            return (self._is_loop_invariant_expression(node.left) and 
                   self._is_loop_invariant_expression(node.right))
        return False
    
    def _can_unroll_loop(self, node):
        """Check if loop can be unrolled"""
        # Simple heuristic: small loops with constant bounds
        if isinstance(node.condition, OperationNode):
            # Check for simple counter-based loops
            return (isinstance(node.condition.left, VariableNode) and
                   isinstance(node.condition.right, NumberNode) and
                   node.condition.right.value <= 10)  # Small constant
        return False
    
    def _has_tail_recursion(self, proc_body, proc_name):
        """Check if procedure has tail recursion"""
        # Simple check - last statement is a call to itself
        last_stmt = self._get_last_statement(proc_body.statement)
        return (isinstance(last_stmt, CallNode) and 
               last_stmt.proc_name == proc_name)
    
    def _get_last_statement(self, stmt):
        """Get the last executed statement in a block"""
        if isinstance(stmt, CompoundNode) and stmt.statements:
            return self._get_last_statement(stmt.statements[-1])
        elif isinstance(stmt, NestedBlockNode) and stmt.statements:
            return self._get_last_statement(stmt.statements[-1])
        return stmt
    
    def _analyze_register_pressure(self):
        """Analyze register allocation opportunities"""
        # Simple heuristic based on live variable count
        live_var_count = len(self.data_flow["live_variables"])
        
        if live_var_count > 8:  # Assume 8 registers available
            self.optimizations["register_allocation"] += live_var_count - 8
            self.transformation_hints.append(
                f"High register pressure: {live_var_count} live variables"
            )
    
    def _detect_optimization_patterns(self):
        """Detect additional optimization patterns"""
        # Check for dead assignments
        for var_name, state in self.data_flow["variable_states"].items():
            if var_name not in self.data_flow["live_variables"]:
                self.data_flow["dead_assignments"] += 1