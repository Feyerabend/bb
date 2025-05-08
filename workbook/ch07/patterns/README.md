
## Design Patterns

In 1994, Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides published
*Design Patterns: Elements of Reusable Object-Oriented Software*.
These four authors are collectively known as the Gang of Four (GoF).

Their book cataloged 23 classic software design patterns--recurring solutions to
common problems in object-oriented software development. The patterns are divided
into three main categories:


|Category	|Description	|Examples|
|--|--|--|
|Creational	|Object creation mechanisms	|Factory Method, Singleton, Builder|
|Structural	|Composing classes and objects into larger structures	|Adapter, Composite, Facade|
|Behavioral	|Managing algorithms, responsibilities, communication	|Strategy, Observer, Command|


```mermaid
flowchart TD
    Creational -->|"Create objects \n (Abstract Factory, Builder)"| Objects
    Structural -->|"Compose structures \n (Decorator, Composite)"| Objects
    Behavioral -->|"Manage communication \n (Observer, Command)"| Objects

    Objects -->|"Loose coupling"| Principles
    Principles --> SOLID
    Principles --> DRY
```


The GoF patterns are not code libraries--they are general reusable solutions that
can be adapted to various programming languages and contexts. They aim to make designs
more flexible, reusable, and maintainable, by anticipating future changes and encouraging
good separation of concerns.

The GoF book emphasizes object-oriented principles like encapsulation, composition over
inheritance, and delegation--themes still relevant today, even beyond OOP-heavy languages.


### DRY Principle (Don’t Repeat Yourself)

Definition:
> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

Introduced in the book *The Pragmatic Programmer* (1999) by Andrew Hunt and David Thomas,
DRY is a principle of software development aimed at reducing repetition of code or logic.

Why it matters:
- Repetition increases the risk of inconsistency and bugs (when one copy changes but others don’t).
- Changes become harder to maintain when logic is duplicated.
- Code becomes harder to understand when behavior is scattered in multiple places.

Typical applications:
- Extracting shared code into functions or methods.
- Using data normalization in databases.
- Applying inheritance or composition to reuse logic.

A DRY codebase is easier to maintain, less error-prone, and clearer to read.


### SOLID Principles

The SOLID acronym represents five fundamental design principles for object-oriented programming,
popularized by Robert C. Martin ("Uncle Bob") in the early 2000s. They guide developers to build
systems that are modular, extensible, and maintainable.

|Principle	|Name	|Summary|
|--|--|--|
|S	|Single Responsibility Principle (SRP)	|A class should have one and only one reason to change.|
|O	|Open/Closed Principle (OCP)	|Software entities should be open for extension, but closed for modification.|
|L	|Liskov Substitution Principle (LSP)	|Subtypes should be substitutable for their base types.|
|I	|Interface Segregation Principle (ISP)	|No client should be forced to depend on methods it does not use.|
|D	|Dependency Inversion Principle (DIP)	|High-level modules should not depend on low-level modules; both should depend on abstractions.|

Quick breakdown:
- SRP: Keep responsibilities focused; split large classes with multiple roles.
- OCP: Favor extending behavior with new code rather than modifying existing code.
- LSP: Ensure derived classes can fully replace their parents without breaking functionality.
- ISP: Design small, focused interfaces, not large "fat" ones.
- DIP: Depend on interfaces or abstractions, not concrete implementations.

These principles complement the use of design patterns. 
Patterns provide reusable solutions--DRY and SOLID help you structure and integrate those solutions cleanly.

### Patterns

| Pattern | Category | Purpose | Example Use Case | Source |
|----|----|----|----|----|
| [Strategy](./strategy/) | Behavioural | Encapsulate interchangeable algorithms or behaviours | Sorting algorithms, payment methods | GoF |
| [Command](./command/) | Behavioural | Encapsulate a request as an object | Undo/Redo, action queues, macro recording | GoF |
| Observer           | Behavioural      | Notify dependent objects of state changes                        | GUIs, event systems, data binding                | GoF            |
| [State](./state/) | Behavioural | Change object behaviour based on internal state | Game AI, UI modes | GoF |
| Decorator          | Structural      | Add behaviour to objects dynamically                              | I/O streams, middleware pipelines                | GoF            |
| Adapter            | Structural      | Convert one interface to another                                 | Legacy code integration, wrapper libraries       | GoF            |
| [Facade](./facade/) | Structural | Provide a unified interface to a set of interfaces in a subsystem | Simplifying complex libraries, subsystems, APIs | GoF |
| [Composite](./composite/) | Structural | Treat objects and groups uniformly | Scene graphs, file system trees | GoF |
| [Factory Method](./factory/) | Creational | Define interface for creating objects, let subclass decide | Plugin creation, document editors | GoF |
| [Abstract Factory](./factory/05/) | Creational | Create families of related objects without specifying classes | GUI themes, cross-platform toolkits | GoF |
| [Singleton](./singleton/)[^single] | Creational | Ensure a class has only one instance | Config manager, global registries | GoF (controversial) |
| [Builder](./builder/) | Creational | Separate construction of a complex object from its representation | Object configurators, UI builders | GoF |
| Prototype          | Creational      | Clone existing objects instead of creating new ones              | Object pools, data templates                     | GoF            |
| Mediator           | Behavioural      | Centralise complex communication between objects                 | Chat servers, air traffic control systems        | GoF            |
| [Visitor](./visitor/) | Behavioural | Separate an algorithm from the objects it operates on | Compilers, AST traversal, document processing | GoF |
| [Dependency Injection](./combined/os/DEPENDENCY.md) | Structural | Provide dependencies from the outside | Testable systems, service wiring | Post-GoF |
| [Null Object](./null/) | Behavioural | Use an object with default behaviour instead of `null` | Safe iteration, fault-tolerant systems | Post-GoF |
| [Event Bus](./event/) | Behavioural | Decouple senders from receivers using a publish/subscribe model | UI events, logging systems | Post-GoF |


Maybe:
| Pattern | Category | Purpose | Example Use Case | Source |
|----|----|----|----|----|
| Bridge | Structural | Decouple abstraction from implementation so they can vary independently | GUI toolkits, device drivers | GoF |
| Template Method | Behavioural | Define the skeleton of an algorithm, let subclasses redefine steps | Frameworks, code generators | GoF |
| Proxy | Structural | Provide a placeholder or surrogate for another object | Remote proxies, lazy loading, access control | GoF |


[^single]: Singleton is often discouraged in modern design due to global state issues; use with care: https://en.wikipedia.org/wiki/Singleton_pattern.


### 1. Behavioural Patterns

```mermaid
classDiagram
    %% Strategy Pattern
    class Strategy {
        <<interface>>
        +execute()
    }
    class ConcreteStrategyA
    class ConcreteStrategyB
    class Context {
        -strategy: Strategy
        +setStrategy()
        +executeStrategy()
    }
    Context --> Strategy
    Strategy <|-- ConcreteStrategyA
    Strategy <|-- ConcreteStrategyB

    %% Observer Pattern
    class Subject {
        +attach(Observer)
        +detach(Observer)
        +notify()
    }
    class Observer {
        <<interface>>
        +update()
    }
    Subject --> Observer

    %% State Pattern
    class StateContext {
        -state: State
        +request()
    }
    class State {
        <<interface>>
        +handle()
    }
    StateContext --> State
    State <|-- ConcreteStateA
    State <|-- ConcreteStateB

    %% Command Pattern
    class Invoker {
        -command: Command
        +executeCommand()
    }
    class Command {
        <<interface>>
        +execute()
    }
    Invoker --> Command
    Command <|-- ConcreteCommand
```

### 2. Structural Patterns

```mermaid
classDiagram
    %% Decorator Pattern
    class Component {
        <<interface>>
        +operation()
    }
    class ConcreteComponent
    class Decorator {
        -component: Component
        +operation()
    }
    Component <|-- ConcreteComponent
    Component <|-- Decorator
    Decorator *-- Component

    %% Adapter Pattern
    class Target {
        <<interface>>
        +request()
    }
    class Adaptee {
        +specificRequest()
    }
    class Adapter {
        -adaptee: Adaptee
        +request()
    }
    Target <|-- Adapter
    Adapter *-- Adaptee

    %% Composite Pattern
    class Component {
        <<interface>>
        +operation()
        +add(Component)
        +remove(Component)
    }
    class Leaf
    class Composite {
        -children: Component[]
    }
    Component <|-- Leaf
    Component <|-- Composite
    Composite *-- Component
```

### 3. Creational Patterns

```mermaid
classDiagram
    %% Abstract Factory
    class AbstractFactory {
        <<interface>>
        +createProductA()
        +createProductB()
    }
    class ConcreteFactory1
    class ConcreteFactory2
    AbstractFactory <|-- ConcreteFactory1
    AbstractFactory <|-- ConcreteFactory2

    %% Builder
    class Director {
        -builder: Builder
        +construct()
    }
    class Builder {
        <<interface>>
        +buildPartA()
        +buildPartB()
        +getResult()
    }
    Director --> Builder
    Builder <|-- ConcreteBuilder

    %% Prototype
    class Prototype {
        <<interface>>
        +clone()
    }
    class ConcretePrototype
    Prototype <|-- ConcretePrototype
```

### 4. Post-GoF Patterns

```mermaid
classDiagram
    %% Dependency Injection
    class Client {
        -service: ServiceInterface
    }
    class ServiceInterface {
        <<interface>>
    }
    class Injector {
        +getService()
    }
    Client --> ServiceInterface
    Injector ..> ServiceInterface

    %% Event Bus
    class EventBus {
        +subscribe()
        +publish()
    }
    class Subscriber {
        +handleEvent()
    }
    EventBus --> Subscriber

    %% Null Object
    class AbstractObject {
        <<interface>>
        +operation()
    }
    class RealObject
    class NullObject
    AbstractObject <|-- RealObject
    AbstractObject <|-- NullObject
```



Abstractions shown:

1. *Interfaces* (<<interface>>) as pattern contracts

2. *Arrow types*:
   - `-->` for dependency
   - `<|--` for inheritance
   - `*--` for composition

3. *Pattern-specific relationships*:
   - Observer's subject-observer binding
   - Decorator's recursive wrapping
   - Composite's tree structure

4. *Post-GoF patterns* with modern tooling (DI containers, event systems)

Each diagram isolates the pattern's essence while maintaining consistent notation.
The meta-diagram shows how categories relate to design principles.

