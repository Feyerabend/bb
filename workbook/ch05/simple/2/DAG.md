
## A Simple Compiler: Directed Acyclic Graph (DAG)

The Abstract Syntax Tree (AST) represents the structure of the code exactly as it is written,
preserving every operation and its operands. Each occurrence of a subexpression here 'a * (b - 1)'
in the code is represented as a distinct subtree in the AST, even if it is identical to another.

The Directed Acyclic Graph (DAG), on the other hand, optimises this representation by eliminating
redundant subtrees. Instead of duplicating nodes for identical subexpressions, the DAG reuses a
single shared node for all occurrences of the same computation. This reduces both the size of
the graph and the amount of computation needed.

Here is a sample:

```python
class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self):
        if self.left is None and self.right is None:
            return str(self.value)
        return f"({self.left} {self.value} {self.right})"


class DAGNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self):
        if self.left is None and self.right is None:
            return str(self.value)
        return f"({self.left} {self.value} {self.right})"


def parse_expression(expression):
    precedence = { '+': 1, '-': 1, '*': 2, '/': 2 }
    ops = []  # operators
    values = []  # operands

    def apply_operator():
        op = ops.pop()
        right = values.pop()
        left = values.pop()
        values.append(ASTNode(op, left, right))

    i = 0
    while i < len(expression):
        char = expression[i]
        if char.isalnum():  # numbers or variables
            start = i
            while i < len(expression) and expression[i].isalnum():
                i += 1
            values.append(ASTNode(expression[start:i]))
            continue
        elif char in precedence:  # operators
            while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence[char]:
                apply_operator()
            ops.append(char)
        elif char == '(':
            ops.append(char)
        elif char == ')':
            while ops and ops[-1] != '(': # .. until '('
                apply_operator()
            ops.pop()  # at last remove '('
        i += 1

    while ops:
        apply_operator()

    return values[0]


def ast_to_optimized_dag(ast):
    memo = { }  # store unique subexpressions and reuse them

    def traverse(node):
        if node is None:
            return None
        if node.left is None and node.right is None:  # leaf node
            return DAGNode(node.value)

        left = traverse(node.left)
        right = traverse(node.right)

        # unique key for the current subexpression
        key = (node.value, str(left), str(right))
        if key in memo:
            # reuse existing node if subexpression is already seen
            return memo[key]

        # else, create a new DAG node and memoize it
        dag_node = DAGNode(node.value, left, right)
        memo[key] = dag_node
        return dag_node

    return traverse(ast)

    ..
```


In this specific example:
- The AST duplicates the 'a * (b - 1)' subtree because it appears twice in the expression.
- The DAG identifies this redundancy and reuses the same node for both instances, marking
  it as [REUSE] in the rendered output.

The expression '((3 + (a * (b - 1))) + [REUSE: a * (b - 1)])' represents the optimised DAG
version of the arithmetic expression.
- The DAG optimises the computation by reusing the result of the subexpression 'a * (b - 1)',
  which appears multiple times in the original expression.
- Instead of *recomputing* 'a * (b - 1)' each time, it is computed once and shared in all
  instances where it appears. This reduces *redundant calculations*.
- The notation '[* (REUSE)] indicates that this specific subexpression has already been computed
  and reused in the DAG, optimising both memory usage and execution time.

By using a DAG:
1. *Fewer nodes*: The graph has fewer nodes, leading to lower memory usage.
2. *Less computation*: Reused nodes avoid recalculating the same values multiple times, which speeds up execution.
3. *Code Optimisation*: This principle underlies many compiler optimisations, such as common subexpression elimination.

In short, the AST is a straightforward representation, while the DAG improves efficiency by recognising and exploiting redundancies.

