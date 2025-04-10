
## Dependent Types in Python

This code base implements a dependent type theory system in Python, with progressive
enhancements across multiple files. Each file builds upon the previous one, adding new
features and capabilities.

### [dep1.py](./dep1.py) - Basic Foundation
- Establishes the core data structure using Python's `dataclasses`
- Defines base types: `NatType`, `PiType`, `IdType`
- Implements basic terms: `Var`, `Lam`, `App`, `Refl`
- Provides a basic type checker with a `Context` dictionary
- Demonstrates a simple lambda term with reflexivity

### [dep2.py](./dep2.py) - Improved Representation
- Refines the structure with better base classes
- Adds string representation methods (`__str__`)
- Focuses on the identity function and Pi types
- Enhances error handling in the type checker
- Includes an example of typechecking the identity function

### [dep3.py](./dep3.py) - Identity Types
- Extends dep2.py with proper identity types
- Adds support for the `Refl` term (reflexivity)
- Improves string representations for all terms
- Demonstrates both the identity function and reflexivity proofs
- Shows Pi types and Id types working together

### [dep4.py](./dep4.py) - Equality Operations
- Adds `Sym` (symmetry) and `Trans` (transitivity) operations
- Enhances the type checker to handle these equality operations
- Shows how to combine equalities using transitivity
- Demonstrates the algebraic properties of the identity type
- Includes comprehensive examples with variables in a context

### [dep5.py](./dep5.py) - Beta Reduction
- Implements beta reduction for evaluating terms
- Adds a substitution function for replacing variables
- Shows how both lambda terms and proof terms reduce
- Demonstrates the computational aspect of the type theory
- Includes examples of applying functions to arguments

### [dep6.py](./dep6.py) - Extended Type System
- Adds new types: `Bool`, `Unit`, `Sigma` (dependent pairs)
- Implements corresponding terms: `TrueTerm`, `FalseTerm`, `UnitTerm`, `Pair`
- Adds projections: `Fst` and `Snd` for pair manipulation
- Extends the type checker and beta reduction for new types
- Shows examples of all new types and operations

### [MISC.md](./MISC.md) - Documentation
- Provides mathematical notation for the implemented constructs
- Explains key concepts in dependent type theory
- Shows examples of terms and their types
- Illustrates proofs using the identity type
- Demonstrates equality operations (symmetry and transitivity)



### Types
- `Nat`: Natural numbers type
- `Pi`: Dependent function types (Π-types)
- `Id`: Identity/equality types
- `Bool`: Boolean type
- `Unit`: Unit type (singleton)
- `Sigma`: Dependent pair types (Σ-types)

### Terms
- `Var`: Variables
- `Lam`: Lambda abstractions (functions)
- `App`: Function application
- `Refl`: Reflexivity proof
- `Sym`: Symmetry operation for equalities
- `Trans`: Transitivity operation for equalities
- `TrueTerm`/`FalseTerm`: Boolean values
- `UnitTerm`: Unit value
- `Pair`: Pair constructor
- `Fst`/`Snd`: Pair projections

### Operations
- Type checking: Verifies that terms have the expected types
- Beta reduction: Evaluates terms by substituting arguments in functions
- Substitution: Replaces variables with terms


### Theoretical Foundation

This implementation follows the Martin-Löf Type Theory, which is a constructive
type theory that serves as a foundation for various proof assistants and dependently
typed programming languages.

1. *Dependent Types*: Types can depend on values
2. *Curry-Howard Correspondence*: Types as propositions, terms as proofs
3. *Identity Types*: Representing equality between terms
4. *Computation*: Terms can be evaluated via beta reduction

The system is capable of expressing both programs and mathematical proofs in the same
framework, embodying the principles of constructive mathematics.
