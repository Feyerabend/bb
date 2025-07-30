class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0  # Next insert
        self.tail = 0  # Next remove
        self.count = 0

    def is_full(self):
        return self.count == self.size

    def is_empty(self):
        return self.count == 0

    def enqueue(self, value):
        if self.is_full():
            return False
        self.buffer[self.head] = value
        self.head = (self.head + 1) % self.size
        self.count += 1
        return True

    def dequeue(self):
        if self.is_empty():
            return None
        value = self.buffer[self.tail]
        self.tail = (self.tail + 1) % self.size
        self.count -= 1
        return value

    def __str__(self):
        elements = [
            str(self.buffer[(self.tail + i) % self.size])
            for i in range(self.count)
        ]
        return "Buffer: [" + " ".join(elements) + "]"

if __name__ == "__main__":
    cb = CircularBuffer(5)

    cb.enqueue(10)
    cb.enqueue(20)
    cb.enqueue(30)
    cb.enqueue(40)
    cb.enqueue(50)

    print(cb)

    print("Dequeued:", cb.dequeue())  # 10
    cb.enqueue(60)

    print(cb)

    while not cb.is_empty():
        print("Dequeued:", cb.dequeue())

    print("Final buffer state:", cb)

