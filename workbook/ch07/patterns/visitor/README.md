
## Visitor Pattern

The Visitor Pattern is a behavioral design pattern that lets you add new operations to existing
object structures without modifying the structures themselves. It is particularly useful when
you have a stable class hierarchy but need to perform operations that are subject to frequent change.

Core Principles
1. Separation of Concerns: The object structure (e.g., a composite of shapes or AST nodes) stays
   stable; new behavior is encapsulated in visitor classes.
2. Double Dispatch: The pattern uses two polymorphic calls—first to the accept() method of the
   element, then to the visit() method of the visitor—which lets you dynamically dispatch both
   on the object and the operation.
3. Extensibility: New operations can be added by creating new visitors, without changing the
   element classes.

Basic Structure
- Element Interface: Has an accept(visitor) method.
- Concrete Elements: Implement accept() and call back visitor.visit(this).
- Visitor Interface: Declares visit() methods for each concrete element.
- Concrete Visitors: Implement operations for each element.


```mermaid
classDiagram
    %% ====== Visitor Pattern ======
    class Visitor {
        <<interface>>
        +visitElementA(ElementA el)
        +visitElementB(ElementB el)
    }

    class Element {
        <<interface>>
        +accept(Visitor v)
    }

    class ConcreteVisitor {
        +visitElementA(ElementA el)
        +visitElementB(ElementB el)
    }

    class ElementA {
        +accept(Visitor v)
    }

    class ElementB {
        +accept(Visitor v)
    }

    Visitor <|-- ConcreteVisitor : Implements
    Element <|-- ElementA : Implements
    Element <|-- ElementB : Implements
    ElementA --> Visitor : Accepts
    ElementB --> Visitor : Accepts
```

```mermaid
sequenceDiagram
    participant Client
    participant Visitor as ConcreteVisitor
    participant ElementA
    participant ElementB

    Client ->> Visitor: Create Visitor
    Client ->> ElementA: accept(Visitor)
    ElementA ->> Visitor: visitElementA(this)
    Visitor -->> ElementA: Perform operation on ElementA
    ElementA -->> Client: Return result (if any)

    Client ->> ElementB: accept(Visitor)
    ElementB ->> Visitor: visitElementB(this)
    Visitor -->> ElementB: Perform operation on ElementB
    ElementB -->> Client: Return result (if any)
```



### Example in C

C doesn’t support OOP directly, so we simulate with function pointers and structs.

```c
#include <stdio.h>

struct Circle;
struct Rectangle;
struct ShapeVisitor;

// Shape interface
typedef struct Shape {
    void (*accept)(struct Shape* self, struct ShapeVisitor* visitor);
} Shape;

// Visitor interface
typedef struct ShapeVisitor {
    void (*visit_circle)(struct ShapeVisitor*, struct Circle*);
    void (*visit_rectangle)(struct ShapeVisitor*, struct Rectangle*);
} ShapeVisitor;

// Circle
typedef struct Circle {
    Shape base;
    int radius;
} Circle;

void circle_accept(Shape* self, ShapeVisitor* visitor) {
    visitor->visit_circle(visitor, (Circle*)self);
}

// Rectangle
typedef struct Rectangle {
    Shape base;
    int width, height;
} Rectangle;

void rectangle_accept(Shape* self, ShapeVisitor* visitor) {
    visitor->visit_rectangle(visitor, (Rectangle*)self);
}

// PrintVisitor
void visit_circle_print(ShapeVisitor* self, Circle* c) {
    printf("Circle with radius %d\n", c->radius);
}

void visit_rectangle_print(ShapeVisitor* self, Rectangle* r) {
    printf("Rectangle %dx%d\n", r->width, r->height);
}

ShapeVisitor PrintVisitor = {
    .visit_circle = visit_circle_print,
    .visit_rectangle = visit_rectangle_print
};

// Main
int main() {
    Circle c = { .base.accept = circle_accept, .radius = 5 };
    Rectangle r = { .base.accept = rectangle_accept, .width = 3, .height = 4 };

    c.base.accept((Shape*)&c, &PrintVisitor);
    r.base.accept((Shape*)&r, &PrintVisitor);
}
```



### Example in Python

Python has dynamic typing, so it’s more concise:

```python
class ShapeVisitor:
    def visit_circle(self, circle): pass
    def visit_rectangle(self, rectangle): pass

class Shape:
    def accept(self, visitor): pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def accept(self, visitor):
        visitor.visit_circle(self)

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def accept(self, visitor):
        visitor.visit_rectangle(self)

class PrintVisitor(ShapeVisitor):
    def visit_circle(self, circle):
        print(f"Circle with radius {circle.radius}")
    def visit_rectangle(self, rectangle):
        print(f"Rectangle {rectangle.width}x{rectangle.height}")

# Example usage
shapes = [Circle(5), Rectangle(3, 4)]
visitor = PrintVisitor()
for shape in shapes:
    shape.accept(visitor)
```




