import random

def randomized_binary_search(arr, left, right, target):
    if left <= right:
        # Instead of always picking middle, randomly choose a position
        mid = random.randint(left, right)
        
        if arr[mid] == target:
            return mid
        
        if arr[mid] > target:
            return randomized_binary_search(arr, left, mid - 1, target)
        else:
            return randomized_binary_search(arr, mid + 1, right, target)
    
    return -1

# Example usage
if __name__ == "__main__":
    arr = [2, 3, 4, 10, 40, 50, 60, 70, 80, 90]
    target = 10
    
    print("Array:", arr)
    
    result = randomized_binary_search(arr, 0, len(arr) - 1, target)
    
    if result != -1:
        print(f"Element {target} found at index {result}")
    else:
        print(f"Element {target} not found")

# This code implements a randomised binary search algorithm.
# It randomly selects a mid-point in the search range
# instead of always picking the middle element.
# This can help in scenarios where the input array is not
# uniformly distributed, potentially improving search performance
# in some cases. The main function demonstrates the search on
# a sample sorted array.