#include <stdio.h>
#include <string.h>

#define MAX 100

typedef struct {
    char u[10];
    char v[10];
} Edge;

Edge edges[] = {
    {"A", "B"},
    {"A", "C"},
    {"B", "D"},
    {"C", "D"},
    {"C", "E"},
    {"D", "E"}
};

int n_edges = 6;

int used[MAX];
char labels[MAX][10];
int label_count = 0;

int index_of(char *label) {
    for (int i = 0; i < label_count; ++i)
        if (strcmp(labels[i], label) == 0)
            return i;
    strcpy(labels[label_count], label);
    return label_count++;
}

int main() {
    int cover[MAX] = {0};

    for (int i = 0; i < n_edges; ++i) {
        int ui = index_of(edges[i].u);
        int vi = index_of(edges[i].v);
        if (!used[ui] && !used[vi]) {
            cover[ui] = 1;
            cover[vi] = 1;
            used[ui] = 1;
            used[vi] = 1;
        }
    }

    printf("Place cameras at intersections: ");
    for (int i = 0; i < label_count; ++i)
        if (cover[i])
            printf("%s ", labels[i]);
    printf("\n");

    return 0;
}

// This code finds a minimal vertex cover for a given set of edges in a graph.
// It uses a greedy approach to select vertices that cover the edges.
// The output will list the vertices where cameras should be placed to cover all edges.
