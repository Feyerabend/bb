# performance_profiler.py
# Performance analysis and profiling plugin

import math

class PerformanceProfilerPlugin(Plugin):
    """Analyzes performance characteristics and generates profiling reports"""
    
    def __init__(self):
        super().__init__(
            "performance_profiler", 
            "Analyzes execution time complexity and performance bottlenecks", 
            "1.0"
        )
        self.dependencies = ["static_analysis", "complexity_analyzer"]
    
    def run(self, ast, context, messages):
        profiler = PerformanceProfiler(messages)
        profile_data = profiler.analyze(ast, context)
        
        # Generate performance report
        report = self._generate_performance_report(profile_data)
        context.generated_outputs["performance_profile"] = report
        
        # Generate instrumented C code for runtime profiling
        instrumented_c = self._generate_instrumented_c(ast, profile_data)
        context.generated_outputs["instrumented_c_code"] = instrumented_c
        
        messages.info(f"Performance analysis complete - estimated complexity: O({profile_data['time_complexity']})")
        
        return profile_data
    
    def _generate_performance_report(self, profile_data):
        """Generate detailed performance report"""
        lines = [
            "Performance Analysis Report",
            "=" * 26,
            "",
            f"Time Complexity Analysis:",
            f"  • Overall complexity: O({profile_data['time_complexity']})",
            f"  • Space complexity: O({profile_data['space_complexity']})",
            f"  • Estimated operations: {profile_data['operation_count']}",
            "",
            f"Performance Hotspots:",
        ]
        
        for hotspot in profile_data['hotspots']:
            lines.append(f"  • {hotspot['type']}: {hotspot['description']} (weight: {hotspot['weight']})")
        
        lines.extend([
            "",
            f"Optimization Recommendations:",
        ])
        
        for rec in profile_data['recommendations']:
            lines.append(f"  • {rec}")
        
        lines.extend([
            "",
            f"Resource Usage:",
            f"  • Stack depth: {profile_data['max_stack_depth']}",
            f"  • Memory allocations: {profile_data['memory_operations']}",
            f"  • I/O operations: {profile_data['io_operations']}",
            f"  • Procedure calls: {profile_data['procedure_calls']}",
        ])
        
        return "\n".join(lines)
    
    def _generate_instrumented_c(self, ast, profile_data):
        """Generate C code with performance instrumentation"""
        instrumenter = CInstrumenter()
        return instrumenter.generate_instrumented_code(ast, profile_data)


class PerformanceProfiler(Visitor):
    """Analyzes performance characteristics of PL/0 programs"""
    
    def __init__(self, messages: MessageCollector):
        self.messages = messages
        
        # Performance metrics
        self.time_complexity = "1"  # Best case: constant time
        self.space_complexity = "1"
        self.operation_count = 0
        self.max_stack_depth = 0
        self.current_stack_depth = 0
        self.memory_operations = 0
        self.io_operations = 0
        self.procedure_calls = 0
        
        # Loop analysis
        self.loop_nesting = 0
        self.max_loop_nesting = 0
        self.loop_complexities = []
        
        # Hotspot detection
        self.hotspots = []
        self.recommendations = []
        
        # Context tracking
        self.in_loop = False
        self.current_procedure = None
        self.procedure_complexities = {}
    
    def analyze(self, ast, context):
        """Perform performance analysis"""
        ast.accept(self)
        
        # Calculate final complexity
        self._calculate_final_complexity()
        self._generate_recommendations()
        
        return {
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "operation_count": self.operation_count,
            "max_stack_depth": self.max_stack_depth,
            "memory_operations": self.memory_operations,
            "io_operations": self.io_operations,
            "procedure_calls": self.procedure_calls,
            "hotspots": self.hotspots,
            "recommendations": self.recommendations,
            "loop_analysis": {
                "max_nesting": self.max_loop_nesting,
                "complexities": self.loop_complexities
            }
        }
    
    def visit_block(self, node: BlockNode):
        """Analyze block performance"""
        self.current_stack_depth += 1
        self.max_stack_depth = max(self.max_stack_depth, self.current_stack_depth)
        
        # Memory for variables
        self.memory_operations += len(node.variables)
        
        # Analyze procedures
        for proc_name, proc_body in node.procedures:
            old_procedure = self.current_procedure
            self.current_procedure = proc_name
            
            old_ops = self.operation_count
            proc_body.accept(self)
            
            # Calculate procedure complexity
            proc_ops = self.operation_count - old_ops
            self.procedure_complexities[proc_name] = proc_ops
            
            if proc_ops > 100:  # Arbitrary threshold
                self.hotspots.append({
                    "type": "Heavy Procedure",
                    "description": f"Procedure '{proc_name}' has {proc_ops} operations",
                    "weight": proc_ops
                })
            
            self.current_procedure = old_procedure
        
        node.statement.accept(self)
        self.current_stack_depth -= 1
    
    def visit_assign(self, node: AssignNode):
        """Analyze assignment performance"""
        self.operation_count += 1
        
        # Analyze expression complexity
        expr_ops = self._count_expression_operations(node.expression)
        self.operation_count += expr_ops
        
        if self.in_loop and expr_ops > 5:
            self.hotspots.append({
                "type": "Complex Loop Assignment",
                "description": f"Assignment to '{node.var_name}' has {expr_ops} operations in loop",
                "weight": expr_ops * 10  # Multiplied by loop factor
            })
        
        node.expression.accept(self)
    
    def visit_call(self, node: CallNode):
        """Analyze procedure call performance"""
        self.procedure_calls += 1
        self.operation_count += 10  # Overhead for call
        
        # Stack overhead
        self.current_stack_depth += 1
        self.max_stack_depth = max(self.max_stack_depth, self.current_stack_depth)
        
        if self.in_loop:
            self.hotspots.append({
                "type": "Procedure Call in Loop",
                "description": f"Call to '{node.proc_name}' inside loop",
                "weight": 50
            })
        
        self.current_stack_depth -= 1
    
    def visit_read(self, node: ReadNode):
        """Analyze input performance"""
        self.io_operations += 1
        self.operation_count += 100  # I/O is expensive
        
        if self.in_loop:
            self.hotspots.append({
                "type": "I/O in Loop",
                "description": f"Input operation for '{node.var_name}' in loop",
                "weight": 200
            })
    
    def visit_write(self, node: WriteNode):
        """Analyze output performance"""
        self.io_operations += 1
        self.operation_count += 50  # Output is less expensive than input
        
        expr_ops = self._count_expression_operations(node.expression)
        self.operation_count += expr_ops
        
        if self.in_loop:
            self.hotspots.append({
                "type": "I/O in Loop",
                "description": f"Output operation in loop",
                "weight": 100
            })
        
        node.expression.accept(self)
    
    def visit_compound(self, node: CompoundNode):
        """Analyze compound statement performance"""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_nested_block(self, node: NestedBlockNode):
        """Analyze nested block performance"""
        self.current_stack_depth += 1
        self.max_stack_depth = max(self.max_stack_depth, self.current_stack_depth)
        self.memory_operations += len(node.variables)
        
        for stmt in node.statements:
            stmt.accept(self)
        
        self.current_stack_depth -= 1
    
    def visit_if(self, node: IfNode):
        """Analyze conditional performance"""
        self.operation_count += 1  # Condition evaluation
        
        cond_ops = self._count_expression_operations(node.condition)
        self.operation_count += cond_ops
        
        node.condition.accept(self)
        
        # Analyze then branch
        old_ops = self.operation_count
        node.then_statement.accept(self)
        branch_ops = self.operation_count - old_ops
        
        # Average case: assume 50% branch taken
        self.operation_count = old_ops + (branch_ops // 2)
    
    def visit_while(self, node: WhileNode):
        """Analyze loop performance"""
        self.loop_nesting += 1
        self.max_loop_nesting = max(self.max_loop_nesting, self.loop_nesting)
        
        old_in_loop = self.in_loop
        self.in_loop = True
        
        # Estimate loop iterations (simplified)
        estimated_iterations = self._estimate_loop_iterations(node.condition)
        
        self.operation_count += 1  # Initial condition check
        cond_ops = self._count_expression_operations(node.condition)
        
        # Analyze body
        old_ops = self.operation_count
        node.condition.accept(self)
        node.body.accept(self)
        
        body_ops = self.operation_count - old_ops - cond_ops
        
        # Total loop cost
        total_loop_ops = (cond_ops + body_ops) * estimated_iterations
        self.operation_count = old_ops + total_loop_ops
        
        # Update complexity based on loop nesting
        current_complexity = f"n^{self.loop_nesting}"
        self.loop_complexities.append({
            "nesting_level": self.loop_nesting,
            "estimated_iterations": estimated_iterations,
            "body_operations": body_ops,
            "complexity": current_complexity
        })
        
        if estimated_iterations > 1000:
            self.hotspots.append({
                "type": "High Iteration Loop",
                "description": f"Loop with ~{estimated_iterations} iterations",
                "weight": estimated_iterations
            })
        
        self.in_loop = old_in_loop
        self.loop_nesting -= 1
    
    def visit_operation(self, node: OperationNode):
        """Analyze operation performance"""
        self.operation_count += 1
        
        # Some operations are more expensive
        if node.operator == "/":
            self.operation_count += 4  # Division is expensive
        elif node.operator == "*":
            self.operation_count += 2  # Multiplication is moderately expensive
        
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_variable(self, node: VariableNode):
        """Analyze variable access performance"""
        # Variable access is essentially free
        pass
    
    def visit_number(self, node: NumberNode):
        """Analyze number literal performance"""
        # Literal access is free
        pass
    
    def _count_expression_operations(self, expr):
        """Count operations in an expression"""
        if isinstance(expr, NumberNode) or isinstance(expr, VariableNode):
            return 0
        elif isinstance(expr, OperationNode):
            return 1 + self._count_expression_operations(expr.left) + self._count_expression_operations(expr.right)
        return 0
    
    def _estimate_loop_iterations(self, condition):
        """Estimate number of loop iterations"""
        # Simplified heuristic based on condition
        if isinstance(condition, OperationNode):
            if isinstance(condition.right, NumberNode):
                # Assume simple counter loop
                return min(condition.right.value, 1000)  # Cap at 1000
        
        # Default assumption for unknown loops
        return 10
    
    def _calculate_final_complexity(self):
        """Calculate overall time complexity"""
        if self.max_loop_nesting == 0:
            self.time_complexity = "1"  # Constant time
        elif self.max_loop_nesting == 1:
            self.time_complexity = "n"  # Linear time
        else:
            self.time_complexity = f"n^{self.max_loop_nesting}"
        
        # Space complexity based on stack depth and variables
        if self.max_stack_depth > 1:
            self.space_complexity = str(self.max_stack_depth)
        else:
            self.space_complexity = "1"
    
    def _generate_recommendations(self):
        """Generate performance recommendations"""
        if self.io_operations > 0:
            self.recommendations.append("Consider batching I/O operations to reduce system call overhead")
        
        if self.max_loop_nesting > 2:
            self.recommendations.append("Consider algorithm redesign to reduce nested loop complexity")
        
        if any(h["type"] == "Procedure Call in Loop" for h in self.hotspots):
            self.recommendations.append("Consider inlining procedures called within loops")
        
        if self.max_stack_depth > 10:
            self.recommendations.append("High stack usage detected - consider iterative algorithms")
        
        if self.operation_count > 10000:
            self.recommendations.append("High operation count - consider algorithmic optimizations")


class CInstrumenter(Visitor):
    """Generates instrumented C code for runtime profiling"""
    
    def __init__(self):
        self.code_lines = []
        self.indent_level = 0
        self.profile_points = 0
    
    def generate_instrumented_code(self, ast, profile_data):
        """Generate C code with performance instrumentation"""
        # Header with profiling includes
        self.code_lines = [
            "#include <stdio.h>",
            "#include <time.h>",
            "#include <sys/time.h>",
            "",
            "// Performance profiling variables",
            "static unsigned long operation_count = 0;",
            "static unsigned long procedure_calls = 0;",
            "static unsigned long io_operations = 0;",
            "static struct timeval start_time, end_time;",
            "",
            "// Profiling macros",
            "#define PROFILE_START() gettimeofday(&start_time, NULL)",
            "#define PROFILE_END() gettimeofday(&end_time, NULL)",
            "#define PROFILE_OP() operation_count++",
            "#define PROFILE_CALL() procedure_calls++",
            "#define PROFILE_IO() io_operations++",
            "",
            "void print_profile_results() {",
            "    double elapsed = (end_time.tv_sec - start_time.tv_sec) + ",
            "                    (end_time.tv_usec - start_time.tv_usec) / 1000000.0;",
            '    printf("\\n--- Performance Profile ---\\n");',
            '    printf("Execution time: %.6f seconds\\n", elapsed);',
            '    printf("Operations: %lu\\n", operation_count);',
            '    printf("Procedure calls: %lu\\n", procedure_calls);',
            '    printf("I/O operations: %lu\\n", io_operations);',
            '    printf("Ops/second: %.0f\\n", operation_count / elapsed);',
            "}",
            ""
        ]
        
        # Generate the instrumented program
        ast.accept(self)
        
        return "\n".join(self.code_lines)
    
    def _add_line(self, line: str = ""):
        """Add a line with proper indentation"""
        if line.strip():
            self.code_lines.append("\t" * self.indent_level + line)
        else:
            self.code_lines.append("")
    
    def visit_block(self, node: BlockNode):
        """Generate instrumented block code"""
        # This is a simplified version - would need the full C compiler logic
        # with instrumentation added at key points
        
        if not hasattr(self, '_main_generated'):
            # Generate main function with profiling
            for var in node.variables:
                self._add_line(f"int {var} = 0;")
            
            # Generate procedures with profiling
            for proc_name, proc_body in node.procedures:
                self._add_line(f"void {proc_name}() {{")
                self.indent_level += 1
                self._add_line("PROFILE_CALL();")
                # Would generate full procedure body here
                self.indent_level -= 1
                self._add_line("}")
                self._add_line()
            
            self._add_line("int main() {")
            self.indent_level += 1
            self._add_line("PROFILE_START();")
            
            # Generate main body with instrumentation
            self._add_line("// Main program body would go here")
            self._add_line("// Each operation would include PROFILE_OP()")
            
            self._add_line("PROFILE_END();")
            self._add_line("print_profile_results();")
            self._add_line("return 0;")
            self.indent_level -= 1
            self._add_line("}")
            
            self._main_generated = True
    
    # Simplified visitor methods for instrumentation
    def visit_assign(self, node): self._add_line("PROFILE_OP();")
    def visit_call(self, node): self._add_line("PROFILE_CALL();")
    def visit_read(self, node): self._add_line("PROFILE_IO();")
    def visit_write(self, node): self._add_line("PROFILE_IO();")
    def visit_compound(self, node): pass
    def visit_nested_block(self, node): pass
    def visit_if(self, node): self._add_line("PROFILE_OP();")
    def visit_while(self, node): self._add_line("PROFILE_OP();")
    def visit_operation(self, node): self._add_line("PROFILE_OP();")
    def visit_variable(self, node): pass
    def visit_number(self, node): pass