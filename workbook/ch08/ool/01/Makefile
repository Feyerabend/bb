PYTHON ?= python3
CC ?= gcc
CFLAGS ?= -Wall -g

# Targets
all: dog animal

# First compilation chain
dog: dog.c
	$(CC) $(CFLAGS) dog.c -o dog

# Generate dog.c from dog.oo
dog.c: dog.oo compiler.py
	$(PYTHON) compiler.py dog.oo

# Second compilation chain
animal: output.c
	$(CC) $(CFLAGS) output.c -o animal

# Generate output.c
output.c: compiler2.py
	$(PYTHON) compiler2.py

# Clean generated files
clean:
	rm -f dog animal dog.c output.c
