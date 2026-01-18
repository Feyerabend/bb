# Variables for C files
CC = gcc
CFLAGS = -Wall -g

# List of C source files and output executables
C_SOURCES = actives.c astar.c avl.c bfs.c bintree.c bloom.c bsearch.c bst.c btree.c cqueue.c dfs.c dijkstra.c disjoint.c dlist.c fenwick.c fibheap.c fw.c hash.c hashs.c heap.c huffman.c kdtree.c kmp.c kruskal.c lcs.c list.c msort.c pqueue.c prims.c rabin.c rmq.c segtree.c skipl.c splayt.c suffix.c treap.c trie.c
C_OBJECTS = $(C_SOURCES:.c=.o)
EXECUTABLES = actives astar avl bfs bintree bloom bsearch bst btree cqueue dfs dijkstra disjoint dlist fenwick fibheap fw hash hashs heap huffman kdtree kmp kruskal lcs list msort pqueue prims rabin rmq segtree skipl splayt suffix treap trie

# Python files
PYTHON_SCRIPTS = actives.py astar.py avl.py bfs.py bintree.py bloom.py bsearch.py bst.py btree.py cmsort.py cqueue.py dfs.py dijkstra.py disjoint.py dlist.py fenwick.py fibheap.py fw.py hash.py heap.py huffman.py kdtree.py kmp.py kruskal.py lcs.py list.py msort.py pqueue.py prims.py rabin.py rmq.py segtree.py skipl.py splayt.py suffix.py treap.py trie.py

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
