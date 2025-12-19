#include <stdio.h>
#include <stdlib.h>

// Strategy Interface (Function Pointer Type)
typedef void (*SortFunction)(int*, size_t);

// Concrete Strategies
void bubble_sort(int* arr, size_t size) {
    for (size_t i = 0; i < size - 1; ++i) {
        for (size_t j = 0; j < size - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

void quick_sort(int* arr, size_t size) {
    if (size < 2) return;
    int pivot = arr[size / 2];
    size_t i = 0, j = size - 1;

    while (i <= j) {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;
        if (i <= j) {
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
            i++;
            j--;
        }
    }

    quick_sort(arr, j + 1);
    quick_sort(arr + i, size - i);
}

// Context
typedef struct {
    SortFunction sort_func;
} Sorter;

void sorter_init(Sorter* sorter, SortFunction func) {
    sorter->sort_func = func;
}

void sorter_perform_sort(Sorter* sorter, int* arr, size_t size) {
    sorter->sort_func(arr, size);
}

// Client Code
int main() {
    int data[] = {3, 1, 4, 1, 5, 9, 2, 6};
    size_t size = sizeof(data) / sizeof(data[0]);

    Sorter sorter;

    // Use Bubble Sort
    sorter_init(&sorter, bubble_sort);
    sorter_perform_sort(&sorter, data, size);
    printf("Bubble Sort: ");
    for (size_t i = 0; i < size; i++) printf("%d ", data[i]);
    printf("\n");

    // Reset data (since it was modified in-place)
    int reset_data[] = {3, 1, 4, 1, 5, 9, 2, 6};
    for (size_t i = 0; i < size; i++) data[i] = reset_data[i];

    // Switch to Quick Sort
    sorter_init(&sorter, quick_sort);
    sorter_perform_sort(&sorter, data, size);
    printf("Quick Sort:  ");
    for (size_t i = 0; i < size; i++) printf("%d ", data[i]);
    printf("\n");

    return 0;
}