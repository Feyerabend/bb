#include <stdio.h>
#include <pthread.h>
#include <stdatomic.h>

#define N 1000000

long long result = 0;
atomic_int done = 0;

void* compute_sum_of_squares(void* arg) {
    long long sum = 0;
    for (int i = 1; i <= N; ++i) {
        sum += (long long)i * i;
    }

    result = sum;

    atomic_thread_fence(memory_order_release);

    // done flag
    atomic_store(&done, 1);

    return NULL;
}

void* reader(void* arg) {

    while (atomic_load(&done) == 0)
        ; // spin

    // visibility of result after flag is seen
    atomic_thread_fence(memory_order_acquire);

    // read and print the result
    printf("Computed sum of squares: %lld\n", result);

    return NULL;
}

int main() {
    pthread_t producer_thread, consumer_thread;

    pthread_create(&producer_thread, NULL, compute_sum_of_squares, NULL);
    pthread_create(&consumer_thread, NULL, reader, NULL);

    pthread_join(producer_thread, NULL);
    pthread_join(consumer_thread, NULL);

    return 0;
}
