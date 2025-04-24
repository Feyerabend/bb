
## Dependency Injection

A design pattern that is not so common, is *Dependency Injection* (DI).

DI is a software design pattern and technique used for achieving
*Inversion of Control* (IoC) between classes and their dependencies.

Inversion of Control (IoC) is a design principle where control over program
flow and object creation is inverted--instead of classes creating their own
dependencies, an external component provides them. This decouples components
and promotes flexibility and testability.

Dependency Injection is a common way to implement IoC.


Without DI:

```python
class Service:
    def do_something(self):
        print("Service doing something")

class Client:
    def __init__(self):
        self.service = Service()  # tightly coupled

    def execute(self):
        self.service.do_something()
```

Here, Client is tightly coupled to Service. You can’t easily replace Service with a
mock or another implementation.

With DI:

```python
class Service:
    def do_something(self):
        print("Service doing something")

class Client:
    def __init__(self, service):
        self.service = service  # injected

    def execute(self):
        self.service.do_something()

#iInjecting dependency
service = Service()
client = Client(service)
client.execute()
```

Now Client doesn't care where the service comes from. It could be a mock, a different
implementation, or even something loaded dynamically.


#### Types of DI

1. Constructor Injection
Dependency is passed via the constructor (like above). Most common.

2. Setter Injection
Dependency is set via a method or property.

```python
class Client:
    def set_service(self, service):
        self.service = service
```

3. Interface Injection
The dependency implements an interface that the client uses to inject the dependency.
Less common in Python.


#### Benefits
- Loose coupling between components
- Easier to test (you can inject mocks)
- Greater flexibility and extensibility
