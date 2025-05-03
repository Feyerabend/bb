# From Basics To Bytecode: A guide to computers and programming
# Workbook


| Concept | Scope | Example (C Project) | Relation to API |
|---------|-------|---------------------|-----------------|
| *Module* | Smallest unit (.c/.h pair) | `arithmetic.c` | Implements internal functionality |
| *Component* | Related modules (folder) | `core/` | Organises modules by concern |
| *Library* | Reusable compiled code | `libccalc.a` | A deliverable exposing an API |
| *API* | Interface (contract) | `ccalc.h` | Defines how users interact with the library |

API = *Public contract*  
Library = *Concrete deliverable*  
Modules/Components = *Internal implementation*


