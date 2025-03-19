
## Implementation Example: Red-Black Tree

The point of this folder is to provide an opportunity to recognise and *compare different
implementations* of the *same algorithm*, in this case across multiple programming languages.
By examining these implementations, you may notice subtle variations--not only in syntax
and structure due to language-specific paradigms, but also in certain aspects of the
algorithm's behavior. Good documentation might therefore be of help for the programmer.

For example, in the case of a red-black tree, the core algorithm does not explicitly
dictate every detail of its implementation. While it enforces properties such as balancing
rules and rotations, certain choices--such as whether an insertion operation should overwrite
an existing entry with the same key or preserve both--are left ambiguous. Different
implementations may handle such cases differently, either by convention or due to
language-specific data structure constraints.

This variability highlights an important aspect of algorithm design: even when working
from a well-defined pseudo-code description, there is room for interpretation in how
edge cases, efficiency optimizations, and data handling are approached.

The pseudo-code for a red-black tree typically defines key operations such as insertion,
deletion, rotations, and rebalancing. However, specific implementations may introduce
additional logic to handle duplicate keys, enforce ordering constraints, or optimize
performance in ways that are not explicitly covered in the abstract algorithm.

By studying and comparing these implementations, you can develop a deeper understanding
of both the algorithm itself and the impact of different programming paradigms on its realization.


### Inserting an Item

In most conventional implementations of a red-black tree (as with other self-balancing binary search trees),
inserting a new node with an existing key usually replaces the previous entry rather than preserving both.
This follows from the general property of binary search trees (BSTs), where each node has a unique key, and
updates are handled by replacing the value associated with that key rather than storing duplicates. Some
variants allow duplicate keys, but this is not the standard behavior.


#### Pseudo-code for Red-Black Tree Insertion

This assumes the tree maintains the standard red-black properties:
1. Each node is either red or black.
2. The root is always black.
3. Red nodes cannot have red children (no two consecutive red nodes).
4. Every path from a node to its descendant NULL nodes must have the same number of black nodes (black-height property).

```plaintext
INSERT(T, z):
    y ← NIL  // Track parent of x
    x ← T.root
    
    // Find the correct insertion position
    while x ≠ NIL do:
        y ← x
        if z.key < x.key then
            x ← x.left
        else if z.key > x.key then
            x ← x.right
        else
            x.value ← z.value  // Update value if key exists
            return  // No need to insert new node

    z.parent ← y
    if y = NIL then
        T.root ← z  // Tree was empty
    else if z.key < y.key then
        y.left ← z
    else
        y.right ← z

    z.left ← NIL
    z.right ← NIL
    z.color ← RED  // New nodes are always red

    INSERT_FIXUP(T, z)  // Restore red-black properties
```


#### Fixing Red-Black Properties After Insertion

Since inserting a new node as red may violate the red-black properties, the tree needs
to be restructured using rotations and recoloring.

```plaintext
INSERT_FIXUP(T, z):
    while z.parent.color = RED do:
        if z.parent = z.parent.parent.left then
            y ← z.parent.parent.right  // Uncle node
            if y.color = RED then  // Case 1: Recolor
                z.parent.color ← BLACK
                y.color ← BLACK
                z.parent.parent.color ← RED
                z ← z.parent.parent
            else
                if z = z.parent.right then  // Case 2: Left-rotation needed
                    z ← z.parent
                    LEFT-ROTATE(T, z)
                z.parent.color ← BLACK  // Case 3: Right-rotation needed
                z.parent.parent.color ← RED
                RIGHT-ROTATE(T, z.parent.parent)
        else
            (same as above, but swap "left" and "right")

    T.root.color ← BLACK
```


This insertion algorithm ensures that:
- If a key already exists, its value is updated instead of inserting a duplicate node.
- The new node is always added as red and then balanced using INSERT_FIXUP().
- The tree remains balanced after insertion using rotations and recoloring.


### Rotations in Red-Black Trees

Rotations are fundamental to maintaining balance in red-black trees, as well as in
other self-balancing trees like AVL trees. They serve to preserve the binary search
tree (BST) ordering while adjusting the structure to maintain balance constraints.

While there is little room for variation in the mechanics of the rotations (since
they must maintain the ordering property of BSTs), there can be small implementation
differences based on how pointers or references are managed in different programming
languages. However, the outcome of rotations is generally consistent--they restore
balance without changing the in-order traversal of the tree.



#### Types of Rotations

There are two basic types of rotations:
1. Left Rotation (Left-rotate)
2. Right Rotation (Right-rotate)

These are used in different configurations to rebalance the tree after an insertion
or deletion that disrupts the red-black properties.


__1. Left Rotation__

A left rotation is performed around a node x when its right child y needs to move up,
making x its left child.


```plaintext
   Before rotation:           After rotation:
       x                          y
      / \                        / \
     α   y        →             x   γ
        / \                    / \
       β   γ                  α   β
```

#### Pseudo-code for Left Rotation

```plaintext
LEFT-ROTATE(T, x):
    y ← x.right  // Set y as the right child of x
    x.right ← y.left  // Move y’s left subtree to x’s right subtree

    if y.left ≠ NIL then
        y.left.parent ← x  // Update parent reference

    y.parent ← x.parent  // Link y to x's old parent

    if x.parent = NIL then
        T.root ← y  // If x was root, now y is root
    else if x = x.parent.left then
        x.parent.left ← y  // x was a left child
    else
        x.parent.right ← y  // x was a right child

    y.left ← x  // Move x to be left child of y
    x.parent ← y
```

Purpose of Left Rotation: A left rotation is applied when balancing violations occur
on the right side of the tree. It moves the heavier right subtree upward, reducing
height differences.



__2. Right Rotation__

A right rotation is the mirror image of a left rotation. It is used when the left
child y of a node x should move up.


```plaintext
   Before rotation:           After rotation:
       x                          y
      / \                        / \
     y   γ        →             α   x
    / \                            / \
   α   β                          β   γ
```


#### Pseudo-code for Right Rotation

```plainttext
RIGHT-ROTATE(T, x):
    y ← x.left  // Set y as the left child of x
    x.left ← y.right  // Move y’s right subtree to x’s left subtree

    if y.right ≠ NIL then
        y.right.parent ← x  // Update parent reference

    y.parent ← x.parent  // Link y to x’s old parent

    if x.parent = NIL then
        T.root ← y  // If x was root, now y is root
    else if x = x.parent.right then
        x.parent.right ← y  // x was a right child
    else
        x.parent.left ← y  // x was a left child

    y.right ← x  // Move x to be right child of y
    x.parent ← y
```

Purpose of Right Rotation: A right rotation is used when balancing violations occur on the left
side of the tree. It shifts the left-heavy subtree upward to balance the height.



#### Combining Rotations: Fixing Red-Black Violations

While single left or right rotations are sufficient for some cases, certain tree structures
require double rotations (a combination of left and right).

1. Left-Right Case (Left Rotation followed by Right Rotation)
- Occurs when the node is the right child of a left child.
- Solution: Left Rotate the child, then Right Rotate the parent.

2. Right-Left Case (Right Rotation followed by Left Rotation)
- Occurs when the node is the left child of a right child.
- Solution: Right Rotate the child, then Left Rotate the parent.

These combinations arise because the tree needs direct parent-child relationships for simple
rotations to work. If a node is in a zig-zag pattern, a double rotation is needed.


#### Summary
- Left rotation moves a right-heavy node down to balance the tree.
- Right rotation moves a left-heavy node down to restore balance.
- Double rotations (Left-Right or Right-Left) fix zig-zag patterns.
- Different implementations may vary in pointer handling, recursion,
  and data structure details, but the fundamental behavior remains the same.
