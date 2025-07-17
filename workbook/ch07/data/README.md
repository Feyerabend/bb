
## Overview: Data, Data Structures, Abstract Data Types and Algorithms

No one can realistically learn or master every possible variant of abstract data structures, as the field
is vast and continuously evolving. However, developing the ability to recognise *when* and *why* certain data
structures are useful can be highly valuable. Gaining an intuition for selecting the right structure in
different scenarios--whether for efficiency, for an optimal solution, simplicity, or maintainability--can
make problem-solving more effective. Additionally, with the advent of large language models (LLMs), you
can leverage AI to brainstorm and explore different data structure choices, comparing their strengths
and trade-offs in various contexts. This can help refine your understanding and decision-making process
when working with real-world applications.

This section dives into data structures, algorithms, and abstract data types with a fresh twist. It skips the
usual beginner's intro, assuming you're already comfortable with the basics. Instead, it zooms in on giving
you a *big-picture view* of the wide variety of code out there--stuff built on years of computer science
breakthroughs. The approach here is "implementation first," (or "code first") meaning you'll jump straight into
real code from the get-go. It's hands-on: you wrestle with the code itself, then strip it down--maybe into
you preferred pseudo-code--to really get what's going on under the hood. After that, you'll see how it all fits
into real life, whether you're crunching numbers or wrangling strings. Starting with the code like this lets you
piece together a solid understanding of how these core ideas play out in practice.

Your task is not just about memorising definitions or implementing textbook versions of data structures and
algorithms. Instead, it's about building a practical and adaptable understanding of them. You'll begin by
exploring abstract data types (ADTs) and algorithms that interest you, but rather than stopping at a theoretical
level, you will engage with them actively--modifying, testing, and extending them in meaningful ways.

This means collecting implementations from various sources, tweaking them to fit different use cases, and
analysing their efficiency in real-world scenarios. You might experiment with how a certain data structure
performs under different constraints, refactor an algorithm to improve its readability or performance, or
generalise a solution to make it more flexible across multiple problem domains.

Beyond this, a key part of the process is exploring alternatives. Many problems can be approached using
multiple data structures or algorithms, each with its own trade-offs. For example, is a hash table always
the best choice for fast lookups, or would a self-balancing tree sometimes be a better fit? Would a brute-force
approach suffice for small datasets, or is an optimised dynamic programming solution worth the effort? By
brainstorming around these questions and comparing different implementations, you'll develop a deeper intuition
for when to apply each technique.

Finally, since problem-solving rarely happens in isolation, a crucial aspect of this task is understanding why
a particular solution works well in a given context. This mindset of continuous refinement--writing test cases,
debugging edge cases, and modifying algorithms for specific needs--will strengthen not just your coding skills
but also your ability to think critically about computational problems.


#### Data

Data refers to raw facts, numbers, characters, symbols, or other forms of unprocessed information that can be
stored and manipulated by a computer. Data on its own has no meaning until it is processed or structured in
a way that provides value. Examples of data include numbers, text, or binary values. This is the lesson we
have learned from Chapter 1 on fundamentals.


#### Data Structures

A data structure is a way of organising and storing data so that it can be efficiently accessed and modified.
Data structures define the relationships between data elements and provide methods for working with them.
Common examples include:
- *Arrays:* A fixed-size collection of elements stored in contiguous memory locations.
- *Linked Lists:* A sequence of nodes, where each node points to the next.
- *Stacks:* A last-in, first-out (LIFO) data structure.
- *Queues:* A first-in, first-out (FIFO) data structure.
- *Trees:* A hierarchical structure with nodes and edges (e.g., binary trees).
- *Graphs:* A collection of nodes (vertices) and connections (edges).

Data structures are fundamental for efficient problem-solving in computing.


#### Abstract Data Types

An Abstract Data Type (ADT) is a concept or logical description of how data can be used, without specifying
its implementation details. It defines a set of operations that can be performed on data but does not dictate
how these operations are implemented. ADTs provide a high-level abstraction over data structures.

For example:
- *List ADT:* Defines operations like `insert()`, `delete()`, and `find()`, but it
  can be implemented using arrays or linked lists.
- *Stack ADT:* Defines `push()`, `pop()`, and `peek()`, but it can be implemented
  using arrays or linked lists.
- *Queue ADT:* Defines `enqueue()` and `dequeue()`, but the implementation could be
  an array, a linked list, or a circular buffer.

Think of ADTs as interfaces or blueprints that describe what a data structure should do, while the actual
data structure provides the implementation.


#### Algorithms

We can also mention algorithms here. An algorithm is a step-by-step procedure or set of rules used to solve
a problem or perform a computation. Algorithms operate on data structures to process and manipulate data efficiently.
Some well-known algorithms include:
- Sorting algorithms: *Bubble Sort*, *Merge Sort*, *Quick Sort*.
- Searching algorithms: *Binary Search*, *Linear Search*.
- Graph algorithms: *Dijkstra's Algorithm*, *Breadth-First Search* (BFS), *Depth-First Search* (DFS).
- String algorithms: *Knuth-Morris-Pratt* (KMP) Algorithm, *Rabin-Karp* Algorithm.

Algorithms are evaluated based on their time complexity (how fast they run) and space complexity (how much memory they use).

Bringing It All Together
- Data is raw information (such as numbers or text).
- Data structures define how to organise and store data (e.g. arrays, linked lists, trees).
- Abstract data types (ADTs) describe what operations can be performed on data without specifying how they are
  implemented (e.g. Stack, Queue).
- Algorithms are procedures for processing data using data structures (e.g. searching, sorting).


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
- `push(x)`: Add x to the top of the stack.
- `pop()`: Remove and return the top element.
- `peek()`: View the top element without removing it.
- `isEmpty()`: Check if the stack is empty.

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
- Data: `{5, 10, 15, 20}` (raw numbers).
- Stack ADT: Defines operations like `push`, `pop`, `peek`, `is_empty`.
- Data Structure: Implemented using a linked list.
- Algorithm: Uses the stack to reverse the order of numbers.

