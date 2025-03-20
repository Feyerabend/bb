
## A Selection of Examples

For a student of this field, understanding algorithms, data structures, and abstract data
types is highly beneficial--not necessarily to memorise every detail, but to recognise *when*
and *why* to use them. As modern programming shifts increasingly toward __orchestrating__ systems
rather than __writing everything from scratch__, having a broad conceptual overview often proves
more valuable than deep memorisation of specific algorithms.

Today, many problems can be solved using existing libraries, frameworks, or even AI-assisted
coding tools. However, knowing the underlying principles allows developers to make informed
decisions, such as choosing the right data structure for performance optimisation or recognising
when a certain algorithm would be inefficient. Instead of focusing on *rote learning*, students
benefit more from developing *algorithmic intuition*--the ability to analyse problems and select
appropriate approaches based on trade-offs like time complexity, space usage, and ease of
implementation.

That said, in fields where performance and efficiency are critical, such as embedded systems,
real-time computing, or advanced algorithmic problem-solving, a deeper understanding remains
essential. Even in higher-level development, knowing the fundamentals can make debugging,
optimising, or extending code much more effective.

Ultimately, the key is balance: the focus should be on developing a broad *understanding* of
algorithms and data structures while diving deeper when necessary. This approach ensures the
ability to apply the right tools effectively, rather than merely recalling definitions.
Here are some starting points to explore.


#### A*
- *Type*: Pathfinding and graph traversal algorithm
- *Explanation*: A* is an informed search algorithm that finds the shortest path from a start node to a goal node using a heuristic function. It combines the cost to reach a node (g-cost) and an estimated cost to the goal (h-cost) to prioritise exploration.
- *Use Case*: Widely used in AI for game development, robotics, GPS navigation, and network routing, where efficient pathfinding is required.
- *Operations*: Initialise open and closed lists, evaluate neighbours based on cost functions, update paths dynamically, and reconstruct the optimal path once the goal is reached.


#### Activity Selection
- *Type*: Greedy algorithm
- *Explanation*: The Activity Selection algorithm solves the problem of selecting the maximum number of non-overlapping activities from a given set, where each activity has a defined start and end time. The greedy approach ensures that activities are chosen in a way that allows the most efficient use of available time.
- *Use Case*: Commonly used in scheduling problems, such as booking meeting rooms, CPU job scheduling, and optimising event planning where tasks must be performed without conflicts.
- *Operations*: Sort activities by finish time, iterate through activities to select non-overlapping ones, maximise total count of selected activities.


#### AVL (Adelson-Velsky and Landis Tree)
- *Type*: Self-balancing Binary Search Tree (BST)
- *Explanation*: AVL trees maintain a balance condition by ensuring that the height difference between the left and right subtrees of any node is at most 1. After every insertion or deletion, the tree performs rotations to maintain this balance.
- *Use Case*: Efficient searching, insertion, and deletion in $O(log n)$ time. Useful in scenarios where frequent insertions and deletions occur, and balanced search time is required.
- *Operations*: Search, insert, delete, rotate.


#### Binary Tree
- *Type*: Hierarchical data structure
- *Explanation*: A binary tree is a tree where each node has at most two children, typically referred to as the left and right child. It does not necessarily need to be balanced or sorted.
- *Use Case*: Representing hierarchical structures, such as file systems or organisational charts, or as the foundation for other specialised trees (like BST or heap).
- *Operations*: Traversals (in-order, pre-order, post-order), search, insert, delete.


#### Binary Search Tree (BST)
- *Type*: Hierarchical data structure (tree-based)
- *Explanation*: A Binary Search Tree (BST) is a node-based structure where each node has at most two children. The left subtree contains nodes with smaller values, while the right subtree contains nodes with larger values. This ordering enables efficient searching, insertion, and deletion.
- *Use Case*: Used in databases for indexing, in-memory searching, and maintaining ordered data structures in applications like symbol tables and auto-suggestions.
- *Operations*: Insert a node, delete a node, search for a value, traverse in-order (sorted order), pre-order, and post-order.


#### Bloom Filter [Probabilistic]
- *Type*: Probabilistic Data Structure
- *Explanation*: A Bloom Filter is a space-efficient, probabilistic data structure used to test whether an element is a member of a set. It uses multiple hash functions to map elements to positions in a bit array. If all bits at the hashed positions are set to 1, the element might be in the set; otherwise, it is definitely not in the set. However, it can produce false positives, meaning it may incorrectly indicate that an element is in the set, but it will never produce false negatives.
- *Use Case*: Bloom Filters are used in scenarios where space is a concern and false positives are acceptable, such as checking membership in large sets, web caching, spell-checking, and network protocols (e.g., in databases or blockchain systems).
- *Operations*: Add, check (membership query).


#### Breadth-First Search (BFS)
- *Type*: Graph traversal algorithm
- *Explanation*: Breadth-First Search (BFS) explores a graph or tree level by level, visiting all neighbours of a node before moving to the next level. It uses a queue to track discovered nodes and ensures all nodes at the current depth are processed before moving deeper.
- *Use Case*: Used in shortest path algorithms (like Dijkstra's algorithm for unweighted graphs), network broadcasting, AI pathfinding (e.g., in game development), and web crawling.
- *Operations*: Initialise a queue, enqueue the starting node, dequeue and process nodes, enqueue unvisited neighbours, repeat until all reachable nodes are visited.


#### B-Tree
- *Type*: Self-balancing search tree
- *Explanation*: A B-Tree is a balanced tree data structure designed for efficient insertion, deletion, and search operations, particularly in database systems and file systems. It maintains balance by ensuring that nodes have a minimum and maximum number of children, reducing the number of disk accesses required for operations. Unlike binary search trees, B-Trees allow multiple keys per node, making them well-suited for handling large amounts of data.
- *Use Case*: Commonly used in databases (e.g., indexing in relational databases), file systems, and applications that require efficient large-scale search operations.
- *Operations*: Insert, delete, search, split nodes, merge nodes, maintain balance.


#### Depth-First Search (DFS)
- *Type*: Graph traversal algorithm
- *Explanation*: Depth-First Search (DFS) explores a graph or tree by starting at a root node and diving as deep as possible along one branch before backtracking. It uses recursion or an explicit stack to keep track of visited nodes. DFS is useful for exploring all possible paths, detecting cycles, and solving problems that require exhaustive searches.
- *Use Case*: Used in maze solving, pathfinding, topological sorting, cycle detection in graphs, and solving puzzles like Sudoku.
- *Operations*: Visit nodes in depth-first order, track visited nodes, backtrack when needed, detect cycles, find connected components.


#### Dijkstra's Algorithm
- *Type*: Graph algorithm (Shortest Path)
- *Explanation*: Dijkstra's algorithm finds the shortest path from a single source vertex to all other vertices in a weighted graph with non-negative edges using a priority queue.
- *Use Case*: Used in network routing, GPS navigation, and AI pathfinding.
- *Operations*: Initialise, relax edges, extract-min, update distances.


#### Disjoint Set (Union-Find)
- *Type*: Data structure for partitioning a set into disjoint subsets
- *Explanation*: Disjoint Set, or Union-Find, is used to keep track of a collection of disjoint sets and provides efficient methods for union and find operations. It uses techniques like path compression and union by rank to speed up these operations.
- *Use Case*: Used in algorithms like Kruskal's algorithm for finding the minimum spanning tree, and for dynamic connectivity problems in networks.
- *Operations*: `find`, `union`, `connected`.


#### Double Linked List
- *Type*: Linked List
- *Explanation*: A doubly linked list is a type of linked list where each node contains a reference (or link) to both the next and previous node. This allows traversal in both directions.
- *Use Case*: Used when frequent insertion and deletion at both ends are required, such as in a browser history or an undo/redo system.
- *Operations*: Insert, delete, traverse forwards/backwards.


#### Fenwick Tree (Binary Indexed Tree, BIT)
- *Type*: Data structure for cumulative frequency/range queries
- *Explanation*: A Fenwick tree provides an efficient way to compute prefix sums and perform point updates in logarithmic time while using minimal space.
- *Use Case*: Used in competitive programming, range sum queries, and frequency analysis.
- *Operations*: Update, prefix sum query.


#### Fibonacci Heap
- *Type*: Advanced priority queue, heap-based
- *Explanation*: A Fibonacci heap is a collection of heap-ordered trees with better amortised time complexity for operations like decrease-key compared to binary or binomial heaps. It supports quick merging and is particularly efficient for graph algorithms.
- *Use Case*: Frequently used in Dijkstra's shortest path algorithm and network optimisation problems.
- *Operations*: Insert, extract-min, decrease-key, delete, merge.


#### Hash Table
- *Type*: Data structure for key-value pairs
- *Explanation*: A hash table stores key-value pairs and uses a hash function to compute an index into an array of buckets or slots, from which the desired value can be found. Collisions are resolved using methods like chaining or open addressing.
- *Use Case*: Fast lookups, insertions, and deletions. Common in implementing associative arrays, sets, and caches.
- *Operations*: Insert, delete, search.


#### Heap
- *Type*: Binary Tree-based data structure
- *Explanation*: A heap is a special tree-based structure that satisfies the heap property: in a max-heap, the value of each node is greater than or equal to its children, and in a min-heap, the value is less than or equal to its children.
- *Use Case*: Used in priority queues, heap sort, and for efficient access to the maximum or minimum element.
- *Operations*: Insert, delete (extract), peek.


#### Huffman Coding
- *Type*: Greedy algorithm for lossless data compression
- *Explanation*: Huffman Coding constructs an optimal prefix-free binary tree based on character frequencies, where more frequent characters get shorter codes and less frequent characters get longer codes. It minimises the average length of encoded messages.
- *Use Case*: Used in data compression formats like JPEG, PNG, MP3, and in text compression applications such as ZIP files.
- *Operations*: Compute character frequencies, build a priority queue, construct a Huffman tree, generate binary codes, encode and decode data.


#### KD-Tree (K-Dimensional Tree)
- *Type*: Binary tree for multidimensional data
- *Explanation*: A k-d tree is a space-partitioning data structure for organising points in a k-dimensional space. It is used to store points and efficiently support range and nearest neighbour queries.
- *Use Case*: Used in multidimensional search spaces like in computer graphics, machine learning (k-nearest neighbours), and spatial databases.
- *Operations*: Insert, query (range search, nearest neighbour).


#### Kruskal's Algorithm
- *Type*: Algorithm for Minimum Spanning Tree
- *Explanation*: Kruskal's algorithm finds the minimum spanning tree of a graph. It sorts the edges of the graph in increasing order and adds edges to the spanning tree, ensuring no cycles form. Disjoint Set is typically used for cycle detection.
- *Use Case*: Used in network design, such as to find the minimum cable length required to connect a set of computers, or in cluster analysis.
- *Operations*: Sort edges, union-find.


#### Linked List
- *Type*: Linear data structure
- *Explanation*: A linked list is a collection of nodes where each node contains data and a reference to the next node in the sequence. It can be singly or doubly linked.
- *Use Case*: Suitable for dynamic data storage where elements are frequently inserted and removed, like in memory management and as an alternative to arrays when memory allocation is a concern.
- *Operations*: Insert, delete, traverse, search.


#### Longest Common Subsequence (LCS) [dynamic programming]
- *Type*: String comparison algorithm
- *Explanation*: The Longest Common Subsequence (LCS) problem finds the longest subsequence that appears in the same relative order in both given sequences but not necessarily contiguously. It is widely used in text comparison, DNA sequence analysis, and diff tools.
- *Use Case*: Useful in version control systems for detecting changes between files, bioinformatics for DNA sequence alignment, and natural language processing for similarity measurement.
- *Operations*: Compute LCS length, reconstruct LCS, optimize space complexity.



#### Merge Sort (+ parallel variant)


#### Priority Queue
- *Type*: Queue with priority
- *Explanation*: A priority queue is a data structure where each element is associated with a priority. Elements with higher priority are dequeued before elements with lower priority. Typically implemented using a heap.
- *Use Case*: Scheduling tasks with priorities, Dijkstra's algorithm, Huffman coding.
- *Operations*: Insert, extract minimum/maximum, peek.


#### Queue
- *Type*: Linear data structure (FIFO)
- *Explanation*: A queue is a collection where elements are added at the rear (enqueue) and removed from the front (dequeue), following the First In, First Out (FIFO) principle.
- *Use Case*: Used in situations like task scheduling, breadth-first search, and buffering.
- *Operations*: Enqueue, dequeue, peek.


#### Quick Sort (+ parallel variant)


#### RMQ (Range Minimum Query)
- *Type*: Query problem with a data structure
- *Explanation*: RMQ is a problem where given an array, you need to find the minimum element in a subarray for any given range. Segment trees, sparse tables, or binary indexed trees can be used to solve this problem efficiently.
- *Use Case*: Used in problems where range queries for minimum/maximum are frequent, such as in image processing, signal processing, or dynamic programming.
- *Operations*: Query, update.


#### Segment Tree
- *Type*: Binary tree for range queries
- *Explanation*: A segment tree is a binary tree used to store intervals or segments. It allows querying and updating the values of array segments in $O(log n)$ time.
- *Use Case*: Used for problems involving range queries like sum, minimum, maximum, or GCD, especially when the array is large and requires frequent updates.
- *Operations*: Build, query, update.


#### Skip List
- *Type*: Probabilistic data structure for ordered sets
- *Explanation*: A skip list is a layered linked list where elements can be accessed faster by skipping over nodes using additional pointers at higher levels. It provides logarithmic search time without explicit balancing.
- *Use Case*: Used as an alternative to balanced search trees in databases, in-memory storage, and indexing systems.
- *Operations*: Insert, delete, search, probabilistic balancing.


#### Splay Tree
- *Type*: Self-adjusting binary search tree
- *Explanation*: A splay tree performs a "splay" operation, moving accessed elements to the root using rotations, which helps keep frequently accessed elements near the top.
- *Use Case*: Suitable for applications where recently accessed elements are likely to be accessed again, such as caches and garbage collection.
- *Operations*: Insert, delete, search, splay (self-adjustment).


#### Treap [probabilistic]
- *Type*: Randomised binary search tree
- *Explanation*: A treap is a combination of a binary search tree (BST) and a heap, where keys follow BST properties, and priorities maintain a heap structure. This helps balance the tree probabilistically.
- *Use Case*: Efficient for dynamic ordered data storage, such as in dynamic sets, maps, and range queries.
- *Operations*: Insert, delete, search, rotation-based balancing.


#### Trie (Prefix Tree)
- *Type*: Tree-based string data structure
- *Explanation*: A trie is a multi-way tree used for storing and searching strings efficiently. Each node represents a character, and paths form words.
- *Use Case*: Used in autocomplete, dictionary applications, and IP routing.
- *Operations*: Insert, search, delete, prefix matching.



### Summary Table of Data Structures

| Data Structure       | Type                       | Time Complexity for Search/Insert/Delete | Common Use Cases                                     |
|-|-|--|-|
| *AVL Tree*          | Balanced Binary Tree       | O(log n) for all operations             | Efficient search, insertion, deletion in dynamic datasets |
| *Binary Tree*       | Tree                       | O(n) for search, O(log n) for insert/delete | Hierarchical data representation                    |
| *Bloom Filter*      | Probabilistic Data Structure  | O(k) for check (where k is the number of hash functions) and O(k) for add (where k is the number of hash functions) | Space-efficient membership testing with false positives  |
| *Dijkstra's Algorithm*        | Graph Algorithm              | O((V + E) log V)                        | Shortest-path finding in graphs |
| *Disjoint Set*      | Union-Find                 | O(log n) with path compression          | Dynamic connectivity problems, Kruskal's algorithm   |
| *Double Linked List*| Linked List                | O(1) for insert/delete at both ends     | Browser history, undo/redo operations                |
| *Fenwick Tree (BIT)*          | Indexed Tree                 | O(log n) update/query                   | Efficient range queries with prefix sums |
| *Fibonacci Heap*              | Heap/Priority Queue          | O(1) insert, O(log n) extract-min       | Efficient priority queue operations in graph algorithms (e.g., Dijkstra's, Prim's) |
| *Hash Table*        | Hashing                    | O(1) average case, O(n) worst case      | Fast lookup, insertion, caching                      |
| *Heap*              | Tree (Binary)              | O(log n) for insert/delete, O(1) for peek | Priority Queue, Heap Sort                            |
| *KD-Tree*           | Binary Tree                | O(log n) for search, O(log n) for nearest neighbour | Spatial data queries (e.g., nearest neighbours)       |
| *Kruskal's Algorithm*| Algorithm                  | O(E log E) (where E is the number of edges) | Minimum Spanning Tree, network design               |
| *Linked List*       | Linear Data Structure      | O(n) for search, O(1) for insert/delete | Dynamic data storage, memory management             |
| *Priority Queue*    | Queue (Heap-based)         | O(log n) for all operations             | Task scheduling, Huffman coding                     |
| *Queue*             | Linear Data Structure (FIFO)| O(1) for enqueue/dequeue                | Task scheduling, breadth-first search               |
| *RMQ*               | Query Problem              | O(log n) for query/update               | Range minimum queries in dynamic arrays             |
| *Segment Tree*      | Tree (Binary)              | O(log n) for query/update               | Range queries (sum, min, max) in dynamic arrays     |
| *Skip List*                   | Probabilistic Linked Structure | O(log n) expected                      | Alternative to balanced trees for ordered lists |
| *Splay Tree*                  | Self-adjusting Binary Search Tree | O(log n) amortised for all operations | Good for caches and frequently accessed elements |
| *Treap*                       | Randomised Binary Search Tree | O(log n) expected                      | Balancing BSTs while keeping operations simple and efficient |
| *Trie (Prefix Tree)*          | Tree for Strings             | O(m) (m = length of word)               | Fast string search, auto-completion, dictionary implementations |

#### Big-O

Big-O notation is a mathematical representation used to describe the efficiency of an algorithm, specifically how its runtime or space requirements grow as the size of the input increases. It provides an upper bound on the growth rate of the algorithm's time complexity, allowing for the comparison of algorithms in terms of their worst-case performance. Big-O notation is often used to characterise the asymptotic behaviour of an algorithm in terms of the input size `n`. For example, an algorithm with a time complexity of `O(n)` indicates that the running time increases linearly with the input size, while `O(n^2)` suggests that the running time increases quadratically as the input size grows.

Common time complexities include `O(1)` for constant time algorithms, where the runtime is unaffected by the input size, `O(log n)` for logarithmic time algorithms, which are typically found in divide-and-conquer algorithms, and `O(n log n)`, which is often seen in efficient sorting algorithms like mergesort. On the other hand, `O(n^2)` is frequently associated with algorithms that involve nested loops, such as bubble sort. Understanding Big-O notation helps developers choose the most efficient algorithm for a given problem and predict how the algorithm will scale with larger inputs.



