def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # base case: 0 coins needed for amount 0

    for i in range(1, amount + 1):
        for coin in coins:
            if i >= coin:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
def main():
    coins = [1, 2, 5]
    amount = 11
    result = coin_change(coins, amount)
    if result != -1:
        print(f"The minimum number of coins needed to make {amount} is {result}.")
    else:
        print(f"It is not possible to make {amount} with the given coins.")

if __name__ == "__main__":
    main()

# This code defines a function to find the minimum number of coins needed to make a given amount
# using a list of coin denominations. It uses dynamic programming to build up a solution.
# The function returns the minimum number of coins needed or -1 if it's not possible to make the amount.

# The sample input is coins = [1, 2, 5] and amount = 11.
# The expected output is "The minimum number of coins needed to make 11 is 3."

