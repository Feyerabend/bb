
## Python OO: Overview

### 1. *Classes and Objects*
- *Class*: A blueprint or template for creating objects. It defines the properties
  (attributes) and behaviors (methods) that the objects created from the class will have.
- *Object*: An instance of a class. It represents a specific entity based on the class definition.

### 2. *Attributes and Methods*
- *Attributes*: Variables that belong to an object or class. They represent the state
  or data of the object.
- *Methods*: Functions that belong to an object or class. They define the behavior
  or actions that the object can perform.

### 3. *Encapsulation*
- The bundling of data (attributes) and methods that operate on the data into a single unit (class).
- Access control: Using private, protected, and public access modifiers to restrict access
  to certain attributes or methods.

### 4. *Inheritance*
- A mechanism where a new class (child class) derives properties and behaviors from an existing
  class (parent class).
- Promotes code reuse and establishes a hierarchical relationship between classes.

### 5. *Polymorphism*
- The ability of different classes to be treated as instances of the same class through a
  common interface.
- Includes method overriding (redefining a method in a child class) and method overloading
  (defining multiple methods with the same name but different parameters).

### 6. *Abstraction*
- Hiding complex implementation details and exposing only the necessary features of an object.
- Achieved through abstract classes and interfaces (in Python, using abstract base classes or duck typing).

### 7. *Constructor and Destructor*
- *Constructor*: A special method (`__init__` in Python) that is automatically called when an
  object is created. It initializes the object's attributes.
- *Destructor*: A special method (`__del__` in Python) that is called when an object is
  destroyed or goes out of scope.

### 8. *Class and Static Methods*
- *Class Methods*: Methods that are bound to the class rather than the instance. They can
  modify class-level attributes.
- *Static Methods*: Methods that belong to the class but do not modify class or instance
  state. They are utility functions.

### 9. *Association, Aggregation, and Composition*
- *Association*: A relationship between two classes where objects of one class are related
  to objects of another class.
- *Aggregation*: A specialized form of association where one class is a "whole" and the other
  is a "part." The part can exist independently of the whole.
- *Composition*: A stronger form of aggregation where the part cannot exist independently of
  the whole. The lifecycle of the part is tied to the whole.

### 10. *Magic/Dunder Methods*
- Special methods in Python that start and end with double underscores (e.g.
  `__str__`, `__eq__`, `__add__`). They allow custom behavior for built-in
  operations like printing, comparison, and arithmetic.
