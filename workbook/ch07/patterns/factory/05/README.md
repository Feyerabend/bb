
## Factory Method vs Abstract Factory  

In software design, *creational patterns* abstract the process of object creation.
Two foundational patterns in this category are *Factory Method* and *Abstract Factory*.
Though conceptually similar, both defer instantiation to subclasses or factories,
their scope and intent differ in significant ways.


### Factory Method Pattern

*Define an interface for creating an object, but let subclasses decide which class to instantiate.*  
The Factory Method allows a class to defer instantiation to subclasses.

| Role              | Description |
|-------------------|-------------|
| *Product*       | The interface or abstract class of objects the factory creates. |
| *ConcreteProduct* | The concrete implementations of the Product interface. |
| *Creator*       | Abstract class that declares the factory method returning a Product object. |
| *ConcreteCreator* | Subclass that overrides the factory method to return a ConcreteProduct instance. |

| Feature | Description |
|---------|-------------|
| Scope | Focused on creating *one type of product*. |
| Extensibility | New product variants require new ConcreteCreator subclasses. |
| Decoupling | The client uses Creator’s interface; it does not depend directly on concrete classes. |

#### Example

- *Product* → LogicalGate (interface)  
- *ConcreteProducts* → AndGate, OrGate, XorGate  
- *Factory Method* → `gate_factory(gate_type)` (returns one LogicalGate at a time)



### Abstract Factory Pattern

*Provide an interface for creating families of related or dependent objects without specifying their concrete classes.*  
Abstract Factory focuses on producing *sets of related objects*.

| Role              | Description |
|-------------------|-------------|
| *AbstractFactory* | Declares an interface for creating each kind of product (multiple factory methods). |
| *ConcreteFactory* | Implements creation methods for a specific product family. |
| *AbstractProduct* | Interfaces for a set of products (family members). |
| *ConcreteProducts* | Concrete implementations of AbstractProducts. |

| Feature | Description |
|---------|-------------|
| Scope | Focused on creating *families of products* (multiple related types). |
| Consistency | Ensures that products created together are compatible or consistent. |
| Extensibility | Adding new product families requires new ConcreteFactory classes. |

#### Example

- *AbstractFactory* → GateFactory (declares `create_and()`, `create_or()`, `create_xor()`)  
- *ConcreteFactory* → BasicGateFactory (returns AndGate, OrGate, XorGate consistently)  
- *AbstractProduct* → LogicalGate  
- *ConcreteProducts* → AndGate, OrGate, XorGate  
- *Client (e.g., HalfAdder)* → Asks *the factory instance* for all gates, ensures consistency.


### Comparison Table

| Aspect | Factory Method | Abstract Factory |
|--------|----------------|------------------|
| *Primary purpose* | Create *one type of object* | Create *families of objects* |
| *Factory type* | Single factory method | Collection of related factory methods |
| *Object relationships* | Unrelated objects | Related, compatible products |
| *Class diagram complexity* | Simpler | More complex |
| *Client interaction* | Client uses Creator’s method to get one object | Client uses AbstractFactory to get multiple products |
| *Example from adder project* | `gate_factory("and")`, `gate_factory("xor")` | `factory.create_and()`, `factory.create_xor()` from a consistent factory object |


### When to Use

| Situation | Factory Method | Abstract Factory |
|-----------|----------------|------------------|
| Need to create *one product at a time*, allowing subclasses to specify the concrete class | x | |
| Need to ensure that multiple objects *work well together* (consistent family) | | x |
| Want to decouple product creation logic from client code | x | x |
| Want to support *multiple interchangeable product families* easily | | x |
| Product variations likely to increase independently | x | |


### Application to Our *Adder Example*

| Stage | Pattern | Rationale |
|-------|---------|-----------|
| *Initial design* — creating gates (AND, OR, XOR) individually | Factory Method | We just need individual gates; no explicit product family concept |
| *Enhanced design* — HalfAdder and FullAdder both require *multiple gates together* | Abstract Factory | We need a family of gates (AND, OR, XOR) that is consistent and interchangeable (e.g., different gate technologies later) |
| *Extending further* — Support different gate technologies (e.g., NAND-only implementations) | Abstract Factory | Multiple ConcreteFactories produce compatible families of gates |


### Summary

| Factory Method | Abstract Factory |
|----------------|------------------|
| Focuses on *one product type* | Focuses on *families of products* |
| Returns *one object* per method | Returns *several related objects* |
| Simpler, less boilerplate | More structure, better consistency |
| Suitable when product families are not relevant | Suitable when *consistent sets* of products matter |

- *Factory Method* excels at decoupling the creation of individual products.
- *Abstract Factory* excels when *multiple products are interrelated* and must
  be used together coherently.
- Our adder project *naturally evolved* from Factory Method (simple gate creation)
  to Abstract Factory (consistent families of gates used across complex components).

Both patterns improve *extensibility* and *decoupling*, but the choice depends on
*the number of products* and *their relationships*.
