## Code

These folders include the complete code corresponding to the examples presented in the book.
While they may occasionally expand upon the book's suggested code, they primarily consist of
direct code references from the text.

The code examples in this book are written in standard Python (version 3), ANSI C, MicroPython
for the Raspberry Pi Pico, and JavaScript compatible with most modern web browsers.
To help readers grasp core programming principles, dependencies have been kept to a minimum.
Except where necessary—-such as for specialized hardware interfaces like an LCD driver—-no
external libraries are used, or at least a few. This approach encourages a focus on foundational
coding concepts without reliance on third-party libraries.


### Libraries

Contrary to common recommendations today, writing code for widely used algorithms instead
of relying on external (third party) libraries can benefit learners by building familiarity
with fundamental techniques and reducing external dependencies. For instance, this book
suggests writing a simple virtual machine to allow code to abstract cleanly from underlying
systems.

While external libraries that are standard, robust, and well-tested should generally be used,
avoid relying on small, non-essential libraries that add little value to the core task and
may introduce unnecessary dependencies.

In the real world, it's worth noting that writing custom solutions for everything can
sometimes 'reinvent the wheel' and increase development time, especially for common tasks
where libraries are standardized, robust, and highly optimized. Established libraries also
tend to be well-documented and peer-reviewed, meaning they've been vetted for reliability
and bugs. The right balance often means selectively using trusted, essential
libraries—-especially for complex tasks that are beyond the immediate scope of this
book—-while still tackle more straightforward implementations.
