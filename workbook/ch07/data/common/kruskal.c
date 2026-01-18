#include <stdio.h>
#include <stdlib.h>

#define MAX 100  // max number edges

typedef struct {
    int u, v, weight;
} Edge;

typedef struct {
    int parent[MAX], rank[MAX];
} DisjointSet;

void initialize(DisjointSet *ds, int n) {
    for (int i = 0; i < n; i++) {
        ds->parent[i] = i;
        ds->rank[i] = 1;
    }
}

int find(DisjointSet *ds, int x) {
    if (ds->parent[x] != x)
        ds->parent[x] = find(ds, ds->parent[x]);  // path compression
    return ds->parent[x];
}

void unionSets(DisjointSet *ds, int x, int y) {
    int rootX = find(ds, x);
    int rootY = find(ds, y);

    if (rootX != rootY) {
        if (ds->rank[rootX] > ds->rank[rootY]) {
            ds->parent[rootY] = rootX;
        } else if (ds->rank[rootX] < ds->rank[rootY]) {
            ds->parent[rootX] = rootY;
        } else {
            ds->parent[rootY] = rootX;
            ds->rank[rootX]++;
        }
    }
}

int compareEdges(const void *a, const void *b) {
    return ((Edge*)a)->weight - ((Edge*)b)->weight;
}

void kruskal(int n, Edge edges[], int edgeCount) {
    qsort(edges, edgeCount, sizeof(Edge), compareEdges); // sort edges by weight
    DisjointSet ds;
    initialize(&ds, n);
    int mst_weight = 0;
    
    printf("Edges in MST:\n");
    for (int i = 0; i < edgeCount; i++) {
        if (find(&ds, edges[i].u) != find(&ds, edges[i].v)) {
            unionSets(&ds, edges[i].u, edges[i].v);
            printf("(%d, %d) - %d\n", edges[i].u, edges[i].v, edges[i].weight);
            mst_weight += edges[i].weight;
        }
    }
    
    printf("Total weight of MST: %d\n", mst_weight);
}

int main() {
    Edge edges[] = {
        {0, 1, 10}, {0, 2, 6}, {0, 3, 5},
        {1, 3, 15}, {2, 3, 4}
    };
    int n = 4;  // num of vertices
    int edgeCount = sizeof(edges) / sizeof(edges[0]);

    kruskal(n, edges, edgeCount);

    return 0;
}