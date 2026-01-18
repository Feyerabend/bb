#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int randomized_binary_search(int arr[], int left, int right, int target) {
    if (left <= right) {
        // Instead of always picking middle, randomly choose a position
        int mid = left + rand() % (right - left + 1);
        
        if (arr[mid] == target) {
            return mid;
        }
        
        if (arr[mid] > target) {
            return randomized_binary_search(arr, left, mid - 1, target);
        } else {
            return randomized_binary_search(arr, mid + 1, right, target);
        }
    }
    return -1;
}

int main() {
    srand(time(NULL));
    
    int arr[] = {2, 3, 4, 10, 40, 50, 60, 70, 80, 90};
    int n = sizeof(arr) / sizeof(arr[0]);
    int target = 10;
    
    printf("Array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    int result = randomized_binary_search(arr, 0, n - 1, target);
    
    if (result != -1) {
        printf("Element %d found at index %d\n", target, result);
    } else {
        printf("Element %d not found\n", target);
    }
    
    return 0;
}

// This code implements a randomized binary search algorithm in C.
// It randomly selects a mid-point in the search range, which can help in scenarios
// where the input array is not uniformly distributed, potentially improving search performance
// in some cases. The main function demonstrates the search on a sample sorted array.

