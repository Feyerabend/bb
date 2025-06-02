#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../plugin_interface.h"

// Plugin state
static int total_sum = 0;

static const char* plugin_name() {
    return "add";
}

static int plugin_init(const char* config) {
    total_sum = 0;
    return 0;
}

static int plugin_execute(const Job* job, char* result, int result_size) {
    if (!job || !job->data) {
        snprintf(result, result_size, "Add: No input data");
        return -1;
    }
    
    // Parse two numbers from data (e.g., "5 10")
    int a, b;
    if (sscanf(job->data, "%d %d", &a, &b) != 2) {
        snprintf(result, result_size, "Add: Invalid input format, need 'num1 num2'");
        return -1;
    }
    
    int sum = a + b;
    total_sum += sum;
    
    if (job->option == 1) {
        snprintf(result, result_size, "Sum of %d + %d = %d (running total: %d)", a, b, sum, total_sum);
    } else {
        snprintf(result, result_size, "Sum: %d", sum);
    }
    return 0;
}

static void plugin_cleanup() {
    total_sum = 0;
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