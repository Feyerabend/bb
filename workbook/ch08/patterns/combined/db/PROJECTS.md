## DB Project Ideas

### A. NoSQL Database with Indexing & Advanced Queries

- *Goal*: Enhance the NoSQL database to support indexing (e.g., B-trees or hash maps) for faster lookups.  
- *Tasks*:  
  - Add secondary indexes (e.g., `db.create_index("users", "age")`).  
  - Support query operators (`$gt`, `$lt`, `$in`, etc.).  
  - Benchmark performance before/after indexing.  

### B. NoSQL Database with Replication & Fault Tolerance
- *Goal*: Simulate a distributed NoSQL database with leader-follower replication.  
- *Tasks*:  
  - Implement a simple *WAL (Write-Ahead Log)* for recovery.  
  - Simulate node failures and automatic failover.  
  - Allow read queries from replicas.  

### C. NoSQL Database with a REST API
- *Goal*: Wrap the NoSQL database in a Flask/FastAPI server.  
- *Tasks*:  
  - Expose endpoints like `/insert`, `/query`, `/update`.  
  - Add authentication (e.g., API keys).  
  - Support JSON payloads for queries.  

### A. SQL Database with Transactions & Locking
- *Goal*: Add ACID transactions to the SQL database.  
- *Tasks*:  
  - Implement *row-level locking* (`SELECT FOR UPDATE`).  
  - Support `BEGIN`, `COMMIT`, `ROLLBACK`.  
  - Simulate concurrent transactions (deadlock detection).  

### B. SQL Query Optimizer
- *Goal*: Improve query performance with cost-based optimisation.  
- *Tasks*:  
  - Track table statistics (e.g., `ANALYZE users`).  
  - Choose between *index scans* vs. *full table scans*.  
  - Support `EXPLAIN` to show query plans.  

### C. SQL Database with a CLI (Interactive Shell)
- *Goal*: Build a MySQL-like interactive shell.  
- *Tasks*:  
  - Autocomplete for SQL keywords.  
  - Pretty-print query results (like `psql`).  
  - Add `.tables`, `.schema` meta-commands.  


__Extra__

### A. NoSQL vs. SQL Performance Benchmark
- *Goal*: Compare the performance of the two databases.  
- *Tasks*:  
  - Measure *insert/update/query* speeds.  
  - Test under different workloads (read-heavy vs. write-heavy).  
  - Visualize results with Matplotlib.  

### B. Distributed Key-Value Store (Mini-Redis)
- *Goal*: Build a simple Redis-like system.
- *Tasks*:
  - Support `SET`, `GET`, `DEL` commands.
  - Add *TTL (Time-To-Live)* for keys.
  - Simulate sharding (partition data across nodes).

__Traits of a Redis-Like System__
  - In-Memory Focus: Prioritise speed over disk persistence.
  - Command-Driven: Clients send text commands (e.g. SET, GET).
  - Data Structures: Support lists, hashes, etc., not just raw strings.
  - Network Interface: Listen for TCP/UDP requests (like a mini-server).

```python
class RedisLike:
    def __init__(self):
        self.data = {}  # key-value store
        self.commands = {
            "SET": self._set,
            "GET": self._get,
            "LPUSH": self._lpush,
        }

    def execute(self, command: str, *args) -> Any:
        cmd = command.upper()
        if cmd in self.commands:
            return self.commands[cmd](*args)
        raise ValueError("Unknown command")

    def _set(self, key, value):
        self.data[key] = value
        return "OK"

    def _get(self, key):
        return self.data.get(key, "(nil)")

    def _lpush(self, key, *values):
        if key not in self.data:
            self.data[key] = []
        self.data[key].extend(values)
        return len(self.data[key])

db = RedisLike()
db.execute("SET", "user:1", "Alice")
print(db.execute("GET", "user:1"))  # Output: "Alice"
```
