
## Event Bus

The `Event Bus` is a messaging design pattern used to enable loosely coupled
communication between components in a system. It is often described as a
publish/subscribe (pub-sub) mechanism where publishers emit events, and
subscribers handle them, without being directly aware of each other.


### Core Concepts

|Concept	|Description|
|--|--|
|Event	|A message or signal representing something that happened.|
|Publisher	|Sends or emits events.|
|Subscriber	|Registers interest in certain types of events and reacts when they occur.|
|Bus	|The mediator that manages event delivery to subscribers.|


Use Cases
- GUI frameworks (e.g., button clicked, mouse moved)
- Game engines (e.g., collision, input events)
- Microservices or plugin systems
- Logging, analytics, or telemetry collection
