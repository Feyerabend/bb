# Compiler to use
CC = gcc

# Compiler flags
CFLAGS = -Wall -O2

# Source directory for generated C files
SRC_DIR = .

# Output directory for executables
OUT_DIR = bin

# Find all .c files in the source directory
SOURCES = $(wildcard $(SRC_DIR)/*.c)

# Generate executable names (e.g., program1 from program1.c)
EXECS = $(patsubst $(SRC_DIR)/%.c,$(OUT_DIR)/%,$(SOURCES))

# Default target
all: $(OUT_DIR) $(EXECS)

# Create output directory if it doesn't exist
$(OUT_DIR):
	mkdir -p $(OUT_DIR)

# Rule to compile each .c file into an executable
$(OUT_DIR)/%: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) $< -o $@

# Clean up generated files
clean:
	rm -rf $(OUT_DIR)/*.o $(OUT_DIR)/*

# Phony targets
.PHONY: all clean
