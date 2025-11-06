class DisjointSet:
    def __init__(self, n):
        self.parent = [i for i in range(n)]  # Each node is its own parent initially
        self.rank = [1] * n  # Rank (size) for union by rank

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)

        if rootX != rootY:
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            elif self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1  # Increase rank if they were of equal height

    def connected(self, x, y):
        return self.find(x) == self.find(y)

# example
ds = DisjointSet(10)
ds.union(1, 2)
ds.union(2, 3)
ds.union(4, 5)
ds.union(6, 7)

print("1 and 3 connected?", ds.connected(1, 3))  # True
print("1 and 4 connected?", ds.connected(1, 4))  # False

ds.union(3, 4)  # Connecting 3 and 4
print("1 and 4 connected after union(3,4)?", ds.connected(1, 4))  # True