
## Optimisation or Optimization

Optimization, or optimisation in British English, in computing refers to the process of improving
software or hardware to maximize efficiency, speed, or resource usage. This practice dates back to
the early days of computing, when hardware was expensive and limited in capability. Early optimisation
efforts focused heavily on reducing memory usage and execution time, as these were critical constraints.

In traditional computing, optimisation often involves making code faster or more resource-efficient.
Similarly, in machine learning, optimisation focuses on improving computational efficiency during model
training and inference. Techniques like gradient checkpointing, quantization, and pruning aim to reduce
memory usage and execution time, particularly for large-scale models deployed in resource-constrained
environments.

The importance of optimisation lies in its ability to extend the utility of hardware, enhance user
experience, and reduce costs. For example, in embedded systems or real-time applications, efficient
code can mean the difference between success and failure due to strict performance requirements.
Similarly, optimisation is vital in large-scale systems, such as cloud infrastructures, where efficiency
translates directly to reduced energy consumption and operational costs.

Historically, optimisation techniques were largely manual, with developers writing highly specific
assembly code. Over time, compilers evolved to include sophisticated optimisation strategies, such
as loop unrolling, instruction pipelining, and inlining, reducing the burden on programmers. However,
these optimisations always come with trade-offs, including increased code complexity or longer compilation
times.

Today, optimisation remains a critical aspect of computing, driven by fields like machine learning,
high-performance computing, and mobile app development. Balancing human-readable, maintainable code
with efficient execution continues to be a central challenge in software development.


### Samples

Some samples are included here, which illustrates different optimisations.

*Exercise: You can apply the following examples to the others, to measure time. Compare the results.*

The following one shows loop unrolling.

```c
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
        arr[i] = i % 100;
    }

    int result;
    clock_t start, end;

    start = clock();
    sum_array_unoptimized(arr, size, &result);
    end = clock();
    printf("Unoptimized sum: %d, Time: %f seconds\n", result, (double)(end - start) / CLOCKS_PER_SEC);

    start = clock();
    sum_array_optimized(arr, size, &result);
    end = clock();
    printf("Optimized sum: %d, Time: %f seconds\n", result, (double)(end - start) / CLOCKS_PER_SEC);

    return 0;
}
```
