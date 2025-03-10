#include <stdio.h>
#include <setjmp.h>

// co state
typedef struct {
    jmp_buf env;      // environment for saving/restoring execution state
    int state;        // current state of the coroutine
    int value;        // value to yield/receive
} coroutine_t;

// frwd decl.
void coroutine_yield(coroutine_t *co, int value);
int coroutine_resume(coroutine_t *co);

// example coroutine function
void example_coroutine(coroutine_t *co) {
    // 1st entry point
    coroutine_yield(co, 1);  // yield 1
    
    // resume point after 1st yield
    printf("Resumed after yielding 1\n");
    coroutine_yield(co, 2);  // yield 2
    
    // resume point after 2nd yield
    printf("Resumed after yielding 2\n");
    coroutine_yield(co, 3);  // yield 3 and finish
}

void coroutine_init(coroutine_t *co) {
    co->state = 0;
}

int coroutine_resume(coroutine_t *co) {
    if (co->state == 0) {
        // 1st call, init jump point
        co->state = 1;
        if (setjmp(co->env) == 0) {
            example_coroutine(co);
            // if coroutine returns without yielding
            return -1;
        }
    } else {
        // subsequent calls, jump back to where we yielded
        if (setjmp(co->env) == 0) {
            longjmp(co->env, 1);
        }
    }
    return co->value;
}

// yield from coroutine
void coroutine_yield(coroutine_t *co, int value) {
    co->value = value;
    longjmp(co->env, 1);
}

int main() {
    coroutine_t co;
    coroutine_init(&co);
    
    printf("Yielded: %d\n", coroutine_resume(&co));
    printf("Yielded: %d\n", coroutine_resume(&co));
    printf("Yielded: %d\n", coroutine_resume(&co));
    
    return 0;
}
