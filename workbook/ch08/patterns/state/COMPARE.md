
## State Machanics vs State Pattern

| Aspect | Automata (DFA/NFA/PDA/TM) | State Pattern (Design Pattern) |
|--------|---------------------------|--------------------------------|
| Purpose | Model computation and recognize languages | Encapsulate varying behavior in OO systems |
| Inputs | External symbols (from alphabet) | Method calls (client code interaction) |
| Outputs | Accept/reject (and sometimes side-effects) | Varying behavior via polymorphism |
| Transition Function | Explicit formal mapping | Dynamic method dispatch |
| Memory | None (DFA/NFA), Stack (PDA), Infinite tape (TM) | Instance variables / object graph |
| State Change Trigger | Input symbol | Method call / internal logic |
| State Representation | Formal set of states (Q), explicit transitions | Concrete classes implementing a State interface |
| Flexibility | Fixed after design (static) | Can add/modify states dynamically (more extensible) |
| Typical Use | Parsers, protocol models, computation theory | UI workflows, game objects, business rules |
| Composability | States and transitions are atomic | States can share behaviour (inheritance/composition) |
