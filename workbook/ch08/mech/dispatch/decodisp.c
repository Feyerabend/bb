#include <stdio.h>
#include <string.h>

typedef int (*Operation)(int, int);

typedef struct {
    const char *name;
    Operation func;
} DispatchEntry;

DispatchEntry dispatch_table[10];
int dispatch_count = 0;

void register_op(const char *name, Operation func) {
    dispatch_table[dispatch_count].name = name;
    dispatch_table[dispatch_count].func = func;
    dispatch_count++;
}

int add(int a, int b) { return a + b; }
int subtract(int a, int b) { return a - b; }

void init_dispatch() {
    register_op("add", add);
    register_op("subtract", subtract);
}

Operation find_operation(const char *name) {
    for (int i = 0; i < dispatch_count; i++) {
        if (strcmp(name, dispatch_table[i].name) == 0) {
            return dispatch_table[i].func;
        }
    }
    return NULL;
}

int main() {
    init_dispatch();
    Operation op = find_operation("add");
    if (op) printf("%d\n", op(2, 3)); // Output: 5
    return 0;
}