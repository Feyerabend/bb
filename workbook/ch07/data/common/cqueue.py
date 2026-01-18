class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self._size = 0

    def enqueue(self, value):
        new_node = Node(value)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        
        removed_value = self.front.value
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return removed_value

    def peek(self):
        if self.is_empty():
            raise IndexError("Peek from empty queue")
        return self.front.value

    def is_empty(self):
        return self.front is None

    def size(self):
        return self._size

    def __repr__(self):
        elements = []
        current = self.front
        while current:
            elements.append(str(current.value))
            current = current.next
        return "Queue([" + ", ".join(elements) + "])"

# example
q = Queue()
q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
print(q.dequeue())  # Output: 10
print(q.peek())     # Output: 20
print(q.is_empty()) # Output: False
print(q.size())     # Output: 2
print(q)            # Output: Queue([20, 30])
