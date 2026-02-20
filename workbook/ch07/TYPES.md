
## Type Systems

Type systems emerged from the intersection of mathematical logic and
the theory of computation. Early influences include the work of *Bertrand Russell*
on logical paradoxes and *Alonzo Church*'s typed lambda calculus (1940s),
which introduced types as a way to prevent nonsensical expressions.
Later, *Haskell Curry* and others formalised connections between logic
and computation, culminating in the *Curry–Howard correspondence*,
where types are viewed as logical propositions and programs as proofs.

In programming languages, type systems became practically important with
languages like *Algol*, *ML*, and *Haskell*, where static typing was used
to improve safety and reasoning about programs. Modern languages now span
a wide spectrum, from dynamically typed (*Python*, *JavaScript*) to richly
statically typed (*Rust*, *Haskell*, *Scala*).



### Informal Description

A type system is a mechanism that classifies values and expressions into
categories called *types*, such as:
- integers
- booleans
- strings
- functions
- structured data

The primary goal is to prevent errors by ensuring operations are applied
to compatible kinds of data.

For example:
- Adding two numbers --> valid
- Adding a number and a string --> usually an error

Type systems help by:
- Catching mistakes early
- Documenting programmer intent
- Enabling compiler optimizations
- Improving program reliability



### Static vs Dynamic Typing

*Static typing*

Types are checked before execution: *compile time*.

Example:
```java
int x = 5;
x = "hello";  // Error
```

*Dynamic typing*

Types are checked at *runtime*.

```python
x = 5
x = "hello"   # Allowed
```



### Simple Examples

#### 1. Basic Type Error

```python
"Age: " + 42
```

This fails in many languages because a string
and an integer are incompatible.



#### 2. Well-Typed Expression

```text
3 + 5
```

Both operands are integers --> valid.



#### 3. Function Types

A function has a type describing its input and output:
```text
f : Int → Int
```

Meaning: `f` takes an integer and returns an integer.




### Why Type Systems?

Type systems are not only about preventing errors. They also:
- Provide a framework for reasoning about programs
- Encode invariants
- Serve as lightweight formal specifications
- Bridge programming and logic

In advanced settings, types can express:
- Polymorphism (`List<T>`)
- Ownership and memory safety (Rust)
- Logical properties (dependent types)




### Formal Introduction

A *type system* classifies program expressions according to the kinds of values they compute,
ensuring certain correctness properties. Typing judgments are written as:

```math
\Gamma \vdash e : \tau
```

where:
- $\Gamma\$ is the typing context (variables and their types)
- $e$ is an expression
- $\tau$ is the type
- $\Gamma \vdash e : \tau$ reads: "under context $\Gamma$, expression $e$ has type $\tau$"



#### Example: Variable Typing

```math
\frac{x:\tau \in \Gamma}{\Gamma \vdash x : \tau} \quad (\text{Var})
```

If a variable $x$ has type $\tau$ in the context, it is assigned type $\tau$.



#### Example: Addition

```math
\frac{\Gamma \vdash e_1 : \text{Int} \quad \Gamma \vdash e_2 : \text{Int}}{\Gamma \vdash e_1 + e_2 : \text{Int}} \quad (\text{Add})
```

If $e_1$ and $e_2$ are integers, then $e_1 + e_2$ is also an integer.



#### Simply-Typed Lambda Calculus

*Abstraction:*

```math
\frac{\Gamma, x:\tau_1 \vdash e : \tau_2}{\Gamma \vdash (\lambda x.e) : \tau_1 \to \tau_2} \quad (\text{Abs})
```

*Application:*

```math
\frac{\Gamma \vdash e_1 : \tau_1 \to \tau_2 \quad \Gamma \vdash e_2 : \tau_1}{\Gamma \vdash e_1 \, e_2 : \tau_2} \quad (\text{App})
```

These formal rules allow reasoning about programs rigorously
and form the foundation for modern type theory.  

