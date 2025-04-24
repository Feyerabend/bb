
## Combined Design Patterns

The sources present implementations of systems including a *[file system](./fs/)*,
two different *NoSQL databases*, an *in-memory SQL-like database* ([databases](./db/)), and
components of a *[simple operating system](./os/)* (specifically process and memory
management).

A central theme across these implementations is the strategic use of numerous
*design patterns* to structure the code and manage complexity.

Key *design patterns* demonstrated include:

- *Composite Pattern*: Used in the file system examples to represent hierarchical
  structures like directories and files, and in the SQL database for evaluating
  complex conditions.

- *Visitor Pattern*: Employed in the file system to perform operations like
  finding or gathering statistics on nodes in a decoupled way. A simple
  example of a visitor pattern for [lists](./../../data/listvisitor/).

- *Strategy Pattern*: Used in various contexts such as path resolution in the
  file system, query matching or command execution logic in the NoSQL databases,
  scheduling and memory allocation in the simple OS components, and query execution
  in the SQL database.

- *Factory Pattern*: Applied for creating objects like file system nodes, database
  commands or collections, and SQL query objects.
 
- *Command Pattern*: Features prominently across the examples to encapsulate operations
  (like file system commands or database actions) as objects, allowing for things like
  queues or logging.
- *Singleton Pattern*: Used to ensure only one instance of core components exists,
  such as the main file system or the SQL database.

- *Observer Pattern*: Implemented in the databases and simple OS kernel to provide
  notification mechanisms for events like data changes or process state transitions.

- *Facade Pattern*: Mentioned as providing a simplified interface over a complex system
  in one of the NoSQL examples.

- *Iterator Pattern*: Used in the SQL database for traversing data structures like a
  [Binary Search Tree](./../../data/).

The sources provide practical illustrations of how these *design patterns* can be applied
to build well-structured and maintainable software systems in different domains.
