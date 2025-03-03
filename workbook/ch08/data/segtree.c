#include <stdio.h>

#define MAX 100

int segmentTree[4 * MAX];

void build(int arr[], int node, int start, int end) {
    if (start == end) {
        segmentTree[node] = arr[start];
    } else {
        int mid = (start + end) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        segmentTree[node] = segmentTree[2 * node] + segmentTree[2 * node + 1];
    }
}

int query(int node, int start, int end, int l, int r) {
    if (r < start || end < l) {
        return 0;
    }
    if (l <= start && end <= r) {
        return segmentTree[node];
    }
    int mid = (start + end) / 2;
    int left = query(2 * node, start, mid, l, r);
    int right = query(2 * node + 1, mid + 1, end, l, r);
    return left + right;
}

void update(int node, int start, int end, int idx, int val) {
    if (start == end) {
        segmentTree[node] = val;
    } else {
        int mid = (start + end) / 2;
        if (start <= idx && idx <= mid) {
            update(2 * node, start, mid, idx, val);
        } else {
            update(2 * node + 1, mid + 1, end, idx, val);
        }
        segmentTree[node] = segmentTree[2 * node] + segmentTree[2 * node + 1];
    }
}

int main() {
    int arr[] = {1, 3, 5, 7, 9, 11};
    int n = 6;
    build(arr, 1, 0, n - 1);
    printf("%d\n", query(1, 0, n - 1, 1, 3));
    update(1, 0, n - 1, 1, 10);
    printf("%d\n", query(1, 0, n - 1, 1, 3));
    return 0;
}