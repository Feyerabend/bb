#include <stdio.h>
#include <stdbool.h>

#define BUFFER_SIZE 5

typedef struct {
    int data[BUFFER_SIZE];
    int head;  // points to the next insertion index
    int tail;  // points to the next removal index
    int count; // number of elements currently in buffer
} CircularBuffer;

void init(CircularBuffer *cb) {
    cb->head = 0;
    cb->tail = 0;
    cb->count = 0;
}

bool is_full(CircularBuffer *cb) {
    return cb->count == BUFFER_SIZE;
}

bool is_empty(CircularBuffer *cb) {
    return cb->count == 0;
}

bool enqueue(CircularBuffer *cb, int value) {
    if (is_full(cb)) return false;

    cb->data[cb->head] = value;
    cb->head = (cb->head + 1) % BUFFER_SIZE;
    cb->count++;
    return true;
}

bool dequeue(CircularBuffer *cb, int *value) {
    if (is_empty(cb)) return false;

    *value = cb->data[cb->tail];
    cb->tail = (cb->tail + 1) % BUFFER_SIZE;
    cb->count--;
    return true;
}

void print_buffer(CircularBuffer *cb) {
    printf("Buffer: ");
    for (int i = 0; i < cb->count; i++) {
        int index = (cb->tail + i) % BUFFER_SIZE;
        printf("%d ", cb->data[index]);
    }
    printf("\n");
}




int main() {
    CircularBuffer cb;
    init(&cb);

    enqueue(&cb, 10);
    enqueue(&cb, 20);
    enqueue(&cb, 30);
    enqueue(&cb, 40);
    enqueue(&cb, 50);  // fills buffer

    print_buffer(&cb);

    int val;
    dequeue(&cb, &val); // removes 10
    printf("Dequeued: %d\n", val);

    enqueue(&cb, 60); // wraps around
    print_buffer(&cb);

    while (dequeue(&cb, &val)) {
        printf("Dequeued: %d\n", val);
    }

    return 0;
}