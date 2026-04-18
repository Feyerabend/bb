
## Dependent Type Theory Examples

__1. Term and its type__

```shell
(λ x : Nat. x)
Type: (Π x : Nat). Nat
```

This is the identity function on $Nat$, and its type is the dependent function type (though not really depending on $x$), i.e.:
$\lambda x : \mathbb{N} \mapsto x \quad : \quad \Pi x : \mathbb{N}. \mathbb{N}$


__2. Proof term (refl)__

```shell
(λ x : Nat. refl(x))
Type: (Π x : Nat). Id(Nat, x, x)
```

This is a proof that every element is equal to itself--the reflexivity axiom. It's the canonical inhabitant of the identity type:
$\lambda x : \mathbb{N} \mapsto \mathsf{refl}(x) \quad : \quad \Pi x : \mathbb{N}. \mathsf{Id}_{\mathbb{N}}(x, x)$


__3. Symmetry__

```shell
sym(p)
Type: Id(Nat, y, x)
```

Given $p : Id(Nat, x, y)$, symmetry gives:
$\mathsf{sym}(p) : \mathsf{Id}_{\mathbb{N}}(y, x)$


__4. Transitivity__

```shell
trans(p, q)
Type: Id(Nat, x, z)
```

Given:
- $p : Id(Nat, x, y)$
- $q : Id(Nat, y, z)$

We get:
$\mathsf{trans}(p, q) : \mathsf{Id}_{\mathbb{N}}(x, z)$


__5. Beta Reduction__

Beta reduction is the process of applying a function to an argument:

```shell
Before beta reduction:
((λ x : Nat. x) y)

After beta reduction:
y
```

The lambda term $(λ x : Nat. x)$ applied to $y$ reduces to $y$ by substituting
$y$ for $x$ in the body of the lambda.

Another example with a reflexivity proof:

```shell
Before beta reduction:
((λ x : Nat. refl(x)) y)

After beta reduction:
refl(y)
```


__6. Additional Types__

__6.1 Bool Type__

```shell
True : Bool
False : Bool
```

Boolean values in the type system.

__6.2 Unit Type__

```shell
() : Unit
```

The Unit type has exactly one inhabitant, the empty tuple.

__6.3 Sigma Types (Dependent Pairs)__

```shell
(x, y) : Sigma(Nat, Nat)
```

Sigma types represent dependent pairs. The type of the second component may depend on the value of the first.


__7. Projections__

For a pair `p = (x, y)`:

```shell
fst(p) : Nat
snd(p) : Nat
```

These extract the first and second components of a pair, respectively.
