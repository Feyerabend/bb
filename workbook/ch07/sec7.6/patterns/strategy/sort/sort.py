from abc import ABC, abstractmethod

# Strategy Interface
class SortingStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

# Concrete Strategies
class BubbleSortStrategy(SortingStrategy):
    def sort(self, data):
        # Create a copy to avoid modifying the original
        sorted_data = list(data)
        n = len(sorted_data)
        for i in range(n):
            for j in range(n - i - 1):
                if sorted_data[j] > sorted_data[j + 1]:
                    sorted_data[j], sorted_data[j + 1] = sorted_data[j + 1], sorted_data[j]
        return sorted_data

class QuickSortStrategy(SortingStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return list(data)
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

# Context
class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy

    def sort(self, data):
        return self.strategy.sort(data)

# Client Code
if __name__ == "__main__":
    data = [3, 1, 4, 1, 5, 9, 2, 6]

    # Use Bubble Sort
    sorter = Sorter(BubbleSortStrategy())
    sorted_data = sorter.sort(data)
    print("Bubble Sort:", sorted_data)

    # Switch to Quick Sort
    sorter.strategy = QuickSortStrategy()
    sorted_data = sorter.sort(data)
    print("Quick Sort:", sorted_data)