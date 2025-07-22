#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int randomized_partition(int arr[], int low, int high) {
    // Randomly select pivot and swap with last element
    int random_index = low + rand() % (high - low + 1);
    swap(&arr[random_index], &arr[high]);
    
    int pivot = arr[high];
    int i = low - 1;
    
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

void randomized_quicksort(int arr[], int low, int high) {
    if (low < high) {
        int pi = randomized_partition(arr, low, high);
        randomized_quicksort(arr, low, pi - 1);
        randomized_quicksort(arr, pi + 1, high);
    }
}

int main() {
    srand(time(NULL));
    
    int arr[] = {64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42};
    int n = sizeof(arr) / sizeof(arr[0]);
    
    printf("Original array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    
    randomized_quicksort(arr, 0, n - 1);
    
    printf("\nSorted array: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    return 0;
}

// This code implements a randomized quicksort algorithm in C.
// It includes functions for partitioning the array and swapping elements.

// This is an example of a Las Vegas algorithm.
