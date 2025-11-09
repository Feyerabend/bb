import sys

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] 
                      for row in range(vertices)]
    
    def min_key(self, key, mst_set):
        min_val = sys.maxsize
        min_index = -1
        
        for v in range(self.V):
            if key[v] < min_val and not mst_set[v]:
                min_val = key[v]
                min_index = v
        
        return min_index
    
    def print_mst(self, parent):
        print("Edge \tWeight")
        for i in range(1, self.V):
            print(f"{parent[i]} - {i} \t{self.graph[i][parent[i]]}")
    

    def prim_mst(self):
        # Key values used to pick minimum weight edge
        key = [sys.maxsize] * self.V
        # Array to store constructed MST
        parent = [None] * self.V
        # Key for the first vertex is 0
        key[0] = 0
        # First node is always the root of MST
        parent[0] = -1
        # To represent set of vertices included in MST
        mst_set = [False] * self.V
        
        for _ in range(self.V):
            # Pick the minimum key vertex from the set of vertices not yet included in MST
            u = self.min_key(key, mst_set)
            
            # Add the picked vertex to the MST Set
            mst_set[u] = True
            
            # Update key value and parent index of the adjacent vertices of the picked vertex
            for v in range(self.V):
                # graph[u][v] is non zero only for adjacent vertices of u
                # mst_set[v] is false for vertices not yet included in MST
                # Update the key only if graph[u][v] is smaller than key[v]
                if self.graph[u][v] > 0 and not mst_set[v] and self.graph[u][v] < key[v]:
                    parent[v] = u
                    key[v] = self.graph[u][v]

        self.print_mst(parent)


if __name__ == "__main__":
    g = Graph(5)
    g.graph = [
        [0, 2, 0, 6, 0],
        [2, 0, 3, 8, 5],
        [0, 3, 0, 0, 7],
        [6, 8, 0, 0, 9],
        [0, 5, 7, 9, 0]
    ]
    
    g.prim_mst()
