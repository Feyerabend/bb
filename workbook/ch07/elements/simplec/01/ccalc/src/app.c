// src/app.c
#include "ui/cli.h"
#include "utils/logger.h"
#include <stdlib.h>

int main(int argc, char* argv[]) {
    set_log_level(LOG_INFO);
    LOG_INFO("Starting ccalc application");
    
    if (!process_args(argc, argv)) {
        return EXIT_FAILURE;
    }
    
    LOG_INFO("Operation completed successfully");
    return EXIT_SUCCESS;
}