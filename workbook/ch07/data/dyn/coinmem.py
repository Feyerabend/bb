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


if __name__ == "__main__":
    coins = [1, 2, 5]
    amount = 11
    result = coin_change_memo(coins, amount)
    if result != -1:
        print(f"The minimum number of coins needed to make {amount} is {result}.")
    else:
        print(f"It's not possible to make {amount} with the given coins.")

