#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../plugin_interface.h"

// Plugin state
static FILE* log_file = NULL;
static int count_jobs = 0;

static const char* plugin_name() {
    return "wordcount";
}

static int plugin_init(const char* config) {
    if (config) {
        log_file = fopen(config, "a");
        if (!log_file) {
            fprintf(stderr, "Wordcount: Failed to open log file %s\n", config);
            return -1;
        }
    }
    count_jobs = 0;
    return 0;
}

static int plugin_execute(const Job* job, char* result, int result_size) {
    if (!job || !job->data) {
        snprintf(result, result_size, "Wordcount: No input data");
        return -1;
    }
    
    // Count words (simple: split by spaces)
    int words = 0;
    const char* ptr = job->data;
    int in_word = 0;
    while (*ptr) {
        if (*ptr == ' ' || *ptr == '\n' || *ptr == '\t') {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            words++;
        }
        ptr++;
    }
    
    // Log if verbose and file is open
    if (job->option == 1 && log_file) {
        fprintf(log_file, "Job %d: Processed '%s', found %d words\n", job->id, job->data, words);
        fflush(log_file);
    }
    
    count_jobs++;
    snprintf(result, result_size, "Word count: %d (total jobs: %d)", words, count_jobs);
    return 0;
}

static void plugin_cleanup() {
    if (log_file) {
        fclose(log_file);
        log_file = NULL;
    }
    count_jobs = 0;
}

Plugin* init_plugin() {
    static Plugin plugin = {
        .name = plugin_name,
        .init = plugin_init,
        .execute = plugin_execute,
        .cleanup = plugin_cleanup
    };
    return &plugin;
}