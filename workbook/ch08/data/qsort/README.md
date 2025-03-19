
## Quicksort

*Quicksort* was developed in 1959 by *Tony Hoare*, a British computer scientist, while he was working
on a machine translation project for the National Physical Laboratory in England. Hoare was seeking an
efficient algorithm to sort words in a dictionary for translation purposes. Inspired by the idea of
partitioning data into smaller subsets, he devised Quicksort, which uses a divide-and-conquer approach
to recursively sort elements around a pivot. The algorithm was first published in 1961 and quickly gained
recognition for its simplicity and efficiency, becoming one of the most widely used sorting algorithms
in computer science.

Over the years, Quicksort has been refined and optimised, with improvements such as better pivot selectio
strategies (e.g. median-of-three) and hybrid approaches that switch to simpler algorithms like Insertion
Sort for small subarrays. Despite its worst-case time complexity of \(O(n^2)\), Quicksort's average-case
performance of \(O(n \log n)\) and in-place sorting capability make it a favourite in practice. It has
influenced the design of many programming languages' standard libraries, including C's `qsort` and
Python's `sorted` function. Today, Quicksort remains a cornerstone of algorithm design and a testament
to the elegance of recursive problem-solving.


### Integer Overflow in Quicksort Implementation

There was an issue some years ago. The issue was not really with the *Quicksort algorithm itself* but
rather with its *implementation* in certain libraries. Specifically, the problem arose when sorting
*extremely large arrays* (with more than \(2^{31}\) elements on 32-bit systems or \(2^{63}\) elements
on 64-bit systems). The root cause was *integer overflow* in the calculation of indices or sizes
during the partitioning step of Quicksort.

#### What Happened?

__1. *Index Calculation*__

- In Quicksort, the algorithm recursively partitions the array into smaller subarrays. To do this,
  it calculates indices and sizes of these subarrays.
- If the array is extremely large, the calculation of indices or sizes (e.g., `mid = (low + high) / 2`)
  can result in *integer overflow*. For example, if `low` and `high` are both close to the maximum value
  of a 32-bit integer, their sum can exceed the maximum representable value, causing undefined behaviour.


__2. *Undefined Behavior*__

- When integer overflow occurs, the behaviour is undefined in C and C++. This can lead to crashes,
  incorrect sorting, or security vulnerabilities.

__3. *Real-World Impact*__

- This issue was discovered in the *GNU C Library (glibc)* implementation of Quicksort (`qsort`).
  It affected applications that sorted very large datasets, such as databases or scientific computing
  software.


### Why Was This Problem Not Caught Earlier?

__1. *Rare Edge Case*__

- The problem only occurs with *extremely large arrays* (billions or trillions of elements). Most
  real-world applications don’t deal with datasets of this size, so the issue went unnoticed for years.

__2. *Assumptions About Input Size*__

- The original implementations assumed that the input size would not exceed the limits of the
  integer type used for indexing. This assumption held true for most practical use cases but failed
  for edge cases.

__3. *Testing Limitations*__

- Testing for such edge cases is challenging because it requires creating and processing massive datasets,
  which is computationally expensive and time-consuming.


### How Was the Problem Fixed?

The issue was addressed by modifying the implementation to *avoid integer overflow*.

1. *Safe Index Calculation*:
   - Instead of calculating indices using `(low + high) / 2`, which can overflow, the implementation
     was updated to use a safer formula:
     ```c
     mid = low + (high - low) / 2;
     ```
   - This avoids overflow because `(high - low)` is always smaller than the size of the array.

2. *Use of Larger Data Types*:
   - For extremely large arrays, implementations now use *64-bit integers* (e.g., `size_t` or `uint64_t`)
     to represent indices and sizes, even on 32-bit systems.

3. *Input Validation*:
   - Libraries now validate the input size to ensure it doesn’t exceed the limits of the data types used for indexing.


### Example of the Fix in C

Here’s an example of how the partitioning step in Quicksort can be implemented safely to avoid integer overflow:

```c
#include <stdint.h>  // For uint64_t

// Safe midpoint calculation to avoid overflow
int64_t safe_mid(int64_t low, int64_t high) {
    return low + (high - low) / 2;
}

// Partition function for Quicksort
int partition(int *arr, int64_t low, int64_t high) {
    int64_t mid = safe_mid(low, high);  // Safe midpoint calculation
    int pivot = arr[mid];
    // Rest of the partitioning logic ..
}

// Quicksort implementation
void quicksort(int *arr, int64_t low, int64_t high) {
    if (low < high) {
        int64_t pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}
```


### Broader Implications

This issue is a reminder that even well-established algorithms and implementations can have hidden
flaws that only surface under extreme conditions. It underscores the importance of:
- *Rigorous Testing*: Testing for edge cases and extreme inputs.
- *Code Audits*: Regularly reviewing and updating code to address potential vulnerabilities.
- *Defensive Programming*: Writing code that anticipates and handles unexpected conditions.
