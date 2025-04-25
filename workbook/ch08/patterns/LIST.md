


Gang-of-Four patterns .. + 3 others

| Pattern            | Category        | Purpose                                                         | Example Use Case                                | Source        |
|--------------------|----------------|------------------------------------------------------------------|--------------------------------------------------|----------------|
| Strategy           | Behavioral      | Encapsulate interchangeable algorithms or behaviors              | Sorting algorithms, payment methods             | GoF            |
| Command            | Behavioral      | Encapsulate a request as an object                               | Undo/Redo, action queues, macro recording       | GoF            |
| Observer           | Behavioral      | Notify dependent objects of state changes                        | GUIs, event systems, data binding                | GoF            |
| State              | Behavioral      | Change object behavior based on internal state                   | Game AI, UI modes                               | GoF            |
| Decorator          | Structural      | Add behavior to objects dynamically                              | I/O streams, middleware pipelines                | GoF            |
| Adapter            | Structural      | Convert one interface to another                                 | Legacy code integration, wrapper libraries       | GoF            |
| Composite          | Structural      | Treat objects and groups uniformly                               | Scene graphs, file system trees                  | GoF            |
| Factory Method     | Creational      | Define interface for creating objects, let subclass decide       | Plugin creation, document editors                | GoF            |
| Abstract Factory   | Creational      | Create families of related objects without specifying classes    | GUI themes, cross-platform toolkits              | GoF            |
| Singleton*         | Creational      | Ensure a class has only one instance                             | Config manager, global registries                | GoF (controversial) |
| Builder            | Creational      | Separate construction of a complex object from its representation | Object configurators, UI builders               | GoF            |
| Prototype          | Creational      | Clone existing objects instead of creating new ones              | Object pools, data templates                     | GoF            |
| Mediator           | Behavioral      | Centralize complex communication between objects                 | Chat servers, air traffic control systems        | GoF            |
| Dependency Injection | Structural    | Provide dependencies from the outside                            | Testable systems, service wiring                 | Post-GoF       |
| Null Object        | Behavioral      | Use an object with default behavior instead of `null`            | Safe iteration, fault-tolerant systems           | Post-GoF       |
| Event Bus          | Behavioral      | Decouple senders from receivers using a publish/subscribe model | UI events, logging systems                       | Post-GoF       |


* Singleton is often discouraged in modern design due to global state issues; use with care.

