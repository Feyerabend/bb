#include <stdio.h>
#include <stdlib.h>

int compare(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

// simplified "sort" using callback for illustration
void custom_sort(int* arr, size_t count, size_t size, int (*compare)(const void*, const void*)) {
    // bubble sort (simple for demonstration)
    for (size_t i = 0; i < count - 1; i++) {
        for (size_t j = 0; j < count - i - 1; j++) {
            //  callback to compare elements
            if (compare(&arr[j], &arr[j + 1]) > 0) {
                // swap elements
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    int arr[] = {5, 2, 8, 1};
    size_t length = sizeof(arr) / sizeof(arr[0]);

    printf("Original array: ");
    for (size_t i = 0; i < length; i++) printf("%d ", arr[i]);

    custom_sort(arr, length, sizeof(int), compare);

    printf("\nSorted array:   ");
    for (size_t i = 0; i < length; i++) printf("%d ", arr[i]);

    return 0;
}

