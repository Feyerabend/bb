
## Singleton

The `Singleton` pattern, as originally defined by the Gang of Four, ensures that a class has
only one instance and provides a global access point to it. This sounds simple and sometimes
even desirable--think of logging systems, configuration managers, or connection pools. But
over time, this pattern has developed a notorious reputation in modern software design,
primarily because of the hidden complexity and coupling it introduces.


Key Problems with Singleton:

__1. Global State in Disguise__

A `Singleton` often behaves like a global variable. This breaks encapsulation and introduces
implicit dependencies. Functions or classes that use a `Singleton` may appear independent in
their interface, but actually depend on hidden shared state. This makes the system:
- Hard to reason about
- Difficult to test
- Fragile in concurrent or distributed contexts


__2. Tight Coupling__

Once components rely directly on a `Singleton`, they are tightly bound to its presence and behaviour.
This makes code harder to change or refactor--swapping in a different implementation becomes non-trivial.


__3. Inhibits Testing__

In unit tests, you typically want to mock or replace dependencies. With a `Singleton`, the instance is
baked into the code and usually resists substitution. This leads to:
- Test order dependencies
- Accidental state sharing between tests
- The need for ugly "reset" hacks


__4. Concurrency Risks__

Since the `Singleton` is a shared object, any mutable state it holds must be protected from race
conditions. In a multithreaded environment, that means additional synchronisation complexity--mutexes,
locks, or atomic operations.


__5. Namespace Pollution__

`Singletons` often become dumping grounds for unrelated logic because "there's already a place for
shared things." This leads to bloated classes with poor cohesion.


### Modern Alternatives

Instead of the traditional `Singleton` pattern, modern design leans on:
- *Dependency Injection* (DI): Pass shared instances explicitly where needed.
  This makes dependencies visible and testable.
- *Service Locators* (used sparingly): Centralised registries that can provide
  services when truly needed, but with the tradeoff of implicit coupling.
- *Module-level singletons* (in Python, JS, etc.): Relying on language/module
  behaviour to ensure single instantiation without enforcing it via class structure.

In short: can be problematic when overused or used without understanding the implications.
It makes global state seem structured, but it’s still global state, and it drags all the
same problems with it.

