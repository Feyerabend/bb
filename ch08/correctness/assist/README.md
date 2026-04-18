
## Dependently Typed Programming Languages and Interactive Theorem Provers

Dependently typed programming languages and interactive theorem provers are powerful
tools for formal verification, proof development, and verified programming. These
systems leverage the deep connection between logic, mathematics, and computation,
rooted in the Curry-Howard correspondence, which equates types to logical propositions
and programs to proofs. This document provides an overview of three prominent
systems--*Agda*, *Coq*, and *Lean*--each embodying distinct approaches to theorem proving,
program verification, and formal mathematics within the framework of dependent types
and constructive logic. Below, we explore their features, mathematical foundations,
historical context, and practical applications, including examples of their use.


### Mathematical Background: Dependent Types and Constructive Logic

Dependently typed systems build on the foundation of *dependent type theory*, an
extension of simple type theory where types can depend on values. For example, in
a dependently typed language, one can define a type `Vector n` of lists with exactly
`n` elements, where `n` is a value, not just a static type. This expressiveness
allows types to encode logical propositions, enabling rigorous specification and
verification of programs and mathematical proofs.

These systems are grounded in *constructive logic* (or intuitionistic logic), where
a proposition is considered true only if a constructive proof--essentially a program
or algorithm--can be provided. Unlike classical logic, which assumes the law of the
excluded middle (i.e., every statement is either true or false), constructive logic
requires explicit evidence, aligning closely with computational processes. The
*Curry-Howard correspondence* underpins this paradigm, treating proofs as programs
and propositions as types, enabling formal verification through type checking.

Historically, dependent type theory emerged from the work of logicians and computer
scientists like *Per Martin-Löf*, whose intuitionistic type theory (1970s–1980s)
forms the basis for Agda and influences Coq and Lean. Martin-Löf’s work built on
earlier ideas from *Alonzo Church*’s lambda calculus and *Haskell Curry*’s combinatory
logic, aiming to provide a unified foundation for mathematics and computation. The
development of these systems reflects a broader trend in computer science and
mathematics toward formalisation, spurred by the need to eliminate errors in software
and proofs, as seen in projects like the formalisation of the *Four Colour Theorem*
or the *Kepler Conjecture*.


### Agda

*Agda* is a dependently typed functional programming language designed for writing
programs and proofs within a single framework. In Agda, types serve as logical
propositions, and programs correspond to proofs of those propositions, following
the Curry-Howard correspondence. Proof construction in Agda is akin to programming:
users write code that must type-check against a specified proposition, ensuring
correctness. Agda emphasises *human-guided proof development* with minimal automation,
relying on explicit constructions and type-driven guidance through its interactive
development environment (e.g., Emacs integration or VS Code with plugins).

#### Features and Philosophy

- *Type-Driven Development*: Agda’s strength lies in its expressive type system,
  which allows users to encode complex specifications directly in types. For example,
  a function’s type can guarantee properties like “this sorting algorithm always
  returns a sorted list.”
- *Minimal Automation*: Agda expects users to construct proofs manually, guided by
  type errors and interactive feedback. This makes it ideal for teaching and
  exploring logical foundations but less suited for large-scale automation.
- *Functional Programming Paradigm*: Agda supports pure functional programming with
  features like pattern matching, higher-order functions, and dependent pattern matching.

#### Example

A classic example in Agda is defining a dependently typed `Vector` type and proving
properties about it. Below is a simplified Agda program defining a `Vector` type
and a safe `head` function that extracts the first element of a non-empty vector:

```agda
data Nat : Set where
  zero : Nat
  suc  : Nat → Nat

data Vector (A : Set) : Nat → Set where
  []   : Vector A zero
  _::_ : {n : Nat} → A → Vector A n → Vector A (suc n)

head : {A : Set} {n : Nat} → Vector A (suc n) → A
head (x :: xs) = x
```

Here, the `head` function is guaranteed to work only on non-empty vectors
(with length `suc n`), preventing runtime errors like accessing the head
of an empty list.

#### History

Agda originated as a research project at *Chalmers University* in Sweden,
with its first version developed in the 1990s by *Catarina Coquand* and others,
building on Martin-Löf’s type theory. The modern version, Agda 2, was developed
by *Ulf Norell* in the 2000s, emphasising usability and integration with
interactive environments. Agda is often used in academic settings for teaching 
ype theory and exploring dependently typed programming.

#### Use Cases

- *Verified Programming*: Writing programs with correctness guarantees, such
  as type-safe data structures or protocols.
- *Teaching Logic*: Agda’s explicit approach makes it ideal for teaching
  constructive logic and type theory.
- *Research in Type Systems*: Agda is a platform for experimenting with
  advanced type system features, like cubical type theory for homotopy type theory.


### Coq

*Coq* is an interactive theorem prover based on the *Calculus of Inductive
Constructions (CIC)*, a powerful dependent type theory that extends Martin-Löf’s
type theory with inductive types and coinductive types. Coq allows users to
construct proofs interactively by applying *tactics*, which are commands that
automate common proof patterns (e.g., induction, rewriting). Coq supports
constructive proofs by default but can be extended to classical logic. It
also allows *program extraction*, enabling verified programs to be translated
into functional languages like OCaml or Haskell.

#### Features and Philosophy

- *Tactic-Based Proving*: Coq’s tactic system allows users to build proofs
  incrementally, combining manual guidance with automation. Tactics like
  `induction` or `simpl` handle repetitive tasks, making Coq suitable for
  large-scale proofs.
- *Program Extraction*: Coq can extract certified programs from proofs,
  enabling the development of verified software.
- *Rich Ecosystem*: Coq has a mature ecosystem with libraries like *Ssreflect*
  for mathematical proofs and tools for integrating with external solvers.


#### Example

A well-known Coq project is the *CompCert* verified C compiler, which guarantees
that compiled code preserves the semantics of the source program. Below is a
simplified Coq example proving that addition is commutative for natural numbers:

```coq
Inductive nat : Type :=
  | O : nat
  | S : nat -> nat.

Fixpoint plus (n m : nat) : nat :=
  match n with
  | O => m
  | S n' => S (plus n' m)
  end.

Theorem plus_comm : forall n m : nat, plus n m = plus m n.
Proof.
  intros n m. induction n as [|n' IH].
  - simpl. induction m as [|m' IHm]. reflexivity. simpl. rewrite <- IHm. reflexivity.
  - simpl. rewrite IH. simpl. reflexivity.
Qed.
```

This proof uses tactics like `intros`, `induction`, and `reflexivity` to
construct a formal argument that `n + m = m + n`.

#### History

Coq was initiated in 1984 at *INRIA* in France by *Thierry Coquand* and
*Gérard Huet*, building on the Calculus of Constructions. Its name is a nod
to both Coquand and the French word for “rooster” (a symbol of France).
Over the decades, Coq has evolved into a robust tool for formal verification,
with significant milestones like the formalisation of the *Four Colour Theorem*
(2005) and the *Feit-Thompson Theorem* (2012).

#### Use Cases

- *Large Formal Proofs*: Coq is used for formalising complex mathematical theorems,
  such as the *Odd Order Theorem*.
- *Verified Software*: Projects like CompCert demonstrate Coq’s ability to verify
  critical software systems.
- *Formalised Mathematics*: Coq’s libraries support formalising areas like algebra,
  number theory, and topology.


### Lean

*Lean* is an interactive theorem prover and dependently typed programming language
designed to combine the expressiveness of Coq with modern programming language features
and stronger automation. Like Coq, Lean is based on a variant of dependent type theory
(similar to the Calculus of Inductive Constructions) but emphasises usability and
performance. Lean is particularly known for its *mathlib* library, an extensive,
community-driven collection of formalised mathematics covering areas from algebra
to analysis.

#### Features and Philosophy

- *Balanced Automation*: Lean offers powerful automation through tactics and decision
  procedures, reducing manual effort compared to Agda or Coq.
- *Modern Design*: Lean’s syntax is inspired by functional programming languages,
  making it accessible to programmers.
- *Mathlib*: Lean’s mathlib is a rapidly growing library that formalises a wide range
  of mathematics, from basic number theory to advanced topics like category theory.

#### Example

Lean is often used to formalise mathematical theorems. Below is an example proving that
the square of an even number is even:

```lean
def even (n : ℕ) : Prop := ∃ k, n = 2 * k

theorem even_square_even : ∀ n : ℕ, even n → even (n * n) :=
begin
  intros n h,
  cases h with k hk,
  use 2 * k * k,
  rw hk,
  ring,
end
```

This proof uses Lean’s tactic system (`begin`/`end` block) and the `ring` tactic to
simplify algebraic expressions.

#### History

Lean was developed by *Leonardo de Moura* at Microsoft Research starting in 2013, with
Lean 4 (released in 2021) introducing significant improvements in performance and usability.
Lean’s design draws inspiration from Coq but prioritises automation and a modern programming
experience. The *mathlib* community, led by mathematicians like *Kevin Buzzard*, has made
Lean a leading tool for formalising mathematics, with projects like the formalisation of
*perfectoid spaces* (2019).

#### Use Cases

- *Formal Mathematics*: Lean’s mathlib supports formalising complex mathematical structures,
  making it popular among mathematicians.
- *Verified Algorithms*: Lean is used to verify algorithms in areas like cryptography and optimisation.
- *Teaching*: Lean’s accessible syntax and automation make it suitable for teaching formal methods.


### Comparison Table

Below is a comparison table summarising the key features of Agda, Coq, and Lean:

| *Tool* | *Type* | *Automation Level* | *Logic / Foundation* | *Typical Use Cases* | *Key Libraries/Tools* |
|----------|----------|----------------------|-------------------------|-----------------------|-------------------------|
| *Agda* | Dependently typed language | Manual (type-driven) | Intuitionistic type theory | Verified programming, type-level proofs, teaching logic | Standard library, Cubical Agda |
| *Coq* | Interactive theorem prover | Semi-automated (tactics) | Calculus of Inductive Constructions | Large formal proofs, verified software, formalized mathematics | Ssreflect, CompCert, Mathematical Components |
| *Lean* | Interactive theorem prover & language | Semi-automated with strong automation | Dependent type theory (CIC variant) | Formal mathematics (mathlib), verified algorithms, teaching | mathlib, Lean 4 metaprogramming |


### Historical Context and Impact

The development of Agda, Coq, and Lean reflects the evolution of formal methods in computer
science and mathematics. In the 1980s and 1990s, the need for reliable software and rigorous
mathematical proofs drove the creation of tools like Coq, which built on earlier systems like
*Automath* (1960s, by Nicolaas de Bruijn). Agda emerged as a research tool to explore dependently
typed programming, while Lean represents a modern synthesis, addressing usability and automation
challenges.

These tools have had a profound impact:
- *Software Verification*: Projects like CompCert (Coq) and *seL4* (a verified microkernel,
  partially using Isabelle/HOL but inspiring Lean and Coq work) demonstrate the practical
  value of formal verification.
- *Mathematical Formalisation*: The *Flyspeck project* (formalising the Kepler Conjecture
  in HOL Light) and Lean’s mathlib highlight the growing role of theorem provers in mathematics.
- *Education*: All three tools are used in universities to teach logic, type theory, and
  formal methods, with Lean gaining traction for its accessibility.


### Future Directions

The field of dependently typed programming and theorem proving continues to evolve. Agda is
exploring advanced type theories like *cubical type theory* for homotopy type theory. Coq is
expanding its libraries and improving tactic automation. Lean, with its active mathlib community,
is pushing the boundaries of formalised mathematics, aiming to formalise modern results like
*Fermat’s Last Theorem*. Integration with AI and machine learning (e.g., Lean’s use in automated
theorem proving research) is also a promising frontier.


### Conclusion

Agda, Coq, and Lean represent distinct but complementary approaches to dependently typed programming
and interactive theorem proving. Agda excels in type-driven, manual proof construction, ideal for 
teaching and research. Coq offers a robust tactic-based system for large-scale verification projects.
Lean balances automation and usability, making it a favourite for formalising mathematics. Together,
these tools advance the goal of error-free software and mathematics, rooted in the deep interplay of
logic and computation.

