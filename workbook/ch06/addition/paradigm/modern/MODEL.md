
## Model Theory

This is a classical model-theoretic style: define a structure, define satisfaction, and only then mention what counts as validity. No proof system is assumed.


### 1. Signature and language

Let the language \mathcal{L}_D consist of:

- A set of propositional symbols $\mathsf{Prop} = \{ p, q, r, \dots \}$
- Boolean connectives $\neg$, $\land$, $\lor$, $\rightarrow$
- Deontic operators:
```math
O \quad \text{(obligation)}, \quad P \quad \text{(permission)}, \quad F \quad \text{(forbidden)}
```
Optionally, allow conditional operators O(\varphi \mid \psi).

No axioms yet.



### 2. Deontic frame (model-theoretic structure)

A deontic frame is a tuple:
```math
\mathcal{F} = \langle W, A \rangle
```
where:
- $W$ is a non-empty set of possible worlds
- A $\subseteq W$ is the set of admissible (norm-compliant) worlds

This differs slightly from standard Kripke frames by fixing admissibility directly,
rather than deriving it from an accessibility relation.

(This is already .. Kangerian.)



### 3. Deontic model

A deontic model is a tuple:
```math
\mathcal{M} = \langle W, A, V \rangle
```
where:
- $\langle W$, A $\rangle$ is a deontic frame
- $V : \mathsf{Prop} \rightarrow \mathcal{P}(W)$ is a valuation function

That is, each atomic proposition is assigned the set of worlds in which it holds.



### 4. Satisfaction relation

We define a satisfaction relation:
```math
\mathcal{M}, w \models \varphi
```
inductively.

Atomic and Boolean cases
Standard:
- $\mathcal{M}, w \models p \iff w \in V(p)$
- Boolean connectives defined classically



### 5. Deontic operators (semantic clauses)

Now the focus part.

Obligation
```math
\mathcal{M}, w \models O\varphi \iff \forall w' \in A:\ \mathcal{M}, w' \models \varphi
```
Note:
- Obligation is global, not relative to w
- Norms apply system-wide, not perspectivally

This likely matches von Wright’s early semantics.


Prohibition
```math
\mathcal{M}, w \models F\varphi \iff \forall w' \in A:\ \mathcal{M}, w' \not\models \varphi
```
Equivalently:
```math
F\varphi \equiv O\neg\varphi
```
but this equivalence is semantic, not axiomatic.



Permission
```math
\mathcal{M}, w \models P\varphi \iff \exists w' \in A:\ \mathcal{M}, w' \models \varphi
```
Permission is existential over admissible worlds.



### 6. Conditional norms

For conditional obligation:
```math
\mathcal{M}, w \models O(\varphi \mid \psi)
\iff
\forall w' \in A:\
(\mathcal{M}, w' \models \psi \Rightarrow \mathcal{M}, w' \models \varphi)
```
This is domain restriction, not implication inside the object language.

This is essential for avoiding contrary-to-duty paradoxes.



### 7. Validity and satisfiability

A formula $\varphi$ is:

- Satisfiable iff there exists a model $\mathcal{M}$ such that $\mathcal{M} \models \varphi$
- $Valid iff for all models \mathcal{M}, \mathcal{M} \models \varphi$

Note: many classical deontic "axioms" are *not* valid under this semantics.

That is intentional. It helps us.



### 8. Adding action (Kanger-style)

To model action logic, extend the frame:
```math
\mathcal{F} = \langle W, A, Act, T \rangle
```
where:

- $Act$ is a set of actions
- $T \subseteq W \times Act \times W$ is a transition relation

An action formula $[\alpha]\varphi$ is satisfied iff:
```math
\mathcal{M}, w \models [\alpha]\varphi
\iff
\forall w' \ (w, \alpha, w') \in T \Rightarrow \mathcal{M}, w' \models \varphi
```
Now deontic constraints restrict which transitions are admissible.

An obligation about actions becomes:
```math
O[\alpha]\varphi
```
meaning: in all admissible worlds, all $\alpha-transitions$ lead to $\varphi$-worlds.

This is close to temporal logic semantics.



### 9. Priority and conflict (semantic, not axiomatic!)

To model overrides, let:
```math
A = \bigcap_{i \in I} A_i
```
where each $A_i$ corresponds to a norm, ordered by priority.

Lower-priority $A_i$ may be dropped if inconsistent.

This is non-monotonic, but model-theoretically clean.



### 10. Why this is genuinely model theory

This framework satisfies all classical criteria:
- Clearly defined structures
- Explicit satisfaction relation
- Validity defined over all models
- No reliance on proof rules
- Semantics primary, syntax secondary

It is model theory applied to normative language.



### 11. Relation to computer science (one sentence)

Replace:
- worlds with states or executions
- admissible worlds with constraint-satisfying states
- satisfaction with model checking

and you have the semantics of Alloy, TLA+, and safety properties.



### 12. Closing perspective

Modal logic becomes computational the moment its semantics is made explicit.
Kanger’s insight was not that norms need special axioms, but that they define a model class.



------


### 1. Transition

Every semantic notion introduced (worlds, admissibility, obligation, action, transition) can be represented as first-order structures and predicates, and satisfaction of deontic formulas can be reduced to first-order satisfaction.

This is a semantic embedding, not a syntactic identification.

By "collapse into first-order logic" we do not mean:
- that deontic logic becomes trivial
- that modal notions disappear
- that proof theory is preserved




### 2. Start from the deontic model

Recall the deontic model:
```math
\mathcal{M} = \langle W, A, V \rangle
```
Where:
- W is a set of worlds
- A \subseteq W are admissible worlds
- V assigns propositions to subsets of W

This is already almost first-order: sets and predicates over a domain.



### 3. First-order signature

We define a first-order language $\mathcal{L}_{FO}$ with:
- A domain of discourse: worlds
- Unary predicates:
- $A(w)$: "w is admissible"
- $P_p(w)$: "proposition p holds in world w"
- Optionally:
- Binary or ternary predicates for actions and transitions

This is entirely standard FOL.



### 4. Translating propositional formulas

For each propositional variable p, introduce a unary predicate:
```math
P_p(w)
```
Boolean connectives translate homomorphically:
- $\neg \varphi → \neg \varphi^\* (w)$
- $\varphi \land \psi → \varphi^\*(w) \land \psi^\*(w)$

This is routine.



### 5. Translating deontic operators

Now the key step.

Obligation

Recall the semantic clause:
```math
\mathcal{M}, w \models O\varphi \iff \forall w' \in A:\ \mathcal{M}, w' \models \varphi
```
First-order translation:
```math
(O\varphi)^\* \equiv \forall w' \, (A(w') \rightarrow \varphi^\*(w'))
```
Note:
- No modal operators
- Pure first-order quantification
- Obligation is a global constraint



Prohibition
```math
(F\varphi)^\* \equiv \forall w' \, (A(w') \rightarrow \neg \varphi^\*(w'))
```
Again, first-order.



Permission
```math
(P\varphi)^\* \equiv \exists w' \, (A(w') \land \varphi^\*(w'))
```
Existential quantification over admissible worlds.



### 6. Conditional obligations

Recall above:
```math
O(\varphi \mid \psi)
```
Semantic clause:
```math
\forall w' \in A:\ (\psi \Rightarrow \varphi)
```
First-order translation:
```math
(O(\varphi \mid \psi))^\*
\equiv
\forall w' \, \big( (A(w') \land \psi^\*(w')) \rightarrow \varphi^\*(w') \big)
```
Again, no modal machinery required.

This is why contrary-to-duty paradoxes evaporate: the condition restricts the quantifier domain.



### 7. Adding action: transition systems in FOL

Extend the signature with:
- A set of actions Act
- A ternary predicate:
```math
T(w, a, w')
```
meaning: "performing action a in world w may lead to w'"

Now define action formulas.

Action necessity
```math
[\alpha]\varphi
```
Semantic clause:
```math
\forall w' \ (T(w, \alpha, w') \rightarrow \varphi(w'))
```
First-order translation:
```math
([\alpha]\varphi)^\*(w)
\equiv
\forall w' \ (T(w, \alpha, w') \rightarrow \varphi^\*(w'))
```
This is standard relational FOL.



Deontic action constraints

Example:
```math
O[\alpha]\varphi
```
Translation:
```math
\forall w \forall w' \,
\big( A(w) \land T(w, \alpha, w') \rightarrow \varphi^\*(w') \big)
```
This is exactly a safety constraint over transitions.



### 8. Priority and overrides (still first-order)

Let norms be indexed $N_i$, each defining admissibility predicates $A_i(w)$.

Define:
```math
A(w) \equiv \bigwedge_{i \in Max} A_i(w)
```
Where Max is the set of highest-priority consistent norms.

This selection mechanism may be meta-theoretic, but the resulting model is first-order.

This mirrors how Alloy or model checking tools handle conflicting constraints.



### 9. Case in Point

At this point:
- Worlds are first-order elements
- Norms are predicates
- Obligation is universal quantification
- Permission is existential quantification
- Actions are relations
- Deontic reasoning is constraint satisfaction

There is no modal residue left in the semantics.



### 10. Why modal logic was ever needed

Modal logic was needed historically because:
- It provided syntax aligned with philosophical intuition
- It packaged quantification patterns compactly
- It avoided explicit reference to worlds in the object language

But semantically, it was always first-order underneath.

Kanger knew this?


### 11. Consequence for computer science

This is the punchline.

Once deontic/modal semantics collapses into FOL:
- Model checking becomes quantifier evaluation
- Alloy becomes bounded first-order satisfiability
- Temporal logic becomes first-order logic over traces
- "Norms" become invariants
- "Ought" becomes "for all admissible states"

Nothing mystical/mythical.



### 12. Final perspective

Deontic action logic was always a discipline for carving out *admissible structures*.
Computer science simply learned how to compute that carving.

In that sense, the line from Kanger to Alloy is not metaphorical at all.
It is model theory. Waiting for machines.

