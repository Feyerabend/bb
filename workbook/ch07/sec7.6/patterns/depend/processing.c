#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


// INTERFACES (Via Function Pointers in C)

// Forward declarations
typedef struct DataProcessor DataProcessor;
typedef struct Logger Logger;
typedef struct MetricsCollector MetricsCollector;

// Data structure being processed
typedef struct {
    char* content;
    size_t length;
    char* metadata;
} DataPacket;

// Logger interface
typedef struct Logger {
    void (*log_info)(struct Logger* self, const char* message);
    void (*log_error)(struct Logger* self, const char* message);
    void (*cleanup)(struct Logger* self);
    void* state;  // Implementation-specific state
} Logger;

// Metrics collector interface
typedef struct MetricsCollector {
    void (*record_processing_time)(struct MetricsCollector* self, 
                                   const char* processor_name, 
                                   double time_ms);
    void (*increment_counter)(struct MetricsCollector* self, 
                             const char* counter_name);
    void (*report)(struct MetricsCollector* self);
    void (*cleanup)(struct MetricsCollector* self);
    void* state;
} MetricsCollector;

// Data processor interface
typedef struct DataProcessor {
    const char* name;
    int (*process)(struct DataProcessor* self, DataPacket* packet);
    void (*cleanup)(struct DataProcessor* self);
    void* state;
    Logger* logger;              // Injected dependency
    MetricsCollector* metrics;   // Injected dependency
} DataProcessor;


// LOGGER IMPLEMENTATIONS

// Console Logger State
typedef struct {
    int message_count;
    FILE* output;
} ConsoleLoggerState;

void console_log_info(Logger* self, const char* message) {
    ConsoleLoggerState* state = (ConsoleLoggerState*)self->state;
    fprintf(state->output, "[INFO] %s\n", message);
    state->message_count++;
}

void console_log_error(Logger* self, const char* message) {
    ConsoleLoggerState* state = (ConsoleLoggerState*)self->state;
    fprintf(state->output, "[ERROR] %s\n", message);
    state->message_count++;
}

void console_logger_cleanup(Logger* self) {
    ConsoleLoggerState* state = (ConsoleLoggerState*)self->state;
    printf("Console logger handled %d messages\n", state->message_count);
    free(state);
}

Logger* create_console_logger() {
    Logger* logger = (Logger*)malloc(sizeof(Logger));
    ConsoleLoggerState* state = (ConsoleLoggerState*)malloc(sizeof(ConsoleLoggerState));
    
    state->message_count = 0;
    state->output = stdout;
    
    logger->log_info = console_log_info;
    logger->log_error = console_log_error;
    logger->cleanup = console_logger_cleanup;
    logger->state = state;
    
    return logger;
}

// File Logger State
typedef struct {
    int message_count;
    FILE* file;
    char* filename;
} FileLoggerState;

void file_log_info(Logger* self, const char* message) {
    FileLoggerState* state = (FileLoggerState*)self->state;
    time_t now = time(NULL);
    char* timestamp = ctime(&now);
    timestamp[strlen(timestamp)-1] = '\0';  // Remove newline
    fprintf(state->file, "[%s] [INFO] %s\n", timestamp, message);
    fflush(state->file);
    state->message_count++;
}

void file_log_error(Logger* self, const char* message) {
    FileLoggerState* state = (FileLoggerState*)self->state;
    time_t now = time(NULL);
    char* timestamp = ctime(&now);
    timestamp[strlen(timestamp)-1] = '\0';
    fprintf(state->file, "[%s] [ERROR] %s\n", timestamp, message);
    fflush(state->file);
    state->message_count++;
}

void file_logger_cleanup(Logger* self) {
    FileLoggerState* state = (FileLoggerState*)self->state;
    printf("File logger wrote %d messages to %s\n", 
           state->message_count, state->filename);
    fclose(state->file);
    free(state->filename);
    free(state);
}

Logger* create_file_logger(const char* filename) {
    Logger* logger = (Logger*)malloc(sizeof(Logger));
    FileLoggerState* state = (FileLoggerState*)malloc(sizeof(FileLoggerState));
    
    state->message_count = 0;
    state->file = fopen(filename, "w");
    state->filename = strdup(filename);
    
    logger->log_info = file_log_info;
    logger->log_error = file_log_error;
    logger->cleanup = file_logger_cleanup;
    logger->state = state;
    
    return logger;
}


// METRICS COLLECTOR IMPLEMENTATIONS

typedef struct {
    double total_time;
    int processing_count;
    int validation_failures;
    int transformations;
} SimpleMetricsState;

void simple_record_time(MetricsCollector* self, const char* name, double time_ms) {
    SimpleMetricsState* state = (SimpleMetricsState*)self->state;
    state->total_time += time_ms;
    state->processing_count++;
}

void simple_increment_counter(MetricsCollector* self, const char* counter_name) {
    SimpleMetricsState* state = (SimpleMetricsState*)self->state;
    if (strcmp(counter_name, "validation_failures") == 0) {
        state->validation_failures++;
    } else if (strcmp(counter_name, "transformations") == 0) {
        state->transformations++;
    }
}

void simple_report(MetricsCollector* self) {
    SimpleMetricsState* state = (SimpleMetricsState*)self->state;
    printf("\n-- Metrics Report --\n");
    printf("Total processing time: %.2f ms\n", state->total_time);
    printf("Packets processed: %d\n", state->processing_count);
    printf("Validation failures: %d\n", state->validation_failures);
    printf("Transformations applied: %d\n", state->transformations);
    printf("Average time per packet: %.2f ms\n", 
           state->total_time / (state->processing_count > 0 ? state->processing_count : 1));
}

void simple_metrics_cleanup(MetricsCollector* self) {
    free(self->state);
}

MetricsCollector* create_simple_metrics() {
    MetricsCollector* metrics = (MetricsCollector*)malloc(sizeof(MetricsCollector));
    SimpleMetricsState* state = (SimpleMetricsState*)calloc(1, sizeof(SimpleMetricsState));
    
    metrics->record_processing_time = simple_record_time;
    metrics->increment_counter = simple_increment_counter;
    metrics->report = simple_report;
    metrics->cleanup = simple_metrics_cleanup;
    metrics->state = state;
    
    return metrics;
}


// DATA PROCESSOR IMPLEMENTATIONS

// Validation Processor
typedef struct {
    int min_length;
    int max_length;
} ValidationState;

int validation_process(DataProcessor* self, DataPacket* packet) {
    ValidationState* state = (ValidationState*)self->state;
    clock_t start = clock();
    
    char log_msg[256];
    snprintf(log_msg, sizeof(log_msg), 
             "Validating packet: length=%zu, min=%d, max=%d",
             packet->length, state->min_length, state->max_length);
    self->logger->log_info(self->logger, log_msg);
    
    int valid = 1;
    if (packet->length < state->min_length || packet->length > state->max_length) {
        self->logger->log_error(self->logger, "Validation failed: packet size out of range");
        self->metrics->increment_counter(self->metrics, "validation_failures");
        valid = 0;
    }
    
    clock_t end = clock();
    double time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    self->metrics->record_processing_time(self->metrics, self->name, time_ms);
    
    return valid;
}

void validation_cleanup(DataProcessor* self) {
    free(self->state);
}

DataProcessor* create_validation_processor(int min_len, int max_len, 
                                           Logger* logger, 
                                           MetricsCollector* metrics) {
    DataProcessor* proc = (DataProcessor*)malloc(sizeof(DataProcessor));
    ValidationState* state = (ValidationState*)malloc(sizeof(ValidationState));
    
    state->min_length = min_len;
    state->max_length = max_len;
    
    proc->name = "ValidationProcessor";
    proc->process = validation_process;
    proc->cleanup = validation_cleanup;
    proc->state = state;
    proc->logger = logger;    // DEPENDENCY INJECTION
    proc->metrics = metrics;  // DEPENDENCY INJECTION
    
    return proc;
}

// Transformation Processor
typedef struct {
    int transform_type;  // 0=uppercase, 1=lowercase, 2=reverse
} TransformState;

int transform_process(DataProcessor* self, DataPacket* packet) {
    TransformState* state = (TransformState*)self->state;
    clock_t start = clock();
    
    self->logger->log_info(self->logger, "Applying transformation to packet");
    
    switch(state->transform_type) {
        case 0:  // uppercase
            for (size_t i = 0; i < packet->length; i++) {
                if (packet->content[i] >= 'a' && packet->content[i] <= 'z') {
                    packet->content[i] -= 32;
                }
            }
            break;
        case 1:  // lowercase
            for (size_t i = 0; i < packet->length; i++) {
                if (packet->content[i] >= 'A' && packet->content[i] <= 'Z') {
                    packet->content[i] += 32;
                }
            }
            break;
        case 2:  // reverse
            for (size_t i = 0; i < packet->length / 2; i++) {
                char temp = packet->content[i];
                packet->content[i] = packet->content[packet->length - 1 - i];
                packet->content[packet->length - 1 - i] = temp;
            }
            break;
    }
    
    self->metrics->increment_counter(self->metrics, "transformations");
    
    clock_t end = clock();
    double time_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    self->metrics->record_processing_time(self->metrics, self->name, time_ms);
    
    return 1;
}

void transform_cleanup(DataProcessor* self) {
    free(self->state);
}

DataProcessor* create_transform_processor(int type, 
                                          Logger* logger, 
                                          MetricsCollector* metrics) {
    DataProcessor* proc = (DataProcessor*)malloc(sizeof(DataProcessor));
    TransformState* state = (TransformState*)malloc(sizeof(TransformState));
    
    state->transform_type = type;
    
    proc->name = "TransformProcessor";
    proc->process = transform_process;
    proc->cleanup = transform_cleanup;
    proc->state = state;
    proc->logger = logger;    // DEPENDENCY INJECTION
    proc->metrics = metrics;  // DEPENDENCY INJECTION
    
    return proc;
}


// PROCESSING PIPELINE

typedef struct {
    DataProcessor** processors;
    int count;
    Logger* logger;
    MetricsCollector* metrics;
} ProcessingPipeline;

ProcessingPipeline* create_pipeline(Logger* logger, MetricsCollector* metrics) {
    ProcessingPipeline* pipeline = (ProcessingPipeline*)malloc(sizeof(ProcessingPipeline));
    pipeline->processors = NULL;
    pipeline->count = 0;
    pipeline->logger = logger;
    pipeline->metrics = metrics;
    return pipeline;
}

void pipeline_add_processor(ProcessingPipeline* pipeline, DataProcessor* processor) {
    pipeline->count++;
    pipeline->processors = (DataProcessor**)realloc(
        pipeline->processors, 
        pipeline->count * sizeof(DataProcessor*)
    );
    pipeline->processors[pipeline->count - 1] = processor;
}

int pipeline_process(ProcessingPipeline* pipeline, DataPacket* packet) {
    char log_msg[256];
    snprintf(log_msg, sizeof(log_msg), 
             "Processing packet through %d stage pipeline", 
             pipeline->count);
    pipeline->logger->log_info(pipeline->logger, log_msg);
    
    for (int i = 0; i < pipeline->count; i++) {
        if (!pipeline->processors[i]->process(pipeline->processors[i], packet)) {
            snprintf(log_msg, sizeof(log_msg), 
                     "Pipeline failed at stage %d (%s)", 
                     i, pipeline->processors[i]->name);
            pipeline->logger->log_error(pipeline->logger, log_msg);
            return 0;
        }
    }
    
    pipeline->logger->log_info(pipeline->logger, "Packet successfully processed");
    return 1;
}

void pipeline_cleanup(ProcessingPipeline* pipeline) {
    for (int i = 0; i < pipeline->count; i++) {
        pipeline->processors[i]->cleanup(pipeline->processors[i]);
        free(pipeline->processors[i]);
    }
    free(pipeline->processors);
    free(pipeline);
}


// DEMO

int main() {
    printf("-- Dependency Injection Demo: Data Processing Pipeline --\n\n");
    
    // STEP 1: Create shared dependencies
    Logger* logger = create_console_logger();
    // Uncomment to use file logger instead:
    // Logger* logger = create_file_logger("pipeline.log");
    
    MetricsCollector* metrics = create_simple_metrics();
    
    // STEP 2: Create processors with injected dependencies
    DataProcessor* validator = create_validation_processor(5, 100, logger, metrics);
    DataProcessor* transformer = create_transform_processor(0, logger, metrics);  // uppercase
    
    // STEP 3: Build pipeline
    ProcessingPipeline* pipeline = create_pipeline(logger, metrics);
    pipeline_add_processor(pipeline, validator);
    pipeline_add_processor(pipeline, transformer);
    
    // STEP 4: Create test data packets
    DataPacket packets[] = {
        {strdup("hello world"), 11, "packet-1"},
        {strdup("dependency injection"), 20, "packet-2"},
        {strdup("abc"), 3, "packet-3"},  // Too short, will fail validation
        {strdup("testing the pipeline with a longer message"), 43, "packet-4"}
    };
    
    // STEP 5: Process packets
    printf("Processing packets..\n\n");
    for (int i = 0; i < 4; i++) {
        printf("--- Packet %d ---\n", i + 1);
        printf("Before: %s\n", packets[i].content);
        
        if (pipeline_process(pipeline, &packets[i])) {
            printf("After:  %s\n", packets[i].content);
        } else {
            printf("Processing failed for this packet\n");
        }
        printf("\n");
    }
    
    // STEP 6: Report metrics
    metrics->report(metrics);
    
    // STEP 7: Cleanup
    for (int i = 0; i < 4; i++) {
        free(packets[i].content);
    }
    pipeline_cleanup(pipeline);
    metrics->cleanup(metrics);
    logger->cleanup(logger);
    free(metrics);
    free(logger);
    
    printf("\n-- Done --\n");
    return 0;
}

