
__1. Term and its type__

$$
(λ x : Nat. x)
Type: (Π x : Nat). Nat
$$

This is the identity function on Nat, and its type is the dependent function type (though not really depending on x), i.e.:
$\lambda x : \mathbb{N} \mapsto x \quad : \quad \Pi x : \mathbb{N}. \mathbb{N}$



__2. Proof term (refl)__

```math
(λ x : Nat. refl(x))
Type: (Π x : Nat). Id(Nat, x, x)
```

This is a proof that every element is equal to itself — the reflexivity axiom. It’s the canonical inhabitant of the identity type:
$\lambda x : \mathbb{N} \mapsto \mathsf{refl}(x) \quad : \quad \Pi x : \mathbb{N}. \mathsf{Id}_{\mathbb{N}}(x, x)$




__3. Symmetry__

```math
sym(p)
Type: Id(Nat, y, x)
```

Given p : Id(Nat, x, y), symmetry gives:
$\mathsf{sym}(p) : \mathsf{Id}_{\mathbb{N}}(y, x)$




__4. Transitivity__

```math
trans(p, q)
Type: Id(Nat, x, z)
```

Given:
- $p : Id(Nat, x, y)$
- $q : Id(Nat, y, z)$

We get:
$\mathsf{trans}(p, q) : \mathsf{Id}_{\mathbb{N}}(x, z)$



