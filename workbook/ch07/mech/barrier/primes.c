#include <stdio.h>
#include <pthread.h>
#include <stdatomic.h>
#include <math.h>

#define MAX 100000
#define NUM_THREADS 4

typedef struct {
    int start, end, id;
} Task;


atomic_int done[NUM_THREADS];
int prime_counts[NUM_THREADS]; // not atomic, but protected by fences

int is_prime(int n) {
    if (n <= 1) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    for (int i = 3; i <= sqrt(n); i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

void* worker(void* arg) {
    Task* task = (Task*)arg;
    int count = 0;
    for (int i = task->start; i <= task->end; ++i) {
        if (is_prime(i)) count++;
    }

    prime_counts[task->id] = count;

    // memory visibility of result
    atomic_thread_fence(memory_order_release);

    // signal completion
    atomic_store(&done[task->id], 1);

    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    Task tasks[NUM_THREADS];
    int range = MAX / NUM_THREADS;

    // init flags
    for (int i = 0; i < NUM_THREADS; ++i) {
        atomic_store(&done[i], 0);
    }

    // spawn threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        tasks[i].start = i * range + 1;
        tasks[i].end = (i == NUM_THREADS - 1) ? MAX : (i + 1) * range;
        tasks[i].id = i;
        pthread_create(&threads[i], NULL, worker, &tasks[i]);
    }

    // wait for all threads to complete
    for (int i = 0; i < NUM_THREADS; ++i) {
        while (atomic_load(&done[i]) == 0)
            ; // spin
        atomic_thread_fence(memory_order_acquire);
    }

    // aggregate results
    int total = 0;
    for (int i = 0; i < NUM_THREADS; ++i) {
        total += prime_counts[i];
    }

    printf("Total number of primes up to %d is %d\n", MAX, total);

    // join threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
