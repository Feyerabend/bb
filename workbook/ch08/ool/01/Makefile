# Compiler and flags
CC = gcc
CFLAGS = -Wall -g

# Source file (change this to your .oo file)
SOURCE = dog.oo
BASE = $(basename $(SOURCE))
OUTPUT = $(BASE)

all: $(OUTPUT)

# Generate C code and compile
$(OUTPUT): $(BASE).c
	$(CC) $(CFLAGS) -o $@ $<

# Rule to generate C code from OO-Lite
%.c: %.oo compiler.py
	python3 compiler.py $<

# Run the program
run: $(OUTPUT)
	./$(OUTPUT)

# Clean generated files
clean:
	rm -f $(BASE).c $(OUTPUT)
	rm -Rf *.dSYM

.PHONY: all run clean
