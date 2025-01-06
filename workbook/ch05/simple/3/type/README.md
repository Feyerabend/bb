
## Types

The programs handled by the TACParser conform to a limited set of constructs in
Three-Address Code (TAC). These programs have their own "types" and structures.


### Types in the Programs

__1. Primitive Types__

	- Integer (int): Represent whole numbers, such as 42 or 0. These are used
        for constants, assignments, or arithmetic operations.

	- Floating-Point (float): Represent real numbers with decimal points, such
        as 3.14 or 20.786. These are inferred from the presence of a decimal point
        in constants.

	- Boolean (bool): While not explicitly represented, conditional statements
        (if t1 goto label) rely on boolean values derived from comparisons like
        <, >, ==. The comparison operators produce implicit boolean values.


__2. Derived Types__

	- Array (array[type, size]): Arrays are explicitly declared using syntax
        like int_array = int[10]. Each array has:
	      - A base type (int, float, etc.).
	      - A size (such as 10 in int[10]).
	      - A value representation, which could be thought of as a list or
              dictionary-like mapping for indices to values.

__3. Labels__

	- Labels (example 'label_1:') act as named markers for control flow. These are
        technically strings but are treated as unique identifiers for jumping in
        the control flow ('goto label_1').

__4. Implicit Types__

	- Temporary Variables: Variables like t1 or t2 store intermediate results.
        Their types are inferred dynamically based on the expressions they evaluate:
	      - t1 = x + 5 implies t1 is of type int if x and 5 are integers.
	      - t2 = y + 3.14 implies t2 is of type float if y is a float(ing point).

__5. Expressions__

	- Expressions involve terms and operators. The types of expressions depend on the operands:
      	- Arithmetic: int + int -> int, float + float -> float, etc.
	      - Comparisons: int < int -> bool, float == float -> bool, etc.

__6. Output Types__

	- The print statements output values, which could be of any type (int, float, etc.).
        This is the only interaction between the program and the "outside world."


#### Dynamic Type Handling

The programs are dynamically typed in execution but statically constrained by syntax and rules:

__1. Variable Type Inference__

Variables get their types at runtime based on context:
- Assignment of constants (x = 9) infers x is an integer.
- Assignment of expressions (t1 = x + 5) determines t1's type from x and the operator.

__2. Array Typing__
Arrays explicitly declare their types during initialization (e.g. int[10]).
Assignments (int_array[0] = 42) enforce type constraints dynamically:
- Assigning float to int_array would be invalid.

__3. Expression Evaluation__
The type of an expression depends on its operands:
- Arithmetic (+, -, *, /): Operands must be compatible, producing a result
  of the same type (int + int -> int).
- Comparisons (<, >, ==): Always produce a boolean type.

__4. Type Coercion__
There is no explicit handling of type coercion in the parser. Operations between
mismatched types (e.g. int + float) would likely result in undefined behavior
unless explicitly extended to handle such cases.

#### Structures and Semantics in the Handled Programs

The programs that the TACParser can handle are structured into specific constructs:

__1. Assignments__
- Syntax: x = 10, t1 = x + 5, etc.
- The left-hand side is a variable, and the right-hand side is an
  expression or constant.
- Type of the variable on the left-hand side is dynamically determined
  based on the right-hand side.

__2. Array Initialization__
- Syntax: int_array = int[10].
- Creates an array with a specified base type (int, float) and size.
  The array's type and size are added to the symbol table.

__3. Array Assignment__
- Syntax: int_array[0] = 42.
- Assigns a value to a specific index in an array. The type of the
  value must match the array's base type.

__4. Labels and Control Flow__
- Labels (label_1:) and control flow statements (if, goto) enable
  branching. For example:

```python
if t1 goto label_2
goto label_1
label_2:
```
- These rely on boolean expressions (t1).

__5. Printing__
- Syntax: print x.
- Outputs the value of a variable or array element to the console.
  The type of the printed value is determined dynamically.


#### Examples of Types in Action

__1. Primitive and Derived Types__

```python
x = 10         # x is int
y = 20.5       # y is float
int_array = int[10]   # int_array is array[int, 10]
float_array = float[5] # float_array is array[float, 5]
```

__2. Expressions__

```python
t1 = x + 5     # t1 is int, inferred from x and 5
t2 = y + 3.14  # t2 is float, inferred from y and 3.14
t3 = x < 15    # t3 is bool, result of comparison
```

__3. Arrays and Indexing__

```python
int_array[0] = 42     # 42 is an int, matching the array type
float_array[2] = 3.14 # 3.14 is a float, matching the array type
```

__4. Control Flow__

```python
t4 = x < 15    # t4 is bool
if t4 goto label_2
```

__5. Output__

```python
print x        # Outputs an int
print float_array[2]  # Outputs a float
```


#### How the Programs Work

The programs operate within a runtime environment where:

__1. Types Drive Behavior__
- Variables and arrays derive their types based on declarations and usage.
- Type mismatches (such as assigning float to int) would cause errors.

__2. Dynamic Symbol Table__
- All variables and arrays are tracked dynamically in the symbol_table.
  This provides a type-safe environment.

__3. Linear Execution with Control Flow__
- Statements are executed linearly, except when control flow constructs
  (if, goto) alter the flow.

__4. Simple Semantics__
- The semantics are straightforward: assignments store values, control
  flow changes the execution path, and printing outputs values.


### Summary

The programs that the TACParser handles have a small, well-defined type system
comprising integers, floats, booleans, arrays, labels, and expressions. The
dynamic nature of the symbol table enables runtime type checking and validation,
while the static constraints imposed by syntax ensure basic type safety. These
programs function as a simple intermediate representation, suitable for straightforward
computations and control flow.
