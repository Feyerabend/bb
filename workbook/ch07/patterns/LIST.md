


Gang-of-Four patterns .. + 3 others

| Pattern            | Category        | Purpose                                                         | Example Use Case                                | Source        |
|--------------------|----------------|------------------------------------------------------------------|--------------------------------------------------|----------------|
| Strategy           | Behavioural      | Encapsulate interchangeable algorithms or behaviours              | Sorting algorithms, payment methods             | GoF            |
| [Command](./command/) | Behavioural | Encapsulate a request as an object | Undo/Redo, action queues, macro recording | GoF |
| Observer           | Behavioural      | Notify dependent objects of state changes                        | GUIs, event systems, data binding                | GoF            |
| [State](./state/) | Behavioural | Change object behaviour based on internal state | Game AI, UI modes | GoF |
| Decorator          | Structural      | Add behaviour to objects dynamically                              | I/O streams, middleware pipelines                | GoF            |
| Adapter            | Structural      | Convert one interface to another                                 | Legacy code integration, wrapper libraries       | GoF            |
| Composite          | Structural      | Treat objects and groups uniformly                               | Scene graphs, file system trees                  | GoF            |
| [Factory Method](./factory/) | Creational | Define interface for creating objects, let subclass decide | Plugin creation, document editors | GoF |
| [Abstract Factory](./factory/05/) | Creational | Create families of related objects without specifying classes | GUI themes, cross-platform toolkits | GoF |
| [Singleton](./singleton/)[^single] | Creational | Ensure a class has only one instance | Config manager, global registries | GoF (controversial) |
| Builder            | Creational      | Separate construction of a complex object from its representation | Object configurators, UI builders               | GoF            |
| Prototype          | Creational      | Clone existing objects instead of creating new ones              | Object pools, data templates                     | GoF            |
| Mediator           | Behavioural      | Centralise complex communication between objects                 | Chat servers, air traffic control systems        | GoF            |
| [Visitor](./visitor/] | Behavioural | Separate an algorithm from the objects it operates on | Compilers, AST traversal, document processing | GoF |
| [Dependency Injection](./combined/os/DEPENDENCY.md) | Structural | Provide dependencies from the outside | Testable systems, service wiring | Post-GoF |
| [Null Object](./null/) | Behavioural | Use an object with default behaviour instead of `null` | Safe iteration, fault-tolerant systems | Post-GoF |
| [Event Bus](./event/) | Behavioural | Decouple senders from receivers using a publish/subscribe model | UI events, logging systems | Post-GoF |


[^single]: Singleton is often discouraged in modern design due to global state issues; use with care: https://en.wikipedia.org/wiki/Singleton_pattern.

