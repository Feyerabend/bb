// logger.h
#ifndef LOGGER_H
#define LOGGER_H

#include <stdio.h>

int logger_init(const char *filename);
void logger_log(const char *format, ...);
void logger_close(void);

#endif // LOGGER_H
