#include "logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <pthread.h>
#include <string.h>

static FILE *log_file = NULL;
static pthread_once_t init_once = PTHREAD_ONCE_INIT;

// fallback initialization if logger_log() is used before logger_init()
static void ensure_initialized(void) {
    if (log_file == NULL) {
        log_file = fopen("/tmp/default.log", "a");
        if (!log_file) {
            perror("Could not open default fallback log file");
            exit(EXIT_FAILURE);
        }
        setvbuf(log_file, NULL, _IONBF, 0);  // Unbuffered I/O
    }
}

int logger_init(const char *filename) {
    if (log_file != NULL) return 0;  // Already initialized

    log_file = fopen(filename, "a");
    if (!log_file) {
        perror("fopen in logger_init");
        return -1;
    }

    setvbuf(log_file, NULL, _IONBF, 0);  // Optional: force unbuffered
    return 0;
}

void logger_log(const char *format, ...) {
    pthread_once(&init_once, ensure_initialized);

    if (!log_file) {
        fprintf(stderr, "logger_log called but no log_file is open\n");
        return;
    }

    va_list args;
    va_start(args, format);
    vfprintf(log_file, format, args);
    fprintf(log_file, "\n");
    va_end(args);
    fflush(log_file);  // Always flush to ensure write
}

void logger_close(void) {
    if (log_file) {
        fclose(log_file);
        log_file = NULL;
    }
}