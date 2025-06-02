#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include "plugin_interface.h"

#define PLUGIN_DIR "plugins"
#define MAX_PLUGINS 100
#define MAX_ERR_MSG 256

// Registry
typedef struct {
    Plugin* plugin;
    void* handle;  // Store handle for dlclose
} PluginEntry;

PluginEntry plugins[MAX_PLUGINS];
int plugin_count = 0;

// Load plugins dynamically
void load_plugins(const char* config) {
    DIR* dir = opendir(PLUGIN_DIR);
    if (!dir) {
        fprintf(stderr, "Error: Could not open plugin directory %s\n", PLUGIN_DIR);
        return;
    }

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strstr(entry->d_name, "_plugin.so") == NULL) continue;
        
        char path[256];
        snprintf(path, sizeof(path), "%s/%s", PLUGIN_DIR, entry->d_name);
        
        void* handle = dlopen(path, RTLD_LAZY);
        if (!handle) {
            fprintf(stderr, "Error loading %s: %s\n", path, dlerror());
            continue;
        }
        
        Plugin* (*init_plugin)(void) = dlsym(handle, "init_plugin");
        if (!init_plugin) {
            fprintf(stderr, "Error: No init_plugin in %s: %s\n", path, dlerror());
            dlclose(handle);
            continue;
        }
        
        if (plugin_count >= MAX_PLUGINS) {
            fprintf(stderr, "Error: Plugin limit reached\n");
            dlclose(handle);
            continue;
        }

        Plugin* plugin = init_plugin();
        if (plugin->init(config) != 0) {
            fprintf(stderr, "Error: Failed to initialize plugin from %s\n", path);
            dlclose(handle);
            continue;
        }

        plugins[plugin_count].plugin = plugin;
        plugins[plugin_count].handle = handle;
        printf("Loaded plugin: %s\n", plugin->name());
        plugin_count++;
    }
    closedir(dir);
}

// Find and run a plugin
int run_command(const char* name, const Job* job, char* result, int result_size) {
    for (int i = 0; i < plugin_count; i++) {
        if (strcmp(plugins[i].plugin->name(), name) == 0) {
            int status = plugins[i].plugin->execute(job, result, result_size);
            if (status != 0) {
                snprintf(result, result_size, "Error: Plugin '%s' failed with status %d", name, status);
                return status;
            }
            return 0;
        }
    }
    snprintf(result, result_size, "Error: Command '%s' not found", name);
    return -1;
}

// Cleanup all plugins
void cleanup_plugins() {
    for (int i = 0; i < plugin_count; i++) {
        if (plugins[i].plugin->cleanup) {
            plugins[i].plugin->cleanup();
        }
        dlclose(plugins[i].handle);
    }
    plugin_count = 0;
}

// Main
int main() {
    char result[MAX_ERR_MSG];
    
    // Load plugins with a sample config (e.g., a log file path)
    load_plugins("log.txt");
    
    // Define sample jobs
    Job job1 = { .data = "Hello world this is a test", .option = 1, .id = 1 };
    Job job2 = { .data = "5 10", .option = 0, .id = 2 };
    
    // Run plugins
    if (run_command("wordcount", &job1, result, MAX_ERR_MSG) == 0) {
        printf("Result: %s\n", result);
    } else {
        fprintf(stderr, "%s\n", result);
    }
    
    if (run_command("add", &job2, result, MAX_ERR_MSG) == 0) {
        printf("Result: %s\n", result);
    } else {
        fprintf(stderr, "%s\n", result);
    }
    
    // Cleanup
    cleanup_plugins();
    return 0;
}