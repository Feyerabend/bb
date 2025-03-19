
## Knaopsack

The *Knapsack Problem* is a classic optimisation problem in computer science and mathematics.
It derives its name from the scenario of a hiker trying to pack the most valuable items into
a knapsack without exceeding its weight limit. The problem has wide-ranging applications,
including resource allocation, financial portfolio optimization, and logistics.


### History of the Knapsack Problem

1. *Origins*:
   - The Knapsack Problem was first formally introduced in the late 19th century by *Tobias Dantzig*,
     who described it as a problem of selecting the most valuable items to carry in a knapsack without
     exceeding its weight capacity.

2. *Mathematical Formulation*:
   - The problem was later formalized in the 20th century as part of operations research and combinatorial
     optimisation.

3. *Applications*:
   - The Knapsack Problem has been applied in various fields, including:
     - *Finance*: Selecting investments to maximize returns without exceeding a budget.
     - *Logistics*: Packing cargo into containers or trucks.
     - *Cryptography*: Designing secure systems based on hard-to-solve instances of the problem.

4. *Complexity*:
   - The Knapsack Problem is *NP-Complete*, meaning there is no known polynomial-time solution for all
     cases. However, efficient algorithms exist for specific variants.


### Problem Definition

Given:
- A set of items, each with a *weight* and a *value*.
- A knapsack with a maximum *weight capacity*.

Goal:
- Select a subset of items to maximize the total value without exceeding the knapsack's weight capacity.


### Variants of the Knapsack Problem

1. *0/1 Knapsack Problem*:
   - Each item can be either included (1) or excluded (0) from the knapsack.

2. *Fractional Knapsack Problem*:
   - Items can be divided, allowing fractional amounts to be included.

3. *Unbounded Knapsack Problem*:
   - There is no limit to the number of copies of each item that can be included.

4. *Multiple Knapsack Problem*:
   - Multiple knapsacks are available, each with its own capacity.


### Solutions to the Knapsack Problem

#### 1. Dynamic Programming (0/1 Knapsack)

The *0/1 Knapsack Problem* can be solved using dynamic programming. The idea is to build a table where
each cell `dp[i][w]` represents the maximum value achievable with the first `i` items and a knapsack
capacity of `w`.


### Implementation in C (0/1 Knapsack)

```c
#include <stdio.h>
#include <stdlib.h>

// Function to return the maximum of two integers
int max(int a, int b) {
    return (a > b) ? a : b;
}

// Function to solve the 0/1 Knapsack problem
int knapsack(int capacity, int weights[], int values[], int n) {
    int dp[n + 1][capacity + 1];

    // Build the DP table
    for (int i = 0; i <= n; i++) {
        for (int w = 0; w <= capacity; w++) {
            if (i == 0 || w == 0) {
                dp[i][w] = 0;  // Base case: no items or no capacity
            } else if (weights[i - 1] <= w) {
                dp[i][w] = max(values[i - 1] + dp[i - 1][w - weights[i - 1]], dp[i - 1][w]);
            } else {
                dp[i][w] = dp[i - 1][w];
            }
        }
    }

    return dp[n][capacity];
}

int main() {
    int values[] = {60, 100, 120};
    int weights[] = {10, 20, 30};
    int capacity = 50;
    int n = sizeof(values) / sizeof(values[0]);

    printf("Maximum value in Knapsack: %d\n", knapsack(capacity, weights, values, n));

    return 0;
}
```


### Implementation in Python (0/1 Knapsack)

```python
def knapsack(capacity, weights, values, n):
    # Create a DP table
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # Build the DP table
    for i in range(n + 1):
        for w in range(capacity + 1):
            if i == 0 or w == 0:
                dp[i][w] = 0  # Base case: no items or no capacity
            elif weights[i - 1] <= w:
                dp[i][w] = max(values[i - 1] + dp[i - 1][w - weights[i - 1]], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]

    return dp[n][capacity]

# Example usage
values = [60, 100, 120]
weights = [10, 20, 30]
capacity = 50
n = len(values)

print("Maximum value in Knapsack:", knapsack(capacity, weights, values, n))
```


### Explanation of the Dynamic Programming Approach

1. *DP Table*:
   - `dp[i][w]` stores the maximum value achievable with the first `i` items and a knapsack capacity of `w`.

2. *Base Case*:
   - If there are no items (`i == 0`) or no capacity (`w == 0`), the maximum value is `0`.

3. *Recurrence Relation*:
   - If the current item's weight is less than or equal to the remaining capacity, choose the maximum between:
     - Including the item: `values[i - 1] + dp[i - 1][w - weights[i - 1]]`
     - Excluding the item: `dp[i - 1][w]`
   - Otherwise, exclude the item.

4. *Result*:
   - The value `dp[n][capacity]` gives the maximum value achievable.


#### 2. Greedy Algorithm (Fractional Knapsack)

The *Fractional Knapsack Problem* can be solved using a *greedy algorithm*.
The idea is to prioritize items with the highest value-to-weight ratio.


### Implementation in Python (Fractional Knapsack)

```python
def fractional_knapsack(capacity, weights, values):
    # Calculate value-to-weight ratio for each item
    items = list(zip(values, weights))
    items.sort(key=lambda x: x[0] / x[1], reverse=True)  # Sort by ratio in descending order

    total_value = 0
    for value, weight in items:
        if capacity >= weight:
            total_value += value
            capacity -= weight
        else:
            total_value += (capacity / weight) * value
            break

    return total_value

# Example usage
values = [60, 100, 120]
weights = [10, 20, 30]
capacity = 50

print("Maximum value in Fractional Knapsack:", fractional_knapsack(capacity, weights, values))
```


### Explanation of the Greedy Approach

1. *Value-to-Weight Ratio*:
   - Calculate the ratio of value to weight for each item.

2. *Sorting*:
   - Sort the items in descending order of their value-to-weight ratio.

3. *Greedy Selection*:
   - Add items to the knapsack in order of priority, taking as much as possible of each item.

4. *Fractional Inclusion*:
   - If the remaining capacity is less than the weight of the current item, take a fraction of it.


### Takeaways

1. *0/1 Knapsack*:
   - Solved using dynamic programming.
   - Time Complexity: \(O(n \cdot W)\), where \(n\) is the number of items and \(W\) is the capacity.

2. *Fractional Knapsack*:
   - Solved using a greedy algorithm.
   - Time Complexity: \(O(n \log n)\) due to sorting.

3. *Applications*:
   - Resource allocation, financial optimization, and logistics.
