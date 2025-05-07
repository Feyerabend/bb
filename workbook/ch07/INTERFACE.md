
## Interfaces

An interface is a boundary or shared surface between two or more systems, components, or entities that
allows them to interact or communicate in a defined, predictable way.

An interface defines how two parties exchange data, control, or resources--but not how either party is
implemented internally.
- It specifies the form, meaning, and rules of interaction, independent of the inner workings of either side.
- It acts as a contract: if both sides adhere to the agreed interface, they can interact successfully,
even if they are otherwise independent or heterogeneous.

What does an interface do?
1. Enables communication: It provides a mechanism for exchanging information.
2. Encapsulates complexity: It hides the internal details of a component behind a clear contract.
3. Supports modularity: Components can be developed, tested, and maintained independently, as long as the interface remains stable.
4. Facilitates interoperability: Allows diverse systems, often written in different languages or running on different platforms, to work together.


What characterizes an interface?

|Characteristic	|Meaning|
|--|--|
|Explicitness	|The interface is clearly specified, not implicit or ad hoc|
|Stability	|Interfaces tend to change less frequently than implementations|
|Abstraction	|It abstracts away implementation details, exposing only what is needed|
|Bidirectionality (optional)	|Some interfaces are unidirectional (e.g., API call); some bidirectional (e.g., protocol negotiation)|
|Well-defined semantics	|Not just syntax--both sides must agree on meaning and effects of interactions|
|Composability	|Interfaces allow parts to be recombined into larger systems|

Metaphor

A wall socket is a physical interface:
- It specifies shape, voltage, and protocol (AC frequency).
- You don’t need to know how the power grid or the appliance works internally:
  just that the plug matches the socket.

In programming

An interface can be:
- A function signature (the caller knows what arguments and return type to expect)
- A file format (both programs know how to read/write a CSV)
- A network protocol (two machines know how to handshake, send, receive messages)

An interface is a shared agreement about how to interact, which enables independent components
to work together in a predictable, reliable way, without requiring knowledge of each other’s internals.

| Interface Type          | Description                               | Example                      | Layer |
|-------------------------|-------------------------------------------|------------------------------|-------|
| Data formats / Schemas  | Shared structure for data exchange        | JSON, XML, Protocol Buffers  | Application |
| File formats            | Disk-persisted data structures            | CSV, SQLite file, PDF        | Application |
| APIs (Application Programming Interface) | Functionality exposure via callable methods | REST API, POSIX API         | Application |
| Protocols               | Agreed rules for communication            | HTTP, TCP/IP, MQTT           | Transport / Network |
| Message queues / Topics | Pub/sub communication model               | RabbitMQ, Kafka              | Application / Middleware |
| Shared memory segments  | Low-level memory sharing                  | POSIX shared memory, mmap    | OS / Kernel |
| Memory layouts / ABIs   | Binary compatibility between modules      | POSIX ABI, x86 calling conv. | OS / Compiler |
| Function signatures     | Language-level invocation contract        | int f(int x) in C            | Language / Compiler |
| Event loops / Callbacks | Asynchronous control handoffs             | JS event loop, GUI callbacks | Application |
| Hardware interfaces     | Software ↔ hardware boundary              | GPIO, PCI bus                | Hardware |
| Command line conventions| Text-based input/output conventions       | UNIX pipes, CLI args         | Application / OS |
| State machines          | Contract for permissible transitions      | TCP handshake, parser automaton | Application / Protocol |
| Signals / Interrupts    | Asynchronous low-level notifications      | POSIX signals, IRQs          | OS / Hardware |
| Contracts / Types       | Declarative behavior specification        | TypeScript types, CORBA IDL  | Language / Application |
| Shared libraries / Linking | Binary module integration              | libc.so, Windows DLL         | OS / Compiler |


These interfaces form layers, where components above depend on or use interfaces below.
1. Hardware interfaces (GPIO, IRQs) sit at the base — interaction between physical devices and low-level software.
2. OS/Kernel-level interfaces (shared memory, signals, ABIs) provide mechanisms for processes and drivers to communicate and interoperate safely.
3. Language/compiler-level interfaces (function signatures, linking, types) define how compiled or interpreted code modules interoperate inside a running process.
4. Middleware/application-level interfaces (APIs, message queues, event loops) support higher-level modules and distributed systems interacting in meaningful ways.
5. Data exchange formats (JSON, file formats, schemas) specify how structured data is shared persistently or across networked boundaries.
6. Protocols span transport and application layers, enforcing consistent rules for remote or local interaction (HTTP, TCP/IP, etc.).

Cross-layer interaction examples:
- A REST API (application) communicates over HTTP (protocol), which rides on TCP/IP (network), implemented by the kernel, and touches hardware network cards.
- A shared library (libc.so) exposes function signatures (language-level) that rely on ABI (binary-level), running in a process (OS-level), on a CPU (hardware).
