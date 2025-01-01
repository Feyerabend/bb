
## A Simple Compiler: Three-Address Code (TAC)

..

```
tac.py -> comp.py -> vm.py
```


### Optimisation

What can this Three-Address Code be used for?

`opt.py`

1. Constant Folding: If both operands in an expression are constants, the expression is evaluated at compile time.


`opt2.py`

1. Constant Folding: If both operands in an expression are constants, the expression is evaluated at compile time.
2. Common Subexpression Elimination (CSE): If an expression is repeated multiple times, it's computed only once and reused.
3. Dead Code Elimination (DCE): If a variable is assigned a value but never used, we remove its computation.



1. Constant Folding:
- Expressions like 7 + 9 are evaluated at compile time and replaced with 16, making the expression simpler. In
  the code, t2 = 7 + 9 becomes t2 = 16.

2. Common Subexpression Elimination (CSE):
- If a subexpression like x + y is computed more than once (e.g., t1 = x + y and t6 = x + y), we reuse it instead
  of recomputing it.
- t6 = x + y would be removed or replaced by using t1.

3. Dead Code Elimination (DCE):
- Variables like t7 that are assigned but never used in subsequent operations are removed.
- t7 = 0 will be eliminated from the final TAC because it's not used anywhere.
