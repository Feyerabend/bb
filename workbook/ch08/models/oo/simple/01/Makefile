# Compiler and flags
CC = gcc
CFLAGS = -Wall -g

# Source file (change this to your .oo file)
SOURCE = dog.oo
BASE = $(basename $(SOURCE))
OUTPUT = $(BASE)

# Paths for symbol table and intermediate files
SYMTABLES = $(BASE).sym
OBJFILES = $(BASE).o

all: $(OUTPUT)

# Generate C code and compile
$(OUTPUT): $(BASE).c
	$(CC) $(CFLAGS) -o $@ $<
	@echo "Compilation successful!"

# Rule to generate C code from OO-Lite
%.c: %.oo compiler.py
	python3 compiler.py $<

# Run the program
run: $(OUTPUT)
	./$(OUTPUT)

# Clean generated files
clean:
	rm -f $(BASE).c $(OUTPUT) $(OBJFILES)
	rm -Rf *.dSYM

# Deep clean - includes symbol tables and all intermediate files
distclean: clean
	rm -f $(SYMTABLES)
	rm -f *.i *.s      # Preprocessor and assembly outputs
	rm -f *~ \#*\#     # Backup and temporary files
	find . -name "*.sym" -type f -delete
	find . -name "*.tmp" -type f -delete
	@echo "All symbol tables and intermediate files removed."

# Generate symbol table for debugging (if needed)
symbols: $(OUTPUT)
	nm -a $(OUTPUT) > $(SYMTABLES)
	@echo "Symbol table generated in $(SYMTABLES)"

# Strip symbols for release version
strip: $(OUTPUT)
	strip -s $(OUTPUT)
	@echo "Symbols stripped from executable"

.PHONY: all run clean distclean symbols strip
