
## Outline for a New Paradigm for Solving Problems with Code

*Project: Discuss "wild ideas" in relation to methodology, methods or philosophy of programming
and computers. Here are some thoughts to start you with, which you may or may not agree with.
Come up with your own set of thoughts, or start digging into some existing perspectives.*

As you've likely noticed, I enjoy shifting perspectives and exploring different ways of looking at
things--some of which I find compelling, others less so. It's probably no surprise, then, that I
advocate for a particular viewpoint on programming and coding. After all, nearly every book on the
subject explicitly or implicitly presents a specific perspective. This isn't about claiming
neutrality or objectivity but rather about offering one (or perhaps a few) lenses through which to
approach the subject. The approach we take to problem-solving in programming is significant, as it
influences our thought processes, the tools we adopt, and ultimately the solutions we devise.

My perspective is that programming, at its core, is a *language problem*. When tackling a problem, it's
not just about writing code; it's about communicating effectively with the client or the problem domain
by building a tailored language. This language serves as the bridge between the problem's requirements
and the solution, providing a clear structure for how the system should behave. Data, the core of what
needs to be solved, takes precedence over the "how" of the solution. In other words, the problem to be
solved (data and its dynamics) is the focus, rather than the technical implementation details of how
the code will run. This is unfortunately often confused by the developer.

Rather than approaching problem-solving from the angle of existing software and APIs, I advocate for
a shift towards *building custom languages* and *defining protocols*. The difference is significant:
APIs often force the programmer to work within the constraints of already established solutions, potentially
limiting creativity and flexibility. Protocols, on the other hand, offer a more abstract and versatile
framework for communication, freeing the programmer from the need to fit the problem into pre-existing
structures. Instead of trying to adapt a problem to an API's way of doing things, we should aim to
solve the problem in a way that is not constrained by software limitations or assumptions about how the
solution should be structured.

While existing software and APIs certainly have value, they are best used as *tools for learning*,
not as the definitive way of solving problems. There is a critical distinction between learning from
existing systems and simply using them. Learning allows us to draw insights and principles, which can
inform our design of new solutions. Using, however, often means adhering to the fixed methodologies or
constraints that those tools impose. This distinction allows us to think more freely and innovatively
when approaching new problems, rather than being tethered to the paradigms already established by others.

*A introductory [podcast](https://notebooklm.google.com/notebook/024ee9d0-8ad1-4dac-b402-e47249d283f9/audio)
generated in NotebookLM.*
NB: For now it requires a Google account for login.
Alternative: Download [podcast](PARADIGM.wav) in WAVE-format.


#### The Importance of Languages in Programming

Programming, at its essence, revolves around the creation, manipulation, and use of *languages* to articulate
solutions to problems. The ultimate goal is to represent these solutions as implementations in high-level
programming languages, and at times, in lower-level languages as well.

This linguistic perspective of programming opens a wealth of avenues for exploration. At its heart,
programming is about translating human thoughts--often ambiguous and multifaceted--into precise,
machine-executable instructions. This process is inherently linguistic in nature. Whether natural
or programming, languages serve as frameworks for structuring, communicating, and reasoning about
complex ideas.

On the other hand, communication with clients (in a typical customer-seller relationship) also heavily
relies on language. This communication may be supplemented by visual aids, physical artefacts, or other
non-verbal means. Not everything in problem-solving or solution implementation must be reduced to language.
Mathematics, for instance, often bypasses natural language entirely, integrating solutions directly into
machine-executable forms or abstract representations that align seamlessly with computational processes.

This interplay between linguistic representation, mathematical abstraction, and practical implementation
highlights the versatility and depth of programming as both a technical and communicative endeavour.


#### Using APIs and Libraries: Language as a Medium

When working with APIs (Application Programming Interfaces), you are effectively engaging with someone else's
"language" for a specific domain. APIs encapsulate a way of thinking and expressing solutions tailored to
that domain, whether it's web development, data processing, or machine learning. They provide powerful
abstractions, allowing developers to achieve complex tasks with relatively simple commands. However,
these abstractions are inherently shaped by the design choices and idioms envisioned by the API's creators.
This means that your approach to problem-solving is often influenced--if not constrained--by the framework of
this pre-defined language.

While APIs and libraries offer convenience and efficiency, they can sometimes create a barrier between you
and the problem domain itself. Instead of deeply understanding and modelling the domain's intricacies, you may
find yourself fitting your solutions into the existing constructs of the API. This trade-off between ease
of use and deeper problem-domain understanding is a recurring theme in programming.

#### Custom Languages: A Creative Alternative

In contrast to adapting to existing APIs, creating your own language allows you to tailor abstractions to
fit the specific problem you're addressing. Whether it's a domain-specific language (DSL) or an entirely
new programming language, the process enables you to design a vocabulary and syntax that mirrors the
concepts and relationships of your domain. This alignment can make reasoning about the problem more intuitive
and expressing solutions more concise and natural.

Domain-specific languages (DSLs) epitomise the tailored approach to problem-solving. Examples like SQL
for database queries or Regex for pattern matching are purpose-built to express solutions in ways that
feel intuitive and efficient for their respective domains.

DSLs also frequently exist as embedded languages within general-purpose programming environments, combining
the power of domain-specific expressiveness with the flexibility of the host language. LINQ in C#, for
instance, enables developers to query collections using a concise and readable syntax, seamlessly integrating
with the broader .NET ecosystem. Similarly, Rake in Ruby provides a DSL for automating tasks such as file
transformations and build processes, while TensorFlow’s computational graph definitions offer a DSL fo
expressing machine learning workflows within Python.

Game engines often provide their own scripting languages, allowing designers to define behaviours and interactions
at a high level without needing to delve into the complexities of the engine's underlying mechanics. These
scripting languages empower creators to work efficiently within the specific constraints and requirements
of their field.

#### The Process of Language Creation

Designing a custom language involves much more than inventing syntax--it's about rethinking how to approach
and solve a problem. The process typically includes:

1. *Identifying Core Abstractions*: Analyzing the problem domain to pinpoint its fundamental concepts and operations.

2. *Designing Syntax and Semantics*: Creating a structure for your language that is both expressive and easy to use.

3. *Implementing the Language*: Building interpreters, compilers, or transpilers to bring the language to life and
   integrate it with existing systems.

By crafting a language, you take control of the problem-solving narrative, creating a tool that adapts to
your thinking rather than forcing your thoughts to conform to an existing framework.

#### Trade-Offs and Practical Considerations

While creating custom languages offers great potential, it also comes with significant challenges.
- *Complexity*: Designing and maintaining a language requires expertise and effort.
- *Integration*: Ensuring your language works seamlessly with other systems and tools can be difficult.
- *Adoption*: A new language introduces a learning curve, which can be a barrier to widespread use.

In many cases, hybrid approaches provide a practical middle ground. Fluent APIs, embedded DSLs, or frameworks
with domain-oriented design act as "mini-languages" within a broader programming environment. These approaches
offer many of the benefits of custom languages without the overhead of building one from scratch.

#### Programming as Communication

Thinking about programming in terms of language highlights its essence as a communicative act--between humans
and machines, and among human collaborators. The act of designing a language is akin to shaping a medium of
expression, enabling clearer, more precise, and more efficient communication.

This perspective aligns with trends in modern programming, such as metaprogramming, where code itself generates
or manipulates other code. Techniques like macros, code generation, and template metaprogramming represent a
natural extension of this linguistic view, empowering programmers to develop tools and languages that streamline
the solution of specific classes of problems.

Ultimately, viewing programming through the lens of language creation broadens the horizon of problem-solving,
offering a powerful framework to rethink and refine how we design, express, and implement solutions.


### Data as the Core of Client Communication in Language

When we shift our focus to data, it becomes clear that it should occupy a central role in discussions with
clients or customers of software. Data often represents the tangible value delivered by a system, serving as
the bridge between technical implementation and user needs.

To illustrate this, we can explore hypothetical dialogues that extend from reasoning about language and data
to the conceptualisation--perhaps even the creation--of a custom language that encapsulates these ideas into
executable code. These interactions demonstrate how aligning on a shared understanding of data can shape the
design and implementation of solutions that truly meet user expectations.

* [Science](DIALOG-SCIENCE.md) explores how data can transcend rigid preconceptions about what a program should
  do, paving the way for more flexible and adaptive implementations.

* [Pharmacy](DIALOG-PHARMACY.md) examines the handling of sensitive data (but do *not* address this exact issue),
  such as patient records, prescriptions, and medical decisions, highlighting the critical importance of
  communication.

* [Library](DIALOG-LIBRARY.md) offers a perspective grounded in legacy systems and established practices,
  reflecting on how a new take on traditional databases and cataloging solutions.

* [Disaster](DIALOG-DISASTER.md) probes the boundaries of this language-driven reasoning, revealing scenarios
  where its limits become evident and exploring potential solutions.

Then some [contrast](CONTRAST.md) to what we have today ..
