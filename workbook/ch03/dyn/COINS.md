
## Coins

Given a set of coins with different denominations and a total amount, determine the minimum
number of coins needed to make that amount. If it's not possible, return -1.

For example, given coins [1, 3, 4] and an amount of 6, the minimum number of coins is 2
(using 3 + 3 or 4 + 1 + 1).

A naïve recursive approach would try every possible combination, leading to an exponential
time complexity. However, we notice that solving amount 6 relies on solving smaller amounts
like 5, 3, and 2--making it a classic overlapping subproblems scenario, ideal for DP.

Let dp[i] represent the minimum number of coins required to make amount i.


#### Bottom-Up (Tabulation) Approach

We iteratively compute the solution for all amounts up to 6, using previously computed values.

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # base case: 0 coins needed for amount 0

    for i in range(1, amount + 1):
        for coin in coins:
            if i >= coin:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

How It Works
1. Start with an array `dp` where `dp[i]` is initialized to infinity, meaning the amount is initially unreachable.
2. Set `dp[0] = 0` because no coins are needed to make amount 0.
3. Iterate through all amounts from 1 to amount, updating `dp[i]` by checking all possible coins.
4. The final result is stored in `dp[amount]`.

Time and Space Complexity
- Time Complexity:  $\`O(n \cdot m)\`$ where n is the target amount and m is the number of coins.
- Space Complexity: $\`O(n)\`$ since we store results for all amounts up to amount.


#### Top-Down (Memoization) Approach

Alternatively, we use recursion with memoization.

```python
def coin_change_memo(coins, amount, memo={}):
    if amount in memo:
        return memo[amount]
    if amount == 0:
        return 0
    if amount < 0:
        return float('inf')

    min_coins = float('inf')
    for coin in coins:
        res = coin_change_memo(coins, amount - coin, memo)
        if res != float('inf'):
            min_coins = min(min_coins, res + 1)

    memo[amount] = min_coins
    return min_coins if min_coins != float('inf') else -1
```

Comparing Approaches
- Tabulation is often faster because it avoids recursive overhead.
- Memoization is easier to understand and more intuitive.
