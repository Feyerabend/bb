
## Implementing Object-Oriented Programming in C with Coroutines

Using coroutines in C can significantly enhance object-oriented implementations by
providing elegant solutions for state management and behavior encapsulation. Since
C lacks native OOP features, coroutines can bridge this gap effectively.

We will look at some ideas presented through code. This might seem awkward as you usually
study language constructions from the top down. However, in this case, approaching the concept
from an example-driven perspective allows us to see the practical benefits before diving into
the underlying mechanisms.

One of the main challenges of implementing object-oriented behavior in C is maintaining
state across function calls while keeping the interface clean and intuitive. Coroutines
help achieve this by enabling functions to retain execution state between invocations,
allowing for more natural and modular design patterns.

We begin by implementing a simple coroutine mechanism using `setjmp` and `longjmp`.
These standard C functions allow us to save and restore execution context, mimicking
the behaviour of coroutine *suspension* and *resumption*.[^co] Consider the following example:

[^co]: *Suspension* happens when `setjmp` captures the execution state and allows the function to exit or pause. *Resumption* occurs when `longjmp` restores that state, allowing execution to continue from where it left off. This technique enables stateful function execution across multiple calls, similar to how coroutines work in languages with built-in support.

```c
#include <stdio.h>
#include <setjmp.h>

typedef struct {
    jmp_buf context;
    int state;
} Coroutine;

void coroutine_init(Coroutine *c) {
    c->state = 0;
}

void coroutine_function(Coroutine *c) {
    if (setjmp(c->context) == 0) return;
    switch (c->state) {
        case 0:
            printf("Step 1\n");
            c->state = 1;
            longjmp(c->context, 1);
        case 1:
            printf("Step 2\n");
            c->state = 2;
            longjmp(c->context, 1);
        case 2:
            printf("Done\n");
            return;
    }
}

int main() {
    Coroutine c;
    coroutine_init(&c);
    for (int i = 0; i < 3; i++) {
        coroutine_function(&c);
    }
    return 0;
}
```

This basic example illustrates how we can structure an object-like coroutine to maintain
execution state across function calls. Expanding on this idea, we can develop more
sophisticated coroutine-based patterns to encapsulate behavior in a way that mimics
object-oriented constructs in C. These patterns can serve both as conceptual tools for
implementing object-oriented features in language design and as practical techniques for
bringing object-oriented principles directly into C programming.


#### 1. Object State Management

Coroutines naturally maintain their state between invocations, providing a mechanism
similar to object state:

```c
typedef struct {
    jmp_buf env;
    int state;
    int current_value;

    // object-specific properties
    int start;
    int increment;
} counter_t;

void counter_init(counter_t* self, int start, int increment) {
    self->state = 0;
    self->start = start;
    self->increment = increment;
    self->current_value = start;
}

void counter_next(counter_t* self) {
    if (self->state == 0) {
        self->state = 1;
        if (setjmp(self->env) == 0) {
            // first execution
            self->current_value = self->start;
            longjmp(self->env, 1);  // return control
        }
    } else {
        // resume execution
        self->current_value += self->increment;
    }
}
```


#### 2. Method Implementation via Continuations

Coroutines can simulate methods that preserve their execution context:

```c
typedef struct {
    jmp_buf env;
    int state;
    char* buffer;
    size_t position;
    size_t capacity;
} string_builder_t;

void string_builder_init(string_builder_t* self, size_t capacity) {
    self->state = 0;
    self->buffer = (char*)malloc(capacity);
    self->position = 0;
    self->capacity = capacity;
}

int string_builder_append(string_builder_t* self, const char* str) {
    size_t len = strlen(str);
    
    if (self->position + len >= self->capacity) {
        // "Method" handles its own error condition
        return -1;
    }
    
    strcpy(self->buffer + self->position, str);
    self->position += len;
    
    return 0;
}
```


#### 3. Implementing Iterators with Coroutines

Coroutines excel at implementing iterators, a key OOP pattern:

```c
typedef struct {
    jmp_buf env;
    int state;
    int value;
    
    // iterator properties
    int* array;
    size_t size;
    size_t current;
} array_iterator_t;

void iterator_init(array_iterator_t* self, int* array, size_t size) {
    self->state = 0;
    self->array = array;
    self->size = size;
    self->current = 0;
}

int iterator_has_next(array_iterator_t* self) {
    return self->current < self->size;
}

int iterator_next(array_iterator_t* self) {
    if (!iterator_has_next(self)) {
        // return error or sentinel
        return -1;
    }
    
    self->value = self->array[self->current++];
    return self->value;
}
```


#### 4. Implementing State Machines with Coroutines

Complex object behaviors can be modeled as state machines:

```c
typedef enum {
    STATE_CREATED,
    STATE_INITIALIZED,
    STATE_RUNNING,
    STATE_PAUSED,
    STATE_STOPPED
} process_state_t;

typedef struct {
    jmp_buf context;
    int coroutine_state;
    
    // object properties
    process_state_t state;
    void* data;
    size_t data_size;
} process_t;

void process_init(process_t* self, void* data, size_t data_size) {
    self->coroutine_state = 0;
    self->state = STATE_CREATED;
    self->data = malloc(data_size);
    memcpy(self->data, data, data_size);
    self->data_size = data_size;
}

int process_run(process_t* self) {
    if (self->coroutine_state == 0) {
        // first entry
        self->coroutine_state = 1;
        self->state = STATE_INITIALIZED;
        
        if (setjmp(self->context) == 0) {
            // initial setup work
            self->state = STATE_RUNNING;
            longjmp(self->context, 1);  // yield
            
            // process first part of data
            // ..
            self->state = STATE_PAUSED;
            longjmp(self->context, 1);  // yield
            
            // process second part of data
            // ..
            self->state = STATE_STOPPED;
            return 0;
        }
    } else {
        // resume execution where we left off
        // works?
        if (setjmp(self->context) == 0) {
            longjmp(self->context, 1);
        }
    }
    
    return self->state == STATE_STOPPED ? 0 : 1;
}
```


#### 5. Implementing Inheritance with Coroutines

Coroutines can help implement virtual methods and inheritance hierarchies:

```c
// base "class" structure
typedef struct {
    jmp_buf env;
    int state;
    
    // virtual method pointers
    void (*initialize)(void* self);
    int (*process)(void* self, void* data);
    void (*finalize)(void* self);
} base_object_t;

// "derived class" structure
typedef struct {
    base_object_t base;  // inheritance by embedding
    
    // additional properties
    int value;
    char* name;
} derived_object_t;

// virtual method implementations
void derived_initialize(void* self) {
    derived_object_t* obj = (derived_object_t*)self;
    obj->value = 0;
    obj->name = strdup("Default");
}

int derived_process(void* self, void* data) {
    derived_object_t* obj = (derived_object_t*)self;
    int* input = (int*)data;
    
    obj->value += *input;
    return obj->value;
}

void derived_finalize(void* self) {
    derived_object_t* obj = (derived_object_t*)self;
    free(obj->name);
}

// object creation function ("constructor")
derived_object_t* create_derived_object() {
    derived_object_t* obj = (derived_object_t*)malloc(sizeof(derived_object_t));
    
    // set up virtual method table
    obj->base.initialize = derived_initialize;
    obj->base.process = derived_process;
    obj->base.finalize = derived_finalize;
    
    obj->base.initialize(obj);
    
    return obj;
}
```


### Advantages of Coroutines for OOP in C

1. State Preservation: Coroutines naturally maintain their state between calls, similar to objects
2. Encapsulation: Related data and behavior can be grouped in structs and coroutines
3. Method Continuations: Allow complex behaviors to be expressed linearly despite being executed across multiple invocations
4. Internal Iteration: Enable elegant iteration patterns without exposing internal implementation
5. Clean Resource Management: Provide clear resource acquisition and release patterns similar to constructors/destructors


### Complete Example: File Processing Object in C

Here's a more complete example of an object-oriented file processor using coroutines:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

typedef struct {
    // coroutine state
    jmp_buf env;
    int state;
    
    // object properties
    FILE* file;
    char* filename;
    char buffer[1024];
    int line_count;
    int current_line;
    int is_open;
} file_processor_t;

// "constructor"
file_processor_t* file_processor_create(const char* filename) {
    file_processor_t* processor = (file_processor_t*)malloc(sizeof(file_processor_t));
    processor->state = 0;
    processor->filename = strdup(filename);
    processor->line_count = 0;
    processor->current_line = 0;
    processor->is_open = 0;
    processor->file = NULL;
    return processor;
}

// "destructor"
void file_processor_destroy(file_processor_t* self) {
    if (self->is_open && self->file) {
        fclose(self->file);
    }
    free(self->filename);
    free(self);
}

// open file "method"
int file_processor_open(file_processor_t* self) {
    if (self->is_open) return 1;
    
    self->file = fopen(self->filename, "r");
    if (!self->file) return 0;
    
    self->is_open = 1;
    return 1;
}

// count lines "method"
int file_processor_count_lines(file_processor_t* self) {
    if (!self->is_open) return -1;
    
    // reset file position
    rewind(self->file);
    
    self->line_count = 0;
    while (fgets(self->buffer, sizeof(self->buffer), self->file)) {
        self->line_count++;
    }
    
    return self->line_count;
}

// process each line with coroutine
int file_processor_process_lines(file_processor_t* self) {
    if (!self->is_open) return -1;
    
    if (self->state == 0) {
        // initial setup
        self->state = 1;
        self->current_line = 0;
        rewind(self->file);
        
        if (setjmp(self->env) == 0) {
            while (fgets(self->buffer, sizeof(self->buffer), self->file)) {
                self->current_line++;
                longjmp(self->env, 1);  // yield current line
            }
            self->state = 0;  // reset state when done
            return 0;  // no more lines
        }
    } else {
        // resume reading
        if (setjmp(self->env) == 0) {
            longjmp(self->env, 1);
        }
    }
    
    return 1;  // more lines ..
}

// example
int main() {
    file_processor_t* processor = file_processor_create("example.txt");
    
    if (!file_processor_open(processor)) {
        printf("Failed to open file\n");
        file_processor_destroy(processor);
        return 1;
    }
    
    int line_count = file_processor_count_lines(processor);
    printf("File has %d lines\n", line_count);
    
    printf("Processing file line by line:\n");
    while (file_processor_process_lines(processor)) {
        printf("Line %d: %s", processor->current_line, processor->buffer);
    }
    
    file_processor_destroy(processor);
    return 0;
}
```

This example demonstrates how coroutines can help implement a clean,
object-oriented approach in C with proper encapsulation, resource management,
and state preservation.
