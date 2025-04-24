
## Databases

We make some remarks on databases here though the folder is intended more as a illustration of several design patterns.
We'll return to this later.


### Some Personal Experiences

*I attended an Informix conference in either 2000 or 2001, in the capacity of a computer journalist. The company had gathered media representatives from around the world, flying everyone in on their dime. It was a full-scale PR effort to generate renewed interest in their products--but the underlying mood was unmistakable: this was a company in its final throes.*

*The event was a mix of high-energy technical demos and quiet corporate desperation. Informix was eager to showcase its parallel database technology, which was genuinely impressive--technically advanced and ahead of many competitors in terms of performance and architecture. Yet, this enthusiasm couldn’t mask the broader signs of trouble.*

*From the upper echelons of the company came a peculiar announcement: Informix would be splitting into two entities. Officially, this was positioned as a strategic move, but it was hard not to interpret it as a distress signal--the kind of manoeuvre a company makes when it’s trying to shed ballast in a storm. Selling off part of the business to stay afloat seemed to be the subtext.*

*One of the company’s founders gave a keynote address, though it left a strange impression. Rather than focus on the company’s direction or technology, he spent a notable portion of the talk showing photos of his grandchildren. It felt like a farewell more than a leadership moment.*

*Still, amid the ambivalence, there were interesting thoughts. One remark that stood out was the idea that stored procedures might represent the future of database logic--due to their proximity to the data itself. In hindsight, that was a prescient comment, anticipating trends in data-centric computing.*

*In the end, it was a curious mix of highs and lows: brilliant engineers and solid products overshadowed by corporate instability and a sense of impending collapse. The whole event had the atmosphere of a last stand--a polished, enthusiastic, but ultimately doomed attempt to reclaim relevance.*

Informix was once a strong competitor in the database wars of the 1990s but lost ground due to financial mismanagement and fierce competition. While it still exists under IBM, its influence has faded, marking the end of an era for a once-prominent database system.


### Historical and Theoretical Background to Databases

The history of databases begins in the 1950s and 60s, when data storage was rudimentary and application-specific. Information was kept in flat files, often with custom formats, tightly coupled to the logic of the program accessing it. These systems lacked abstraction, and as they grew in complexity, issues like data redundancy, inconsistency, and difficulty in managing concurrent access became major obstacles. As organisations needed to manage larger and more diverse datasets, this model proved increasingly brittle.

In response to these limitations, more structured database models emerged. The first were *hierarchical databases*, where data was organised as a tree of records. IBM’s IMS (Information Management System) was one of the first commercial systems of this type. While fast for predefined queries, hierarchical models were inflexible--changing the schema or querying the data in a new way was difficult and often required rewriting code.

The next development was the *network database model*, formalised by the CODASYL group. It offered more flexibility by allowing data to be structured as a graph rather than a strict tree. However, querying and navigating these systems still required imperative, record-at-a-time traversal logic, which made them hard to use and maintain.

A major conceptual leap came in 1970, when *Edgar F. Codd*, working at IBM, introduced the *relational model*. This was a mathematically grounded approach that treated data as sets of tuples grouped into relations--what we now call tables. Codd’s model was based on set theory and predicate logic, and it emphasised a *declarative* approach: users would describe what data they wanted, rather than how to fetch it. *This separation of logical structure from physical storage and access paths was revolutionary.*

The relational model laid the theoretical groundwork for a new kind of database system, and several experimental and commercial RDBMS (Relational Database Management Systems) soon followed. Among the earliest were *System R* from IBM and *Ingres* from the University of California, Berkeley. These systems introduced *SQL (Structured Query Language)*, which became the dominant query language for relational systems and remains so today.

By the 1980s and 90s, relational databases had become the foundation of enterprise data management. Vendors like Oracle, IBM (with DB2), Informix, Sybase, and Microsoft all competed in this space, each providing robust implementations of SQL-based systems. As data applications evolved, many systems added features like stored procedures, triggers, and support for complex types, leading to so-called *object-relational databases*.

However, not all workloads fit neatly into the relational paradigm. In the 2000s, as web-scale and cloud-based applications proliferated, a new category emerged: *NoSQL databases*. These systems abandoned the relational model in favour of simpler, often schema-less data models designed for horizontal scalability, availability, and performance over massive datasets. They include document stores (like MongoDB), key-value stores (like Redis), wide-column stores (like Cassandra), and graph databases (like Neo4j). Unlike traditional RDBMSs, NoSQL systems typically emphasise eventual consistency and flexible data structures.

More recently, the trend has been toward *polyglot persistence*--using different types of databases for different parts of a system depending on the data and query characteristics. In parallel, *NewSQL* systems like CockroachDB and Google Spanner attempt to blend the consistency and familiarity of SQL with the scalability of NoSQL. Cloud-native databases, time-series databases, and vector databases have all emerged to meet new types of analytical, transactional, or AI-focused workloads.

Databases today sit at the center of virtually every computing system. The evolution from flat files to modern distributed, transactional, and query-optimised systems reflects a broader narrative of abstraction, formalisation, and the tension between generality and specialisation.


### SQL in Brief

*SQL (Structured Query Language)* originated in the 1970s as part of IBM’s System R project. It was initially called SEQUEL (Structured English Query Language) and still it is often pronounced as 'sequel,' but the name was later substituted due to trademark issues. SQL became the standard language for interacting with relational databases, formalised by ANSI and ISO in the 1980s.

What sets SQL apart is its *declarative nature*. Instead of specifying how to retrieve data, users declare what data they want, and the database engine determines the most efficient way to execute the query. SQL operates on *tables* (relations) and returns result sets also in tabular form.

SQL is divided into several sublanguages:

- *DDL (Data Definition Language)*: for defining schemas (`CREATE TABLE`, `ALTER TABLE`)
- *DML (Data Manipulation Language)*: for inserting, updating, or deleting rows (`INSERT`, `UPDATE`, `DELETE`)
- *DQL (Data Query Language)*: for querying data (`SELECT`)
- *TCL (Transaction Control Language)*: for managing atomicity (`BEGIN`, `COMMIT`, `ROLLBACK`)
- *DCL (Data Control Language)*: for setting access permissions (`GRANT`, `REVOKE`)

Here’s a simple example of a SQL query:

```sql
SELECT name, age
FROM users
WHERE age > 30
ORDER BY age DESC;
```


### sql.py

This database is a simple in-memory SQL-like system built on a binary search tree. It is designed for learning and experimentation, and does not support many features found in full-scale database management systems.

Here are its limitations:

The database does not support transactions, concurrency, or advanced SQL features such as joins or indexes. It is case-sensitive for both column names and values. SQL injection prevention is not implemented, and the system does not enforce data validation or constraints.

It does not support foreign keys or relationships between tables, and there is no support for advanced or custom data types. Backup, restore, or data migration features are not provided. Schema evolution is also not supported.

User authentication, access control, data encryption, and other security-related features are not available. The database lacks logging, auditing, performance tuning, or optimisation capabilities.

There is no functionality for importing, exporting, visualising, or reporting data. It does not include features for data analysis, machine learning, or big data processing. Integration with cloud platforms or distributed systems is not supported.

The system does not support NoSQL, document-based, graph, time-series, or spatial/geospatial database features. Full-text search and indexing are not available. There is no support for data partitioning, sharding, replication, clustering, high availability, failover, load balancing, or caching.

Monitoring, alerting, APIs, and integration with external systems or tools are not provided. Additionally, the database does not support any data governance, compliance, privacy, or protection features.

Lifecycle management, data archiving, retention policies, data quality control, cleansing, profiling, discovery, lineage, mapping, cataloging, metadata management, modelling, design, interoperability, semantics, or ontology support are all out of scope.


### nosql.py

Same as above with the exception for NoSQL, which it is.


### Projects

From the list it should be obvious what projects might be suitable. Choose a project which is surely within the scope of your training and learning.

*The point is here that following design pattern makes the code not only often more readable, but also easier to __extend__.* Extend!

