from typing import List, Optional, Union
from ..components.tokens import Token, TokenType
from ..components.operators.base import OperatorRegistry
from ..components.functions.base import FunctionRegistry
from .exceptions import EvaluationError


class Evaluator:
    """Evaluates tokenized expressions using Shunting Yard algorithm."""
    
    def __init__(self, operator_registry: OperatorRegistry, function_registry: Optional[FunctionRegistry] = None):
        self.operator_registry = operator_registry
        self.function_registry = function_registry
    
    def evaluate(self, tokens: List[Token]) -> float:
        """Evaluate tokens to produce numerical result."""
        if not tokens:
            raise EvaluationError("Empty expression")
        
        # Convert to postfix notation using Shunting Yard
        postfix = self._to_postfix(tokens)
        
        # Evaluate postfix expression
        return self._evaluate_postfix(postfix)
    
    def _to_postfix(self, tokens: List[Token]) -> List[Token]:
        """Convert infix tokens to postfix using Shunting Yard algorithm."""
        output = []
        operator_stack = []
        
        for token in tokens:
            if token.is_number():
                output.append(token)
            
            elif token.is_function():
                operator_stack.append(token)
            
            elif token.value == ',':
                # Pop operators until we find opening parenthesis
                while operator_stack and operator_stack[-1].value != '(':
                    output.append(operator_stack.pop())
            
            elif token.is_operator():
                while (operator_stack and 
                       operator_stack[-1].is_operator() and
                       self._should_pop_operator(token, operator_stack[-1])):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            
            elif token.value == '(':
                operator_stack.append(token)
            
            elif token.value == ')':
                # Pop operators until opening parenthesis
                while operator_stack and operator_stack[-1].value != '(':
                    output.append(operator_stack.pop())
                
                if not operator_stack:
                    raise EvaluationError("Mismatched parentheses")
                
                operator_stack.pop()  # Remove opening parenthesis
                
                # If there's a function on top of stack, add it to output
                if operator_stack and operator_stack[-1].is_function():
                    output.append(operator_stack.pop())
        
        # Pop remaining operators
        while operator_stack:
            if operator_stack[-1].value in '()':
                raise EvaluationError("Mismatched parentheses")
            output.append(operator_stack.pop())
        
        return output
    
    def _should_pop_operator(self, current: Token, stack_top: Token) -> bool:
        """Determine if stack operator should be popped based on precedence."""
        current_op = self.operator_registry.get(current.value)
        stack_op = self.operator_registry.get(stack_top.value)
        
        if current_op is None or stack_op is None:
            raise EvaluationError(f"Unknown operator: {current.value if current_op is None else stack_top.value}")
        
        if current_op.associativity == "left":
            return current_op.precedence <= stack_op.precedence
        else:  # right associative
            return current_op.precedence < stack_op.precedence
    
    def _evaluate_postfix(self, tokens: List[Token]) -> float:
        """Evaluate postfix expression."""
        stack = []
        
        for token in tokens:
            # Debug: Log stack before each token
            print(f"Stack before {token.value}: {stack}")
            
            if token.is_number():
                stack.append(token.value)
            
            elif token.is_operator():
                operator = self.operator_registry.get(token.value)
                if operator is None:
                    raise EvaluationError(f"Unknown operator: {token.value}")
                
                if len(stack) < operator.arity:
                    raise EvaluationError(f"Not enough operands for operator {token.value} (needs {operator.arity}, got {len(stack)})")
                
                operands = []
                for _ in range(operator.arity):
                    operands.append(stack.pop())
                operands.reverse()  # Correct order for non-commutative operations
                
                try:
                    result = operator.apply(*operands)
                    if not isinstance(result, (int, float)):
                        raise EvaluationError(f"Operator {token.value} returned non-numeric result: {result}")
                    stack.append(result)
                    # Debug: Log operation and result
                    print(f"Applied {token.value} to {operands} -> {result}")
                except Exception as e:
                    raise EvaluationError(f"Error applying operator {token.value} to {operands}: {e}")
            
            elif token.is_function():
                if not self.function_registry:
                    raise EvaluationError("Functions not enabled")
                
                function = self.function_registry.get(token.value)
                if function is None:
                    raise EvaluationError(f"Unknown function: {token.value}")
                
                if len(stack) < function.arity:
                    raise EvaluationError(f"Not enough arguments for function {token.value} (needs {function.arity}, got {len(stack)})")
                
                args = []
                for _ in range(function.arity):
                    args.append(stack.pop())
                args.reverse()  # Correct order
                
                try:
                    result = function.apply(*args)
                    if not isinstance(result, (int, float)):
                        raise EvaluationError(f"Function {token.value} returned non-numeric result: {result}")
                    stack.append(result)
                    # Debug: Log function and result
                    print(f"Applied {token.value} to {args} -> {result}")
                except Exception as e:
                    raise EvaluationError(f"Error applying function {token.value} to {args}: {e}")
        
        # Debug: Log final stack
        print(f"Final stack: {stack}")
        
        if not stack:
            raise EvaluationError("No result after evaluation (empty stack)")
        if len(stack) > 1:
            raise EvaluationError(f"Invalid expression: too many values left on stack {stack}")
        
        return stack[0]