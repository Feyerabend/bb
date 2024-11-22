## Basic Tests

### Unit

Unit tests are designed to verify the correctness of individual units of code, such as
functions or methods. These tests focus on testing a small, isolated piece of functionality
in the application, typically without dependencies on other parts of the system. The purpose
is to ensure that each function behaves as expected under various conditions. Unit tests
are often fast and deterministic, meaning they should produce the same result each time
they are run, assuming the code being tested remains unchanged. Unit tests are written in
a way that allows them to mock or simulate external dependencies, which helps to test the
unit in isolation.

### Integration

Integration tests, on the other hand, are concerned with the interactions between different
components or systems within an application. While unit tests focus on individual units of code,
integration tests verify that these units work together as expected. For example, an integration
test might verify that a database correctly stores data when interacting with a data access layer,
or that an API properly integrates with a third-party service. These tests typically involve more
complex setups than unit tests and may require real or simulated external services, such as database
or web servers. Integration tests are often slower and more complex because they verify interactions
across multiple components.

### Functional

Functional tests are designed to ensure that the application behaves correctly from an end-user
perspective, simulating real-world usage scenarios. These tests typically focus on the system as
a whole, verifying that features and functions work as expected when executed in the correct sequence.
Functional tests are often more user-focused, aiming to confirm that the software performs its
intended tasks, such as processing input, generating output, and managing user interactions.
While unit and integration tests focus on the correctness of components and their interactions,
functional tests ensure that the application delivers the expected results when used in real-world
scenarios. These tests may involve interacting with a user interface, testing entire workflows,
or running a series of commands that reflect how the application will be used in practice.


### Code

The code extends from a simulated database:

```python
class Database:
    def add(self, key, value):
        ..
    def delete(self, key):
        ..
    def get(self, key):
        ..
    def is_integer(self, key):
        ..
```

A class for static 'stored procedures':

```python
class DatabaseProcedures:
    @staticmethod
    def increment_value(db, key, amount):
        ..

    # new feature!
    @staticmethod
    def bulk_delete(db, prefix):
        ..
```


And an interpreter:

```python
class SimpleInterpreter:
    def execute(self, command):
        
        if match := add_pattern.match(command):
            ..
            return

        elif match := delete_pattern.match(command):
            ..
            return

        elif match := increment_pattern.match(command):
            ..
            return

        return "Invalid command"
```

#### Process

1. First, we evaluate the behavior of individual components using unit tests. These tests focus
on isolated units of code, such as functions or methods, ensuring they work correctly in
isolation. By testing each unit separately, we can pinpoint issues at a granular level without
interference from other parts of the system. This approach helps maintain the reliability of
smaller code segments, making it easier to identify and resolve bugs quickly.

2. Next, we move on to integration tests, which examine how multiple components or classes work
together as a system. These tests are essential for verifying that interactions between components
function correctly, such as how a database integrates with the application logic or how different
services communicate with each other. Integration tests help uncover issues that arise when components
are combined, ensuring they cooperate as intended.

3. Finally, we conduct functional tests to assess the system’s overall behavior in real-world
scenarios. These tests simulate user interactions and workflows, validating that the application
delivers the expected results when used as an end product. Functional tests focus on end-to-end
functionality, confirming that the system behaves as users would expect, covering everything from
processing input to generating output. This final stage ensures that the application is not only
technically sound but also practical and reliable for its intended use.
