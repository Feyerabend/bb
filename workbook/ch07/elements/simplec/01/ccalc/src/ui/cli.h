// src/ui/cli.h
#ifndef CLI_H
#define CLI_H

#include <stdbool.h>

void print_usage(const char* program_name);
bool process_args(int argc, char* argv[]);

#endif // CLI_H