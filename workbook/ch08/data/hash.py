
# we got dictionaries in python, but let's implement our own hash table
# we will use chaining to handle collisions, and linked list to implement chaining
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [None] * self.size

    def _hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self._hash(key)
        if self.table[index] is None:
            self.table[index] = Node(key, value)
        else:
            current = self.table[index]
            while current:
                if current.key == key:
                    current.value = value
                    return
                if current.next is None:
                    break
                current = current.next
            current.next = Node(key, value)

    def get(self, key):
        index = self._hash(key)
        current = self.table[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def delete(self, key):
        index = self._hash(key)
        current = self.table[index]
        prev = None
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.table[index] = current.next
                return
            prev = current
            current = current.next

    def display(self):
        for i, node in enumerate(self.table):
            current = node
            print(f"Index {i}:", end=" ")
            while current:
                print(f"({current.key}: {current.value})", end=" -> ")
                current = current.next
            print("None")

ht = HashTable()
ht.insert("a", 1)
ht.insert("b", 2)
ht.insert("c", 3)
ht.insert("a", 10)
ht.display()
ht.delete("b")
ht.display()
print(ht.get("a"))
print(ht.get("b"))