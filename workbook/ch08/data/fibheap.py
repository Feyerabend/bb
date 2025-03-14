import math

class Node:
    def __init__(self, key):
        self.key = key
        self.degree = 0
        self.parent = None
        self.child = None
        self.mark = False
        self.next = self
        self.prev = self

class FibonacciHeap:
    def __init__(self):
        self.min = None
        self.total_nodes = 0

    def insert(self, key):
        node = Node(key)
        self.min = self._merge_lists(self.min, node)
        self.total_nodes += 1
        return node

    def _merge_lists(self, a, b):
        if not a: return b
        if not b: return a
        
        a.next, b.prev, a.prev, b.next = b, a, b.next, a.prev
        return a if a.key < b.key else b

    def extract_min(self):
        min_node = self.min
        if min_node:
            if min_node.child:
                children = []
                child = min_node.child
                while True:
                    children.append(child)
                    child = child.next
                    if child == min_node.child:
                        break
                
                for child in children:
                    child.parent = None
                    self.min = self._merge_lists(self.min, child)
            
            self._remove_from_list(min_node)
            if min_node == min_node.next:
                self.min = None
            else:
                self.min = min_node.next
                self._consolidate()
            
            self.total_nodes -= 1
        return min_node

    def _remove_from_list(self, node):
        if node.next == node:
            return
        node.prev.next = node.next
        node.next.prev = node.prev

    def _consolidate(self):
        max_degree = int(math.log(self.total_nodes) * 2) if self.total_nodes > 0 else 1
        degree_table = [None] * max_degree

        nodes = []
        x = self.min
        if x:
            while True:
                nodes.append(x)
                x = x.next
                if x == self.min:
                    break
        
        for node in nodes:
            d = node.degree
            while degree_table[d]:
                other = degree_table[d]
                if node.key > other.key:
                    node, other = other, node
                self._link(other, node)
                degree_table[d] = None
                d += 1
            degree_table[d] = node
        
        self.min = None
        for entry in degree_table:
            if entry:
                self.min = self._merge_lists(self.min, entry)

    def _link(self, child, parent):
        self._remove_from_list(child)
        child.next = child.prev = child
        parent.child = self._merge_lists(parent.child, child)
        child.parent = parent
        parent.degree += 1
        child.mark = False

fib_heap = FibonacciHeap()
fib_heap.insert(10)
fib_heap.insert(3)
fib_heap.insert(7)
print("Extracted min:", fib_heap.extract_min().key)  # Output: 3
