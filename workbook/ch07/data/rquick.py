import random

def randomized_partition(arr, low, high):
    # Randomly select pivot and swap with last element
    random_index = random.randint(low, high)
    arr[random_index], arr[high] = arr[high], arr[random_index]
    
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def randomized_quicksort(arr, low, high):
    if low < high:
        pi = randomized_partition(arr, low, high)
        randomized_quicksort(arr, low, pi - 1)
        randomized_quicksort(arr, pi + 1, high)

# Example usage
if __name__ == "__main__":
    arr = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
    print("Original array:", arr)
    
    randomized_quicksort(arr, 0, len(arr) - 1)
    print("Sorted array:", arr)

# This code implements a randomized quicksort algorithm.
# It randomly selects a pivot to improve performance on average cases.
# The partitioning is done in-place, and the algorithm sorts the array
# in O(n log n) time on average.

# This is an example of a Las Vegas algorithm.
