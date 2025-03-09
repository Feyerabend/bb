
## Data Structures Overview

No one can realistically learn or master every possible variant of abstract data structures, as the field
is vast and continuously evolving. However, developing the ability to recognize when and why certain data
structures are useful can be highly valuable. Gaining an intuition for selecting the right structure in
different scenarios--whether for efficiency, simplicity, or maintainability--can make problem-solving more
effective. Additionally, with the advent of large language models (LLMs), you can leverage AI to brainstorm
and explore different data structure choices, comparing their strengths and trade-offs in various contexts.
This can help refine your understanding and decision-making process when working with real-world applications.


### 1. AVL (Adelson-Velsky and Landis Tree)
- *Type*: Self-balancing Binary Search Tree (BST)
- *Explanation*: AVL trees maintain a balance condition by ensuring that the height difference between the left and right subtrees of any node is at most 1. After every insertion or deletion, the tree performs rotations to maintain this balance.
- *Use Case*: Efficient searching, insertion, and deletion in O(log n) time. Useful in scenarios where frequent insertions and deletions occur, and balanced search time is required.
- *Operations*: Search, insert, delete, rotate.


### 2. Binary Tree
- *Type*: Hierarchical data structure
- *Explanation*: A binary tree is a tree where each node has at most two children, typically referred to as the left and right child. It does not necessarily need to be balanced or sorted.
- *Use Case*: Representing hierarchical structures, such as file systems or organisational charts, or as the foundation for other specialised trees (like BST or heap).
- *Operations*: Traversals (in-order, pre-order, post-order), search, insert, delete.


### 3. Bloom Filter
- *Type*: Probabilistic Data Structure
- *Explanation*: A Bloom Filter is a space-efficient, probabilistic data structure used to test whether an element is a member of a set. It uses multiple hash functions to map elements to positions in a bit array. If all bits at the hashed positions are set to 1, the element might be in the set; otherwise, it is definitely not in the set. However, it can produce false positives, meaning it may incorrectly indicate that an element is in the set, but it will never produce false negatives.
- *Use Case*: Bloom Filters are used in scenarios where space is a concern and false positives are acceptable, such as checking membership in large sets, web caching, spell-checking, and network protocols (e.g., in databases or blockchain systems).
- *Operations*: Add, check (membership query).


### 4. Disjoint Set (Union-Find)
- *Type*: Data structure for partitioning a set into disjoint subsets
- *Explanation*: Disjoint Set, or Union-Find, is used to keep track of a collection of disjoint sets and provides efficient methods for union and find operations. It uses techniques like path compression and union by rank to speed up these operations.
- *Use Case*: Used in algorithms like Kruskal’s algorithm for finding the minimum spanning tree, and for dynamic connectivity problems in networks.
- *Operations*: `find`, `union`, `connected`.


### 5. Double Linked List
- *Type*: Linked List
- *Explanation*: A doubly linked list is a type of linked list where each node contains a reference (or link) to both the next and previous node. This allows traversal in both directions.
- *Use Case*: Used when frequent insertion and deletion at both ends are required, such as in a browser history or an undo/redo system.
- *Operations*: Insert, delete, traverse forwards/backwards.


### 6. Hash Table
- *Type*: Data structure for key-value pairs
- *Explanation*: A hash table stores key-value pairs and uses a hash function to compute an index into an array of buckets or slots, from which the desired value can be found. Collisions are resolved using methods like chaining or open addressing.
- *Use Case*: Fast lookups, insertions, and deletions. Common in implementing associative arrays, sets, and caches.
- *Operations*: Insert, delete, search.


### 7. Heap
- *Type*: Binary Tree-based data structure
- *Explanation*: A heap is a special tree-based structure that satisfies the heap property: in a max-heap, the value of each node is greater than or equal to its children, and in a min-heap, the value is less than or equal to its children.
- *Use Case*: Used in priority queues, heap sort, and for efficient access to the maximum or minimum element.
- *Operations*: Insert, delete (extract), peek.


### 8. KD-Tree (K-Dimensional Tree)
- *Type*: Binary tree for multidimensional data
- *Explanation*: A k-d tree is a space-partitioning data structure for organising points in a k-dimensional space. It is used to store points and efficiently support range and nearest neighbour queries.
- *Use Case*: Used in multidimensional search spaces like in computer graphics, machine learning (k-nearest neighbours), and spatial databases.
- *Operations*: Insert, query (range search, nearest neighbour).


### 9. Kruskal’s Algorithm
- *Type*: Algorithm for Minimum Spanning Tree
- *Explanation*: Kruskal’s algorithm finds the minimum spanning tree of a graph. It sorts the edges of the graph in increasing order and adds edges to the spanning tree, ensuring no cycles form. Disjoint Set is typically used for cycle detection.
- *Use Case*: Used in network design, such as to find the minimum cable length required to connect a set of computers, or in cluster analysis.
- *Operations*: Sort edges, union-find.


### 10. Linked List
- *Type*: Linear data structure
- *Explanation*: A linked list is a collection of nodes where each node contains data and a reference to the next node in the sequence. It can be singly or doubly linked.
- *Use Case*: Suitable for dynamic data storage where elements are frequently inserted and removed, like in memory management and as an alternative to arrays when memory allocation is a concern.
- *Operations*: Insert, delete, traverse, search.


### 11. Priority Queue
- *Type*: Queue with priority
- *Explanation*: A priority queue is a data structure where each element is associated with a priority. Elements with higher priority are dequeued before elements with lower priority. Typically implemented using a heap.
- *Use Case*: Scheduling tasks with priorities, Dijkstra’s algorithm, Huffman coding.
- *Operations*: Insert, extract minimum/maximum, peek.


### 12. Queue
- *Type*: Linear data structure (FIFO)
- *Explanation*: A queue is a collection where elements are added at the rear (enqueue) and removed from the front (dequeue), following the First In, First Out (FIFO) principle.
- *Use Case*: Used in situations like task scheduling, breadth-first search, and buffering.
- *Operations*: Enqueue, dequeue, peek.


### 13. RMQ (Range Minimum Query)
- *Type*: Query problem with a data structure
- *Explanation*: RMQ is a problem where given an array, you need to find the minimum element in a subarray for any given range. Segment trees, sparse tables, or binary indexed trees can be used to solve this problem efficiently.
- *Use Case*: Used in problems where range queries for minimum/maximum are frequent, such as in image processing, signal processing, or dynamic programming.
- *Operations*: Query, update.


### 14. Segment Tree
- *Type*: Binary tree for range queries
- *Explanation*: A segment tree is a binary tree used to store intervals or segments. It allows querying and updating the values of array segments in O(log n) time.
- *Use Case*: Used for problems involving range queries like sum, minimum, maximum, or GCD, especially when the array is large and requires frequent updates.
- *Operations*: Build, query, update.


### Summary Table of Data Structures

| Data Structure       | Type                       | Time Complexity for Search/Insert/Delete | Common Use Cases                                     |
|-|-|--|-|
| *AVL Tree*          | Balanced Binary Tree       | O(log n) for all operations             | Efficient search, insertion, deletion in dynamic datasets |
| *Binary Tree*       | Tree                       | O(n) for search, O(log n) for insert/delete | Hierarchical data representation                    |
| *Bloom Filter*      | Probabilistic Data Structure  | O(k) for check (where k is the number of hash functions) and O(k) for add (where k is the number of hash functions) | Space-efficient membership testing with false positives  |
| *Disjoint Set*      | Union-Find                 | O(log n) with path compression          | Dynamic connectivity problems, Kruskal’s algorithm   |
| *Double Linked List*| Linked List                | O(1) for insert/delete at both ends     | Browser history, undo/redo operations                |
| *Hash Table*        | Hashing                    | O(1) average case, O(n) worst case      | Fast lookup, insertion, caching                      |
| *Heap*              | Tree (Binary)              | O(log n) for insert/delete, O(1) for peek | Priority Queue, Heap Sort                            |
| *KD-Tree*           | Binary Tree                | O(log n) for search, O(log n) for nearest neighbour | Spatial data queries (e.g., nearest neighbours)       |
| *Kruskal’s Algorithm*| Algorithm                  | O(E log E) (where E is the number of edges) | Minimum Spanning Tree, network design               |
| *Linked List*       | Linear Data Structure      | O(n) for search, O(1) for insert/delete | Dynamic data storage, memory management             |
| *Priority Queue*    | Queue (Heap-based)         | O(log n) for all operations             | Task scheduling, Huffman coding                     |
| *Queue*             | Linear Data Structure (FIFO)| O(1) for enqueue/dequeue                | Task scheduling, breadth-first search               |
| *RMQ*               | Query Problem              | O(log n) for query/update               | Range minimum queries in dynamic arrays             |
| *Segment Tree*      | Tree (Binary)              | O(log n) for query/update               | Range queries (sum, min, max) in dynamic arrays     |

Big-O notation is a mathematical representation used to describe the efficiency of an algorithm, specifically how its runtime or space requirements grow as the size of the input increases. It provides an upper bound on the growth rate of the algorithm's time complexity, allowing for the comparison of algorithms in terms of their worst-case performance. Big-O notation is often used to characterize the asymptotic behavior of an algorithm in terms of the input size `n`. For example, an algorithm with a time complexity of `O(n)` indicates that the running time increases linearly with the input size, while `O(n^2)` suggests that the running time increases quadratically as the input size grows.

Common time complexities include `O(1)` for constant time algorithms, where the runtime is unaffected by the input size, `O(log n)` for logarithmic time algorithms, which are typically found in divide-and-conquer algorithms, and `O(n log n)`, which is often seen in efficient sorting algorithms like mergesort. On the other hand, `O(n^2)` is frequently associated with algorithms that involve nested loops, such as bubble sort. Understanding Big-O notation helps developers choose the most efficient algorithm for a given problem and predict how the algorithm will scale with larger inputs.
