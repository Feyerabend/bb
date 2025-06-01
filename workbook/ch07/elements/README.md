
## Fossilised Lessons from Computing's Perpetual Reformation

*Software architecture is the conceptual blueprint that defines the fundamental structures, behaviours,
and evolution pathways of a software system.* It emerges from deliberate choices about how components
interact, how responsibilities are partitioned, and how quality attributes like performance, security,
and maintainability are prioritised. At its core, *architecture is the art of managing complexity through
abstraction*--creating boundaries that allow humans to comprehend and modify systems that would otherwise
exceed cognitive limits.

If we shortly reflect on what *methodology* is in contrast ([ch06](./../../ch06/method/)):

| Aspect | *Architecture* | *Methodology* |
|---|---|---|
|  *Definition* | A structural or design framework of a system—*the blueprint*. | A process or set of practices—*the ritual or routine* of making. |
|  *Temporal Nature* | More static and foundational; about system *structure*. | More dynamic and iterative; about *practice and behavior*. |
|  *Challenge (Innovator's Dilemma)* | Becomes outdated as new systems require new design paradigms. | Becomes ritualised and loses adaptability; risks becoming cargo cult. |
|  *Relation to Tools* | Tools are built *on top of* architecture. | Tools *manifest* methodology—ritualised in things like SCRUM boards or CI/CD YAMLs. |
|  *Nature of Evolution* | Architecture must be refactored or rethought when requirements shift. | Methodology often cycles and reincarnates older ideas in new forms. |


### Folders

__*Principles*__
* [simplec](./simplec/) -- A project where we illustrate the API (public contract), library (concrete
                           deliverable), and modules/components (internal implementation).
                           The structure/architecture is highly dependent on the programming language C. 
* [simplepy]

__*Simple*__
* [config](./config/) -- A project that offers many configuration possibilities. You can start by passing
                         arguments to main from the command line, and use YAML files to configure aspects
                         such as font rendering. The architecture could be improved by restructuring the
                         configuration system to support more flexible and thoughtful organisation.

__*Ready-made*__
* [basic]

__*Explorative*__
* vector



### History

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
https://ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf. 
REST is often misunderstood. It is not an API or protocol but an *architectural style*: a set of constraints
(such as statelessness, uniform interface) guiding how APIs should be structured, typically over HTTP but not
limited to it.

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

These foundational structures are not mere conventions but the distilled lessons of computing's iterative
reformation, each pattern a response to the chaos of unbridled complexity or the rigidity of over-engineered
systems. Let's explore a few illustrative examples of how these concepts manifest in code organisation,
grounding the theoretical in the practical, and tracing their roots to the architectural challenges they
were designed to address.


#### Modular Decomposition: Python

Consider a simple Python project structured to embody Parnas' principle of information hiding. A directory
might look like this:

```
/my_project
  /core
    __init__.py
    data_processor.py
    storage.py
  /interfaces
    __init__.py
    api.py
  main.py
```

Here, `data_processor.py` encapsulates logic for transforming data, exposing only high-level functions like
`process_dataset()`. The `storage.py` module handles persistence, abstracting whether data is saved to disk
or a database behind a clean interface like `save_data()`. The `api.py` in the `interfaces` directory defines
an external contract, perhaps a REST API endpoint, that orchestrates calls to `core` without exposing its
internals. This structure echoes Dijkstra's 1960s call for structured programming, where clear boundaries
prevent the "spaghetti code" that plagued early systems. By organising code into modules, the architect ensures
that changes to `storage.py` (e.g., swapping a file-based store for a cloud database) don't ripple through
the entire system, a direct application of Parnas' 1972 insight that modules should conceal their "secrets."


#### Libraries: C

In C, the `.h` and `.c` file pair is a classic embodiment of the library concept, designed for reuse across
projects. Consider a simple math library:

```
/mathlib
  mathlib.h
  mathlib.c
  main.c
```

The `mathlib.h` header declares function prototypes like `double compute_average(double* values, int size);`,
while `mathlib.c` contains the implementation. A consuming program, `main.c`, includes `mathlib.h` and links
against the compiled library, unaware of its internal logic. This separation, rooted in the 1970s modular
design movement, ensures that the library can evolve (e.g., optimising the averaging algorithm) without
recompiling dependent programs, provided the interface remains stable. The library concept reflects architecture's
eternal quest for reuse, a principle that powered the success of Unix's modular utilities and survives in
modern ecosystems like Python's `numpy` or Rust's `crates`.


#### APIs: Contracts for Interoperation

An API, whether a local function interface or a networked REST endpoint, formalises interaction contracts.
Consider a REST API service in a Node.js project:

```
/api_service
  /routes
    users.js
    orders.js
  /models
    user.js
    order.js
  server.js
```

Here, `users.js` defines endpoints like `GET /users/:id`, orchestrating calls to `user.js` for data access.
The API's public contract—its endpoints, request formats, and response codes—remains stable, even if the
underlying `user.js` model switches from a SQL to a NoSQL database. This structure descends from the 1990s
component-based design era and conceptually inspired by Roy Fielding's 2000 REST dissertation, which argued
that stateless, resource-oriented interfaces enable scalable, evolvable systems. The API's role as a contract
mirrors the IDL's cross-language ambitions, ensuring that a Python client or a Go microservice can interact
with the Node.js service without knowing its internals.


#### Frameworks and Plugins: Guiding and Extending

Frameworks like Django or Qt impose architectural discipline, providing a skeleton that developers flesh out.
A Django project might look like:

```
/django_app
  /my_app
    migrations/
    models.py
    views.py
    urls.py
  manage.py
  settings.py
```

Django's structure enforces the Model-View-Controller (MVC) pattern, with `models.py` defining data schemas,
`views.py` handling logic, and `urls.py` mapping routes. This rigidity, a deliberate constraint, prevents the
entropy of ad-hoc designs, a lesson from the 1980s object-oriented movement that valued guided development
over unrestricted freedom. Plugins, conversely, offer extension points. In a VSCode plugin project:

```
/vscode_plugin
  extension.js
  package.json
```

The `extension.js` hooks into VSCode's API to add custom functionality, like a new command. This extensibility,
a direct descendant of Unix's filter paradigm and Parnas' change-accommodation principle, allows the core system
to remain stable while enabling user-driven innovation.


#### Configuration: Separating the Mutable

Configuration files, often in YAML or JSON, encode the lesson from the Y2K crisis that mutable values must be
externalised. A simple project might include:

```
/project
  config.yaml
  app.py
```

Where `config.yaml` specifies parameters like `database_url: postgres://localhost:5432`, and `app.py` reads it
to initialise the system. This separation ensures that deploying the same codebase to different environments
(e.g., development vs. production) requires only a config change, not code modification—a principle that saved
countless systems during the Y2K remediation efforts.


### Tying It to the Broader Narrative

These *organisational patterns* are not arbitrary but the scars of battles fought against complexity, fragility,
and obsolescence. The Python module inherits Parnas' modular wisdom; the C library operationalises the 1970s
reuse imperative; the REST API service channels Kleinrock's packet-switching vision into modern cloud systems.
Each structure is a vote for how systems should evolve, balancing immediate needs with the inevitability of
change. As microservices face scrutiny for their operational overhead—perhaps the next architectural paradigm
to be questioned—these foundational patterns remind us that architecture is less about inventing anew and more
about recombining proven elements in response to shifting constraints.

Real-world projects build on these foundations, scaling them into distributed systems, cloud-native deployments,
or AI-driven architectures. Yet, the core principles—modularity, encapsulation, stable interfaces—remain the
bedrock, ensuring that as systems grow, they remain comprehensible, adaptable, and resilient. *Architects, like
historians, must learn from the past to design for the future, knowing that every choice they make will one day
be a fossilised lesson for the next reformation.*

Working in a library with special collections--manuscripts, letters, early printed books--the librarians over the
centuries have developed physical systems to maintain order amidst growing complexity. One such mechanism is
the use of *signia*: small, discrete identifiers used to mark and reference items. A signium acts like a
pointer--an abstract handle that links to a concrete object. But like pointers in programming, they are vulnerable to
context loss: when shelving systems change, or rooms are reordered, the signium may no longer resolve. In this
way, even the archival world encounters the limits of indirection and the fragility of implicit architecture.

Just as software engineers rely on type systems or URI schemes to stabilise references, librarians codify their
linking mechanisms into catalogues and finding aids. Whether in bytes or in bindings, the struggle to preserve
meaning across time and transformation reflects a shared architectural concern: how to design structures that
survive reorganisation, reinterpretation, and decay. Working in a library with exactly these fossilised structures,
I can testify to the interesting, but sometimes cumbersome historical artifacts.[^ub]

One often encounters systems whose original rationale has been lost, yet which continue to shape present-day
practice--schemas that reflect obsolete taxonomies, shelving codes from long-abandoned floor plans, or index cards
repurposed from earlier cataloguing philosophies. These are not just legacy systems; they are inherited interfaces,
accidentally stable, quietly constraining. To revise them is to risk breaking the fragile web of references that
binds generations of curators, scholars, and systems together.

In this sense, both software and archives face the same quiet dilemma: *how to modernise without erasing context*,
*how to refactor without corrupting meaning*. Architectural wisdom, then, is not simply a matter of design skill--it
is an ethics of continuity, a discipline of stewardship. What we inherit is structure; what we pass on is form and
intent embedded in that structure. The challenge is to make it legible--to expose structure and intent clearly--without
making it brittle or overly rigid. And to evolve it--adapting it to new contexts or needs--without erasing the historical
layers that give it meaning.

[^ub]: Uppsala University Library: https://www.uu.se/en/library.


### References

* Conway, M. E. (1968). How do committees invent? *Datamation*, 14(4), 28–31.

* Dijkstra, E. W. (1968). Go to statement considered harmful. *Communications of the ACM*, 11(3), 147–148. https://doi.org/10.1145/362929.362947

* Dijkstra, E. W. (1972). The humble programmer. *Communications of the ACM*, 15(10), 859–866. https://doi.org/10.1145/355604.361591

* Fielding, R. T. (2000). *Architectural styles and the design of network-based software architectures* (Doctoral dissertation). University of California, Irvine. 

* Kleinrock, L. (1964). *Communication nets: Stochastic message flow and delay*. New York: McGraw-Hill.

* Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623



