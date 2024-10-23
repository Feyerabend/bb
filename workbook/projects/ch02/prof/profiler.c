#include "profiler.h"

void profiler_init(Profiler* profiler) {
    for (int i = 0; i < 256; i++) {
        profiler->opcode_count[i] = 0;
        profiler->opcode_time[i] = 0;
    }
    profiler->frame_push_count = 0;
    profiler->frame_pop_count = 0;
    profiler->stack_push_count = 0;
    profiler->stack_pop_count = 0;
    profiler->total_time = 0;
}

void profiler_start(Profiler* profiler) {
    profiler->total_time = clock();
}

void profiler_record_opcode(Profiler* profiler, int opcode, clock_t start_time) {
    profiler->opcode_count[opcode]++;
    profiler->opcode_time[opcode] += clock() - start_time;
}

void profiler_record_push_frame(Profiler* profiler) {
    profiler->frame_push_count++;
}

void profiler_record_pop_frame(Profiler* profiler) {
    profiler->frame_pop_count++;
}

void profiler_record_push(Profiler* profiler) {
    profiler->stack_push_count++;
}

void profiler_record_pop(Profiler* profiler) {
    profiler->stack_pop_count++;
}

void profiler_report(Profiler* profiler) {
    printf("\n--- Profiler Report ---\n");
    printf("Total execution time: %.2f seconds\n", (double)(clock() - profiler->total_time) / CLOCKS_PER_SEC);
    
    printf("\nOpcode Execution Counts:\n");
    for (int i = 0; i < 256; i++) {
        if (profiler->opcode_count[i] > 0) {
            printf("Opcode %d executed %d times, total time: %.2f ms\n",
                   i, profiler->opcode_count[i],
                   (double)profiler->opcode_time[i] * 1000 / CLOCKS_PER_SEC);
        }
    }

    printf("\nFrame Push Count: %d\n", profiler->frame_push_count);
    printf("Frame Pop Count: %d\n", profiler->frame_pop_count);
    printf("Stack Push Count: %d\n", profiler->stack_push_count);
    printf("Stack Pop Count: %d\n", profiler->stack_pop_count);
}
