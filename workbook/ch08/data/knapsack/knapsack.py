# Recursive approach
def knapsack_recursive(W, wt, val, n):
    # Base case
    if n == 0 or W == 0:
        return 0
    
    # If weight of item is more than capacity, skip it
    if wt[n-1] > W:
        return knapsack_recursive(W, wt, val, n-1)
    
    # Return maximum of two cases:
    # 1. Item n-1 included
    # 2. Item n-1 not included
    else:
        return max(val[n-1] + knapsack_recursive(W - wt[n-1], wt, val, n-1),
                   knapsack_recursive(W, wt, val, n-1))


# Dynamic programming approach
def knapsack_dp(W, wt, val, n):
    # Initialize the table
    K = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    
    # Build table K[][] in bottom-up manner
    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
            elif wt[i-1] <= w:
                K[i][w] = max(val[i-1] + K[i-1][w-wt[i-1]], K[i-1][w])
            else:
                K[i][w] = K[i-1][w]
    
    # Trace back to find the selected items
    selected_items = []
    i, w = n, W
    while i > 0 and w > 0:
        if K[i][w] != K[i-1][w]:
            selected_items.append(i-1)
            w -= wt[i-1]
        i -= 1
    
    return K[n][W], selected_items


# Example usage
if __name__ == "__main__":
    val = [60, 100, 120]
    wt = [10, 20, 30]
    W = 50
    n = len(val)
    
    print(f"Recursive approach result: {knapsack_recursive(W, wt, val, n)}")
    
    max_value, selected = knapsack_dp(W, wt, val, n)
    print(f"Dynamic programming approach result: {max_value}")
    print(f"Selected items (0-indexed): {selected}")
