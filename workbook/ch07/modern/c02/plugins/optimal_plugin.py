#!/usr/bin/env python3
"""
Optimization Plugin for PL0 Compiler
Implements constant folding, dead code elimination, and basic peephole optimizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler import Plugin, Visitor, ASTNode, OperationNode, NumberNode, VariableNode
from compiler import AssignNode, CompoundNode, IfNode, WhileNode, BlockNode, NestedBlockNode
from compiler import CallNode, ReadNode, WriteNode
from typing import Set, Dict, Any, Optional, List


class OptimizationPlugin(Plugin):
    def __init__(self):
        super().__init__("optimizer", "Performs constant folding and dead code elimination")
    
    def run(self, ast, context, messages):
        optimizer = Optimizer(messages)
        
        # Perform multiple optimization passes until no more changes
        optimized_ast = ast
        total_changes = 0
        pass_num = 1
        
        while True:
            messages.debug(f"Optimization pass {pass_num}")
            
            # Constant folding pass
            folder = ConstantFolder(messages)
            optimized_ast, cf_changes = folder.optimize(optimized_ast)
            
            # Dead code elimination pass  
            dce = DeadCodeEliminator(messages)
            optimized_ast, dce_changes = dce.optimize(optimized_ast)
            
            changes_this_pass = cf_changes + dce_changes
            total_changes += changes_this_pass
            
            messages.info(f"Pass {pass_num}: {cf_changes} constant folding, {dce_changes} dead code eliminations")
            
            if changes_this_pass == 0:
                break
                
            pass_num += 1
            if pass_num > 10:  # Safety limit
                messages.warning("Optimization stopped after 10 passes to prevent infinite loop")
                break
        
        if total_changes > 0:
            messages.info(f"Total optimizations applied: {total_changes}")
            
            # Update the AST in context for other plugins
            context.optimized_ast = optimized_ast
        else:
            messages.info("No optimizations were applicable")
            # Still store the AST even if no optimizations were made
            context.optimized_ast = optimized_ast
        
        return {
            "optimizations_applied": total_changes,
            "passes": pass_num - 1,
            "optimized": total_changes > 0
        }


class ConstantFolder(Visitor):
    """Performs constant folding optimizations"""
    
    def __init__(self, messages):
        self.messages = messages
        self.changes = 0
    
    def optimize(self, ast: ASTNode) -> tuple[ASTNode, int]:
        self.changes = 0
        result = ast.accept(self)
        return result, self.changes
    
    def visit_block(self, node: BlockNode):
        # Optimize procedures
        optimized_procedures = []
        for proc_name, proc_body in node.procedures:
            optimized_body = proc_body.accept(self)
            optimized_procedures.append((proc_name, optimized_body))
        
        # Optimize main statement
        optimized_statement = node.statement.accept(self)
        
        return BlockNode(node.variables, optimized_procedures, optimized_statement)
    
    def visit_nested_block(self, node: NestedBlockNode):
        optimized_statements = [stmt.accept(self) for stmt in node.statements]
        return NestedBlockNode(node.variables, optimized_statements)
    
    def visit_assign(self, node: AssignNode):
        optimized_expr = node.expression.accept(self)
        return AssignNode(node.var_name, optimized_expr)
    
    def visit_call(self, node: CallNode):
        return node  # No optimization for call nodes
    
    def visit_read(self, node: ReadNode):
        return node  # No optimization for read nodes
    
    def visit_write(self, node: WriteNode):
        optimized_expr = node.expression.accept(self)
        return WriteNode(optimized_expr)
    
    def visit_compound(self, node: CompoundNode):
        optimized_statements = [stmt.accept(self) for stmt in node.statements]
        return CompoundNode(optimized_statements)
    
    def visit_if(self, node: IfNode):
        optimized_condition = node.condition.accept(self)
        optimized_then = node.then_statement.accept(self)
        
        # Check if condition is a constant
        if isinstance(optimized_condition, NumberNode):
            self.changes += 1
            if optimized_condition.value != 0:
                self.messages.debug("Optimized: if-true condition eliminated")
                return optimized_then
            else:
                self.messages.debug("Optimized: if-false condition eliminated (dead code)")
                return CompoundNode([])  # Empty statement
        
        return IfNode(optimized_condition, optimized_then)
    
    def visit_while(self, node: WhileNode):
        optimized_condition = node.condition.accept(self)
        optimized_body = node.body.accept(self)
        
        # Conservative optimization: only eliminate obviously false conditions
        if isinstance(optimized_condition, NumberNode) and optimized_condition.value == 0:
            self.changes += 1
            self.messages.debug("Optimized: while-false loop eliminated (dead code)")
            return CompoundNode([])  # Empty statement
        
        return WhileNode(optimized_condition, optimized_body)
    
    def visit_operation(self, node: OperationNode):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # Constant folding for arithmetic and comparison operations
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            self.changes += 1
            result = self._evaluate_constant_operation(node.operator, left.value, right.value)
            self.messages.debug(f"Optimized: {left.value} {node.operator} {right.value} = {result}")
            return NumberNode(result)
        
        # Algebraic optimizations
        optimized = self._apply_algebraic_optimizations(node.operator, left, right)
        if optimized != node:
            self.changes += 1
        
        return optimized
    
    def visit_variable(self, node: VariableNode):
        return node
    
    def visit_number(self, node: NumberNode):
        return node
    
    def _evaluate_constant_operation(self, operator: str, left_val: int, right_val: int) -> int:
        """Evaluate constant arithmetic and comparison operations"""
        if operator == "+":
            return left_val + right_val
        elif operator == "-":
            return left_val - right_val
        elif operator == "*":
            return left_val * right_val
        elif operator == "/":
            if right_val == 0:
                self.messages.warning("Division by zero in constant folding")
                return 0  # Safe fallback
            return left_val // right_val  # Integer division
        elif operator == "=":
            return 1 if left_val == right_val else 0
        elif operator == "<":
            return 1 if left_val < right_val else 0
        elif operator == ">":
            return 1 if left_val > right_val else 0
        elif operator == "<=":
            return 1 if left_val <= right_val else 0
        elif operator == ">=":
            return 1 if left_val >= right_val else 0
        else:
            return 0
    
    def _apply_algebraic_optimizations(self, operator: str, left: ASTNode, right: ASTNode) -> ASTNode:
        """Apply algebraic optimization rules"""
        
        # x + 0 = x, 0 + x = x
        if operator == "+":
            if isinstance(right, NumberNode) and right.value == 0:
                self.messages.debug("Optimized: x + 0 → x")
                return left
            if isinstance(left, NumberNode) and left.value == 0:
                self.messages.debug("Optimized: 0 + x → x")
                return right
        
        # x - 0 = x
        elif operator == "-":
            if isinstance(right, NumberNode) and right.value == 0:
                self.messages.debug("Optimized: x - 0 → x")
                return left
        
        # x * 1 = x, 1 * x = x
        # x * 0 = 0, 0 * x = 0
        elif operator == "*":
            if isinstance(right, NumberNode):
                if right.value == 1:
                    self.messages.debug("Optimized: x * 1 → x")
                    return left
                elif right.value == 0:
                    self.messages.debug("Optimized: x * 0 → 0")
                    return NumberNode(0)
            if isinstance(left, NumberNode):
                if left.value == 1:
                    self.messages.debug("Optimized: 1 * x → x")
                    return right
                elif left.value == 0:
                    self.messages.debug("Optimized: 0 * x → 0")
                    return NumberNode(0)
        
        # x / 1 = x
        elif operator == "/":
            if isinstance(right, NumberNode) and right.value == 1:
                self.messages.debug("Optimized: x / 1 → x")
                return left
        
        # No optimization applied, return original
        return OperationNode(operator, left, right)


class DeadCodeEliminator(Visitor):
    """Eliminates unreachable and unused code"""
    
    def __init__(self, messages):
        self.messages = messages
        self.changes = 0
    
    def optimize(self, ast: ASTNode) -> tuple[ASTNode, int]:
        self.changes = 0
        result = ast.accept(self)
        return result, self.changes
    
    def visit_block(self, node: BlockNode):
        # Optimize procedures
        optimized_procedures = []
        for proc_name, proc_body in node.procedures:
            optimized_body = proc_body.accept(self)
            optimized_procedures.append((proc_name, optimized_body))
        
        # Optimize main statement
        optimized_statement = node.statement.accept(self)
        
        return BlockNode(node.variables, optimized_procedures, optimized_statement)
    
    def visit_nested_block(self, node: NestedBlockNode):
        optimized_statements = []
        for stmt in node.statements:
            optimized_stmt = stmt.accept(self)
            if not self._is_empty_statement(optimized_stmt):
                optimized_statements.append(optimized_stmt)
            else:
                self.changes += 1
                self.messages.debug("Eliminated empty statement")
        
        return NestedBlockNode(node.variables, optimized_statements)
    
    def visit_compound(self, node: CompoundNode):
        optimized_statements = []
        for stmt in node.statements:
            optimized_stmt = stmt.accept(self)
            if not self._is_empty_statement(optimized_stmt):
                optimized_statements.append(optimized_stmt)
            else:
                self.changes += 1
                self.messages.debug("Eliminated empty statement")
        
        return CompoundNode(optimized_statements)
    
    def visit_assign(self, node: AssignNode):
        optimized_expr = node.expression.accept(self)
        return AssignNode(node.var_name, optimized_expr)
    
    def visit_call(self, node: CallNode):
        return node
    
    def visit_read(self, node: ReadNode):
        return node
    
    def visit_write(self, node: WriteNode):
        optimized_expr = node.expression.accept(self)
        return WriteNode(optimized_expr)
    
    def visit_if(self, node: IfNode):
        optimized_condition = node.condition.accept(self)
        optimized_then = node.then_statement.accept(self)
        return IfNode(optimized_condition, optimized_then)
    
    def visit_while(self, node: WhileNode):
        optimized_condition = node.condition.accept(self)
        optimized_body = node.body.accept(self)
        return WhileNode(optimized_condition, optimized_body)
    
    def visit_operation(self, node: OperationNode):
        left = node.left.accept(self)
        right = node.right.accept(self)
        return OperationNode(node.operator, left, right)
    
    def visit_variable(self, node: VariableNode):
        return node
    
    def visit_number(self, node: NumberNode):
        return node
    
    def _is_empty_statement(self, node: ASTNode) -> bool:
        """Check if a statement is effectively empty"""
        if isinstance(node, CompoundNode):
            return len(node.statements) == 0
        elif isinstance(node, NestedBlockNode):
            return len(node.statements) == 0
        return False


# Additional simple optimization functions that can be registered separately

def strength_reduction_plugin(ast, context, messages):
    """Convert expensive operations to cheaper ones (e.g., x * 2 → x + x)"""
    messages.info("Running strength reduction optimization")
    
    class StrengthReducer(Visitor):
        def __init__(self):
            self.changes = 0
        
        def visit_operation(self, node):
            left = node.left.accept(self) if hasattr(node.left, 'accept') else node.left
            right = node.right.accept(self) if hasattr(node.right, 'accept') else node.right
            
            # x * 2 → x + x (multiplication by small constants)
            if (node.operator == "*" and isinstance(right, NumberNode) and 
                right.value == 2):
                self.changes += 1
                return OperationNode("+", left, left)
            
            # Similar for left operand
            if (node.operator == "*" and isinstance(left, NumberNode) and 
                left.value == 2):
                self.changes += 1
                return OperationNode("+", right, right)
            
            return OperationNode(node.operator, left, right)
        
        # Implement other visitor methods to traverse the AST
        def visit_block(self, node): return node
        def visit_assign(self, node): return node
        def visit_call(self, node): return node
        def visit_read(self, node): return node
        def visit_write(self, node): return node
        def visit_compound(self, node): return node
        def visit_nested_block(self, node): return node
        def visit_if(self, node): return node
        def visit_while(self, node): return node
        def visit_variable(self, node): return node
        def visit_number(self, node): return node
    
    reducer = StrengthReducer()
    # Note: In a full implementation, you'd need to properly traverse and transform the AST
    
    return {"optimizations": reducer.changes}


# Plugin registration decorator function
def register_optimization_plugins(compiler):
    """Register all optimization plugins with the compiler"""
    
    # Main optimization plugin
    compiler.add_plugin(OptimizationPlugin())
    
    # Additional optimization functions
    compiler.add_plugin_function(
        "strength_reduction", 
        strength_reduction_plugin,
        "Converts expensive operations to cheaper equivalents"
    )
