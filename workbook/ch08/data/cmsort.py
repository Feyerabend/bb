import concurrent.futures

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort(arr):
    if len(arr) <= 1:
        return arr  # base case: already sorted

    mid = len(arr) // 2  # find middle point
    left = arr[:mid]  # divide array into two halves
    right = arr[mid:]

    # recursively sort both halves
    left = merge_sort(left)
    right = merge_sort(right)

    # merge sorted halves
    return merge(left, right)

# as you might guess, small arrays should be sorted sequentially
# to avoid overhead of parallelism
#def parallel_merge_sort(arr, threshold=1000):
#    if len(arr) <= threshold:
#        return merge_sort(arr)  # sequential Merge Sort for small! arrays

def parallel_merge_sort(arr):
    if len(arr) <= 1:
        return arr  # base case: already sorted

    mid = len(arr) // 2  # find middle point
    left = arr[:mid]  # divide array into two halves
    right = arr[mid:]

    # UProcessPoolExecutor to sort the two halves in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_left = executor.submit(parallel_merge_sort, left)
        future_right = executor.submit(parallel_merge_sort, right)

        # wait for results
        left = future_left.result()
        right = future_right.result()

    # merge sorted halves
    return merge(left, right)


if __name__ == "__main__":
    arr = [12, 11, 13, 5, 6, 7, 1, 3, 2, 8, 9, 4, 10]
    print("Original array:", arr)

    sorted_arr = parallel_merge_sort(arr)
    print("Sorted array:", sorted_arr)
