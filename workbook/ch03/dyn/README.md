
## Dynamic Programming

Dynamic Programming (DP) is an optimisation technique used for solving problems that can
be broken down into overlapping subproblems with optimal substructure. It is particularly
useful for problems where a naïve recursive approach would lead to excessive recomputation
and inefficiency. Instead of recalculating results repeatedly, DP stores computed results
(memoization) or builds solutions iteratively (tabulation).


### What is Dynamic Programming?

Dynamic Programming is a method for solving complex problems by breaking them into smaller
subproblems, solving each subproblem once, and storing the results to avoid redundant work.
It is often used in optimisation problems where multiple decisions must be made, and the
goal is to find the best possible outcome.


### Why Dynamic Programming?

The motivation for DP comes from the inefficiency of recursive solutions in problems with
overlapping subproblems. For example, in computing Fibonacci numbers using a basic recursive
approach:

```math
F(n) = F(n-1) + F(n-2)
```
the number of redundant computations grows exponentially. DP transforms such problems into
polynomial time by reusing previously computed values.


### How Does Dynamic Programming Work?

Dynamic programming works by solving subproblems in a systematic way. There are two common
approaches:

1. __Top-Down (Memoization)__: This is a recursive approach where we solve a problem as usual
but store results of already computed subproblems in a table (often a dictionary or array)
to avoid redundant calculations.

```python
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

2. __Bottom-Up (Tabulation)__: This approach iteratively builds up the solution from base cases
without using recursion, often leading to better performance.

```python
def fib(n):
    if n <= 1:
        return n
    dp = [0] * (n+1)
    dp[1] = 1
    for i in range(2, n+1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```


Here is a C implementation of the Fibonacci sequence using dynamic programming
with both *memoization* (top-down approach) and *tabulation* (bottom-up approach).


4. __Memoization (Top-Down)__

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


4. __Tabulation (Bottom-Up)__

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

5. __Optimised Tabulation (Space-Efficient)__

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

A very similar example can be found in [COINS](./COINS.md).


### Variations of Dynamic Programming

Dynamic Programming appears in different forms depending on the nature of the problem:
1. Linear DP: Problems where decisions are made in a linear sequence, such as Fibonacci,
   coin change, and knapsack problems.
2. Grid-Based DP: Used in pathfinding and combinatorial problems, like computing the number
   of ways to traverse a grid.
3. Tree-Based DP: Applied to problems involving trees, such as computing the longest path
   in a tree.
4. Bitmask DP: Used in combinatorial problems that involve subsets, often seen in the
   Traveling Salesman Problem (TSP).
5. Interval DP: Used in segment-based problems, like matrix chain multiplication.
6. State-Based DP: Applied in problems where multiple attributes define a state, such as
   dynamic programming in artificial intelligence or Markov Decision Processes (MDPs).


### Considerations When Building Dynamic Programs
1. Identifying Overlapping Subproblems: DP is only effective when the problem contains
   subproblems that repeat.
2. Defining the State: Clearly define what information needs to be stored to avoid
   recomputation.
3. Choosing Between Memoization and Tabulation: Recursive memoization is easier to
   implement but may cause stack overflow for large inputs. Tabulation avoids recursion
   but requires careful initialisation.
4. Optimising Space Complexity: Many DP solutions can be improved by reducing storage
   from `O(n)` to `O(1)`, as in Fibonacci where only two previous values need to be stored.
5. Understanding Order of Computation: Some problems require computing subproblems
   in a specific order to ensure correct results.


### Advanced Dynamic Programming

A much more advanced example can be seen in [GRID](./GRID.md) on State DP and
Q-Learing. There are some suggested [projects](./PROJECTS.md) for DP, where a
sample solution is in [ELEV](./ELEV.md) of reinforcement learning for an elevator
optimising movements.

