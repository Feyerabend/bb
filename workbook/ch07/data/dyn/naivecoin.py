def coin_change(coins, amount):
    if amount == 0:
        return 0  # base case: no coins needed for amount 0
    if amount < 0:
        return float('inf')  # impossible case: return a large number

    min_coins = float('inf')

    for coin in coins:
        result = coin_change(coins, amount - coin)  # recursive call with reduced amount
        if result != float('inf'):
            min_coins = min(min_coins, result + 1)  # take the minimum

    return min_coins if min_coins != float('inf') else -1  # return -1 if no solution

coins = [1, 3, 4]
amount = 6
print(coin_change(coins, amount))  # Output: 2
