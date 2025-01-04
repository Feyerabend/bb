
## Simple Compiler: Static Single Assignment (SSA) Form

Static Single Assignment (SSA) is an intermediate representation (IR) used in compilers and program
analysis to simplify certain optimization techniques. In SSA form, each variable is assigned exactly
once, and every variable is defined by a unique assignment. This makes control flow analysis and optimization
easier.

1. *One Assignment per Variable*: Each variable in the program is assigned a value exactly once. If a variable
   is re-assigned, a new version of the variable is created.

2. *Phi Functions*: At points where control flow merges (e.g. after an if or goto), SSA introduces special
   functions called "phi functions." These functions combine the values of variables from different branches
   of the control flow.

3. *Simplified Control Flow*: Since variables are assigned only once, SSA eliminates the need for complex data
   flow analysis and simplifies optimizations like constant propagation, dead code elimination, and loop
   optimizations.


### Example Program and Conversion Process

The example TAC (Three-Address Code) program provided performs a simple conditional check and updates a
variable x based on the value of t1. The TAC representation of the program is:

```
x = 10
t1 = x < 15
label label_1:
if t1 goto label_2
t2 = x + 1
x = t2
goto label_1
label label_2:
```

But to simplify and avoid parsing again, we use the TAC in the following form:

```python
tac_program = [
    {"type": "assignment", "left": "x", "right": {"type": "term", "value": "10"}},
    {"type": "assignment", "left": "t1", "right": {"type": "binary_op", "left": "x", "operator": "<", "right": "15"}},
    {"type": "label", "name": "label_1"},
    {"type": "if", "condition": {"type": "term", "value": "t1"}, "label": "label_2"},
    {"type": "assignment", "left": "t2", "right": {"type": "binary_op", "left": "x", "operator": "+", "right": "1"}},
    {"type": "assignment", "left": "x", "right": {"type": "term", "value": "t2"}},
    {"type": "goto", "label": "label_1"},
    {"type": "label", "name": "label_2"}
]
```

This program includes basic operations like assignments, binary operations, a conditional jump (if),
and labels. In SSA, every variable is versioned, and at the points where control flow merges (like the
if statement or goto), we introduce phi functions.


__1. Initial Setup__
- We initialize a SSAConverter class, which takes the TAC program and prepares to convert it into SSA form.
- The converter uses `self.variable_versions` to keep track of versions of variables (so `x_0`, `t1_0`), ensuring
  each variable is assigned exactly once.

__2. Processing the Program__
- The program is processed instruction by instruction:
- Assignments: For every assignment, the variable on the left-hand side (LHS) is assigned a new version
  (`x_0`, `t1_0` ..).
- Binary Operations: If the right-hand side (RHS) involves binary operations, the operands are replaced
  with their latest versions.
- Control Flow (if and goto): When a conditional or jump occurs, phi functions are added to merge variable
  versions across control flow branches.
- Labels: At the labels where control flow converges, phi functions are inserted to handle different variable
  versions that may arrive from different branches.

__3. Handling Phi Functions__
- At labels where variables' values may come from different branches (after an if or goto), we add phi functions.
  These functions select the appropriate value based on the execution path.
- The `add_phi_function` method records the phi functions for variables that may have different values at a label.

__4. SSA Output__
- After processing all statements, the SSA form of the program is produced, with updated versions of variables
  and phi functions at control flow merge points.


```python
class SSAConverter:
    def __init__(self, tac_program):
        self.tac_program = tac_program
        self.variable_versions = {}  # tracks versions of variables
        self.ssa_program = []        # stores the SSA program instructions
        self.label_to_phi = {}       # tracks phi functions at labels
```

We set up containers to track variable versions, the final SSA program, and phi functions at labels.

```python
    def get_new_version(self, var):
        if var not in self.variable_versions:
            self.variable_versions[var] = 0
        else:
            self.variable_versions[var] += 1
        return f"{var}_{self.variable_versions[var]}"
```

`get_new_version` generates a new version for a variable by incrementing its version count.

```python
    def get_current_version(self, var):
        if var.isdigit():
            return var
        return f"{var}_{self.variable_versions.get(var, 0)}"
```

`get_current_version` fetches the latest version of a variable, or simply returns its constant
value if it's not a variable.

```python
    def add_phi_function(self, label, var):
        if label not in self.label_to_phi:
            self.label_to_phi[label] = {}
        if var not in self.label_to_phi[label]:
            self.label_to_phi[label][var] = []
        self.label_to_phi[label][var].append(self.get_current_version(var))
```

The `add_phi_function` inserts phi functions at the appropriate labels where control flow merges.

```python
    def convert(self):
        for stmt in self.tac_program:
            if stmt['type'] == "assignment":
                new_var = self.get_new_version(stmt['left'])
                if stmt['right']['type'] == "binary_op":
                    left = self.get_current_version(stmt['right']['left'])
                    right = self.get_current_version(stmt['right']['right'])
                    stmt['right']['left'] = left
                    stmt['right']['right'] = right
                elif stmt['right']['type'] == "term":
                    stmt['right']['value'] = self.get_current_version(stmt['right']['value'])
                stmt['left'] = new_var
                self.ssa_program.append(stmt)
            elif stmt['type'] == "if":
                condition = stmt['condition']
                if condition['type'] == "term":
                    condition['value'] = self.get_current_version(condition['value'])
                stmt['condition'] = condition
                label = stmt['label']
                for var in self.variable_versions:
                    self.add_phi_function(label, var)
                self.ssa_program.append(stmt)
            elif stmt['type'] == "goto":
                label = stmt['label']
                for var in self.variable_versions:
                    self.add_phi_function(label, var)
                self.ssa_program.append(stmt)
            elif stmt['type'] == "label":
                self.ssa_program.append(stmt)
                label_name = stmt['name']
                if label_name in self.label_to_phi:
                    for var, versions in self.label_to_phi[label_name].items():
                        phi_stmt = {
                            "type": "phi",
                            "var": var,
                            "versions": versions
                        }
                        self.ssa_program.append(phi_stmt)
            else:
                self.ssa_program.append(stmt)
        return self.ssa_program
```

The convert method processes each TAC statement:
- Assignments are updated with new versions.
- Conditions are modified to use the current versions.
- Phi functions are added at labels where control flow merges.
- Labels and Gotos also trigger the insertion of phi functions.


### Output

For the provided TAC input, the resulting SSA program would look something like this:

```python
x_0 = 10
t1_0 = x_0 < 15
label label_1:
if t1_0 goto label_2
t2_0 = x_0 + 1
x_1 = t2_0
goto label_1
label label_2:
x = phi(x_0)
t1 = phi(t1_0)
```

Things that happends:
- *Variable Renaming*: Every variable has been renamed with a unique version, such as `x_0`, `t1_0`, etc.
- *Phi Functions*: At `label_2`, we use a phi function to merge different versions of variables coming
  from different control flow paths.

The current implementation correctly handles the introduction of phi functions, but by optimising their
management further (removing redundant ones and ensuring they are only used when truly necessary), we can make
the SSA form more efficient for later stages of compilation or analysis. The key is tracking when a
variable is reassigned and eliminating phi functions when the variable no longer needs to merge different
control flow values. This ensures that the SSA representation remains optimal and doesn't include
unnecessary operations.


### The Phi Function in SSA

In SSA, if a variable needs to take on different values depending on control flow, it gets
renamed each time it is assigned a new value. However, control flow (such as conditionals
or loops) can cause a variable to have multiple potential values coming from different branches
of the program. In these cases, a phi function is used to select the correct value depending
on which branch of the program was executed.

A phi function (usually denoted as the Greek letter φ) is a special kind of function used to
merge variables in SSA form when there are multiple control flow paths leading to the same
point. It's a tool used to ensure that the proper value is chosen from different branches of
execution.

1. *Merging Control Flow*: The phi function merges values coming from different control flow
   paths (like branches in an if statement or goto).

2. *Selects One Value*: The phi function allows a variable to have different possible values
   depending on which path was taken. It selects the correct value at the merge point.

3. *Used Only at Merge Points*: Phi functions only appear at points in the program where
   control flow paths merge (such as after a conditional jump, like the end of an if statement
   or goto).

A phi function is typically represented as:

$$var = φ(var_1, var_2, ..., var_n)$$

This means that at this point in the program, var can take any of the values var1, var2, .., varn,
depending on which control flow path was taken to reach this point.

#### When Do You Need Phi Functions?

Control Flow Divergence: Phi functions are needed when a variable can have different values from
different execution paths. For instance:
- In an if statement, the variable might be assigned different values in the true or false branches.
- In a loop, a variable may take on values from multiple iterations or different parts of the loop.
- Variable Merging: When two control flow paths come together (such as after an if-else or goto),
  the values from those paths must be merged, and phi functions handle that merging.

#### How Phi Functions Work

Consider a situation where you have two branches, and a variable is assigned a value in each branch.
When the branches merge, the value of the variable at the merge point depends on which branch was
executed. The phi function resolves this ambiguity by selecting the correct value.

Here's a simple example without specific syntax:

1. Branch 1 assigns a value to x: `x = 5`

2. Branch 2 assigns a different value to x: `x = 10`

Now, both branches merge into a common point. At this merge point, we can't just use x because there
are two possible values for x. This is where the phi function comes in. The phi function will decide
which value to use at this merge point:

- At the merge point: `x = φ(5, 10)`

This means:

- If the execution came from Branch 1, x will be 5.
- If the execution came from Branch 2, x will be 10.

Now in SSA, as we have learned every variable gets a version number whenever it's assigned a new value.
For example, `x_1`, `x_2`, etc. would be different versions of the variable x. But after a merge point
(like after an if or goto), we need to combine these versions to make it clear which version of x should
be used at the merge point. The phi function accomplishes this.

The phi function typically appears as part of the intermediate representation (IR) of a program, just
before the program's control flow continues after a branch. The variable is assigned the appropriate
version coming from the control flow path.

Phi Function Rules:
1. *One Phi Function Per Variable*: At a merge point, there will be one phi function for each variable
   that has different values on the different control flow paths.
2. *Merging from Multiple Paths*: The phi function can merge values from more than two paths. For example,
   in a program with multiple conditionals or loops, a variable could come from more than two paths and
   the phi function will merge these values.
3. *Used Only at Merge Points*: You will only see phi functions at points where multiple execution paths
   converge (e.g., at the target of an if statement or a loop).


- Phi Functions are Static: The phi function doesn't depend on runtime values but rather on the static
  structure of the program's control flow. It doesn't perform an operation during runtime;
  it is simply part of the SSA representation.
- Efficiency: Phi functions add clarity to SSA form but can be costly to compute in terms of the number
  of operations. However, they are crucial for representing complex control flow with proper variable assignments.

Example in the Context of Control Flow:

```
if condition:
    x = 5
else:
    x = 10

y = x + 1
```

Before SSA, we have:
- In the if branch: x = 5
- In the else branch: x = 10
- After the branches merge, y = x + 1, but we don't know which x value to use since it could either be 5 or 10.

In SSA, at the merge point of the branches, we would have:

```
x = φ(5, 10)
y = x + 1
```

Here, x takes the correct value depending on whether the if or else branch was executed.

#### Summary of Phi Functions in SSA

* Phi functions are used in SSA to handle variable assignments that depend on control flow.
* They merge values coming from different control flow paths (e.g., after an if statement or goto).
* They ensure correct value selection at merge points, enabling a program to correctly choose
  between different potential values based on the execution path taken.
* Each variable that could have multiple values at a merge point will have a corresponding phi function.

Phi functions are critical for keeping track of variables that could change at multiple points
due to branching and are an essential feature of SSA-based intermediate representations. They 
allow compilers to reason more effectively about variables, optimize code, and perform advanced
analyses like constant propagation, dead code elimination, and more.

