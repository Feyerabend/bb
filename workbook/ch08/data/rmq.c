#include <stdio.h>
#include <limits.h>

#define MAX 100

int segmentTree[4 * MAX];

void build(int arr[], int node, int start, int end) {
    if (start == end) {
        segmentTree[node] = arr[start];
    } else {
        int mid = (start + end) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        segmentTree[node] = (segmentTree[2 * node] < segmentTree[2 * node + 1]) ? segmentTree[2 * node] : segmentTree[2 * node + 1];
    }
}

int query(int node, int start, int end, int l, int r) {
    if (r < start || end < l) {
        return INT_MAX;
    }
    if (l <= start && end <= r) {
        return segmentTree[node];
    }
    int mid = (start + end) / 2;
    int left = query(2 * node, start, mid, l, r);
    int right = query(2 * node + 1, mid + 1, end, l, r);
    return (left < right) ? left : right;
}

int main() {
    int arr[] = {1, 3, 2, 7, 9, 11, 5};
    int n = 7;
    build(arr, 1, 0, n - 1);
    
    printf("%d\n", query(1, 0, n - 1, 1, 4));  // Query min between index 1 and 4 (output: 2)
    printf("%d\n", query(1, 0, n - 1, 2, 6));  // Query min between index 2 and 6 (output: 2)
    
    return 0;
}