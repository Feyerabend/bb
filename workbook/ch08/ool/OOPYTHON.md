
## Python OO: Overview

#### 1. *Classes and Objects*
- *Class*: A blueprint or template for creating objects. It defines the properties
  (attributes) and behaviors (methods) that the objects created from the class will have.
- *Object*: An instance of a class. It represents a specific entity based on the class definition.

#### 2. *Attributes and Methods*
- *Attributes*: Variables that belong to an object or class. They represent the state
  or data of the object.
- *Methods*: Functions that belong to an object or class. They define the behavior
  or actions that the object can perform.

#### 3. *Encapsulation*
- The bundling of data (attributes) and methods that operate on the data into a single unit (class).
- Access control: Using private, protected, and public access modifiers to restrict access
  to certain attributes or methods.

#### 4. *Inheritance*
- A mechanism where a new class (child class) derives properties and behaviors from an existing
  class (parent class).
- Promotes code reuse and establishes a hierarchical relationship between classes.

#### 5. *Polymorphism*
- The ability of different classes to be treated as instances of the same class through a
  common interface.
- Includes method overriding (redefining a method in a child class) and method overloading
  (defining multiple methods with the same name but different parameters).

#### 6. *Abstraction*
- Hiding complex implementation details and exposing only the necessary features of an object.
- Achieved through abstract classes and interfaces (in Python, using abstract base classes or duck typing).

#### 7. *Constructor and Destructor*
- *Constructor*: A special method (`__init__` in Python) that is automatically called when an
  object is created. It initializes the object's attributes.
- *Destructor*: A special method (`__del__` in Python) that is called when an object is
  destroyed or goes out of scope.

#### 8. *Class and Static Methods*
- *Class Methods*: Methods that are bound to the class rather than the instance. They can
  modify class-level attributes.
- *Static Methods*: Methods that belong to the class but do not modify class or instance
  state. They are utility functions.

#### 9. *Association, Aggregation, and Composition*
- *Association*: A relationship between two classes where objects of one class are related
  to objects of another class.
- *Aggregation*: A specialized form of association where one class is a "whole" and the other
  is a "part." The part can exist independently of the whole.
- *Composition*: A stronger form of aggregation where the part cannot exist independently of
  the whole. The lifecycle of the part is tied to the whole.

#### 10. *Magic/Dunder Methods*
- Special methods in Python that start and end with double underscores (e.g.
  `__str__`, `__eq__`, `__add__`). They allow custom behavior for built-in
  operations like printing, comparison, and arithmetic.


### Object-Oriented Programming: Examples and details

Object-oriented programming (OOP) is a paradigm that models software design around objects,
which represent entities with state (data) and behavior (methods). It is based on several
fundamental principles--*encapsulation*, *inheritance*, and *polymorphism*--but deeper abstraction
reveals its role in modularity, design architecture, and system evolution.


__1. The Nature of Object Orientation: Ontology and Identity__

OOP is deeply rooted in ontology, the study of being. Objects exist in a system with a unique
identity, even when their state changes over time. This is distinct from functional programming,
where computation is more declarative and transformations are stateless.

An object's identity is independent of its attributes. If two objects have identical attributes
but are different instances, they remain distinct. This is why we differentiate between equality
(`==`) and identity (`is`) in Python.

```python
class Entity:
    def __init__(self, name):
        self.name = name

e1 = Entity("Alice")
e2 = Entity("Alice")

print(e1 == e2)  # False (unless __eq__ is overridden)
print(e1 is e2)  # False (different memory addresses)
```


__2. Abstraction and Class Design: The Role of Interfaces__

Abstraction in OOP refers to exposing only essential features of an object while hiding implementation
details. Abstract classes and interfaces enforce a contract for subclasses to implement.

A pure abstract class (similar to an interface in Java) contains only method signatures, ensuring
that derived classes implement them.

```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self):
        pass

class Circle(Drawable):
    def draw(self):
        print("Drawing a Circle")

c = Circle()
c.draw()
```

Why use abstraction?
- Reduces coupling between components.
- Encourages interface-driven design.
- Facilitates dependency inversion (a key SOLID principle).

An abstract class provides a template for behavior, while an interface defines a strict contract.


__3. The Duality of Class and Type: Metaprogramming__

In Python, everything is an object, including classes themselves. Classes are instances of a special
class called `type`. This allows metaprogramming, where classes can dynamically modify themselves or
generate new behavior.

```python
class Meta(type):
    def __new__(cls, name, bases, dct):
        print(f"Creating class {name}")
        return super().__new__(cls, name, bases, dct)

class Example(metaclass=Meta):
    pass  # class creation triggers Meta.__new__
```

- Metaclasses are the "class of a class."
- They enable framework-level design, such as ORM libraries (Django models use metaclasses).


__4. Composition Over Inheritance: Avoiding the Inheritance Hell__

While inheritance promotes reuse, deep inheritance chains lead to tight coupling and fragile base
class problems. Composition is often preferable.

Instead of:

```python
class Animal:
    def move(self):
        print("Moving..")

class Bird(Animal):
    def fly(self):
        print("Flying..")

class Penguin(Bird):
    def fly(self):  # overriding in an unnatural way
        raise Exception("Penguins can't fly!")

penguin = Penguin()
penguin.fly()  # error
```

We use composition:

```python
class CanFly:
    def fly(self):
        print("Flying..")

class Bird:
    def __init__(self):
        self.movement = CanFly()

penguin = Bird()
penguin.movement.fly()
```

By favoring composition over inheritance, we achieve:
- Decoupling: Changes in base classes don’t ripple unpredictably.
- Dynamic behavior: Components can be swapped at runtime.
- Better testability: Individual components can be tested separately.


__5. Behavioral and Structural Design Patterns in OOP__

OOP enables powerful design patterns, which solve common architectural problems.

__Behavioral Patterns__

Patterns that govern object communication:
- Strategy Pattern: Swap algorithms dynamically.
- Observer Pattern: Event-driven programming.
- Command Pattern: Encapsulating actions as objects.

Example: Strategy Pattern

```python
class Strategy:
    def execute(self):
        pass

class ConcreteStrategyA(Strategy):
    def execute(self):
        print("Using Strategy A")

class ConcreteStrategyB(Strategy):
    def execute(self):
        print("Using Strategy B")

class Context:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def execute_strategy(self):
        self.strategy.execute()

context = Context(ConcreteStrategyA())
context.execute_strategy()  # Strategy A

context.strategy = ConcreteStrategyB()
context.execute_strategy()  # Strategy B
```

This allows runtime behavior modification without modifying existing classes.


__Structural Patterns__

Patterns that define object composition:
- Adapter Pattern: Convert one interface into another.
- Decorator Pattern: Add behavior dynamically.
- Proxy Pattern: Control access to an object.

*Example: Decorator Pattern*

```python
def logging_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logging_decorator
def greet():
    print("Hello!")

greet()
```

Decorators are widely used in Python (e.g., `@staticmethod`, `@property`).


__6. Object Lifetime, Memory Model, and Garbage Collection__

In Python, memory is managed automatically via reference counting and garbage collection.

__Reference Counting__

Each object keeps track of how many references point to it. When this count reaches zero, the object is destroyed.

```python
import sys

class Example:
    pass

e = Example()
print(sys.getrefcount(e))  # 2 (one from assignment, one from getrefcount)
```

__Cyclic References and Garbage Collector__

Python's garbage collector handles circular references using a generational garbage collection algorithm.

```python
import gc

class A:
    def __init__(self):
        self.b = B(self)

class B:
    def __init__(self, a):
        self.a = a

a = A()
del a  # normally, circular references would prevent deletion
gc.collect()  # forces garbage collection
```

- Generational collection optimizes memory cleanup.
- Weak references (weakref module) allow tracking objects without affecting garbage collection.


__7. The Open-Closed Principle and Dependency Inversion__

A key OOP design principle is open-closed, which states that:

> A class should be open for extension but closed for modification.

Instead of modifying existing classes when requirements change, we extend them.

```python
class Shape:
    def area(self):
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2
```

Additionally, dependency inversion ensures that high-level modules do not depend on low-level modules.

Instead of:

```python
class Service:
    def operation(self):
        return "Processing"

class Client:
    def __init__(self):
        self.service = Service()

    def run(self):
        return self.service.operation()
```

We introduce inversion via abstraction:

```python
class AbstractService(ABC):
    @abstractmethod
    def operation(self):
        pass

class ConcreteService(AbstractService):
    def operation(self):
        return "Processing"

class Client:
    def __init__(self, service: AbstractService):
        self.service = service

    def run(self):
        return self.service.operation()

client = Client(ConcreteService())  # dependency injected
```

This makes components loosely coupled, enhancing scalability and testability.


### Conclusion

Object-oriented programming is not just about encapsulation, inheritance, and polymorphism--it
is a methodology for managing complexity. Understanding design patterns, metaprogramming, composition,
and dependency inversion allows developers to write more scalable, reusable, and maintainable code.
