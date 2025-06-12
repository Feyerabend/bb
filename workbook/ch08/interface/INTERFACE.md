
## Interfaces

An interface is a defined boundary or shared surface between systems, components, or entities that enables
interaction or communication in a predictable and structured way.

An interface defines how two sides exchange data, control, or resources--but *not* *how* either side is
implemented internally.
- It specifies the form, meaning, and rules of interaction.
- It enables components to collaborate despite internal differences.
- It acts as a contract: as long as both sides respect the interface, they can interact successfully.

This principle applies across technical layers—from transistors to user interfaces.


### What does an interface do?

1. Enables communication: Defines how information flows between components.
2. Encapsulates complexity: Hides internal details behind a stable interaction point.
3. Supports modularity: Components can be developed independently as long as the interface is preserved.
4. Facilitates interoperability: Allows independently-built systems—often in different languages or
   domains—to work together.

| Characteristic       | Meaning                                                                 |
|--|--|
| Explicitness         | Clearly specified, documented, and understood by both sides             |
| Stability            | Interfaces evolve more slowly than implementations                      |
| Abstraction          | Hides internal mechanisms, exposing only what’s necessary               |
| Bidirectionality     | Some interfaces are one-way (API calls); others are negotiated (protocols) |
| Well-defined semantics | Defines not just syntax but also meaning and expected behavior         |
| Composability        | Interfaces enable reuse and reassembly into larger systems              |


### Interface metaphor

A wall socket is a physical interface:
- Specifies shape, voltage, and electrical protocol.
- Allows diverse devices to connect without knowing how power is generated or distributed.
- A stable contract that enables safe interaction despite internal heterogeneity.



### Interface Types and Examples

Interfaces take many forms in computing—from low-level machine integration to human-facing systems.

| Interface Type            | Description                                | Example                        | Layer                          |
|--|--|--|--|
| User Interfaces (UI)  | Boundary between human and system behavior | GUI buttons, CLI, touch events | Application / Presentation      |
| Data formats / Schemas    | Structured data exchange                   | JSON, XML, Protocol Buffers    | Application                     |
| File formats              | Persistent data structures                 | CSV, SQLite, PDF               | Application                     |
| APIs                      | Callable program functions                 | POSIX, REST                    | Application                     |
| Protocols                 | Agreed communication rules                 | HTTP, TCP/IP, MQTT             | Network / Transport             |
| Message queues / Topics   | Asynchronous pub/sub model                 | Kafka, RabbitMQ                | Middleware                      |
| Event loops / Callbacks   | Async control handoffs                     | JS loop, GUI events            | Application                     |
| Function signatures       | Invocation contract between code units     | int f(int) in C              | Language / Compiler             |
| Shared libraries / Linking| Binary integration of code modules        | libc.so, DLLs                | OS / Compiler                   |
| Memory layouts / ABIs     | Binary compatibility between binaries      | x86 calling convention         | OS / Compiler                   |
| Shared memory segments    | Low-level memory access sharing            | mmap, POSIX shm              | OS / Kernel                     |
| Signals / Interrupts      | Async system-level notifications           | IRQs, UNIX signals             | OS / Hardware                   |
| State machines            | Defined transition models                  | TCP handshake, parser automaton| Application / Protocol          |
| Command line conventions  | Text-based interaction contract            | UNIX pipes, CLI arguments      | Application / OS                |
| Contracts / Types         | Declarative interface specs                | TypeScript types, CORBA IDL    | Language / Application          |
| Hardware interfaces       | Software ↔ hardware interaction            | GPIO, PCI bus                  | Hardware                        |


### UI as Interface

A User Interface (UI) is a direct interaction surface between a human and a system:
- A UI defines input modalities (e.g., clicks, gestures, keystrokes) and output formats (e.g., visuals, sounds).
- Like any interface, it hides implementation details and exposes a consistent interaction contract.
- It enables people to control or observe a system without understanding its internals.

From this perspective, a UI is not separate from interface theory—it is simply a human-facing interface, governed
by the same principles: abstraction, encapsulation, explicit structure, and predictable semantics.



### Layered Interface Model

Interfaces stack and interact across system layers:

1. Hardware: GPIO, buses, voltage levels
2. Kernel/OS: Signals, shared memory, ABIs
3. Language/Compiler: Function signatures, types, linking
4. Middleware/Application: APIs, event loops, protocols, queues
5. Presentation/Interaction: UIs, file formats, data schemas


Cross-layer example
- A user clicks a button (UI),
- which calls a JavaScript function (API),
- which sends a REST request over HTTP (protocol),
- routed via TCP/IP (network stack),
- handled by a kernel driver (OS),
- that writes to a device register (hardware).

Each step uses a specific interface, layered but interdependent.


### Summary

Interfaces are contracts that enable interaction between components, regardless of their implementation.
Whether machine-to-machine or human-to-machine (UI), interfaces enable modularity, abstraction, and
communication across technological boundaries.
