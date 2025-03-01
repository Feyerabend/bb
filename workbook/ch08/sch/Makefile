CC = gcc           # Compiler to use
CFLAGS = -Wall     # Compiler flags, e.g., to show warnings

# Targets for each program
TARGETS = sch sche

# Default target (build both executables)
all: $(TARGETS)

# Compile sch.c into sch executable
sch: sch.o
	$(CC) -o sch sch.o

# Compile sche.c into sche executable
sche: sche.o
	$(CC) -o sche sche.o

# Rule for compiling C files into object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up object and executable files
clean:
	rm -f *.o $(TARGETS)

# Run sch executable
run_sch: sch
	./sch

# Run sche executable
run_sche: sche
	./sche