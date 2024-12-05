#include <stdio.h>
#include <time.h>

void sum_array_unoptimized(int *arr, int size, int *result) {
    *result = 0;
    for (int i = 0; i < size; i++) {
        *result += arr[i];
    }
}

void sum_array_optimized(int *arr, int size, int *result) {
    *result = 0;
    int i;
    for (i = 0; i <= size - 4; i += 4) {
        *result += arr[i] + arr[i + 1] + arr[i + 2] + arr[i + 3];
    }
    for (; i < size; i++) {
        *result += arr[i];
    }
}

int main() {
    const int size = 1000000;
    int arr[size];
    for (int i = 0; i < size; i++) {
        arr[i] = i % 100;  //  sample data
    }

    int result;
    clock_t start, end;

    //  unoptimised 
    start = clock();
    sum_array_unoptimized(arr, size, &result);
    end = clock();
    printf("Unoptimized sum: %d, Time: %f seconds\n", result, (double)(end - start) / CLOCKS_PER_SEC);

    //  optimised 
    start = clock();
    sum_array_optimized(arr, size, &result);
    end = clock();
    printf("Optimized sum: %d, Time: %f seconds\n", result, (double)(end - start) / CLOCKS_PER_SEC);

    return 0;
}
