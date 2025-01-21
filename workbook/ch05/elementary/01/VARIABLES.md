
## Rules for Variables and Scope in PL/0

1. Declaration and Scope:
- Variables must be declared in the declaration section of a block before they can be used.
  This applies to the main program block as well as nested procedure blocks.
- The scope of a variable is limited to the block in which it is declared, including any
  nested blocks or procedures. However, inner blocks can shadow variables from outer blocks.
  (We restrict this to local variables declared in procedures, from the global level?)

2. Global vs. Local Variables:
- Global variables:
    - Variables declared in the main program block are global.
    - They are accessible throughout the entire program, including inside procedures,
      unless shadowed by a local variable with the same name.
- Local variables:
    - Variables declared within a procedure block are local to that procedure.
    - They are not accessible outside the procedure in which they are defined.

3. Lifetime:
- The lifetime of a variable is tied to the activation of the block in which it is declared:
    - Global variables persist for the lifetime of the entire program.
    - Local variables are created when the block or procedure is entered and destroyed when
      the block or procedure exits. (Runtime.)

4. Usage in Expressions:
- Variables can be used in expressions and assignments once declared. For example:

```pascal
var x, y;
x := y + 5;
```

5. Variable Shadowing:
- A variable declared in an inner block can shadow a variable with the same name from an outer
  block. In such cases, the inner variable takes precedence within the inner block.

6. Procedures and Parameters:
- PL/0 does not support procedure parameters in its standard form. We do not either.

Example of Variable Scopes in PL/0

```pascal
var x, y;           // global variables
procedure P;
    var y, z;       // local variables to P
    begin
        y := 10;    // refers to local y
        z := x + y; // refers to global x and local y
    end;

begin
    x := 5;         // assign to global x
    call P;         // call procedure P
end.
```

- Global Variables:
    - x and y are declared at the program level and accessible throughout the entire program.
- Local Variables:
    - y and z inside P are local to P and not accessible outside it.
- Shadowing:
    - The y inside P shadows the global y. Any reference to y inside P uses the local y.

In extended versions of PL/0 (which often support procedure parameters),
the behavior aligns more closely with Pascal.

In Summary
- Variables in PL/0 are declared in the declaration section of a block.
- Global variables are declared in the main program block and are accessible
  everywhere unless shadowed.
- Local variables are declared in procedures and are accessible only within
  that procedure.
- PL/0 uses block scoping rules, where each block introduces a new scope,
  and variables have a lifetime tied to their block's execution.
