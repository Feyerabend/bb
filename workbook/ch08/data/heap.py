
class MinHeap:
    def __init__(self):
        self.heap = []

    def _parent(self, index):
        return (index - 1) // 2

    def _left_child(self, index):
        return 2 * index + 1

    def _right_child(self, index):
        return 2 * index + 2

    def insert(self, value):
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        parent = self._parent(index)
        if index > 0 and self.heap[index] < self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def extract_min(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()  # last element -> root
        self._heapify_down(0)
        return root

    def _heapify_down(self, index):
        left = self._left_child(index)
        right = self._right_child(index)
        smallest = index

        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def peek(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def __str__(self):
        return str(self.heap)


class MaxHeap:
    def __init__(self):
        self.heap = []

    def _parent(self, index):
        return (index - 1) // 2

    def _left_child(self, index):
        return 2 * index + 1

    def _right_child(self, index):
        return 2 * index + 2

    def insert(self, value):
        self.heap.append(value)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        parent = self._parent(index)
        if index > 0 and self.heap[index] > self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def extract_max(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()  # last element -> root
        self._heapify_down(0)
        return root

    def _heapify_down(self, index):
        left = self._left_child(index)
        right = self._right_child(index)
        largest = index

        if left < len(self.heap) and self.heap[left] > self.heap[largest]:
            largest = left
        if right < len(self.heap) and self.heap[right] > self.heap[largest]:
            largest = right

        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)

    def peek(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def __str__(self):
        return str(self.heap)


# example
min_heap = MinHeap()
min_heap.insert(5)
min_heap.insert(3)
min_heap.insert(8)
min_heap.insert(2)

print("Min-Heap:", min_heap)  # Output: [2, 3, 8, 5]
print("Extracted Min:", min_heap.extract_min())  # Output: 2
print("Min-Heap after extraction:", min_heap)  # Output: [3, 5, 8]

max_heap = MaxHeap()
max_heap.insert(5)
max_heap.insert(3)
max_heap.insert(8)
max_heap.insert(2)

print("Max-Heap:", max_heap)  # Output: [8, 5, 3, 2]
print("Extracted Max:", max_heap.extract_max())  # Output: 8
print("Max-Heap after extraction:", max_heap)  # Output: [5, 2, 3]
