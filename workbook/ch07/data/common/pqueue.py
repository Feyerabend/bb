
class PriorityQueue:
    def __init__(self, is_min_heap=True):
        self.heap = []
        self.is_min_heap = is_min_heap

    def _parent(self, index):
        return (index - 1) // 2

    def _left_child(self, index):
        return 2 * index + 1

    def _right_child(self, index):
        return 2 * index + 2

    def insert(self, priority, value):
        entry = (priority, value) if self.is_min_heap else (-priority, value)
        self.heap.append(entry)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        parent = self._parent(index)
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:  
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def extract(self):
        if not self.heap:
            raise IndexError("Priority queue is empty")
        if len(self.heap) == 1:
            return self.heap.pop()[1]  # only value

        root_value = self.heap[0][1]  # extract value
        self.heap[0] = self.heap.pop()  # last element -> root
        self._heapify_down(0)
        return root_value

    def _heapify_down(self, index):
        left = self._left_child(index)
        right = self._right_child(index)
        smallest = index

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def peek(self):
        if not self.heap:
            raise IndexError("Priority queue is empty")
        return self.heap[0][1]

    def is_empty(self):
        return len(self.heap) == 0

    def __str__(self):
        return str([(p if self.is_min_heap else -p, v) for p, v in self.heap])
    

# example
print("Min-Priority Queue (lower number = higher priority):")
min_pq = PriorityQueue(is_min_heap=True)
min_pq.insert(3, "Task A")
min_pq.insert(1, "Task B")
min_pq.insert(2, "Task C")

print("Queue:", min_pq)  # Output: [(1, 'Task B'), (3, 'Task A'), (2, 'Task C')]
print("Extracted:", min_pq.extract())  # Output: 'Task B' (priority 1)
print("Queue after extraction:", min_pq)  # Output: [(2, 'Task C'), (3, 'Task A')]

print("\nMax-Priority Queue (higher number = higher priority):")
max_pq = PriorityQueue(is_min_heap=False)
max_pq.insert(3, "Task A")
max_pq.insert(1, "Task B")
max_pq.insert(2, "Task C")

print("Queue:", max_pq)  # Output: [(3, 'Task A'), (1, 'Task B'), (2, 'Task C')]
print("Extracted:", max_pq.extract())  # Output: 'Task A' (priority 3)
print("Queue after extraction:", max_pq)  # Output: [(2, 'Task C'), (1, 'Task B')]
