# Variables for C files
CC = gcc
CFLAGS = -Wall -g

# List of C source files and output executables
C_SOURCES = dlist.c hash.c hashs.c heap.c list.c pqueue.c queue.c
C_OBJECTS = $(C_SOURCES:.c=.o)
EXECUTABLES = dlist hash hashs heap list pqueue queue

# Python files
PYTHON_SCRIPTS = dlist.py hash.py heap.py list.py pqueue.py queue.py

# Default target: build all C programs and run Python scripts
all: $(EXECUTABLES) run_python

# Rule to build each C program
$(EXECUTABLES): %: %.o
	$(CC) $(CFLAGS) -o $@ $^

# Rule to compile C source files into object files
%.o: %.c
	$(CC) $(CFLAGS) -c $<

# Rule to run Python scripts
run_python: $(PYTHON_SCRIPTS)
	@for script in $(PYTHON_SCRIPTS); do \
		echo "Running $$script"; \
		python3 $$script; \
	done

# Clean up object files and executables
clean:
	rm -f $(C_OBJECTS) $(EXECUTABLES)

# Phony targets (these aren't actual files, they're just commands)
.PHONY: all clean run_python
