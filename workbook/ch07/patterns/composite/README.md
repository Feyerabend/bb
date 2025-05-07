
## Composite Pattern

The Composite pattern is used when you need to represent a hierarchy of objects
where both individual objects (leaves) and groups of objects (composites) are
treated the same way. 

- *Component*: An abstract class/interface that defines the common operations for
  both simple (leaf) and composite objects.

- *Leaf*: Represents individual objects in the composition (they have no children).

- *Composite*: Stores child components (either leaves or other composites) and
  implements operations defined in the component.

The key idea is that a *Composite* can contain other *Composites* or *Leaves*,
forming a recursive tree structure.


### Why Use the Composite Pattern?

1. *Uniform Treatment*: Clients don’t need to differentiate between a single object
   and a group of objects.
2. *Simplifies Client Code*: The same operations can be applied over the whole structure.
3. *Flexible Hierarchies*: New component types can be added without breaking existing code.
4. *Recursive Behavior*: Operations can be applied recursively over the entire tree.


### When to Use the Composite Pattern?

- You need to represent part-whole hierarchies (e.g., file systems, GUI components,
  organisation structures).
- You want clients to ignore differences between compositions and individual objects.
- You need to perform operations recursively over a tree structure.


### How It Works (Structure)

1. *Component (Abstract Class/Interface)*
   - Declares common operations (`operation()`) and may include methods for managing
     child components.

2. *Leaf (Implements Component)*
   - Represents an end object (no children).
   - Implements `operation()` for itself.

3. *Composite (Implements Component)*
   - Stores child components (can be leaves or other composites).
   - Implements `operation()` by delegating to child components.
   - Provides methods to add/remove children.


### Example Use Cases

1. *File System*  
   - *Component*: `FileSystemElement` (with `display()` method).  
   - *Leaf*: `File`.  
   - *Composite*: `Directory` (contains multiple files/directories).  
   - Calling `display()` on a `Directory` recursively calls it on all children.

2. *GUI Widgets*  
   - *Component*: `Widget` (with `render()`).  
   - *Leaf*: `Button`, `TextBox`.  
   - *Composite*: `Panel` (contains multiple widgets).  
   - `render()` on `Panel` renders all child widgets.

3. *Organization Structure*  
   - *Component*: `Employee`.  
   - *Leaf*: `Developer`, `Manager`.  
   - *Composite*: `Team` (contains multiple employees).  
   - Calculating total salary recursively sums up all team members.



### Pros & Cons

 *Pros*  
- Simplifies client code (treats composites and leaves uniformly).  
- Supports recursive operations.  
- Makes it easy to add new component types.  

 *Cons*  
- Can make the design overly general (not all components should support child management).  
- Harder to restrict certain operations on leaves vs. composites.  


### Example in Pseudocode

```java
interface Graphic {
    void draw();
}

class Circle implements Graphic {
    void draw() { /* .. draw circle .. */ }
}

class Group implements Graphic {
    List<Graphic> children = new ArrayList<>();

    void add(Graphic g) { children.add(g); }
    void remove(Graphic g) { children.remove(g); }

    void draw() {
        for (Graphic child : children) {
            child.draw(); // delegate to children
        }
    }
}
```

A `Group` can contain `Circle` objects or other `Group` objects, forming a tree.


### Composite in General

The Composite pattern is powerful for modeling hierarchical structures where individual
and grouped objects need the same interface. It promotes *recursive composition* and
*transparent handling* of objects, making it ideal for systems like file explorers,
UI frameworks, and organisational structures.

A very similar structure occurs in the included graphical sample.

The base structure that defines common operations for both leaf nodes and composites:
- Contains function pointers for rendering and cleanup
- Both individual shapes and groups share this interface

Leaf Classes (Circle, Rectangle, Triangle):
- Concrete shapes that can be rendered
- Each implements its own rendering behavior

Composite Class (CompositeGroup):
- Contains and manages a collection of child components
- Children can be individual shapes or other composites
- Rendering a composite renders all its children

Some pattern features demonstrated:
- *Uniform Treatment*: Both individual shapes and groups of shapes are treated
  through the same interface (`GraphicComponent`)
- *Recursive Composition*: The scene contains shapes and also a house, which itself
  is composed of shapes
- *Polymorphic Behaviour*: Each component defines its own rendering logic, but
  can be used interchangeably

The program creates a simple scene with:
- Individual shapes (circle, rectangle, triangle)
- A composite "house" made of multiple shapes
- A composite "scene" that contains both individual shapes and the house composite
