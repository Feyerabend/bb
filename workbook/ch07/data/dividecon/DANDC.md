
## A practical comparison between *Dynamic Programming (DP)* and *Divide-and-Conquer (D&C)*.

| Feature | Divide-and-Conquer | Dynamic Programming (DP) |
|---|---|---|
| Core Idea                      | Divide --> Solve subproblems --> Combine            | Break into subproblems --> Remember answers --> Reuse |
| Do subproblems overlap?        | *No* (usually independent)                    | *Yes* (lots of repeated subproblems)           |
| Do we store intermediate results? | Usually *no* (recompute them)               | *Yes* — in a table (memoization or tabulation) |
| Recursion style                | Natural and clean                               | Also recursive, but we add caching               |
| Time Complexity (typical)      | O(n log n) for classic ones (MergeSort, QuickSort) | Often reduces from exponential --> polynomial     |
| Space Complexity               | O(log n) recursion stack (or O(1) iterative)    | O(n), O(n²), etc. for the DP table              |
| Classic Examples               | MergeSort, QuickSort, Binary Search, Strassen Matrix Mul, Closest Pair of Points | 0/1 Knapsack, Fibonacci, Longest Common Subsequence, Matrix Chain Multiplication, Edit Distance, Coin Change, Egg Dropping (optimized) |

### Real-World Examples Side-by-Side

| Problem | Naive / D&C approach | Why DP is better (or needed) | Final winner |
|---|---|---|
| Fibonacci(n)                   | Pure recursion --> 2ⁿ time                 | Same subproblems (Fib(n-2), etc.) computed millions of times --> DP in O(n) | *DP* |
| Longest Common Subsequence     | Try all possibilities --> exponential      | LCS(i,j) depends on LCS(i-1,j), LCS(i,j-1), etc. --> huge overlap --> DP table | *DP* |
| MergeSort                      | Recursively split and merge              | Subproblems are independent --> no benefit from storing --> D&C is perfect | *D&C* |
| Binary Search                  | Recursively halve the range              | No overlapping subproblems --> iterative or recursive D&C is best | *D&C* |
| 0/1 Knapsack                   | Recursion with choices --> 2ⁿ              | Same (weight, items) combinations recomputed --> DP table removes redundancy | *DP* |
| Minimum cost to reach top of stairs (2 or 3 steps) | Simple recursion works fine            | Slight overlap, but DP is still very easy and common | DP usually chosen for clarity |
| Finding maximum in an array    | Recursively split --> O(n)                 | No overlap at all --> just a simple loop is better | Simple loop (D&C idea but no recursion needed) |


### Quick Decision Cheat-Sheet

Ask yourself two questions:

1. *Are subproblems overlapping / repeated?*  

   --> Yes --> *Use Dynamic Programming*

   --> No --> *Use Divide-and-Conquer* (or even simpler greedy/loop)

2. *Do you need the optimal solution for every subproblem?*  

   --> Yes --> DP (store everything)  

   --> No, you only need to combine independent parts --> D&C


### One-Liner Summary

- *Divide-and-Conquer* = “Split into independent pieces, solve separately, combine.”

- *Dynamic Programming* = “Split into overlapping pieces, solve each only once, store and reuse.”


