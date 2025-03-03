class RMQSegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [float('inf')] * (4 * self.n)
        self.build(arr, 0, 0, self.n - 1)
    
    def build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self.build(arr, 2 * node + 1, start, mid)
            self.build(arr, 2 * node + 2, mid + 1, end)
            self.tree[node] = min(self.tree[2 * node + 1], self.tree[2 * node + 2])
    
    def query(self, node, start, end, l, r):
        if r < start or end < l:
            return float('inf')
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        left = self.query(2 * node + 1, start, mid, l, r)
        right = self.query(2 * node + 2, mid + 1, end, l, r)
        return min(left, right)

arr = [1, 3, 2, 7, 9, 11, 5]
seg_tree = RMQSegmentTree(arr)

print(seg_tree.query(0, 0, len(arr) - 1, 1, 4))  # Query min between index 1 and 4 (output: 2)
print(seg_tree.query(0, 0, len(arr) - 1, 2, 6))  # Query min between index 2 and 6 (output: 2)