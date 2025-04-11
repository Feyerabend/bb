
## Cut Elimination and Proof Normalisation

The "cut rule" in logic allows us to use a lemma or intermediate result in a proof.
If we prove A, and separately prove that A implies B, the cut rule lets us conclude B.
Cut elimination demonstrates that any proof using cuts can be transformed into a "direct"
proof without cuts.

In our implementation, cut elimination corresponds to removing unnecessary intermediate
steps in logical proofs, making the proofs more direct and often simpler.


### Implementation Details

1. *`normalise(term: Term) -> Term`*
   - The main normalisation function that applies both beta reduction and cut elimination
   - First reduces the term using beta reduction, then applies cut elimination rules

2. *`apply_cut_elimination(term: Term) -> Term`*
   - Recursively applies cut elimination transformations
   - Handles specific patterns for each type of term

3. *`is_free_in(var_name: str, term: Term) -> bool`*
   - Helper function to check if a variable appears free in a term
   - Essential for implementing proper variable substitution rules


### Cut Elimination Rules

1. *Modus Ponens (→E)*
   - When we have `ImpliesElim(ImpliesIntro(x, A, M), N)`, we simplify to `M[x := N]`
   - This eliminates the detour of introducing an implication only to eliminate it immediately

2. *Conjunction Elimination (∧E)*
   - When we have `AndElim(AndIntro(L, R), left)`, we simplify to just `L` (or `R` if right)
   - This removes the detour of creating a pair only to immediately extract a component

3. *Transitivity of Equality (Trans)*
   - Simplifications like `trans(refl(a), p)` to just `p`
   - Associativity transformations to normalise equality chains

4. *Commuting Conversions*
   - Rules that push eliminations through introductions
   - For example, transforming `AndElim(ImpliesIntro(x, A, M), left)` to `ImpliesIntro(x, A, AndElim(M, left))`


## Example

Consider the following example from the code:

```python
# Assume we have P → Q and Q → R and P
p_implies_q = Var("p_implies_q")
q_implies_r = Var("q_implies_r")
p_var = Var("p")

# Derive Q using modus ponens
q_proof = ImpliesElim(p_implies_q, p_var)

# Derive R using Q and Q → R
r_proof = ImpliesElim(q_implies_r, q_proof)
```

This proof has a "cut"--we derive the intermediate result Q and then use it.
After normalisation, we get a more direct proof that goes from P to R in one step.


## Connection to Lambda Calculus

Cut elimination is closely related to beta reduction in lambda calculus.
In fact, under the Curry-Howard correspondence:

- Cut elimination ↔ Beta reduction
- Lemmas/intermediate results ↔ Let-bindings or function applications
- Direct proofs ↔ Normal forms of terms

This correspondence is why our implementation uses similar techniques for
both computational reduction (beta reduction) and logical simplification
(cut elimination).


## Benefits

1. *Simplified Proofs*: Normalised proofs are often shorter and more direct
2. *Consistency Check*: The ability to normalise proofs is related to the consistency of the logical system
3. *Computational Interpretation*: Normalised proofs have clear computational meaning
4. *Subformula Property*: Normalised proofs only use subformulas of the conclusion or assumptions


## Applications

1. *Automated Theorem Proving*: Normalisation helps in proof search and checking
2. *Program Optimisation*: Via Curry-Howard, proof normalisation corresponds to program optimisation
3. *Type Checking*: Normalisation can simplify complex dependent types

The implementation demonstrates these principles and provides a foundation
for further extensions to more complex logical systems.
