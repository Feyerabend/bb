#include <stdio.h>

#define MAX 1000  // max number elements

typedef struct {
    int parent[MAX];
    int rank[MAX];
} DisjointSet;

void initialize(DisjointSet *ds, int n) {
    for (int i = 0; i < n; i++) {
        ds->parent[i] = i;  // each node is its own parent initially
        ds->rank[i] = 1;  // rank starts at 1
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

int connected(DisjointSet *ds, int x, int y) {
    return find(ds, x) == find(ds, y);
}

int main() {
    DisjointSet ds;
    int n = 10;
    initialize(&ds, n);

    unionSets(&ds, 1, 2);
    unionSets(&ds, 2, 3);
    unionSets(&ds, 4, 5);
    unionSets(&ds, 6, 7);

    printf("1 and 3 connected? %s\n", connected(&ds, 1, 3) ? "Yes" : "No");  // Yes
    printf("1 and 4 connected? %s\n", connected(&ds, 1, 4) ? "Yes" : "No");  // No

    unionSets(&ds, 3, 4);  // Connecting 3 and 4

    printf("1 and 4 connected after union(3,4)? %s\n", connected(&ds, 1, 4) ? "Yes" : "No");  // Yes

    return 0;
}
