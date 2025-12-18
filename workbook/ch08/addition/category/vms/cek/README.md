
## The CEK: Control, Environment, and Continuation Machine

The CEK machine belongs to a family of abstract machines developed to give precise, operational
accounts of functional programming languages, particularly the lambda calculus. Its name reflects
its core components: Control, Environment, and Continuation. Each of these corresponds to a concept
that had previously existed implicitly in high-level semantic descriptions but was made explicit
in the transition from denotational and big-step semantics to small-step operational models.

Historically, the development of the CEK machine can be traced to work in the late 1970s and early
1980s on the operational semantics of the lambda calculus and functional languages. During this
period, researchers sought alternatives to denotational semantics, which, while mathematically
elegant, were often too indirect to support reasoning about concrete execution, implementation
strategies, or resource usage. Small-step abstract machines provided a way to bridge this gap by
modelling evaluation as a sequence of simple, mechanically interpretable transitions.

The CEK machine is closely related to earlier models such as the [SECD machine](./),
introduced by Landin in 1964. While the SECD machine used an explicit stack and dump to manage
control flow, later machines, including CEK, refined this structure by isolating continuations
as first-class representations of "the rest of the computation." This shift was influenced by
the growing theoretical understanding of continuations in the 1970s, particularly through the
work of Reynolds and others on continuation-passing style.

Conceptually, the CEK machine decomposes evaluation into three interacting components.
The control component represents the term currently being evaluated. The environment records
variable bindings and enforces lexical scoping. The continuation encodes the evaluation context,
making explicit what remains to be done with the current result. Evaluation proceeds by repeatedly
rewriting the machine state, step by step, until a final value is reached and the continuation is empty.

This structure serves several purposes. First, it provides a faithful operational model for
call-by-value evaluation of the lambda calculus, including higher-order functions and closures.
Second, it makes control flow explicit, which is essential for understanding advanced language
features such as exceptions, non-local exits, and first-class continuations. Third, it offers a
direct blueprint for implementation: many interpreters, bytecode engines, and compilers can be
understood as refinements or transformations of CEK-like machines.

From an implementation perspective, the CEK machine explains how closures are created and applied,
how environments are extended, and how tail calls naturally avoid stack growth. Unlike naive recursive
interpreters, a CEK machine does not rely on the host language’s call stack, which makes properties
such as tail-call optimisation explicit and predictable. This aspect was particularly important in
the design and implementation of functional languages where unbounded recursion is idiomatic.

More broadly, the CEK machine occupies an intermediate position between high-level semantic descriptions
and low-level execution models. It is abstract enough to support formal reasoning, equivalence proofs,
and program transformations, yet concrete enough to be implemented directly in imperative languages.
For this reason, CEK and related machines are widely used in the study of programming language semantics,
compiler construction, and the formal analysis of control and effects.

In summary, the CEK machine arose from the need to reconcile mathematical clarity with operational precision.
It provides a clear answer to how functional programs execute, why certain implementation strategies work,
and how language features relate to underlying control structures. Its enduring relevance lies in its ability
to connect theory with practice in a way that remains both rigorous and executable.


### Step 1: What a CEK machine is, operationally

A CEK machine evaluates lambda calculus using an explicit machine state:

```
⟨ Control , Environment , Kontinuation ⟩
```

- Control (C): the term currently being evaluated
- Environment (E): maps variables to values
- Continuation (K): “what to do next”

A transition step is:

```
⟨ C , E , K ⟩ → ⟨ C' , E' , K' ⟩
```

This is already a state-transition system.



### Step 2: Write down the monad we need

We want:
- mutable environment
- explicit control flow
- explicit continuation

That suggests a computation of the form:

```
CEK a = (Env, Kont) -> Result
```

where a result is either:
- a final value, or
- a request to continue with a new control term

Let’s define this precisely.

```python
def CEK(comp):
    # comp : (env, kont) -> result
    return comp
```

We now define the monad structure.



### Step 3: The monad operations


__Return__

A value does not change the environment and immediately invokes the continuation.

```python
def unit(value):
    def comp(env, kont):
        return kont(value, env)
    return comp
```

__Bind__

Bind sequences computations by installing a new continuation.

```python
def bind(m, f):
    def comp(env, kont):
        def new_kont(value, env2):
            return f(value)(env2, kont)
        return m(env, new_kont)
    return comp
```

This is crucial:
*bind* constructs the continuation explicitly.

At this point, we already have:
- control flow
- environment threading
- continuation capture

No CEK yet--but everything needed for one.



### Step 4: Terms of the language

We now choose a language. Minimal lambda calculus:

```python
class Var: 
    def __init__(self, name): self.name = name

class Lam:
    def __init__(self, x, body): self.x, self.body = x, body

class App:
    def __init__(self, f, a): self.f, self.a = f, a
```

Values are closures:

```python
class Closure:
    def __init__(self, x, body, env):
        self.x, self.body, self.env = x, body, env
```



### Step 5: Evaluation as a monadic program

Now we define evaluation:

```python
def eval(term):
    if isinstance(term, Var):
        return CEK(lambda env, kont:
            kont(env[term.name], env)
        )

    if isinstance(term, Lam):
        return CEK(lambda env, kont:
            kont(Closure(term.x, term.body, env), env)
        )

    if isinstance(term, App):
        return bind(eval(term.f), lambda fun:
               bind(eval(term.a), lambda arg:
               apply(fun, arg)))
```

Nothing magical happened.
We are just sequencing computations with bind.



### Step 6: Application introduces CEK structure

Application is where CEK appears explicitly.

```python
def apply(fun, arg):
    def comp(env, kont):
        if not isinstance(fun, Closure):
            raise Exception("Not a function")
        new_env = fun.env.copy()
        new_env[fun.x] = arg
        return eval(fun.body)(new_env, kont)
    return CEK(comp)
```

Look closely:
- Control: fun.body
- Environment: new_env
- Continuation: kont

That is a CEK transition.



### Step 7: Extracting the CEK machine states

If we inline the monad, each call has the shape:

```python
eval(term)(env, kont)
```

So the implicit machine state is:

```
⟨ term , env , kont ⟩
```

Each function body corresponds to a CEK transition rule.

For example, application becomes:

```
⟨ (f a), env, K ⟩
→ ⟨ f, env, K_app(a, env, K) ⟩
```

That `K_app` is exactly the continuation created by bind.



### Step 8: Continuations become data (optional but enlightening)

If we reify continuations:

```python
class Kont:
    pass

class Halt(Kont):
    def __call__(self, v, env): return v

class AppFun(Kont):
    def __init__(self, arg, env, k): ..
```

then the monad-generated continuations become exactly the CEK continuation stack.

So:
- bind = push continuation frame
- unit = invoke continuation
- eval = control component
- environment passing = E
- continuation closures = K



### Final synthesis

We did not "implement" a CEK machine.
We derived it.

1. Start with a monad that sequences computations.
2. Choose environment-passing and continuation-passing.
3. Write evaluation compositionally.
4. Inline the monad.
5. The CEK machine appears as the operational semantics.

A CEK machine is what you get when you operationalise a continuation-and-environment
monad and make its implicit state explicit.

.. Now an implementation in [cek.py](./cek.py)
