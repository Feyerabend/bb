import concurrent.futures

def quicksort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]  # choose middle element as pivot
    left = [x for x in arr if x < pivot]  # elements less than pivot
    middle = [x for x in arr if x == pivot]  # elements equal to pivot
    right = [x for x in arr if x > pivot]  # elements greater than pivot

    # recursively sort the left and right subarrays
    return quicksort(left) + middle + quicksort(right)

def parallel_quicksort(arr):
    if len(arr) <= 1:
        return arr  # base case: already sorted

    # same as above
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    # ProcessPoolExecutor to sort left and right subarrays in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_left = executor.submit(parallel_quicksort, left)
        future_right = executor.submit(parallel_quicksort, right)

        # wait for results
        sorted_left = future_left.result()
        sorted_right = future_right.result()

    # combine results
    return sorted_left + middle + sorted_right


if __name__ == "__main__":
    arr = [10, 7, 8, 9, 1, 5, 3, 6, 2, 4]
    print("Original array:", arr)

    sorted_arr = parallel_quicksort(arr)
    print("Sorted array:", sorted_arr)
