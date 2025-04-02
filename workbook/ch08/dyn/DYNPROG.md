
## Dynamic Programming: Two Approaches to Fibonacci

Here is a C implementation of the Fibonacci sequence using dynamic programming
with both *memoization* (top-down approach) and *tabulation* (bottom-up approach).


### Memoization (Top-Down)

This approach uses recursion with an array to store previously computed values,
avoiding redundant calculations.

```c
#include <stdio.h>

#define MAX 100

int fibMemo[MAX];

int fibonacci(int n) {
    if (n <= 1) 
        return n;
    if (fibMemo[n] != -1) 
        return fibMemo[n];
    
    fibMemo[n] = fibonacci(n - 1) + fibonacci(n - 2);
    return fibMemo[n];
}

int main() {
    int n = 10; // compute Fibonacci number
    for (int i = 0; i < MAX; i++)
        fibMemo[i] = -1; // init memoization array with -1
    
    printf("Fibonacci(%d) = %d\n", n, fibonacci(n));
    return 0;
}
```


### Tabulation (Bottom-Up)

This approach iteratively builds up the solution using an array.

```c
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1) 
        return n;

    int fib[n + 1];
    fib[0] = 0;
    fib[1] = 1;

    for (int i = 2; i <= n; i++) 
        fib[i] = fib[i - 1] + fib[i - 2];

    return fib[n];
}

int main() {
    int n = 10; // compute ¨Fibonacci number
    printf("Fibonacci(%d) = %d\n", n, fibonacci(n));
    return 0;
}
```

### Optimized Tabulation (Space-Efficient)

Since we only need the last two Fibonacci numbers at any time,
we can optimise space usage.

```c
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1) 
        return n;

    int a = 0, b = 1, c;
    
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    
    return b;
}

int main() {
    int n = 10; // compute Fibonacci number
    printf("Fibonacci(%d) = %d\n", n, fibonacci(n));
    return 0;
}
```

The *memoization* approach is useful when solving problems with recursion and
overlapping subproblems, while *tabulation* is generally more efficient in terms
of execution speed. The optimised tabulation approach minimises *memory usage*.
