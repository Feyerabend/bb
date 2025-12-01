
## Reflections

This book begins with a simple assumption: you are not an empty vessel. You have already
written code, experimented with ideas, encountered frustration, and discovered moments of
insight. You bring with you a history of learning that is unique to you. Instead of
ignoring that, we use it.

Traditional teaching often seeks to level the field, to give everyone the same foundation
before any real exploration begins. This can simplify the job of the teacher, but it also
reduces students to passive listeners. Their diverse backgrounds and interests are sidelined
in favor of a standardized sequence of content.

Here, the goal is different.

This book is not meant to be followed step by step or consumed passively. It is meant to provoke,
encourage, and support exploration. It provides a structure, but not a pathway. It contains ideas,
but not a curriculum. The real work happens when students and teachers together decide what matters,
what questions to pursue, and what skills to deepen.

Learning to program--and learning about computation more broadly--is not a linear process.
It is a field defined by branching paths, unexpected connections, and personal motivations.
By acknowledging this, we shift the focus away from "covering material" and toward "growing capability."
Because of this openness, the references and suggestions in this book are not demands.
They are invitations. Where you go from here depends on your interests, your curiosity,
and the conversations you have with others in your learning environment. You are not expected
to learn everything. You are encouraged to learn meaningfully.


### Programming Languages

Because this book takes code itself as its starting point, existing programming languages naturally
become the primary tools through which we explore the concepts. To support this, I have chosen three
languages--C, Python, and JavaScript. Each of them has its own personality, strengths, and historical
context, yet all are accessible enough for beginners while remaining powerful for more advanced exploration.


#### C: Simplicity, Control, and Foundations

We begin with C. Although it is considered a low-level language, it remains one of the most influential
languages ever created. It is widely used, widely understood, and forms the basis of many modern systems.
Even though some of its traditional domains have shifted toward languages like C++, and perhaps eventually
to Rust, C maintains a unique value for learners.

C offers a kind of transparent simplicity: you can see how data is stored, how memory is managed, and how
the computer actually executes your instructions. The language provides direct control with very few
abstractions hiding the details. For this reason, C is an ideal starting point for understanding what
programming really means at the machine level, without getting lost in complex modern features.


#### Python: Expressiveness and Modern Abstractions

Python, on the other hand, sits at a higher level. It is known for being easy to read and easy to write,
but beneath its simplicity lies a sophisticated set of concepts. Python supports object-oriented programming,
functional programming, dynamic typing, and a rich ecosystem of libraries. It represents a more "modern"
approach to programming, where the language takes care of many details so that the programmer can focus
on ideas, structure, and experimentation.

Python is also highly relevant beyond foundational learning. It is central in fields such as data science,
machine learning, automation, scientific computing, and AI research. Learning Python not only expands your
conceptual toolkit but also connects you to many of today's most active areas of computation.


#### JavaScript: Accessibility and the Web as a Platform

JavaScript doesn't appear in the the examples in this book, but it remains a compelling option for
exercises and projects. Its greatest strength is accessibility. In its simplest form, JavaScript runs
directly in any modern web browser--no specialised installations required. All you need is a text
editor and a browser, making it one of the easiest entry points into real programming environments.

Beyond accessibility, JavaScript has grown into a versatile and powerful language, used not only for
web development but also for servers, mobile apps, and even embedded systems. For beginners, though,
its immediate "type-and-see" nature helps reduce barriers and encourages experimentation.


#### Why These Three?

Together, C, Python, and JavaScript offer three distinct perspectives on computation:
C teaches control, structure, and how a machine actually works.
Python teaches abstraction, expressiveness, and modern programming paradigms.
JavaScript teaches accessibility, rapid experimentation, and interaction with the web.
These languages do not form a strict path or hierarchy; instead, they give you multiple angles from
which to understand code. You can choose the one that resonates with your interests, or use all three
to see how different languages shape your thinking.
This book uses them not as endpoints, but as starting points--lenses through which we can approach
the broader study of programming, algorithms, and computational ideas.


#### Personal Background

My own learning began with C in the early 1980s, when it was a hot topic in the emerging world of
microcomputers. Naturally, everyone owned the classic K&R book--*The C Programming Language* by
Kernighan and Ritchie. That was simply the starting point for anyone serious about programming at the time.

* Kernighan, B. W., & Ritchie, D. M. (1988). *The C Programming Language* (2nd ed.). Prentice Hall.

I became aware of Python later, largely through Bruce Eckel and his books on Java. He made electronic
editions freely available for anyone willing to host them on their own website. I was one of the relatively
few--fewer than fifteen, if I remeber correctly--who actually did this. Eckel also expressed a strong interest
in Python. I skimmed it out of curiosity, but didn't pursue it further; at the time Python still
felt too new and immature.

When Netscape introduced LiveScript, allowing programs to run directly inside the browser, I was far more
motivated to explore this new approach. In the beginning, only a few browsers could run LiveScript, and when
Microsoft entered as a competitor, they released their own implementation. Performance was slow, and for a
while it was still easier to write programs in Java using applets.

But as LiveScript evolved into JavaScript and support across browsers improved, it eventually became another
valuable language in my programming toolbox.



### General Computer Science

Computer science is often more theoretical and less accessible than learning programming languages.
The topic, though, has traditionally focused on foundational subjects such as algorithms, data structures,
formal logic, and computational theory. These areas form the backbone of the field: they explain not
just *how* to program, but *why* certain approaches work, how systems behave under different constraints,
and what is mathematically or practically possible.

As the discipline expands, however, computer science increasingly opens the door to areas influenced
by machine learning, data-driven methods, and intelligent systems. The boundaries of the field are shifting.
Concepts once considered peripheral--like probabilistic reasoning, neural networks, optimisation techniques,
and large-scale data processing--are now central to both research and industry practice.

In this changing landscape, reference materials and recommended learning pathways will inevitably evolve as
well. Topics such as statistics, linear algebra, ethics in AI, model interpretability, and even domain-specific
applications (from biology to linguistics) are becoming essential parts of the modern computational toolkit.
The future of computer science will likely be more interdisciplinary, more applied, and more connected to
real-world data and intelligent behavior.

This book does not aim to cover all of these developments comprehensively, but it encourages curiosity and
exploration beyond traditional boundaries. For students who wish to deepen their understanding--whether in
classical computer science or emerging areas of machine learning--the following resources can serve as
starting points and inspiration.


#### Suggestions for further study

1. **Classic Computer Science Foundations**

   * *Introduction to Algorithms* by Cormen, Leiserson, Rivest, and Stein
   * *Structure and Interpretation of Computer Programs* by Abelson and Sussman
   * Courses in discrete mathematics, logic, and automata theory

2. **Programming Language Theory & Design**

   * *Programming Languages: Application and Interpretation* by Krishnamurthi
   * Explore functional languages (Haskell), systems languages (Rust), or logic languages (Prolog)

3. **Machine Learning and Data Science**

   * *The Elements of Statistical Learning* by Hastie, Tibshirani, and Friedman
   * *Deep Learning* by Goodfellow, Bengio, and Courville
   * Practical resources such as fast.ai or scikit-learn tutorials

4. **Systems, Architecture, and Performance**

   * *Computer Systems: A Programmer's Perspective* by Bryant and O'Hallaron
   * Operating systems courses or resources on concurrency and distributed systems

5. **Ethics, Society, and the Impact of Computing**

   * Literature on algorithmic fairness, data privacy, and responsible AI
   * Interdisciplinary studies connecting computing with philosophy, sociology, and law



#### Personal Experience

Crossing over from programming into a broader curiosity about computers and their place in human knowledge,
I developed the ambition to attend university and study the subject from a wider perspective. At that moment,
I found myself standing between two distinct academic paths: a program in Information Systems and a program
in Theoretical Philosophy.

What made the choice surprisingly difficult was that Theoretical Philosophy in the Nordic tradition includes
much more than abstract speculation. It encompasses formal logic, automata theory, philosophy of language,
and many conceptual tools that overlap with computing. These connections become even more apparent later,
when one encounters topics such as Hoare Logic, type theory, dependent types, and the foundations of verification.
In many ways, philosophy--at least this branch of it--offered a different but deeply compatible lens through
which to understand computation.

In the end, I chose the latter. One reason was the strong intersection I saw between my interests and the
philosophical study of logic. At the time, logic formed the intellectual core of much of AI research. In the
early 1980s, artificial intelligence was still largely driven by symbolic reasoning, theorem proving, and
formal representations of knowledge. It seemed perfectly reasonable--almost natural--that someone interested
in both computing and intelligence would pursue logical foundations through philosophy.

That decision shaped not only how I approached computer science later, but also how I came to view programming 
languages, algorithms, and machine intelligence--as objects grounded not only in engineering, but in reasoning,
structure, and meaning.


