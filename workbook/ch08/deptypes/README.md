
## Dependent Types

Here we collect in part comments and references from the book, for easy access. Another part
is a practical introduction to dependent types with less assumptions of mathematical or formal
logic background i contrast to the book, which you can find below.


### Comments to the Book

Papers by Per Martin-Löf: https://archive-pml.github.io/. Wikipedia on Per Martin-Löf:
https://en.wikipedia.org/wiki/Per_Martin-L%C3%B6f.

..


### Practical Introduction

Dependent types[^dep] are a fascinating and powerful concept in type theory that blur the traditional
boundary between *types* (which classify data) and *values* (the data itself). If you’re familiar
with basic type systems in languages like Java or Haskell--where types like `int` or `List<String>`
restrict what values a variable can hold--dependent types take this idea further: they allow types
to depend on runtime *values*. This means you can express richer, more precise guarantees about
your programs at compile time.

[^dep]: Overview: https://en.wikipedia.org/wiki/Dependent_type.


### Types That "Depend" on Values

In most languages, types and values live in separate worlds. For example:
- A function `head : List<Int> → Int` might crash if the list is empty.
- An array’s type `Array<Int>` doesn’t specify its length, so you can’t statically prevent out-of-bounds
  errors.

With dependent types, *types can be parameterized by values*. For instance:
- `head : (v : Vector n) → n > 0 → Int`  
  Here, the type system enforces that `head` can only be called on a `Vector` with length `n > 0`.
- `Matrix m n` (a matrix with `m` rows and `n` columns) ensures at compile time that multiplying two
  matrices `Matrix m n` and `Matrix n p` produces a `Matrix m p`.

This turns many runtime errors (like "empty list" or "dimension mismatch") into *compile-time type errors*.


### Practical Benefits

1. *Safer Code*: By encoding invariants (e.g., list length, divisor ≠ 0) directly into types, bugs
   are caught earlier.

2. *Documentation*: Types become self-documenting. For example, a sorting function's type could
   specify that the output is sorted:
   ```idris
   sort : (list : List Int) -> (sortedList : List Int * IsSorted sortedList)
   ```

3. *Formal Verification*: Dependent types bridge programming and mathematical proofs. A function
   that appends two vectors can have a type proving the output length is `n + m`:
   ```agda
   append : Vector n A → Vector m A → Vector (n + m) A
   ```

### Curry-Howard Connection

Dependent types are deeply tied to the *Curry-Howard isomorphism*, which views:
- *Types* as logical *propositions*,
- *Programs* as *proofs* of those propositions.

For example, the type `∀ n : Nat, Vector n Int → n ≥ 0` is a proposition stating "all vectors have
non-negative length." A program inhabiting this type is a *proof* of that fact. This lets you write
code that's also a machine-checkable mathematical proof.


### Languages with Dependent Types

- *Idris*: Designed for practical programming with dependent types.

- *Agda*: Focused on proof assistants and formal mathematics.

- *Coq*: A proof assistant used for verified software (e.g., CompCert compiler).

- *Lean 4*: Combines dependent types with a powerful programming ecosystem.


### Challenges

1. *Complexity*: Type checking can become undecidable (though languages impose restrictions).

2. *Verbosity*: Writing detailed type annotations and proofs requires effort.

3. *Tooling*: Less mature than mainstream languages, but improving!


### Useful?

Dependent types are a frontier in making software *safer* and *more reliable*. They’re used in:

1. *Critical Systems*:
   - Aerospace, medical devices, or cryptography, where bugs are catastrophic. Example:
     [*Fiat Cryptography*](https://github.com/mit-plv/fiat-crypto) uses Coq to generate
     verified cryptographic code.

2. *Formally Verified Software*:
   - Projects like [*CompCert*](https://compcert.org/) (a verified C compiler) or
     [*seL4*](https://sel4.systems/) (a verified microkernel) rely on dependent types
     for correctness.

3. *Domain-Specific Invariants*:
   - Matrix dimensions in linear algebra, financial calculations (e.g., ensuring
     `balance ≥ 0`), or hardware design (e.g., bit-width guarantees).

4. *Research and Education*:
   - Teaching formal methods, exploring program correctness, or modeling mathematical
     structures (e.g., homotopy type theory).

Dependent types might feel abstract at first, but they offer a way to unify *programming*, *logic*,
and *proofs*--all while writing code that's correct by construction.


### Trade-offs

Dependent types are powerful, but they come with trade-offs and aren’t universally applicable.

1. *Complexity and Learning Curve*:
   - *Type systems become Turing-complete*: With dependent types, types can depend on arbitrary
     computations, making type checking as hard as solving arbitrary mathematical problems. This
     can lead to undecidable type checking unless restricted (e.g., via termination checking in
     Agda/Idris).
   - *Cognitive overhead*: Developers must think simultaneously about programming *and* proving
     properties, which requires familiarity with formal logic and type theory.

2. *Verbosity*:
   - *Explicit proof terms*: To satisfy the type checker, programmers often need to write detailed
     proofs (e.g., `n + m ≡ m + n` for commutativity). This can bloat code with boilerplate.
   - *Annotation burden*: Types may require explicit value parameters (e.g., `Vector 5 Int` instead
     of just `List Int`), complicating code.

3. *Tooling and Ecosystem*:
   - *Immature tooling*: Languages like Idris, Agda, and Lean have fewer debuggers, IDE integrations,
     and libraries compared to mainstream languages.
   - *Limited community*: Smaller ecosystems mean fewer tutorials, examples, and Stack Overflow answers.

4. *Performance*:
   - *Proofs at runtime*: In some languages (e.g., Idris), proof terms are retained at runtime, adding
     overhead. While techniques like proof erasure exist, they’re not always automatic.
   - *Compilation time*: Type checking with complex dependent types can slow compilation.

5. *Overkill for Simple Problems*:
   - For many applications (e.g., a simple CRUD app), dependent types add unnecessary complexity.
     A Python script with unit tests might be more pragmatic.


### *Not* Successful?

1. *Rapid Prototyping*:
   - If speed of development is critical, dependent types can slow you down. For example, tweaking
     a UI or experimenting with a new algorithm might not benefit from formal proofs.

2. *Dynamic Domains*:
   - Problems requiring runtime flexibility (e.g., processing unstructured JSON data, scripting)
     clash with dependent types’ static guarantees.

3. *Team Expertise*:
   - Teams unfamiliar with formal methods or type theory may struggle to adopt dependent types effectively.

4. *Undecidable Properties*:
   - Some invariants can’t be easily encoded in types (e.g., "this function connects to a database").
     Here, runtime checks or contracts may still be needed.


Dependent types excel in *high-assurance, low-defect-tolerance domains* but are overkill for general-purpose programming.
