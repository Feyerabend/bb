# Define compiler and flags
CC = gcc
CFLAGS = -Wall -g
PLUGIN_FLAGS = -shared -fPIC
LDLIBS = -ldl

# Directories
PLUGIN_DIR = plugins
BIN = core

# Source files
CORE_SRC = core.c
PLUGIN_SRCS = $(PLUGIN_DIR)/wordcount_plugin.c $(PLUGIN_DIR)/add_plugin.c
PLUGIN_OBJS = $(PLUGIN_SRCS:.c=.so)

# Default target
all: $(BIN) $(PLUGIN_OBJS)

# Build the core program
$(BIN): $(CORE_SRC)
	$(CC) $(CFLAGS) -o $@ $< $(LDLIBS)

# Build plugin shared objects
$(PLUGIN_DIR)/%.so: $(PLUGIN_DIR)/%.c
	$(CC) $(CFLAGS) $(PLUGIN_FLAGS) -o $@ $<

# Clean up
clean:
	rm -f $(BIN) $(PLUGIN_DIR)/*.so

# Phony targets
.PHONY: all clean