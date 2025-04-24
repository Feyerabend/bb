
## Hybrid Projects

### A. Tiny Database-Driven OS

*This project combines operating system principles with database design.
You use SQL tables to model and interact with internal OS components--a
kind of "database as OS state representation."*

- Demonstrates integration between DBMS concepts and OS architecture.
- Encourages thinking in terms of declarative querying (SELECT) rather
  than imperative data access.
- Enables live introspection into the system via queries--very powerful
  for debugging or monitoring.

Potential Features
- SQL tables for: processes, memory pages, I/O buffers, file metadata.
- Write triggers or views for system policies (e.g. eviction, scheduling).
- Implement a SQL-based REPL for system interaction.


### B. Test Code Strategies (Refactoring)

This is about learning through contrast: first build a feature "naïvely"
(without patterns), then refactor it with design patterns. Alternatively,
extend code already refactored.

#### Two Approaches

__1. Build First Without Patterns, Then Refactor__

- Good for learning why patterns matter.
- Lets you see what problems design patterns solve.
- Encourages critical thinking about coupling, cohesion, reuse, and readability.

Cons
- May involve more work if the initial codebase becomes hard to adapt.


__2. Extend Existing Patterned Code__

- Encourages thinking in terms of composition, interfaces, and extensibility
  from the start.
- Often more scalable.

Cons
- Risk of "overfitting" to patterns without understanding the tradeoffs.
- Less opportunity to see the pain that patterns relieve.


#### Which do *you* find best?

Argument: For learning purposes, option 1 is better.
- Build something functional without patterns, then refactor it with clear,
  documented transformations.
- This gives you concrete insight into when patterns help and forces you
  to deal with complexity first-hand.

Agree or disagree? Arguments! What about in production in real settings?


### C & D. Compose Database and Filesystem

The concept of merging filesystems and databases into a unified abstraction
has surfaced many times, including Microsoft's WinFS project (as I read in
a paper as part of the "Longhorn" vision, early 2000s). It ultimately failed
to ship, but the motivation behind it was intriguing.


__1. Filesystem becomes a database__

This means modeling a filesystem where files, directories, and metadata are
stored and queried using relational or key-value structures.

Advantages
- Enables rich querying: SELECT name FROM files WHERE size > 1GB AND tag = 'media'
- Tags and metadata replace brittle hierarchies.
- Easier to implement fine-grained access control and versioning.
- Native indexing, searching, and constraints.

Challenges
- Breaks the path-based assumptions of Unix/POSIX systems.
- File operations are transactional and may introduce overhead.
- Mapping to low-level storage (blocks, pages) is more complex when bound to SQL semantics.
- Compatibility layers are required for legacy applications.

Examples an dInspirations
- WinFS: Built on top of NTFS + SQL Server, tried to unify documents, media, email, etc.
- Btrfs, ZFS: Have advanced metadata layers, not SQL but hint at structured storage.
- ReiserFS (v4): Explored using file-as-object models, which approximates database thinking.


__2. Database is implemented as a filesystem__

Now we imagine flipping it: the database doesn't have its own storage engine but uses the
filesystem API to store its tables, indexes, and data.

Advantages
- Simplifies DB engine design by offloading persistence and file management.
- Easier to use in embedded systems or VMs with sandboxed environments.
- Fits well with object storage or flat-file semantics (e.g. SQLite).

Challenges
- Performance: File I/O overhead and lack of control over block layout.
- No native support for transactions, locking, consistency (must be implemented on top).
- Metadata operations (like listing or checking timestamps) are not designed for high-frequency updates.

Examples
- SQLite: A full relational DB in a single file--not a filesystem, but uses it directly.
- Berkeley DB: Key-value store built on top of standard file I/O.
- Some NoSQL systems use flat file chunks (e.g. RocksDB, LevelDB) and memory-map them for performance.


#### Deeper Reflections

Why hasn't this fully happened?
- Filesystems and databases optimise for different access patterns.
- FS: hierarchical, stream-oriented, opaque contents.
- DB: flat/tabular, structured access, typed contents.
- OS-level integration is risky: One failure mode affects the whole system.
- Ecosystem inertia: Too much software assumes a POSIX-style filesystem.
- Complexity: A merged system is harder to design, debug, and optimize.

__Should It Happen?__

In some ways, it already is happening, just not monolithically:
- Filesystems are gaining rich metadata (extended attributes, journaling).
- Databases are becoming more embeddable and lighter-weight (e.g., DuckDB).
- Search tools like Tracker, Beagle, and macOS Spotlight add query layers over files.

We may eventually see:
- Filesystems with built-in structured indexing layers.
- Databases exposing virtual filesystems (like FUSE for tables and views).
- Event-based systems where files and records are streamed into pipelines,
  not statically stored.


### C. Structured Filesystem with SQL Interface

*Filesystem becomes a database*

Implement a virtual filesystem that stores files and directories in a relational schema,
allowing you to query and manipulate them with SQL.

Tables:
- files(name, size, created, modified, type, parent_dir)
- directories(name, created, parent_dir)
- Query interface via a SQLite shell:
```sql
SELECT name FROM files WHERE size > 10000 AND type = 'txt';
```
- File contents stored as BLOBs in the database (or external files, indexed by DB).
- Basic operations: create/delete file/dir, list contents, rename, move.
- Implement a mock ls, find, mv, cp using SQL queries.
- Optional: Add user permissions (file_access(user, file, mode)).

Learning Goals:
- Filesystem hierarchy mapping to relational schema
- SQL for structural file queries
- Simulating file operations as transactions


### D. Database-on-Filesystem with Custom Storage Layout

*Database implemented as a filesystem*

Build a minimalist relational database engine that stores tables and indexes as structured
files, one file per table, with binary layout and block-level access.

- Each table = one file
- Row format: fixed-length or simple record markers
- Index file per table (B-tree or hashmap)
- Simple SQL-like parser for:
```sql
CREATE TABLE users(id INT, name TEXT);
INSERT INTO users VALUES (1, 'Alice');
SELECT * FROM users WHERE id = 1;
```
- Implement SELECT, INSERT, basic WHERE clause.
- Use OS filesystem as backend--no 'mmap' or abstraction.
- Optional: Add journal/log file for durability and crash recovery.

Learning Goals:
- Manual binary file I/O
- Storage formats: rows, pages, index structures
- Basic parsing, execution engine
- Transaction simulation (write-ahead logging)
