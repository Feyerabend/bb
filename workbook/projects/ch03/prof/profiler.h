#ifndef PROFILER_H
#define PROFILER_H

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    int opcode_count[256]; // max number opcodes 256
    clock_t opcode_time[256];
    int frame_push_count;
    int frame_pop_count;
    int stack_push_count;
    int stack_pop_count;
    clock_t total_time;
} Profiler;

void profiler_init(Profiler* profiler);
void profiler_start(Profiler* profiler);
void profiler_record_opcode(Profiler* profiler, int opcode, clock_t start_time);
void profiler_record_push_frame(Profiler* profiler);
void profiler_record_pop_frame(Profiler* profiler);
void profiler_record_push(Profiler* profiler);
void profiler_record_pop(Profiler* profiler);
void profiler_report(Profiler* profiler);

#endif // PROFILER_H
