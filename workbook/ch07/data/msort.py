def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2  # find middle point
        left_half = arr[:mid]  # divide array into two halves
        right_half = arr[mid:]

        # recursively sort both halves
        merge_sort(left_half)
        merge_sort(right_half)

        # merge sorted halves
        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        # any remaining elements in left_half
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        # any remaining elements in right_half
        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1


arr = [12, 11, 13, 5, 6, 7]
print("Original array:", arr)

merge_sort(arr)
print("Sorted array:", arr)
