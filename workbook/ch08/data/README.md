
## Overview: Data, Data Structures, Abstract Data Types and Algorithms

No one can realistically learn or master every possible variant of abstract data structures, as the field
is vast and continuously evolving. However, developing the ability to recognise when and why certain data
structures are useful can be highly valuable. Gaining an intuition for selecting the right structure in
different scenarios--whether for efficiency, simplicity, or maintainability--can make problem-solving more
effective. Additionally, with the advent of large language models (LLMs), you can leverage AI to brainstorm
and explore different data structure choices, comparing their strengths and trade-offs in various contexts.
This can help refine your understanding and decision-making process when working with real-world applications.

#### Data

Data refers to raw facts, numbers, characters, symbols, or other forms of unprocessed information that can be
stored and manipulated by a computer. Data on its own has no meaning until it is processed or structured in
a way that provides value. Examples of data include numbers, text, or binary values.


#### Data Structures

A data structure is a way of organising and storing data so that it can be efficiently accessed and modified.
Data structures define the relationships between data elements and provide methods for working with them.
Common examples include:
- Arrays: A fixed-size collection of elements stored in contiguous memory locations.
- Linked Lists: A sequence of nodes, where each node points to the next.
- Stacks: A last-in, first-out (LIFO) data structure.
- Queues: A first-in, first-out (FIFO) data structure.
- Trees: A hierarchical structure with nodes and edges (e.g., binary trees).
- Graphs: A collection of nodes (vertices) and connections (edges).

Data structures are fundamental for efficient problem-solving in computing.


#### Abstract Data Types

An Abstract Data Type (ADT) is a concept or logical description of how data can be used, without specifying
its implementation details. It defines a set of operations that can be performed on data but does not dictate
how these operations are implemented. ADTs provide a high-level abstraction over data structures.

For example:
- List ADT: Defines operations like insert(), delete(), and find(), but it can be implemented using arrays or linked lists.
- Stack ADT: Defines push(), pop(), and peek(), but it can be implemented using arrays or linked lists.
- Queue ADT: Defines enqueue() and dequeue(), but the implementation could be an array, a linked list, or a circular buffer.

Think of ADTs as interfaces or blueprints that describe what a data structure should do, while the actual
data structure provides the implementation.


#### Algorithms

We can also mention algorithms here. An algorithm is a step-by-step procedure or set of rules used to solve
a problem or perform a computation. Algorithms operate on data structures to process and manipulate data efficiently.
Some well-known algorithms include:
- Sorting algorithms: Bubble Sort, Merge Sort, Quick Sort.
- Searching algorithms: Binary Search, Linear Search.
- Graph algorithms: Dijkstra's Algorithm, Breadth-First Search (BFS), Depth-First Search (DFS).
- String algorithms: Knuth-Morris-Pratt (KMP) Algorithm, Rabin-Karp Algorithm.

Algorithms are evaluated based on their time complexity (how fast they run) and space complexity (how much memory they use).

Bringing It All Together
- Data is raw information (e.g., numbers, text).
- Data structures define how to organise and store data (e.g., arrays, linked lists, trees).
- Abstract data types (ADTs) describe what operations can be performed on data without specifying how they are implemented (e.g., Stack, Queue).
- Algorithms are procedures for processing data using data structures (e.g., searching, sorting).


### Scenario: Implementing a Stack

A stack is an example of an Abstract Data Type (ADT) that follows the Last-In, First-Out (LIFO) principle.


__1. Data__

Imagine we have a set of numbers that we want to process in a specific order:

```
5, 10, 15, 20
```

These are just raw data values.


__2. Abstract Data Type (Stack ADT)__

The Stack ADT defines operations like:
- push(x): Add x to the top of the stack.
- pop(): Remove and return the top element.
- peek(): View the top element without removing it.
- isEmpty(): Check if the stack is empty.

Note that the ADT does not specify how the stack is implemented-only how it should behave.


__3. Data Structures (Implementation of Stack ADT)__

To implement a stack, we can use two different data structures:
- Array-based implementation
- Uses a fixed-size array where elements are added or removed from the top.
- Efficient but has a fixed size (or needs resizing).
- Linked List-based implementation
- Uses a dynamic linked list where each node points to the next.
- More flexible but requires extra memory for pointers.

Here's an example of a linked list-based implementation of a stack in Python:

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class Stack:
    def __init__(self):
        self.top = None

    def push(self, value):
        new_node = Node(value)
        new_node.next = self.top
        self.top = new_node

    def pop(self):
        if self.top is None:
            raise IndexError("Stack is empty")
        value = self.top.value
        self.top = self.top.next
        return value

    def peek(self):
        if self.top is None:
            return None
        return self.top.value

    def is_empty(self):
        return self.top is None
```

__4. Algorithm__

Now, let's use an algorithm that operates on this data structure.
Suppose we want to reverse a sequence of numbers using a stack:

```python
stack = Stack()

# push numbers onto the stack
stack.push(5)
stack.push(10)
stack.push(15)
stack.push(20)

# pop numbers from the stack to reverse order
while not stack.is_empty():
    print(stack.pop())  
```

*Expected Output:*

```python
20
15
10
5
```

Here, the algorithm follows these steps:
1. Push each number onto the stack.
2. Pop them off in reverse order.

Summary
- Data: {5, 10, 15, 20} (raw numbers).
- Stack ADT: Defines operations like push, pop, peek, is_empty.
- Data Structure: Implemented using a linked list.
- Algorithm: Uses the stack to reverse the order of numbers.


### Listing of Arbitrary Examples

For a student of this field, understanding algorithms, data structures, and abstract data
types is highly beneficial--not necessarily to memorise every detail, but to recognise when
and why to use them. As modern programming shifts increasingly toward orchestrating systems
rather than writing everything from scratch, having a broad conceptual overview often proves
more valuable than deep memorisation of specific algorithms.

Today, many problems can be solved using existing libraries, frameworks, or even AI-assisted
coding tools. However, knowing the underlying principles allows developers to make informed
decisions, such as choosing the right data structure for performance optimisation or recognising
when a certain algorithm would be inefficient. Instead of focusing on rote learning, students
benefit more from developing algorithmic intuition--the ability to analyse problems and select
appropriate approaches based on trade-offs like time complexity, space usage, and ease of
implementation.

That said, in fields where performance and efficiency are critical, such as embedded systems,
real-time computing, or advanced algorithmic problem-solving, a deeper understanding remains
essential. Even in higher-level development, knowing the fundamentals can make debugging,
optimising, or extending code much more effective.

Ultimately, the key is balance: the focus should be on developing a broad understanding of
algorithms and data structures while diving deeper when necessary. This approach ensures the
ability to apply the right tools effectively, rather than merely recalling definitions.
Here are some starting points to explore.


#### AVL (Adelson-Velsky and Landis Tree)
- *Type*: Self-balancing Binary Search Tree (BST)
- *Explanation*: AVL trees maintain a balance condition by ensuring that the height difference between the left and right subtrees of any node is at most 1. After every insertion or deletion, the tree performs rotations to maintain this balance.
- *Use Case*: Efficient searching, insertion, and deletion in O(log n) time. Useful in scenarios where frequent insertions and deletions occur, and balanced search time is required.
- *Operations*: Search, insert, delete, rotate.


#### Binary Tree
- *Type*: Hierarchical data structure
- *Explanation*: A binary tree is a tree where each node has at most two children, typically referred to as the left and right child. It does not necessarily need to be balanced or sorted.
- *Use Case*: Representing hierarchical structures, such as file systems or organisational charts, or as the foundation for other specialised trees (like BST or heap).
- *Operations*: Traversals (in-order, pre-order, post-order), search, insert, delete.


#### Bloom Filter
- *Type*: Probabilistic Data Structure
- *Explanation*: A Bloom Filter is a space-efficient, probabilistic data structure used to test whether an element is a member of a set. It uses multiple hash functions to map elements to positions in a bit array. If all bits at the hashed positions are set to 1, the element might be in the set; otherwise, it is definitely not in the set. However, it can produce false positives, meaning it may incorrectly indicate that an element is in the set, but it will never produce false negatives.
- *Use Case*: Bloom Filters are used in scenarios where space is a concern and false positives are acceptable, such as checking membership in large sets, web caching, spell-checking, and network protocols (e.g., in databases or blockchain systems).
- *Operations*: Add, check (membership query).


#### Dijkstra's Algorithm




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


#### Fenwick Tree
..

#### Fibonacci Heap
- *Type*: Advanced priority queue, heap-based
- *Explanation*: A Fibonacci heap is a collection of heap-ordered trees with better amortized time complexity for operations like decrease-key compared to binary or binomial heaps. It supports quick merging and is particularly efficient for graph algorithms.
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


#### RMQ (Range Minimum Query)
- *Type*: Query problem with a data structure
- *Explanation*: RMQ is a problem where given an array, you need to find the minimum element in a subarray for any given range. Segment trees, sparse tables, or binary indexed trees can be used to solve this problem efficiently.
- *Use Case*: Used in problems where range queries for minimum/maximum are frequent, such as in image processing, signal processing, or dynamic programming.
- *Operations*: Query, update.


#### Segment Tree
- *Type*: Binary tree for range queries
- *Explanation*: A segment tree is a binary tree used to store intervals or segments. It allows querying and updating the values of array segments in O(log n) time.
- *Use Case*: Used for problems involving range queries like sum, minimum, maximum, or GCD, especially when the array is large and requires frequent updates.
- *Operations*: Build, query, update.


#### Skip List
..


#### Splay Tree
- *Type*: Self-adjusting binary search tree
- *Explanation*: A splay tree performs a "splay" operation, moving accessed elements to the root using rotations, which helps keep frequently accessed elements near the top.
- *Use Case*: Suitable for applications where recently accessed elements are likely to be accessed again, such as caches and garbage collection.
- *Operations*: Insert, delete, search, splay (self-adjustment).


#### Tread
..


#### Trie
..


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



---

Splay Tree
Tread
Dijkstra Algo
Fenwick Tree
Skip List

