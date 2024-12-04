import random
import time

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def compare_algorithms():
    dataset_sizes = [10, 100, 1000, 5000]
    for size in dataset_sizes:
        data = [random.randint(1, 10000) for _ in range(size)]
        print(f"\nDataset size: {size}")

        bubble_data = data.copy()
        start_time = time.time()
        bubble_sort(bubble_data)
        bubble_time = time.time() - start_time
        print(f"Bubble Sort Time: {bubble_time:.5f} seconds")

        quick_data = data.copy()
        start_time = time.time()
        quick_sort(quick_data)
        quick_time = time.time() - start_time
        print(f"Quick Sort Time: {quick_time:.5f} seconds")

compare_algorithms()
