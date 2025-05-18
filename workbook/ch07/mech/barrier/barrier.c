#include <stdatomic.h>
#include <stdio.h>
#include <pthread.h>

#define BUFFER_SIZE 256

// Shared data
char buffer[BUFFER_SIZE];
atomic_int ready = 0; // Flag: 0 = not ready, 1 = ready

void* producer(void* arg) {
    snprintf(buffer, BUFFER_SIZE, "Hello from producer!");

    // Memory fence to ensure buffer write completes before flag is set
    atomic_thread_fence(memory_order_release);

    // Signal data is ready
    atomic_store(&ready, 1);

    return NULL;
}

void* consumer(void* arg) {
    // Wait until data is ready
    while (atomic_load(&ready) == 0)
        ; // busy-wait

    // Memory fence to ensure flag read happens before buffer read
    atomic_thread_fence(memory_order_acquire);

    printf("Consumer received: %s\n", buffer);
    return NULL;
}

int main() {
    pthread_t t1, t2;

    pthread_create(&t1, NULL, producer, NULL);
    pthread_create(&t2, NULL, consumer, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
