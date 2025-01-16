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

### Acceptance

Acceptance tests verify whether a system meets the intended requirements and works as expected
from an end-user perspective. They focus on simulating real-world usage scenarios, ensuring that
the system behaves correctly across various interactions or workflows, such as adding, modifying,
or deleting data. These tests confirm that the features are functional and that the system satisfies
the business needs without delving into the underlying implementation details. Acceptance tests
typically cover higher-level functionalities and integration points, often representing the final
step before releasing a product. (Acceptance tests work with scenarios, in contrast to functional
tests that works from workflows.)

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

3. Next, we conduct functional tests to assess the system's overall behavior in real-world
scenarios. These tests simulate user interactions and workflows, validating that the application
delivers the expected results when used as an end product. Functional tests focus on end-to-end
functionality, confirming that the system behaves as users would expect, covering everything from
processing input to generating output. This final stage ensures that the application is not only
technically sound but also practical and reliable for its intended use.

4. Finally, the acceptance tests validate key user scenarios for the database system by simulating
realistic interactions: adding a record, incrementing its value, and then deleting it; verifying
that non-numeric values cannot be incremented; and ensuring bulk deletion works correctly for
keys with a specific prefix. These tests focus on confirming that the system behaves as expected
from a user's perspective, emphasising high-level functionality rather than implementation details.

### Exercises or Projects

1. *How can the 'bulk_delete' feature be incorporated into the existing database structure?*
    - Analyze the requirements for implementing the bulk_delete method and discuss the necessary modifications to ensure it integrates seamlessly with the current functionality.

2. *What steps are required to organise tests into a hierarchy of unit, integration, and functional tests?*
	- Evaluate how to categorize and structure the tests to reflect their roles, ensuring that each type of test is clearly separated and systematically executed.

3. *How can error handling be improved in the system to better manage invalid inputs or commands?*
    - Propose enhancements to the error-handling mechanisms in both the interpreter and database, considering how they interact and communicate feedback.

4. *What trade-offs arise when adding new features to an existing system?*
	- Explore the balance between extending functionality, maintaining system performance, and preserving code clarity and test coverage.

5. *How does the design of the database interface influence testability and maintainability?*
	- Discuss the impact of interface design decisions on the ease of writing comprehensive tests and ensuring long-term code reliability.

6. *How can test coverage be measured and improved across all levels of testing?*
	- Examine methods for evaluating test coverage and identify strategies to fill gaps, ensuring thorough validation of the system’s functionality.

7. *How can the database be enhanced to support more complex data types?*
    - Investigate the steps needed to allow storage and manipulation of non-integer values or more structured data, such as lists or dictionaries.

8. *What considerations are required to ensure the tests cover edge cases effectively?*
    - Identify potential edge cases for the database and interpreter, and discuss how to include them in unit, integration, and functional tests.

9. *What changes would be necessary to expand the system to handle concurrency?*
	- Examine the modifications required in the database and interpreter to handle simultaneous user interactions and maintain data consistency.
