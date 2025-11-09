#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int size;
    int *tree;
} FenwickTree;

FenwickTree* createFenwickTree(int size) {
    FenwickTree *ft = (FenwickTree*)malloc(sizeof(FenwickTree));
    ft->size = size;
    ft->tree = (int*)calloc(size + 1, sizeof(int));
    return ft;
}

void update(FenwickTree *ft, int index, int delta) {
    while (index <= ft->size) {
        ft->tree[index] += delta;
        index += index & -index;
    }
}

int prefix_sum(FenwickTree *ft, int index) {
    int sum = 0;
    while (index > 0) {
        sum += ft->tree[index];
        index -= index & -index;
    }
    return sum;
}

int range_sum(FenwickTree *ft, int left, int right) {
    return prefix_sum(ft, right) - prefix_sum(ft, left - 1);
}

void freeFenwickTree(FenwickTree *ft) {
    free(ft->tree);
    free(ft);
}

int main() {
    FenwickTree *ft = createFenwickTree(10);

    update(ft, 1, 5);
    update(ft, 3, 7);
    update(ft, 7, 4);

    printf("Prefix sum up to index 3: %d\n", prefix_sum(ft, 3));
    printf("Sum from index 2 to 7: %d\n", range_sum(ft, 2, 7));

    freeFenwickTree(ft);
    return 0;
}