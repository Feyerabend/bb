# Variables for C files
CC = gcc
CFLAGS = -Wall -g

# List of C source files and output executables
C_SOURCES = avl.c bintree.c bloom.c btree.c disjoint.c dlist.c hash.c hashs.c heap.c kdtree.c kruskal.c list.c pqueue.c queue.c rmq.c segtree.c
C_OBJECTS = $(C_SOURCES:.c=.o)
EXECUTABLES = avl bintree bloom btree disjoint dlist hash hashs heap kdtree kruskal list pqueue queue rmq segtree

# Python files
PYTHON_SCRIPTS = avl.py bintree.py bloom.py btree.py disjoint.py dlist.py hash.py heap.py kdtree.py kruskal.py list.py pqueue.py queue.py rmq.py segtree.py

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
