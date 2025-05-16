import sys
import re
import functools
import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union, Optional, Any

Atom = Union[int, float, str, bool]
Vector = List
Value = Union[Atom, Vector]
MonadicFunction = Callable[[Value], Value]
DyadicFunction = Callable[[Value, Value], Value]
Dictionary = Dict[Value, Value]

global_variables = {}

@dataclass
class Operation:
    symbol: str
    monadic: Optional[MonadicFunction] = None
    dyadic: Optional[DyadicFunction] = None
    description: str = ""
    
    def __post_init__(self):
        if self.monadic is None and self.dyadic is None:
            raise ValueError(f"Operation {self.symbol} must have at least one implementation")

class OperationRegistry:
    def __init__(self):
        self.operations: Dict[str, Operation] = {}
    
    def register(self, operation: Operation) -> None:
        if operation.symbol in self.operations:
            raise ValueError(f"Operation {operation.symbol} is already registered")
        self.operations[operation.symbol] = operation
    
    def get_monadic(self, symbol: str) -> MonadicFunction:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        monadic = self.operations[symbol].monadic
        if monadic is None:
            raise_error(f"operation {symbol} does not have a monadic form")
        
        return monadic
    
    def get_dyadic(self, symbol: str) -> DyadicFunction:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        dyadic = self.operations[symbol].dyadic
        if dyadic is None:
            raise_error(f"operation {symbol} does not have a dyadic form")
        
        return dyadic
    
    def get_operation(self, symbol: str) -> Operation:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        return self.operations[symbol]
    
    def has_monadic(self, symbol: str) -> bool:
        return symbol in self.operations and self.operations[symbol].monadic is not None
    
    def has_dyadic(self, symbol: str) -> bool:
        return symbol in self.operations and self.operations[symbol].dyadic is not None

operation_registry = OperationRegistry()

def is_atomic(value):
    return isinstance(value, (int, float, str, bool))

def get_type(value):
    if isinstance(value, bool):
        return 'b'
    elif isinstance(value, int):
        return 'i'
    elif isinstance(value, float):
        return 'f'
    elif isinstance(value, str):
        return 's'
    elif isinstance(value, list):
        return 'l'
    elif isinstance(value, dict):
        return 'd'
    else:
        return '?'

def raise_error(message="not yet implemented"):
    raise Exception(f"error: {message}")

def negate(value):
    if is_atomic(value):
        if isinstance(value, (int, float)):
            return -value
        elif isinstance(value, bool):
            return not value
        else:
            raise_error("type error: cannot negate string")
    else:
        return list(map(negate, value))

def generate_sequence(value):
    if is_atomic(value):
        if isinstance(value, (int, float)):
            return list(range(0, int(value)))
        else:
            raise_error("type error: iota requires numeric argument")
    else:
        raise_error("rank error: iota requires atomic value")

def get_length(value):
    if is_atomic(value):
        if isinstance(value, str):
            return len(value)
        else:
            raise_error("rank error: cannot get length of atomic value")
    else:
        return len(value)

def ensure_list(value):
    return [value] if is_atomic(value) else value

def reverse_list(value):
    if is_atomic(value):
        if isinstance(value, str):
            return value[::-1]
        else:
            raise_error("rank error: cannot reverse non-sequence atomic value")
    else:
        return list(reversed(value))

def first_element(value):
    if is_atomic(value) and isinstance(value, str):
        return value[0] if value else ""
    elif not is_atomic(value):
        return value[0] if value else None
    else:
        raise_error("rank error: cannot get first element of an atom")

def get_type_info(value):
    if is_atomic(value):
        return get_type(value)
    else:
        return [get_type(x) for x in value]

def where(value):
    if is_atomic(value):
        raise_error("rank error: where requires a list")
    
    result = []
    for i, count in enumerate(value):
        if not isinstance(count, (int, bool)):
            raise_error("type error: where requires integer counts")
        result.extend([i] * int(count))
    return result

def group(value):
    if is_atomic(value):
        raise_error("rank error: group requires a list")
    
    groups = {}
    for i, v in enumerate(value):
        key_str = str(v)
        if key_str not in groups:
            groups[key_str] = []
        groups[key_str].append(i)
    
    result = {}
    for k, v in groups.items():
        try:
            if k.lower() == 'true':
                result[True] = v
            elif k.lower() == 'false':
                result[False] = v
            elif '.' in k and all(c.isdigit() or c == '.' for c in k.replace('-', '', 1)):
                result[float(k)] = v
            elif k.isdigit() or (k[0] == '-' and k[1:].isdigit()):
                result[int(k)] = v
            else:
                result[k] = v
        except:
            result[k] = v
    
    return result

def unique(value):
    if is_atomic(value):
        return value
    
    seen = set()
    result = []
    for item in value:
        item_str = str(item)
        if item_str not in seen:
            seen.add(item_str)
            result.append(item)
    return result

def sort(value):
    if is_atomic(value):
        raise_error("rank error: sort requires a list")
    
    try:
        return sorted(value)
    except TypeError:
        return sorted(value, key=str)

def sum_values(value):
    if is_atomic(value):
        return value
    
    if not value:
        return 0
    
    try:
        return sum(value)
    except TypeError:
        raise_error("type error: cannot sum non-numeric elements")

def minimum(value):
    if is_atomic(value):
        return value
    
    if not value:
        raise_error("domain error: empty list has no minimum")
    
    try:
        return min(value)
    except TypeError:
        raise_error("type error: cannot compare mixed types for minimum")

def maximum(value):
    if is_atomic(value):
        return value
    
    if not value:
        raise_error("domain error: empty list has no maximum")
    
    try:
        return max(value)
    except TypeError:
        raise_error("type error: cannot compare mixed types for maximum")

def average(value):
    if is_atomic(value):
        return float(value)
    
    if not value:
        raise_error("domain error: cannot average empty list")
    
    try:
        return sum(value) / len(value)
    except TypeError:
        raise_error("type error: average requires numeric elements")

def raze(value):
    if is_atomic(value):
        return [value]
    
    result = []
    for item in value:
        if is_atomic(item):
            result.append(item)
        else:
            result.extend(item)
    return result

def flip_matrix(value):
    if is_atomic(value):
        raise_error("rank error: flip requires a matrix")
    
    if not value:
        return []
    
    if not all(not is_atomic(row) for row in value):
        raise_error("rank error: all elements must be lists for flip")
    
    row_lengths = [len(row) for row in value]
    if len(set(row_lengths)) != 1:
        raise_error("rank error: all rows must have same length for flip")
    
    return [list(col) for col in zip(*value)]

def coalesce(value):
    if is_atomic(value):
        return value
    
    for item in value:
        if item is not None:
            return item
    
    return None

def apply_dyadic(x, y, operation):
    if is_atomic(x):
        if is_atomic(y):
            return operation(x, y)
        else:
            return list(map(lambda element: operation(x, element), y))
    elif is_atomic(y):
        return list(map(lambda element: operation(element, y), x))
    elif len(x) != len(y):
        raise_error("rank error: lists must have equal length for dyadic operations")
    else:
        return list(map(lambda pair: operation(pair[0], pair[1]), zip(x, y)))

def add(x, y):
    def add_atoms(a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
        elif isinstance(a, str) and isinstance(b, str):
            return a + b
        elif isinstance(a, bool) and isinstance(b, bool):
            return a or b
        else:
            raise_error(f"type error: cannot add {type(a)} and {type(b)}")
    
    return apply_dyadic(x, y, add_atoms)

def logical_and(x, y):
    def and_atoms(a, b):
        if isinstance(a, int) and isinstance(b, int):
            return a & b
        elif isinstance(a, bool) and isinstance(b, bool):
            return a and b
        else:
            raise_error(f"type error: cannot apply & to {type(a)} and {type(b)}")
    
    return apply_dyadic(x, y, and_atoms)

def logical_or(x, y):
    def or_atoms(a, b):
        if isinstance(a, int) and isinstance(b, int):
            return a | b
        elif isinstance(a, bool) and isinstance(b, bool):
            return a or b
        else:
            raise_error(f"type error: cannot apply | to {type(a)} and {type(b)}")
    
    return apply_dyadic(x, y, or_atoms)

def not_equal(x, y):
    return apply_dyadic(x, y, lambda a, b: a != b)

def equals(x, y):
    return apply_dyadic(x, y, lambda a, b: a == b)

def multiply(x, y):
    def multiply_atoms(a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a * b
        elif isinstance(a, str) and isinstance(b, int):
            return a * b
        elif isinstance(a, int) and isinstance(b, str):
            return b * a
        elif isinstance(a, bool) and isinstance(b, bool):
            return a and b
        else:
            raise_error(f"type error: cannot multiply {type(a)} and {type(b)}")
    
    return apply_dyadic(x, y, multiply_atoms)

def subtract(x, y):
    def subtract_atoms(a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a - b
        elif isinstance(a, bool) and isinstance(b, bool):
            return a and not b
        else:
            raise_error(f"type error: cannot subtract {type(b)} from {type(a)}")
    
    return apply_dyadic(x, y, subtract_atoms)

def divide(x, y):
    def divide_atoms(a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if b == 0:
                raise_error("domain error: division by zero")
            return (a / b) * 100  # Scale by 100 for percentage returns
        else:
            raise_error(f"type error: cannot divide {type(a)} by {type(b)}")
    
    return apply_dyadic(x, y, divide_atoms)

def modulo(x, y):
    if not is_atomic(x):
        raise_error("rank error: modulo requires atomic first argument")
    
    if not isinstance(x, (int, float)):
        raise_error("type error: modulo requires numeric first argument")
    
    def mod_atom(y_val, x_val):
        if isinstance(y_val, (int, float)):
            return y_val % x_val
        else:
            raise_error(f"type error: cannot apply modulo to {type(y_val)}")
    
    if is_atomic(y):
        return mod_atom(y, x)
    else:
        return list(map(lambda element: mod_atom(element, x), y))

def take(x, y):
    if not is_atomic(x):
        raise_error("rank error: take requires atomic first argument")
    
    if not isinstance(x, int):
        raise_error("type error: take requires integer first argument")
    
    if is_atomic(y):
        return [y] * x
    else:
        if x >= 0:
            result = []
            for i in range(x):
                result.append(y[i % len(y)])
            return result
        else:
            x = abs(x)
            result = []
            for i in range(x):
                result.append(y[-(i % len(y) + 1)])
            return list(reversed(result))

def drop(x, y):
    if not is_atomic(x):
        raise_error("rank error: drop requires atomic first argument")
    
    if not isinstance(x, int):
        raise_error("type error: drop requires integer first argument")
    
    if is_atomic(y):
        if isinstance(y, str):
            return y[x:] if x >= 0 else y[:x]
        else:
            raise_error("rank error: cannot drop from atomic value")
    else:
        return y[x:] if x >= 0 else y[:x]

def find(x, y):
    if is_atomic(y):
        if isinstance(y, str):
            if is_atomic(x) and isinstance(x, str):
                indices = []
                start = 0
                while True:
                    pos = y.find(x, start)
                    if pos == -1:
                        break
                    indices.append(pos)
                    start = pos + 1
                return indices
            else:
                raise_error("type error: finding in string requires string pattern")
        else:
            raise_error("rank error: find requires sequence as second argument")
    else:
        return [i for i, val in enumerate(y) if val == x]

def concatenate(x, y):
    if is_atomic(x) and is_atomic(y):
        if isinstance(x, str) and isinstance(y, str):
            return x + y
        else:
            return [x, y]
    elif is_atomic(x):
        return [x] + y
    elif is_atomic(y):
        return x + [y]
    else:
        return x + y

def index_access(x, y):
    if is_atomic(x):
        if isinstance(x, str):
            if is_atomic(y):
                if isinstance(y, int):
                    if y >= len(x) or y < -len(x):
                        raise_error("index error: string index out of range")
                    return x[y]
                else:
                    raise_error("type error: string indexing requires integer index")
            else:
                return ''.join(x[i] for i in y)
        else:
            raise_error("rank error: cannot index atomic non-string value")
    else:
        if is_atomic(y):
            if isinstance(y, int):
                if y >= len(x) or y < -len(x):
                    raise_error("index error: list index out of range")
                return x[y]
            else:
                raise_error("type error: list indexing requires integer index")
        else:
            return [x[i] for i in y]

def dict_lookup(x, y):
    if isinstance(x, dict):
        if is_atomic(y):
            return x.get(y, None)
        else:
            return [x.get(k, None) for k in y]
    else:
        raise_error("type error: first argument must be a dictionary")

def amend(x, y, z):
    if is_atomic(x):
        raise_error("rank error: cannot amend atomic value")
    
    result = x.copy() if isinstance(x, list) else list(x)
    
    if is_atomic(y):
        result[y] = z
    else:
        if is_atomic(z):
            for idx in y:
                result[idx] = z
        else:
            if len(y) != len(z):
                raise_error("rank error: indices and values must have same length")
            for idx, val in zip(y, z):
                result[idx] = val
    
    return result

class LambdaFunction:
    def __init__(self, body):
        self.body = body
        self.params = ['x', 'y', 'z']
    
    def __call__(self, *args):
        old_vars = global_variables.copy()
        
        try:
            for i, arg in enumerate(args):
                if i < len(self.params):
                    global_variables[self.params[i]] = arg
            
            return evaluate_expression(self.body)
        finally:
            for param in self.params:
                if param in global_variables and param not in old_vars:
                    del global_variables[param]
                elif param in old_vars:
                    global_variables[param] = old_vars[param]

class ComposedFunction:
    def __init__(self, f, g):
        self.f = f
        self.g = g
    
    def __call__(self, *args):
        return self.f(self.g(*args))

class PartialFunction:
    def __init__(self, func, arg, is_left=True):
        self.func = func
        self.arg = arg
        self.is_left = is_left
    
    def __call__(self, x):
        if self.is_left:
            return self.func(self.arg, x)
        else:
            return self.func(x, self.arg)

def fold(operation, sequence):
    if not sequence:
        raise_error("domain error: cannot fold empty sequence")
    return functools.reduce(lambda acc, element: operation(acc, element), sequence)

def scan(operation, sequence):
    if not sequence:
        return []
    return list(itertools.accumulate(sequence, lambda acc, element: operation(acc, element)))

def each(operation, sequence):
    if is_atomic(sequence):
        raise_error("rank error: each requires a sequence")
    return [operation(element) for element in sequence]

def each_right(operation, left, sequence):
    if is_atomic(sequence):
        raise_error("rank error: each_right requires a sequence as right argument")
    return [operation(left, element) for element in sequence]

def each_left(operation, sequence, right):
    if is_atomic(sequence):
        raise_error("rank error: each_left requires a sequence as left argument")
    return [operation(element, right) for element in sequence]

def each_pair(operation, left_sequence, right_sequence):
    if is_atomic(left_sequence) or is_atomic(right_sequence):
        raise_error("rank error: each_pair requires two sequences")
    
    if len(left_sequence) != len(right_sequence):
        raise_error("rank error: sequences must have same length for each_pair")
    
    return [operation(left, right) for left, right in zip(left_sequence, right_sequence)]

def register_standard_operations():
    operation_registry.register(Operation(
        symbol="+",
        monadic=sum_values,
        dyadic=add,
        description="Sum of list (monadic) or addition (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="-",
        monadic=negate,
        dyadic=subtract,
        description="Subtraction operator (dyadic) or negation (monadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="!",
        monadic=generate_sequence,
        dyadic=modulo,
        description="Generate sequence (monadic) or modulo (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="#",
        monadic=get_length,
        dyadic=take,
        description="Length of list (monadic) or take elements (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="_",
        monadic=None,
        dyadic=drop,
        description="Drop elements from a list or string"
    ))
    
    operation_registry.register(Operation(
        symbol="?",
        monadic=unique,
        dyadic=find,
        description="Unique elements (monadic) or find occurrences (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="^",
        monadic=where,
        dyadic=group,
        description="Where indices (monadic) or group by value (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol=",",
        monadic=ensure_list,
        dyadic=concatenate,
        description="Ensure value is a list (monadic) or concatenate lists (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="@",
        monadic=first_element,
        dyadic=index_access,
        description="First element (monadic) or index access (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="$",
        monadic=get_type_info,
        dyadic=dict_lookup,
        description="Get type info (monadic) or dictionary lookup (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="`",
        monadic=sort,
        dyadic=None,
        description="Sort elements in ascending order"
    ))
    
    operation_registry.register(Operation(
        symbol="=",
        monadic=None,
        dyadic=equals,
        description="Equality check"
    ))
    
    operation_registry.register(Operation(
        symbol="~",
        monadic=None,
        dyadic=not_equal,
        description="Inequality check"
    ))
    
    operation_registry.register(Operation(
        symbol="&",
        monadic=minimum,
        dyadic=logical_and,
        description="Minimum value (monadic) or bitwise AND (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="|",
        monadic=reverse_list,
        dyadic=logical_or,
        description="Reverse list (monadic) or bitwise OR (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="*",
        monadic=maximum,
        dyadic=multiply,
        description="Maximum value (monadic) or multiplication (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol="%",
        monadic=average,
        dyadic=divide,
        description="Calculate average (monadic) or percentage division (dyadic)"
    ))
    
    operation_registry.register(Operation(
        symbol=";",
        monadic=raze,
        dyadic=None,
        description="Flatten a list of lists"
    ))
    
    operation_registry.register(Operation(
        symbol=".",
        monadic=flip_matrix,
        dyadic=None,
        description="Transpose a matrix"
    ))
    
    operation_registry.register(Operation(
        symbol=":",
        monadic=coalesce,
        dyadic=None,
        description="First non-null value from a list"
    ))

def parse_value(token):
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    
    elif token.lower() == "true":
        return True
    elif token.lower() == "false":
        return False
        
    elif '.' in token and all(c.isdigit() or c == '.' for c in token.replace('-', '', 1)):
        return float(token)
        
    elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
        return int(token)
        
    else:
        return token

def evaluate_expression(expression):
    # Handle empty expression
    if not expression:
        return None
    
    # Handle pre-parsed list expressions
    if isinstance(expression, list):
        if not expression:
            return []
        
        # Monadic operation: [op, arg]
        if len(expression) == 2:
            op, arg = expression
            if isinstance(op, str) and operation_registry.has_monadic(op):
                if isinstance(arg, str) and arg in global_variables:
                    evaluated_arg = global_variables[arg]
                else:
                    evaluated_arg = evaluate_expression(arg)
                return operation_registry.get_monadic(op)(evaluated_arg)
        
        # Dyadic operation: [left, op, right]
        if len(expression) == 3:
            left, op, right = expression
            if isinstance(op, str) and operation_registry.has_dyadic(op):
                # Evaluate left
                if isinstance(left, str) and left in global_variables:
                    evaluated_left = global_variables[left]
                else:
                    evaluated_left = evaluate_expression(left)
                # Evaluate right
                if isinstance(right, (int, float)):
                    evaluated_right = right
                elif isinstance(right, str) and right in global_variables:
                    evaluated_right = global_variables[right]
                else:
                    evaluated_right = evaluate_expression(right)
                return operation_registry.get_dyadic(op)(evaluated_left, evaluated_right)
        
        # Handle lists of atomic values (e.g., [1.0, 2.0, 3.0])
        if all(is_atomic(item) and not isinstance(item, str) for item in expression):
            return expression
        
        raise_error("syntax error: invalid list expression")
    
    # Handle atomic values (int, float, bool)
    if isinstance(expression, (int, float, bool)):
        return expression
    
    # Handle string expressions
    if isinstance(expression, str):
        # List literal: (1;2;3)
        if expression.startswith('(') and expression.endswith(')'):
            items = []
            current = ''
            paren_count = 0
            i = 1
            
            while i < len(expression) - 1:
                char = expression[i]
                
                if char == '(':
                    paren_count += 1
                    current += char
                elif char == ')':
                    paren_count -= 1
                    current += char
                elif char == ';' and paren_count == 0:
                    if current.strip():
                        items.append(evaluate_expression(current.strip()))
                    current = ''
                else:
                    current += char
                i += 1
            
            if current.strip():
                items.append(evaluate_expression(current.strip()))
            
            return items
        
        # Dictionary literal: [a:1;b:2]
        if expression.startswith('[') and expression.endswith(']'):
            result = {}
            current = ''
            bracket_count = 0
            i = 1
            
            while i < len(expression) - 1:
                char = expression[i]
                
                if char == '[':
                    bracket_count += 1
                    current += char
                elif char == ']':
                    bracket_count -= 1
                    current += char
                elif char == ';' and bracket_count == 0:
                    if current.strip():
                        key_val = current.split(':')
                        if len(key_val) != 2:
                            raise_error("syntax error: invalid dictionary entry")
                        key = evaluate_expression(key_val[0].strip())
                        val = evaluate_expression(key_val[1].strip())
                        result[key] = val
                    current = ''
                else:
                    current += char
                i += 1
            
            if current.strip():
                key_val = current.split(':')
                if len(key_val) != 2:
                    raise_error("syntax error: invalid dictionary entry")
                key = evaluate_expression(key_val[0].strip())
                val = evaluate_expression(key_val[1].strip())
                result[key] = val
            
            return result
        
        # Lambda expression: {x+y}
        if expression.startswith('{') and expression.endswith('}'):
            body = expression[1:-1]
            return LambdaFunction(body)
        
        # Atomic value or variable
        value = parse_value(expression)
        if isinstance(value, str) and not (expression.startswith('"') and expression.endswith('"')):
            if value in global_variables:
                return global_variables[value]
            else:
                raise_error(f"undefined variable: {value}")
        return value
    
    raise_error("syntax error: cannot evaluate expression")