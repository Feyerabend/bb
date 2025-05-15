
## C Project

> [!WARNING]  
> In this example the (file) *structure* is the important focus, and __not__ the *implementation*.
> Actual code might therefore not be correct or even compile. You might undertake this as a task to do!

### Core Concepts

| Concept | Scope | Example (C Project) | Relation to API |
|---------|-------|---------------------|-----------------|
| *Module* | Smallest unit (.c/.h pair) | `arithmetic.c` | Implements internal functionality |
| *Component* | Related modules (folder) | `core/` | Organises modules by concern |
| *Library* | Reusable compiled code | `libccalc.a` | A deliverable exposing an API |
| *API* | Interface (contract) | `ccalc.h` | Defines how users interact with the library |

API = *Public contract*  
Library = *Concrete deliverable*  
Modules/Components = *Internal implementation*


### Project Structure
```
ccalc/
├── src/
│   ├── core/               # Core calculator engine
│   │   ├── arithmetic.c    # Module
│   │   ├── arithmetic.h
│   │   ├── advanced.c      # Module
│   │   ├── advanced.h
│   │   ├── fixedpoint.c    # Module
│   │   └── fixedpoint.h
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
│   ├── test_fixedpoint.c
│   └── test_cli.c
├── build/
├── Makefile
└── README.md
```

| Path | Type | Role / Purpose |
|------|------|----------------|
| `core/arithmetic.c` | Module | Implements +, −, ×, ÷ |
| `core/advanced.c` | Module | Implements sin, cos, log |
| `core/fixedpoint.c` | Module | Implements 16.16 fixed-point arithmetic |
| `core/` | Component | Core calculator logic |
| `ui/cli.c` | Module | CLI interface (parse args, display) |
| `ui/` | Component | User Interface |
| `utils/logger.c` | Module | Logging helpers |
| `utils/validators.c` | Module | Input validation |
| `utils/` | Component | Utility functions |
| `app.c` | Module | Application entry point |
| `include/ccalc.h` | Public API (Library interface) | Expose functions to users |
| `Makefile` | Build system | Build + Link everything |


### Example

#### Core Arithmetic Module
```c
// src/core/arithmetic.c
#include "arithmetic.h"

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    if (b == 0) {
        // in real code: you'd handle this error properly
        return 0;
    }
    return a / b;
}
```

```c
// src/core/arithmetic.h
#ifndef ARITHMETIC_H
#define ARITHMETIC_H

int add(int a, int b);
int subtract(int a, int b);
int multiply(int a, int b);
int divide(int a, int b);

#endif // ARITHMETIC_H
```

### Advanced Math Module
```c
// src/core/advanced.c
#include "advanced.h"
#include <math.h>

double sine(double angle) {
    return sin(angle);
}

double cosine(double angle) {
    return cos(angle);
}

double logarithm(double value, double base) {
    if (value <= 0 || base <= 0 || base == 1) {
        // in real code: you'd handle these errors properly
        return 0;
    }
    return log(value) / log(base);
}
```

```c
// src/core/advanced.h
#ifndef ADVANCED_H
#define ADVANCED_H

double sine(double angle);
double cosine(double angle);
double logarithm(double value, double base);

#endif // ADVANCED_H
```

#### Fixed-Point Module (16.16)
```c
// src/core/fixedpoint.c
#include "fixedpoint.h"

// 16.16 fixed point format: 16 bits for integer part, 16 bits for fractional part
typedef int32_t fixed_t;

// integer --> fixed point
fixed_t int_to_fixed(int i) {
    return i << 16;
}

// fixed point --> integer (truncates)
int fixed_to_int(fixed_t f) {
    return f >> 16;
}

// float --> fixed point
fixed_t float_to_fixed(float f) {
    return (fixed_t)(f * 65536.0f);
}

// fixed point --> float
float fixed_to_float(fixed_t f) {
    return f / 65536.0f;
}

// fixed-point addition
fixed_t fixed_add(fixed_t a, fixed_t b) {
    return a + b;
}

// fixed-point subtraction
fixed_t fixed_subtract(fixed_t a, fixed_t b) {
    return a - b;
}

// fixed-point multiplication
fixed_t fixed_multiply(fixed_t a, fixed_t b) {
    // use 64-bit arithmetic to avoid overflow
    int64_t result = (int64_t)a * (int64_t)b;
    return (fixed_t)(result >> 16);
}

// fixed-point division
fixed_t fixed_divide(fixed_t a, fixed_t b) {
    if (b == 0) {
        // division by zero
        return 0;
    }
    // pre-shift a to avoid overflow and maintain precision
    int64_t temp = (int64_t)a << 16;
    return (fixed_t)(temp / b);
}

// print fixed-point number
void fixed_print(fixed_t f) {
    int integer_part = fixed_to_int(f);
    int fractional_part = (int)(((f & 0xFFFF) * 10000) >> 16);
    printf("%d.%04d", integer_part, fractional_part);
}
```

```c
// src/core/fixedpoint.h
#ifndef FIXEDPOINT_H
#define FIXEDPOINT_H

#include <stdint.h>
#include <stdio.h>

typedef int32_t fixed_t;

fixed_t int_to_fixed(int i);
int fixed_to_int(fixed_t f);
fixed_t float_to_fixed(float f);
float fixed_to_float(fixed_t f);

fixed_t fixed_add(fixed_t a, fixed_t b);
fixed_t fixed_subtract(fixed_t a, fixed_t b);
fixed_t fixed_multiply(fixed_t a, fixed_t b);
fixed_t fixed_divide(fixed_t a, fixed_t b);

void fixed_print(fixed_t f);

#endif // FIXEDPOINT_H
```

#### Logger Module
```c
// src/utils/logger.c
#include "logger.h"
#include <stdio.h>
#include <time.h>
#include <stdarg.h>

static log_level_t current_log_level = LOG_INFO;

void set_log_level(log_level_t level) {
    current_log_level = level;
}

void log_message(log_level_t level, const char* format, ...) {
    if (level < current_log_level) {
        return;
    }
    
    time_t now;
    time(&now);
    char time_str[26];
    ctime_r(&now, time_str);
    time_str[24] = '\0'; // no newline
    
    const char* level_str;
    switch (level) {
        case LOG_DEBUG: level_str = "DEBUG"; break;
        case LOG_INFO:  level_str = "INFO"; break;
        case LOG_WARN:  level_str = "WARN"; break;
        case LOG_ERROR: level_str = "ERROR"; break;
        default:        level_str = "UNKNOWN";
    }
    
    printf("[%s] [%s] ", time_str, level_str);
    
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    
    printf("\n");
}
```

```c
// src/utils/logger.h
#ifndef LOGGER_H
#define LOGGER_H

typedef enum {
    LOG_DEBUG = 0,
    LOG_INFO  = 1,
    LOG_WARN  = 2,
    LOG_ERROR = 3
} log_level_t;

void set_log_level(log_level_t level);
void log_message(log_level_t level, const char* format, ...);

#define LOG_DEBUG(...) log_message(LOG_DEBUG, __VA_ARGS__)
#define LOG_INFO(...)  log_message(LOG_INFO, __VA_ARGS__)
#define LOG_WARN(...)  log_message(LOG_WARN, __VA_ARGS__)
#define LOG_ERROR(...) log_message(LOG_ERROR, __VA_ARGS__)

#endif // LOGGER_H
```

#### Validators Module
```c
// src/utils/validators.c
#include "validators.h"
#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>

bool is_valid_number(const char* str) {
    if (str == NULL || *str == '\0') {
        return false;
    }
    
    // check for valid sign
    if (*str == '+' || *str == '-') {
        str++;
    }
    
    // check for at least one digit
    bool has_digit = false;
    bool has_decimal = false;
    
    while (*str) {
        if (isdigit((unsigned char)*str)) {
            has_digit = true;
        } else if (*str == '.' && !has_decimal) {
            has_decimal = true;
        } else {
            return false;
        }
        str++;
    }
    
    return has_digit;
}

bool parse_int(const char* str, int* result) {
    if (!is_valid_number(str)) {
        return false;
    }
    
    char* end;
    errno = 0;
    long val = strtol(str, &end, 10);
    
    if (errno != 0 || end == str || *end != '\0') {
        return false;
    }
    
    if (val > INT_MAX || val < INT_MIN) {
        return false;
    }
    
    *result = (int)val;
    return true;
}

bool is_valid_operation(const char* op) {
    if (op == NULL) {
        return false;
    }
    
    return (strcmp(op, "add") == 0 ||
            strcmp(op, "sub") == 0 ||
            strcmp(op, "mul") == 0 ||
            strcmp(op, "div") == 0 ||
            strcmp(op, "sin") == 0 ||
            strcmp(op, "cos") == 0 ||
            strcmp(op, "log") == 0);
}
```

```c
// src/utils/validators.h
#ifndef VALIDATORS_H
#define VALIDATORS_H

#include <stdbool.h>

bool is_valid_number(const char* str);
bool parse_int(const char* str, int* result);
bool is_valid_operation(const char* op);

#endif // VALIDATORS_H
```

#### CLI Module
```c
// src/ui/cli.c
#include "cli.h"
#include "../core/arithmetic.h"
#include "../core/advanced.h"
#include "../core/fixedpoint.h"
#include "../utils/validators.h"
#include "../utils/logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void print_usage(const char* program_name) {
    printf("Usage: %s operation [arguments]\n", program_name);
    printf("Operations:\n");
    printf("  add a b        - Add two integers\n");
    printf("  sub a b        - Subtract b from a\n");
    printf("  mul a b        - Multiply two integers\n");
    printf("  div a b        - Divide a by b\n");
    printf("  sin angle      - Calculate sine of angle (in radians)\n");
    printf("  cos angle      - Calculate cosine of angle (in radians)\n");
    printf("  log value base - Calculate logarithm of value with given base\n");
    printf("  fixed op a b   - Perform operation (add,sub,mul,div) using 16.16 fixed-point\n");
}

bool process_args(int argc, char* argv[]) {
    if (argc < 2) {
        LOG_ERROR("No operation specified");
        print_usage(argv[0]);
        return false;
    }
    
    const char* operation = argv[1];
    
    if (!is_valid_operation(operation) && strcmp(operation, "fixed") != 0) {
        LOG_ERROR("Invalid operation: %s", operation);
        print_usage(argv[0]);
        return false;
    }
    
    // basic arithmetic
    if (strcmp(operation, "add") == 0 || 
        strcmp(operation, "sub") == 0 || 
        strcmp(operation, "mul") == 0 || 
        strcmp(operation, "div") == 0) {
        
        if (argc != 4) {
            LOG_ERROR("Arithmetic operations require exactly 2 arguments");
            return false;
        }
        
        int a, b, result;
        if (!parse_int(argv[2], &a) || !parse_int(argv[3], &b)) {
            LOG_ERROR("Invalid number format");
            return false;
        }
        
        if (strcmp(operation, "add") == 0) {
            result = add(a, b);
            printf("%d + %d = %d\n", a, b, result);
        } else if (strcmp(operation, "sub") == 0) {
            result = subtract(a, b);
            printf("%d - %d = %d\n", a, b, result);
        } else if (strcmp(operation, "mul") == 0) {
            result = multiply(a, b);
            printf("%d * %d = %d\n", a, b, result);
        } else if (strcmp(operation, "div") == 0) {
            if (b == 0) {
                LOG_ERROR("Division by zero");
                return false;
            }
            result = divide(a, b);
            printf("%d / %d = %d\n", a, b, result);
        }
        
        return true;
    }
    
    // advanced functions
    if (strcmp(operation, "sin") == 0 || strcmp(operation, "cos") == 0) {
        if (argc != 3) {
            LOG_ERROR("Trigonometric operations require exactly 1 argument");
            return false;
        }
        
        double angle = atof(argv[2]);
        double result;
        
        if (strcmp(operation, "sin") == 0) {
            result = sine(angle);
            printf("sin(%f) = %f\n", angle, result);
        } else {
            result = cosine(angle);
            printf("cos(%f) = %f\n", angle, result);
        }
        
        return true;
    }
    
    if (strcmp(operation, "log") == 0) {
        if (argc != 4) {
            LOG_ERROR("Logarithm operation requires exactly 2 arguments");
            return false;
        }
        
        double value = atof(argv[2]);
        double base = atof(argv[3]);
        
        if (value <= 0 || base <= 0 || base == 1) {
            LOG_ERROR("Invalid arguments for logarithm");
            return false;
        }
        
        double result = logarithm(value, base);
        printf("log_%f(%f) = %f\n", base, value, result);
        
        return true;
    }
    
    // fixed-point operations
    if (strcmp(operation, "fixed") == 0) {
        if (argc != 5) {
            LOG_ERROR("Fixed-point operation requires 3 arguments: operation and two numbers");
            return false;
        }
        
        const char* fixed_op = argv[2];
        float a = atof(argv[3]);
        float b = atof(argv[4]);
        
        fixed_t fixed_a = float_to_fixed(a);
        fixed_t fixed_b = float_to_fixed(b);
        fixed_t result;
        
        if (strcmp(fixed_op, "add") == 0) {
            result = fixed_add(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" + ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "sub") == 0) {
            result = fixed_subtract(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" - ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "mul") == 0) {
            result = fixed_multiply(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" * ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "div") == 0) {
            if (b == 0) {
                LOG_ERROR("Division by zero");
                return false;
            }
            result = fixed_divide(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" / ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else {
            LOG_ERROR("Invalid fixed-point operation: %s", fixed_op);
            return false;
        }
        
        return true;
    }
    
    return false;
}
```

```c
// src/ui/cli.h
#ifndef CLI_H
#define CLI_H

#include <stdbool.h>

void print_usage(const char* program_name);
bool process_args(int argc, char* argv[]);

#endif // CLI_H
```

#### Main Application Entry Point

```c
// src/app.c
#include "ui/cli.h"
#include "utils/logger.h"
#include <stdlib.h>

int main(int argc, char* argv[]) {
    set_log_level(LOG_INFO);
    LOG_INFO("Starting ccalc application");
    
    if (!process_args(argc, argv)) {
        return EXIT_FAILURE;
    }
    
    LOG_INFO("Operation completed successfully");
    return EXIT_SUCCESS;
}
```

#### Public API Header

```c
// include/ccalc.h
#ifndef CCALC_H
#define CCALC_H

// core
#include "../src/core/arithmetic.h"
#include "../src/core/advanced.h"
#include "../src/core/fixedpoint.h"

// utilities (if needed by API users)
#include "../src/utils/logger.h"
#include "../src/utils/validators.h"

// library version information
#define CCALC_VERSION_MAJOR 1
#define CCALC_VERSION_MINOR 0
#define CCALC_VERSION_PATCH 0

// library initialization (if needed)
int ccalc_init(void);
void ccalc_cleanup(void);

#endif // CCALC_H
```


#### Makefile

```makefile
CC = gcc
CFLAGS = -Iinclude -Isrc -Wall -Wextra -Werror -pedantic -std=c11 -g
LDFLAGS = -lm

SRC_DIR = src
BUILD_DIR = build
BIN_DIR = bin
LIB_DIR = lib

# source files by component
CORE_SRCS = $(wildcard $(SRC_DIR)/core/*.c)
UI_SRCS = $(wildcard $(SRC_DIR)/ui/*.c)
UTILS_SRCS = $(wildcard $(SRC_DIR)/utils/*.c)
APP_SRC = $(SRC_DIR)/app.c

# object files
CORE_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(CORE_SRCS))
UI_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(UI_SRCS))
UTILS_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(UTILS_SRCS))
APP_OBJ = $(BUILD_DIR)/app.o

# library and executable targets
LIB_TARGET = $(LIB_DIR)/libccalc.a
EXE_TARGET = $(BIN_DIR)/ccalc

# test files
TEST_SRCS = $(wildcard tests/*.c)
TEST_OBJS = $(patsubst tests/%.c,$(BUILD_DIR)/tests/%.o,$(TEST_SRCS))
TEST_BINS = $(patsubst tests/%.c,$(BIN_DIR)/tests/%,$(TEST_SRCS))

# all targets
.PHONY: all clean test dirs

all: dirs $(LIB_TARGET) $(EXE_TARGET) test

# create necessary directories
dirs:
	mkdir -p $(BUILD_DIR)/core $(BUILD_DIR)/ui $(BUILD_DIR)/utils $(BUILD_DIR)/tests $(BIN_DIR)/tests $(LIB_DIR)

# rules for building object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/tests/%.o: tests/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# build the static library
$(LIB_TARGET): $(CORE_OBJS) $(UTILS_OBJS)
	ar rcs $@ $^

# build the executable
$(EXE_TARGET): $(APP_OBJ) $(UI_OBJS) $(LIB_TARGET)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# build and run tests
test: $(TEST_BINS)
	@echo "Running tests..."
	@for test in $(TEST_BINS); do \
		echo "Running $$test..."; \
		$$test; \
	done

$(BIN_DIR)/tests/%: $(BUILD_DIR)/tests/%.o $(LIB_TARGET)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) $(LIB_DIR)
```


#### Example Test File

```c
// tests/test_fixedpoint.c
#include "../src/core/fixedpoint.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>

#define EPSILON 0.0001

void test_conversions() {
    printf("Testing fixed-point conversions...\n");
    
    // Test integer conversions
    fixed_t a = int_to_fixed(5);
    assert(fixed_to_int(a) == 5);
    
    // Test float conversions
    fixed_t b = float_to_fixed(3.25f);
    float b_float = fixed_to_float(b);
    assert(fabs(b_float - 3.25f) < EPSILON);
    
    // Test negative values
    fixed_t c = int_to_fixed(-10);
    assert(fixed_to_int(c) == -10);
    
    fixed_t d = float_to_fixed(-7.5f);
    float d_float = fixed_to_float(d);
    assert(fabs(d_float - (-7.5f)) < EPSILON);
    
    printf("Conversion tests passed!\n");
}

void test_operations() {
    printf("Testing fixed-point operations...\n");
    
    // Test addition
    fixed_t a = float_to_fixed(5.25f);
    fixed_t b = float_to_fixed(3.75f);
    
    fixed_t sum = fixed_add(a, b);
    float sum_float = fixed_to_float(sum);
    assert(fabs(sum_float - 9.0f) < EPSILON);
    
    // Test subtraction
    fixed_t diff = fixed_subtract(a, b);
    float diff_float = fixed_to_float(diff);
    assert(fabs(diff_float - 1.5f) < EPSILON);
    
    // Test multiplication
    fixed_t prod = fixed_multiply(a, b);
    float prod_float = fixed_to_float(prod);
    assert(fabs(prod_float - 19.6875f) < EPSILON);
    
    // Test division
    fixed_t quot = fixed_divide(a, b);
    float quot_float = fixed_to_float(quot);
    assert(fabs(quot_float - 1.4f) < EPSILON);
    
    printf("Operation tests passed!\n");
}

int main() {
    printf("Running fixed-point tests...\n");
    
    test_conversions();
    test_operations();
    
    printf("All fixed-point tests passed!\n");
    
    return 0;
}
```


#### Example Usage

```c
// example_usage.c
#include "ccalc.h"
#include <stdio.h>

int main() {
    // Integer arithmetic
    int a = 10, b = 3;
    printf("Integer arithmetic:\n");
    printf("%d + %d = %d\n", a, b, add(a, b));
    printf("%d - %d = %d\n", a, b, subtract(a, b));
    printf("%d * %d = %d\n", a, b, multiply(a, b));
    printf("%d / %d = %d\n", a, b, divide(a, b));
    
    // Advanced math
    double angle = 0.5;
    printf("\nAdvanced math:\n");
    printf("sin(%f) = %f\n", angle, sine(angle));
    printf("cos(%f) = %f\n", angle, cosine(angle));
    printf("log_10(100) = %f\n", logarithm(100, 10));
    
    // Fixed-point math
    printf("\nFixed-point (16.16) math:\n");
    fixed_t fp_a = float_to_fixed(3.14159f);
    fixed_t fp_b = float_to_fixed(2.71828f);
    
    printf("Value a = ");
    fixed_print(fp_a);
    printf("\nValue b = ");
    fixed_print(fp_b);
    
    printf("\na + b = ");
    fixed_print(fixed_add(fp_a, fp_b));
    
    printf("\na * b = ");
    fixed_print(fixed_multiply(fp_a, fp_b));
    
    // Logging examples
    printf("\n\nLogging examples:\n");
    set_log_level(LOG_DEBUG);
    LOG_DEBUG("This is a debug message");
    LOG_INFO("This is an info message");
    LOG_WARN("This is a warning message");
    LOG_ERROR("This is an error message");
    
    return 0;
}
```


### Design Principles

#### Modularity
- Each module (.c/.h pair) has a single responsibility
- Modules expose minimal interfaces through header files
- Implementation details are hidden in .c files

#### Component Organisation
- Related modules are grouped into components (directories)
- Components form logical subsystems (core, ui, utils)
- Components may have internal APIs for communication

#### Library Design
- Public API is defined in a central header (ccalc.h)
- Implementation details are hidden from library users
- Library provides a stable interface contract

#### API Best Practices
- Clear function naming conventions
- Consistent error handling patterns
- Proper use of types and documentation
- Versioning information for compatibility

#### Build System
- Manages dependencies between components
- Produces both library (.a) and executable outputs
- Supports automated testing
- Provides clean targets for maintenance
