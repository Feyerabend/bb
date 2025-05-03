# From Basics To Bytecode: A guide to computers and programming
# Workbook


software engineering elements




| Concept | Scope | Example (C Project) | Relation to API |
|---------|-------|---------------------|-----------------|
| *Module* | Smallest unit (.c/.h pair) | `arithmetic.c` | Implements internal functionality |
| *Component* | Related modules (folder) | `core/` | Organises modules by concern |
| *Library* | Reusable compiled code | `libccalc.a` | A deliverable exposing an API |
| *API* | Interface (contract) | `ccalc.h` | Defines how users interact with the library |

API = *Public contract*  
Library = *Concrete deliverable*  
Modules/Components = *Internal implementation*



broader but not all included

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
| *Configuration* | Behavior customisation | Small-large | YAML config |


