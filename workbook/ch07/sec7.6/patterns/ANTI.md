
## Anti-Patterns

#### Why We Use Anti-Patterns (Sometimes)

In this book/workbook, we often take intentional shortcuts--techniques that in a professional
context might be considered a really "bad practice" or even classified as anti-patterns. This
may seem contradictory in a text that ultimately aims to build sound programming habits. But
there is a reason for this approach.


#### The Purpose of Simplicity in Teaching

When you’re just learning about operating systems, file systems, simple database engines, or
any such coding, adding too many layers of abstraction, dependency management, or pattern-based
design would do more harm than good. It would distract from the core ideas.

For example:
- We might use global variables where a production system would pass structured context objects.
- We might avoid error handling and validation to keep the control flow readable and linear.
- We might cram too much responsibility into a single function or module--the God Object anti-pattern
  below--just to keep the entire system visible on one screen.

These are *didactic simplifications*, not *prescriptions* for real-world engineering.


#### But Real Systems Demand More Discipline

In production code, we are not writing for a single reader, or even just for ourselves.
We write for a team:
- For coworkers trying to extend a module a year from now.
- For maintainers debugging a critical failure at 3 AM.
- For ourselves, who may return to this code after months of working on other things.

In such contexts, anti-patterns create:
- Technical debt
- Fragile systems
- Poor testability
- Confusing architectures
- Burnout among team members

That’s why disciplines such as modularity, encapsulation, error propagation, and design
patterns exist--not as bureaucratic overhead, but as tools to manage complexity over time.


#### Learning First, Discipline Later

This workbook’s approach is to lower the cognitive barrier to entry. You will see simplified
systems that do things in ways that might make a senior developer wince--and that’s okay.
These systems are stepping stones. You will rebuild them, and you will refactor them.
That’s part of the process.

Eventually, the same patterns you now avoid--separation of concerns, inversion of control,
dependency injection--will become second nature. But only after you’ve felt why they’re needed.



| Anti-Pattern         | Description                                                                 | Misused For                          | Why It's Harmful                                           | Better Alternative                        |
|--|--|--|--|--|
| God Object           | A class that knows too much or does too much                               | "Centralizing logic"                 | Violates SRP, hard to test, fragile                        | Decompose into focused, smaller classes    |
| Spaghetti Code       | Tangled, unstructured, jumpy control flow (e.g. too many `goto`, nested)   | "Quick hacks"                        | Impossible to understand, debug, or extend                 | Use functions, modular design              |
| Lava Flow            | Dead or outdated code that remains in the system                           | "Preserving legacy code"             | Increases maintenance cost, misleads developers            | Remove unused code, document decisions     |
| Copy-Paste Programming | Duplicating code instead of abstracting                                   | "Avoiding abstraction overhead"      | Bug fixes must be repeated, DRY violated                   | Extract reusable components or functions   |
| Golden Hammer        | Applying a familiar solution to every problem                              | "Tool familiarity"                   | Wrong tools reduce quality, increase complexity            | Evaluate each problem independently        |
| Magic Numbers        | Using unexplained numeric constants inline                                 | "Speed and brevity"                  | Reduces readability and maintainability                    | Use named constants or enums               |
| Hard Coding          | Embedding config, paths, values directly in code                           | "Quick fixes"                        | Fragile, non-portable, not testable                        | Use config files, environment variables    |
| Premature Optimization | Optimizing before understanding real bottlenecks                         | "Being clever"                       | Wastes time, complicates code                              | Profile first, then optimize selectively   |
| Shotgun Surgery      | A small change requires many scattered modifications                       | "Modularizing without cohesion"      | Increases chance of bugs and inconsistency                 | Improve cohesion, group related behavior   |
| Anchoring            | Sticking too rigidly to an initial (possibly bad) decision                 | "Respecting original design"         | Missed opportunity for better solutions                    | Be open to revisiting design choices       |
| Reinventing the Wheel| Creating custom solutions for well-solved problems                         | "Learning exercise" or NIMBY         | Likely buggier and less efficient                          | Use mature, tested libraries or standards  |
| Poltergeist          | Short-lived objects used only to pass data                                 | "Decoupling"                         | Adds unnecessary indirection                               | Collapse into meaningful abstractions      |
| Object Orgy          | All objects freely access each other’s data                                | "Sharing is caring"                  | Breaks encapsulation, makes debugging a nightmare          | Use interfaces, restrict visibility        |
| Overengineering      | Building far beyond actual requirements                                    | "Future-proofing"                    | Waste of time, bloated code, unclear responsibilities       | YAGNI (You Ain’t Gonna Need It)            |



### Examples of Anti-Patterns


__1. God Object__

#### Bad: One object doing everything

```python
class AppController:
    def handle_user_input(self):
        ...
    def draw_ui(self):
        ...
    def save_data(self):
        ...
    def manage_network(self):
        ...
```

Fix: Split into UIManager, NetworkManager, StorageService.


__2. Magic Numbers__

```c
// Bad
if (temperature > 451) { burn(); }

// Good
const int FAHRENHEIT_BURN_POINT = 451;
if (temperature > FAHRENHEIT_BURN_POINT) { burn(); }
```


__3. Copy-Paste Programming__

```c
// Bad
function getUserById(id) { ... }
function getOrderById(id) { ... } // identical! logic

// Good
function getEntityById(type, id) { ... }
```


__4. Golden Hammer__

Using the Observer pattern for everything, even when a simple callback would
suffice--leads to untraceable control flow and debugging nightmares.


__5. Premature Optimisation__

```c
// Bad: Using manual memory manipulation too early
char* buffer = malloc(1024); // "because it’s faster"
```

Profiling may reveal that disk I/O, not memory, is the bottleneck.
