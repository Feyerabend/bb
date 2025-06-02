#ifndef PLUGIN_INTERFACE_H
#define PLUGIN_INTERFACE_H

// Structured input for plugins: a "job" with data and options
typedef struct {
    const char* data;   // Input data (e.g., string to process)
    int option;         // An option flag (e.g., 0 for default, 1 for verbose)
    int id;             // Job ID for tracking
} Job;

// Plugin interface
typedef struct {
    const char* (*name)(void);                  // Plugin name
    int (*init)(const char* config);            // Initialize with config
    int (*execute)(const Job* job, char* result, int result_size); // Process job, return status
    void (*cleanup)(void);                      // Cleanup resources
} Plugin;

#endif // PLUGIN_INTERFACE_H