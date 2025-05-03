
## 

| Concept | Scope | Example (C Project) | Relation to API |
|---------|-------|---------------------|-----------------|
| *Module* | Smallest unit (.c/.h pair) | `arithmetic.c` | Implements internal functionality |
| *Component* | Related modules (folder) | `core/` | Organises modules by concern |
| *Library* | Reusable compiled code | `libccalc.a` | A deliverable exposing an API |
| *API* | Interface (contract) | `ccalc.h` | Defines how users interact with the library |

API = *Public contract*  
Library = *Concrete deliverable*  
Modules/Components = *Internal implementation*

```
ccalc/
├── src/
│   ├── core/               # Core calculator engine
│   │   ├── arithmetic.c    # Module
│   │   ├── arithmetic.h
│   │   ├── advanced.c      # Module
│   │   └── advanced.h
│   ├── ui/                 # User interface
│   │   ├── cli.c           # Module
│   │   └── cli.h
│   ├── utils/              # Utilities
│   │   ├── logger.c        # Module
│   │   ├── logger.h
│   │   ├── validators.c    # Module
│   │   └── validators.h
│   ├── app.c               # Main entry point (Module)
├── include/                # Public headers (for library users)
│   └── ccalc.h
├── tests/
│   ├── test_arithmetic.c
│   ├── test_advanced.c
│   └── test_cli.c
├── build/
├── Makefile
└── README.md
```



| Path | Type | Role / Purpose |
|------|------|----------------|
| `core/arithmetic.c` | Module | Implements +, −, ×, ÷ |
| `core/advanced.c` | Module | Implements sin, cos, log |
| `core/` | Component | Core calculator logic |
| `ui/cli.c` | Module | CLI interface (parse args, display) |
| `ui/` | Component | User Interface |
| `utils/logger.c` | Module | Logging helpers |
| `utils/validators.c` | Module | Input validation |
| `utils/` | Component | Utility functions |
| `app.c` | Module | Application entry point |
| `include/ccalc.h` | Public API (Library interface) | Expose functions to users |
| `Makefile` | Build system | Build + Link everything |




```c
// src/core/arithmetic.c
#include "arithmetic.h"

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}
```
```c
// src/core/arithmetic.h
#ifndef ARITHMETIC_H
#define ARITHMETIC_H

int add(int a, int b);
int subtract(int a, int b);

#endif
```


```c
// include/ccalc.h
#ifndef CCALC_H
#define CCALC_H

#include "core/arithmetic.h"
#include "core/advanced.h"
#include "utils/logger.h"
#include "utils/validators.h"

#endif
```

```makefile
CC = gcc
CFLAGS = -Iinclude -Wall
SRC = src
OBJ = build

CORE_SRC = $(SRC)/core/arithmetic.c $(SRC)/core/advanced.c
UI_SRC = $(SRC)/ui/cli.c
UTILS_SRC = $(SRC)/utils/logger.c $(SRC)/utils/validators.c
APP_SRC = $(SRC)/app.c

ALL_SRC = $(CORE_SRC) $(UI_SRC) $(UTILS_SRC) $(APP_SRC)

TARGET = ccalc

$(TARGET): $(ALL_SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(ALL_SRC) -lm

clean:
	rm -f $(TARGET)
```



```c
#include "ccalc.h"
#include <stdio.h>

// usage
int main() {
    int a = 5, b = 3;
    printf("Add: %d\n", add(a, b));
    printf("Sub: %d\n", subtract(a, b));
    return 0;
}
```


- Module = .c + .h (one responsibility)
- Component = folder of related modules
- Library = public headers + compiled code (reusable)

Component:
- Groups related modules (e.g., core/ containing arithmetic.c, advanced.c, etc.)
- Represents a functional subsystem
- May have its own internal API (header files)
- Becomes a building block for libraries



