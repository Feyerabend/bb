// main.c
#include "logger.h"
#include <unistd.h>

int main(void) {
    if (logger_init("system.log") != 0) {
        perror("Logger failed to initialize");
        return 1;
    }

    logger_log("System started, PID=%d", getpid());
    logger_log("Some diagnostic value: %f", 3.1415);

    logger_close();
    return 0;
}
