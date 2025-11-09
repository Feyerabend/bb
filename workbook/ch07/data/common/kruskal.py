class DisjointSet:
    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.rank = [1] * n

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
                self.rank[rootX] += 1  # Increase rank if same height

def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])  # Sort by weight
    ds = DisjointSet(n)
    mst = []
    mst_weight = 0

    for u, v, weight in edges:
        if ds.find(u) != ds.find(v):  # Check if cycle is formed
            ds.union(u, v)
            mst.append((u, v, weight))
            mst_weight += weight

    return mst, mst_weight

# example
edges = [
    (0, 1, 10), (0, 2, 6), (0, 3, 5),
    (1, 3, 15), (2, 3, 4)
]
n = 4  # Number of vertices

mst, weight = kruskal(n, edges)
print("Edges in MST:", mst)
print("Total weight of MST:", weight)

'''
The implementations provided illustrate Kruskal’s Algorithm for computing the Minimum Spanning Tree (MST) of a graph. A Minimum Spanning Tree is a subset of the edges that connects all vertices of a graph while minimising the total edge weight. This is particularly useful in network design (such as laying out communication networks, electrical grids, or roadways) where minimising cost is essential.

Kruskal’s Algorithm works by sorting all edges by weight and then adding them one by one to the MST, ensuring no cycles are formed. The Disjoint Set (Union-Find) data structure plays a crucial role in efficiently detecting cycles by keeping track of which components are connected. The two key operations in this structure are Find(), which determines the root of a set (optimised using path compression), and Union(), which merges two sets (optimised using union by rank to keep trees shallow).

The Python implementation provides a clean, readable approach, making it easy to understand the algorithm. The C implementation, on the other hand, is more optimized for performance, using qsort() for sorting edges efficiently. Both versions demonstrate how Kruskal’s Algorithm selects the optimal edges, ensuring an MST with the lowest possible weight. These examples are crucial for understanding graph algorithms, network optimisation, and efficient data structures in real-world applications.
'''