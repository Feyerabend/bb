#include <stdio.h>
#include <stdlib.h>

/* fwd decl. */
int max(int a, int b);
int knapsack_recursive(int W, int wt[], int val[], int n);
int knapsack_dp(int W, int wt[], int val[], int n, int **selected, int *selected_count);

/* Util function to return maximum of two integers */
int max(int a, int b) {
    return (a > b) ? a : b;
}

/* Recursive */
int knapsack_recursive(int W, int wt[], int val[], int n) {
    /* Base case */
    if (n == 0 || W == 0) {
        return 0;
    }
    
    /* If weight of item is more than capacity, skip it */
    if (wt[n-1] > W) {
        return knapsack_recursive(W, wt, val, n-1);
    }
    
    /* Return maximum of two cases:
     * 1. Item n-1 included
     * 2. Item n-1 not included */
    else {
        return max(val[n-1] + knapsack_recursive(W - wt[n-1], wt, val, n-1),
                   knapsack_recursive(W, wt, val, n-1));
    }
}

/* Dynamic programming */
int knapsack_dp(int W, int wt[], int val[], int n, int **selected, int *selected_count) {
    int i, w;
    int **K;
    int max_value;
    
    /* Allocate memory for the table */
    K = (int **)malloc((n + 1) * sizeof(int *));
    for (i = 0; i <= n; i++) {
        K[i] = (int *)malloc((W + 1) * sizeof(int));
    }
    
    /* Build table K[][] in bottom-up manner */
    for (i = 0; i <= n; i++) {
        for (w = 0; w <= W; w++) {
            if (i == 0 || w == 0) {
                K[i][w] = 0;
            }
            else if (wt[i-1] <= w) {
                K[i][w] = max(val[i-1] + K[i-1][w-wt[i-1]], K[i-1][w]);
            }
            else {
                K[i][w] = K[i-1][w];
            }
        }
    }
    
    max_value = K[n][W];
    
    /* Trace back to find the selected items */
    *selected = (int *)malloc(n * sizeof(int));
    *selected_count = 0;
    i = n;
    w = W;
    
    while (i > 0 && w > 0) {
        if (K[i][w] != K[i-1][w]) {
            (*selected)[*selected_count] = i - 1;
            (*selected_count)++;
            w -= wt[i-1];
        }
        i--;
    }
    
    /* Free table */
    for (i = 0; i <= n; i++) {
        free(K[i]);
    }
    free(K);
    
    return max_value;
}


int main() {
    int val[] = {60, 100, 120};
    int wt[] = {10, 20, 30};
    int W = 50;
    int n = sizeof(val) / sizeof(val[0]);
    int *selected;
    int selected_count;
    int i;
    int result;
    
    /* Recursive approach */
    result = knapsack_recursive(W, wt, val, n);
    printf("Recursive approach result: %d\n", result);
    
    /* Dynamic programming approach */
    result = knapsack_dp(W, wt, val, n, &selected, &selected_count);
    printf("Dynamic programming approach result: %d\n", result);
    printf("Selected items (0-indexed): ");
    for (i = selected_count - 1; i >= 0; i--) {
        printf("%d", selected[i]);
        if (i > 0) {
            printf(", ");
        }
    }
    printf("\n");
    
    free(selected);
    
    return 0;
}
