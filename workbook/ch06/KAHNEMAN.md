
## Psychology and programming

* Kahneman, Daniel (2011). *Thinking, fast and slow.* 1.ed. New York: Farrar, Straus and Giroux
* Kahneman, D., Sibony, O. & Sunstein, C.R. (2021). *Noise: a flaw in human judgment.* London: William Collins.

Daniel Kahneman, a psychologist, is best known for his groundbreaking work on decision-making, behavioral
economics, and cognitive biases. His work, particularly in collaboration with Amos Tversky, has had a
profound influence on understanding how humans think, make decisions, and solve problems. While his ideas
primarily come from psychology and behavioral economics, many of them are highly relevant to programming,
software engineering, and even software development processes.

It can be challenging to fully grasp Kahneman's ideas, and interpretations may deviate from his original
perspective. Nonetheless, exploring fields beyond the confines of strictly programming can be profoundly
enriching and offer valuable insights.

*Project: Discuss Kahnemans ideas and their possible applications to programming.*


### System 1 and System 2 thinking

One of Kahneman's most influential ideas is the distinction between *two modes of thinking*.

* *System 1*: Fast, automatic, intuitive, and often unconscious. This system relies on heuristics
  (mental shortcuts) and is quick to form conclusions, which can lead to errors in judgment.

* *System 2*: Slow, deliberate, effortful, and logical. This system is used for more complex
  problem-solving and critical thinking but requires more cognitive resources.


*Programming and debugging*: When debugging, many programmers tend to rely on System 1 thinking--jumping to
conclusions or making quick assumptions about the cause of a problem. This can lead to errors or missed
edge cases. By deliberately engaging System 2 thinking, developers can approach problems more logically,
carefully testing assumptions and investigating the issue step by step.

*Example*: If a bug occurs, a developer might quickly assume it's a variable initialization issue (System 1),
but by taking the time to step through the code, use a debugger, or add unit tests, they engage System 2
thinking and can often find the root cause more effectively.

*Code reviews*: During a code review, it's easy to fall into System 1 thinking, focusing on quickly identifying
style issues or patterns that "look wrong." But using System 2 thinking can help reviewers critically assess
the logic, scalability, and overall design of the code, which is more beneficial in the long run.


### Cognitive biases (heuristics)

Kahneman and Tversky identified various cognitive biases that affect human judgment. Many of these biases
can influence programmers, especially when making decisions about code, algorithms, or design patterns.

#### Relevant to programming

__Anchoring bias__: *The tendency to rely too heavily on the first piece of information (the "anchor") when
making decisions.*

*Application*: A programmer may overestimate the complexity of a new technology or approach simply because
it's similar to something they've used before, without considering whether it's the best solution for the
current problem.

__Availability heuristic__: *Making decisions based on easily available information or experiences, rather
than all relevant data.*

*Application*: A developer might choose a solution or tool based on their recent experiences with it (e.g.
a particular library or framework) rather than doing a comprehensive evaluation of alternatives.

__Confirmation bias__: *The tendency to search for or interpret information in a way that confirms existing
beliefs or assumptions.*

*Application*: When debugging, a programmer might focus only on information that supports their initial
hypothesis about the cause of the bug, ignoring evidence that suggests a different issue. This can lead
to missing the real cause of the problem.

__Overconfidence bias__: *Believing you know more or can do more than you actually can, often leading to
overly optimistic estimates of how long a task will take or how difficult it will be.*

*Application*: Estimation errors are common in software development. Overconfidence in knowing how to
solve a problem can lead to underestimating the time needed for completion, which can negatively impact
project timelines.


#### Mitigation strategies

*Designing for bias*: Being aware of these cognitive biases and how they influence decision-making can
help programmers consciously correct them. For example, performing peer reviews, seeking feedback, and
deliberately questioning assumptions can reduce bias.

*Use of checklists and formal methods*: Having a formal, systematic approach to debugging, writing tests,
and designing code can help reduce reliance on biases and increase the chances of catching potential issues.


### Planning fallacy

The planning fallacy is the tendency to underestimate the time needed to complete tasks, even when
past experiences show that tasks tend to take longer than expected.


__Time estimation__: Developers often underestimate how long a project or feature will take to complete.
This is especially true when they focus on the ideal scenario (things going smoothly) rather than
accounting for obstacles, dependencies, and potential issues.

*Solution*: Kahneman suggests using reference class forecasting: looking at similar past projects to
make more accurate predictions. In programming, this means drawing on previous experiences with similar
tasks to better estimate how long something will take and accounting for potential roadblocks.

*Feature creep*: The planning fallacy can also contribute to feature creep, where the scope of a project
expands beyond the original plan, often without re-assessing time or resource constraints. Scope management
and incremental development (e.g. Agile practices) can/might help mitigate this.


### Loss aversion and risk aversion

Kahneman's work on loss aversion suggests that people are more sensitive to losses than to gains of the
same size. In other words, losing something feels worse than gaining something of equivalent value feels
good.

__Refactoring and changes__: Developers may be averse to changing working code due to the fear of
introducing bugs, even if the change could significantly improve the codebase in the long run.

*Solution*: Encouraging incremental refactoring and focusing on small, low-risk changes can help
overcome this bias. Developers can use tests and continuous integration to minimise the perceived
risk of making changes.

__Risk-averse decisions__: Programmers may stick to known, but suboptimal, solutions because they
fear the risks associated with trying new tools or technologies.

*Solution*: Experimentation, prototyping, and adopting a growth mindset (viewing mistakes as learning
opportunities) can help overcome this fear and encourage more innovation.


### The halo effect

The halo effect is the tendency for an overall impression of a person, company, or product to
influence specific judgments about them. For example, if you know a developer is skilled in
one area, you might assume they are equally skilled in others. To be purely speculative:
this might be observed in a crafts culture where certain persons have a higher status than
others, and the culture have the tacit assumption built-in.

__Bias in code reviews__: In a code review, if a programmer has a good reputation or is known
to have written clean, efficient code in the past, reviewers might be biased toward assuming
that the current code is also of high quality, potentially overlooking issues.

*Solution*: Adopting a standardized code review process and using objective metrics (e.g.,
automated tests, static analysis tools) can help ensure reviews are not influenced by biases.


### Endowment effect

The endowment effect refers to the tendency for people to value something more highly simply
because they own it.

__Code ownership__: Developers may overvalue their own code and resist changes or refactoring
because they have invested time and effort in it, even when the code could be improved.

*Solution*: Encouraging a collaborative mindset and creating a culture of continuous improvement
can help developers separate their identity from their code, making them more open to suggestions
for improvement. Or, simply: "kill your darlings."


### Conclusion: Applying Kahneman's insights to programming

Kahneman's insights into human behavior, decision-making, and cognitive biases offer a rich toolkit for
improving programming practices. By understanding concepts like System 1 and System 2 thinking, cognitive biases,
and heuristics, programmers can make more rational decisions, avoid common traps in estimation and debugging,
and improve their collaboration with others.

While programmers may not explicitly use Kahneman's terms in everyday development, applying the principles behind
them can lead to better outcomes, whether it's through more accurate time estimations, improved debugging techniques,
or making more informed decisions about software design and architecture. Kahneman's work helps us recognize unconscious
influences on our thinking and provides strategies for overcoming them, leading to more effective and rational
problem-solving in programming.
