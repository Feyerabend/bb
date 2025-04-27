
## Design Patterns in Banking Sample

Compare the samples 'banking.py' with 'banking2.py'. The former code adheres to more
low-level constructions suitable for embedded microcontroller today, while the latter
is illustrating more higher-level constructions. 


#### 1. Command Pattern

- The Command pattern is a key element in the design of this system. It is used to encapsulate
  actions or operations in separate command objects that can be executed on request.

- Classes like AddCommand, MultiplyCommand, ConcatCommand, ReverseCommand, and MainCommand each
  represent a specific command that can be executed. These commands implement the execute method
  from the Command interface (defined as a Protocol in Python).

- The Bank class registers commands with a bank using the register method, which maps command
  IDs to command instances. This setup allows the BankManager to execute specific commands by
  referencing their IDs without needing to know the details of the operations being performed.

- Advantage: The code can easily extend to new commands without modifying existing code, adhering
  to the Open-Closed Principle (a key design goal of Command patterns).


#### 2. Memento Pattern

- The Memento pattern is used to capture and restore the state of an object. In this code, the
  Memento class is used to save the state of the current bank (bank name) and the return program
  counter (return_pc) when making calls between different banks.

- The SharedRAM class manages the call_stack, which holds these Memento objects. When the BankManager
  makes a call to another bank, the current bank is saved in a Memento, allowing the program to
  "return" to the original bank later (via the ret method).

- Advantage: The state of the system can be preserved and restored, allowing for features like
  backtracking or undoing operations.


#### 3. Factory Method Pattern
- The Factory Method pattern is applied in the creation of banks. The functions create_math_bank,
  create_string_bank, and create_main_bank are factory methods that instantiate Bank objects,
  register specific commands, and return the banks.

- Advantage: These methods abstract the creation of banks with their associated commands, providing
  a clear structure for organizing commands in different banks. New banks can be created without
  modifying the core logic of the system.


#### 4. Strategy Pattern

- The Strategy pattern could be loosely considered for the BankManager when calling different commands.
  In the call method of BankManager, different strategies (commands) are executed based on the function
  ID (such as AddCommand, MultiplyCommand, etc.). The BankManager doesn’t need to know how each specific
  command is implemented; it delegates the execution to the appropriate command object.

- Advantage: The behavior of the system can be modified dynamically by changing or adding new strategies
  (commands) without changing the structure of BankManager.

#### 5. Observer Pattern (Implicit)

- Although not fully implemented here, the Observer pattern is indirectly supported by the SharedRAM’s
  log method. The log method appends messages to an output_buffer, which acts as a log. This pattern could
  be expanded if more observers (such as external systems) needed to track these logs or react to certain
  actions (such as function calls or exceptions). Project!

- Advantage: The system can support logging or tracking behaviors without tightly coupling other components
  to the SharedRAM.


### Summary
- Command Pattern: Encapsulates operations into command objects (e.g., AddCommand, MultiplyCommand).
- Memento Pattern: Saves and restores the state of the system (e.g., Memento objects in the call stack).
- Factory Method Pattern: Abstracts the creation of Bank objects and their associated commands.
- Strategy Pattern: Allows for dynamic execution of commands by BankManager based on function IDs.
- Observer Pattern (implicit): Log tracking could be extended to an observer system for monitoring system behavior.

These patterns help organise and decouple the system, making it more modular, extensible, and easier to maintain.
