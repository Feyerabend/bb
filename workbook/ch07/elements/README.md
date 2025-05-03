
## Fossilised Lessons from Computing's Perpetual Reformation

Software architecture is the conceptual blueprint that defines the fundamental structures, behaviours,
and evolution pathways of a software system. It emerges from deliberate choices about how components
interact, how responsibilities are partitioned, and how quality attributes like performance, security,
and maintainability are prioritised. At its core, *architecture is the art of managing complexity through
abstraction*--creating boundaries that allow humans to comprehend and modify systems that would otherwise
exceed cognitive limits.  

The history of software architecture mirrors the evolution of computing itself. In the 1960s, as systems
grew beyond trivial programs, pioneers like Edsger Dijkstra advocated for structured programming to
combat "spaghetti code." The 1970s saw David Parnas formalise modular design principles, arguing that
modules should hide implementation details behind stable interfaces. The object-oriented revolution of
the 1980s, exemplified by Smalltalk and C++, introduced encapsulation and inheritance as architectural
tools. By the 1990s, patterns movement leaders like the Gang of Four codified reusable solutions to
recurring design problems, while UML emerged as a visual language for architectural modelling. The 2000s
brought service-oriented architecture (SOA) and cloud computing, decoupling systems into network-accessible
components. Today's landscape blends microservices, serverless computing, and AI-driven architecture
synthesis, reflecting an ongoing tension between centralisation and distribution. From what I've heard
microservices might be the next one for the chopping block ..  

When crafting architecture, practitioners must balance competing forces: immediate functionality against
long-term adaptability, technical purity against business constraints, innovation against technical debt.
They must consider how organisational structure (as per Conway's Law) inevitably shapes system design,
how to make irreversible decisions reversible, and how to measure what matters--not just lines of code,
but coupling density, interface stability, and deployment agility. Ethical dimensions now demand attention:
architectures that enable surveillance capitalism differ fundamentally from those preserving privacy by design.
The rise of sustainability concerns adds energy efficiency as first-class architectural constraint, while AI's
ascendance forces reconsideration of traditional boundaries between code and data. Ultimately, good
architecture creates a fertile ground for evolution, anticipating that today's optimal structure will become
tomorrow's legacy system--and designing graceful degradation paths for that inevitability.


### Elements

| Concept | Focus | Scope | Examples |
|---------|-------|-------|----------|
| *Module* | Organisation | Small | Python module |
| *API* | Interaction contract | Any | math API, REST API |
| *Library* | Reuse | Medium | math lib, numpy |
| *Package* | Namespace / Distribution | Medium | Python `numpy`, Debian package |
| *Framework* | Application skeleton | Large | Django, Qt |
| *Component* | Encapsulation | Medium-large | GUI widget, microservice |
| *Service* | Deployable unit | Large | REST API service |
| *Plugin* | Extension point | Small | VSCode plugin |
| *SDK* | Development toolkit | Large | Android SDK |
| *Middleware* | Interconnection | Medium | RabbitMQ, SQLAlchemy |
| *IDL* | Interface description | Cross-lang | Protocol Buffers |
| *Configuration* | Behaviour customisation | Small-large | YAML config |


The architectural concepts in this table form the *lexicon of structural possibilities* that architects combine
and configure to manifest their vision—each entry represents a fundamental building block in the eternal dance
between human cognition and system complexity. Consider *modules*, born from Parnas' 1972 revelation that information
hiding could tame the spaghetti code monsters of early computing; they are the atoms in this periodic table of
structure, the minimal units where architectural intent first crystallises. *APIs* and *IDLs* carry the DNA of
1990s component-based design, formalising the lesson that durable systems require interface contracts more stable
than their implementations--a wisdom echoing Roy Fielding's REST dissertation that later revolutionised web
services.[^rest]

[^rest]: Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures*
(Doctoral dissertation). University of California, Irvine. 
https://ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf

The progression from *library* to *framework* mirrors architecture's historical pendulum between freedom and
constraint: where 1980s Smalltalk encouraged open experimentation, modern frameworks like React enforce unidirectional
data flows, proving that architectural value often lies in *limiting possibilities* to prevent entropy.
*Components* and *services* embody the decades-long evolution from monolithic fortresses to distributed
citadels--the former recalling 1990s CORBA's ambitious failure at cross-language unity, the latter manifesting
Amazon's 2002 SOA mandate that birthed cloud-scale systems.

*Middleware* like RabbitMQ operationalises the 1970s theoretical dream of loose coupling, becoming the synaptic
gaps between architectural neurones. *Plugins* actualise Parnas' "secret" of change accommodation through extension
points--a principle that made Unix's filter paradigm outlast its contemporaries. Even *configuration files*,
seemingly mundane, encode architecture's hardest lesson from the Y2K crisis: separate what changes from what
remains, lest hardcoded values become time bombs.  

The *SDK* represents architecture's shift from artisanal craft to industrialised practice--the Android SDK
being less a toolkit than an *ecosystem constitution*, enforcing Google's architectural will on millions of
devices. *Packages* in their Python/Debian incarnations solve the "DLL Hell" that haunted 1990s Windows,
proving that namespacing and versioning are not technical details but *architectural survival strategies*.

So, the REST API service inherits Leonard Kleinrock's 1960s packet-switching insights. The YAML config file
distills lessons from Microsoft's registry debacles. When architects combine these elements, they're not
just designing systems: they're composing a symphony where every note carries the weight of decades of
accumulated wisdom, every structural choice a vote for how future generations will inherit or curse their work.


### Code Organisation: Some Foundational Structures

This small overview in the folders explores fundamental code organisation patterns--such as modules, libraries,
and APIs--through simple directory structures and examples. While far exhaustive, it highlights core concepts
for modularity and reuse. Real-world projects often extend these ideas into advanced packaging, distribution,
or deployment.

Examples draw from multi-language patterns (e.g., .c/.h pairs in C, .py modules in Python).

Your projects might evolve this further into real-world entities ..

