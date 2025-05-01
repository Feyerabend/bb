
## Factory Pattern

Factory Pattern is a creational design pattern that provides an interface for
creating objects, but allows subclasses or a separate factory module to alter
the type of objects that will be created. The client code requests an object
from the factory and receives an instance that satisfies an agreed-upon interface,
without knowing the exact class or configuration of the created object.


### Motivation

In software systems, object creation often becomes complex as systems scale
and the number of concrete types increases. The Factory Pattern centralises
the creation logic and isolates it from the client code, which improves
maintainability, scalability, and clarity.

#### Components

| Role                 | Description |
|----------------------|-------------|
| Product (Interface)  | The abstract type or interface the client uses |
| Concrete Product     | A specific class/type that implements the product interface |
| Creator (Factory)    | A function or class that creates and returns Product objects |
| Client               | Code that requests and uses Product objects |

#### Benefits

| Benefit | Description |
|---------|-------------|
| Encapsulation | Hides object construction logic from the client |
| Decoupling | Client code depends only on the abstract Product interface |
| Flexibility | New concrete products can be introduced without modifying client code |
| Maintainability | Centralised construction logic is easier to update |




### Samples

| General Factory Concept | Code |
|-------------------------|-------------|
| Product Interface | `Adder` struct (function pointer + opaque data pointer) |
| Concrete Product | HalfAdder or FullAdder (concrete structs `HalfAdderData`, `FullAdderData`) |
| Factory Function | `create_adder(AdderType type)` |
| Client | `main.c` (code requesting HalfAdder or FullAdder) |

We want to:
- Isolate the creation and wiring of Adder objects (HalfAdder, FullAdder) into a factory function.
- Allow the client code to simply request "give me a HalfAdder" or "give me a FullAdder",
  without manually constructing or wiring the underlying gates (XOR, AND, OR).

The construction of an 8-bit adder exemplifies a gradual development process, culminating in
the final implementation presented ([04](./04/)). Throughout this progression, particular
attention must be given to the *signatures* of the factory functions employed. Since the C
programming language lacks inherent support for polymorphism, developers often emulate
polymorphic behaviour through explicit type casting and the application of uniform function
interfaces.

This technique, while effective, introduces potential risks related to type safety
and interface mismatches. Consequently, compilers may emit warnings when inconsistencies arise
in function prototypes or when implicit conversions are detected. It is therefore critical to
maintain rigorous consistency in factory function signatures to preserve both code correctness
and maintainability.

There is also a sample of the pattern in Python.

#### HalfAdder

The client wants an adder that computes sum = a XOR b, carry = a AND b.

```c
Adder ha = create_adder(HALF_ADDER);
ha.compute(ha.data, a, b, cin, &sum, &cout);
```

Factory code

```c
Adder create_adder(AdderType type) {
    Adder adder;
    if (type == HALF_ADDER) {
        HalfAdderData* data = malloc(sizeof(HalfAdderData));
        data->xor = XOR;
        data->and = AND;
        adder.data = data;
        adder.compute = HalfAdder_compute;
    }
    return adder;
}
```

The factory function create_adder allocates and wires the gates necessary for a HalfAdder.
The client code does not interact with gates directly; it receives a fully configured Adder object.


#### HalfAdder and FullAdder

We extend functionality to also support FullAdder, which computes
```c
sum = a XOR b XOR cin,
carry = (a AND b) OR (cin AND (a XOR b)).
```

Factory code (extended)

```c
Adder create_adder(AdderType type) {
    Adder adder;
    switch (type) {
        case HALF_ADDER: {
            HalfAdderData* data = malloc(sizeof(HalfAdderData));
            data->xor = XOR;
            data->and = AND;
            adder.data = data;
            adder.compute = HalfAdder_compute;
            break;
        }
        case FULL_ADDER: {
            FullAdderData* data = malloc(sizeof(FullAdderData));
            data->xor1 = XOR;
            data->xor2 = XOR;
            data->and1 = AND;
            data->and2 = AND;
            data->or = OR;
            adder.data = data;
            adder.compute = FullAdder_compute;
            break;
        }
    }
    return adder;
}
```

Client code

```c
Adder ha = create_adder(HALF_ADDER);
ha.compute(ha.data, a, b, cin, &sum, &cout);

Adder fa = create_adder(FULL_ADDER);
fa.compute(fa.data, a, b, cin, &sum, &cout);
```

Description

The factory function now supports creation of two concrete products:
HalfAdder and FullAdder.
Both conform to the same Adder interface--compute function and opaque data pointer.
The client code uses both uniformly and does not need to know internal gate wiring.

| Advantage | Description |
|-----------|-------------|
| Abstraction | Client does not know or care how gates are wired |
| Scalability | New adder types can be added easily by extending factory |
| Maintainability | Changes in gate composition do not affect client |
| Code clarity | Client interacts uniformly with HalfAdder and FullAdder |



### Conclusion

- The Factory Pattern cleanly separates adder construction logic from client code.
- You achieve clear, scalable, safe instantiation of both HalfAdder and FullAdder.
- Future extensions (e.g., RippleCarryAdder, LookAheadAdder) require minimal
  client-side change--only factory modification.
