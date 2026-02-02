# Z80 Emulator and Test Suite Makefile
# ======================================

# Compiler settings
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2
LDFLAGS =

# Python assembler
ASM = python3 z80asm.py
ASMFLAGS = -s ZASM --fill 0xFF

# Test programs
Z80_SOURCES = hello.z80 math.z80 loop.z80 registers.z80 stack.z80 subroutine.z80
COM_FILES = $(Z80_SOURCES:.z80=.com)
LST_FILES = $(Z80_SOURCES:.z80=.lst)

# C sources and objects
C_SOURCES = run_test.c z80.c
OBJECTS = $(C_SOURCES:.c=.o)
EXECUTABLE = run_test

# Default target
.PHONY: all
all: $(EXECUTABLE) $(COM_FILES)

# Compile C source files
%.o: %.c z80.h
	$(CC) $(CFLAGS) -c $< -o $@

# Link the executable
$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $^ -o $@

# Assemble Z80 programs
%.com: %.z80
	$(ASM) $(ASMFLAGS) -b $@ -l $*.lst $<

# Test targets
.PHONY: test test-hello test-math test-loop test-registers test-stack test-subroutine test-all

# Run the default test (hello)
test: test-hello

# Individual test targets
test-hello: hello.com $(EXECUTABLE)
	@echo "=== Running hello.z80 test ==="
	@ln -sf hello.com test.com
	@./$(EXECUTABLE)
	@echo ""

test-math: math.com $(EXECUTABLE)
	@echo "=== Running math.z80 test ==="
	@ln -sf math.com test.com
	@./$(EXECUTABLE)
	@echo ""

test-loop: loop.com $(EXECUTABLE)
	@echo "=== Running loop.z80 test ==="
	@ln -sf loop.com test.com
	@./$(EXECUTABLE)
	@echo ""

test-registers: registers.com $(EXECUTABLE)
	@echo "=== Running registers.z80 test ==="
	@ln -sf registers.com test.com
	@./$(EXECUTABLE)
	@echo ""

test-stack: stack.com $(EXECUTABLE)
	@echo "=== Running stack.z80 test ==="
	@ln -sf stack.com test.com
	@./$(EXECUTABLE)
	@echo ""

test-subroutine: subroutine.com $(EXECUTABLE)
	@echo "=== Running subroutine.z80 test ==="
	@ln -sf subroutine.com test.com
	@./$(EXECUTABLE)
	@echo ""

# Run all tests
test-all: $(COM_FILES) $(EXECUTABLE)
	@echo "=========================================="
	@echo "  Running All Z80 Tests"
	@echo "=========================================="
	@echo ""
	@$(MAKE) --no-print-directory test-hello
	@$(MAKE) --no-print-directory test-math
	@$(MAKE) --no-print-directory test-loop
	@$(MAKE) --no-print-directory test-registers
	@$(MAKE) --no-print-directory test-stack
	@$(MAKE) --no-print-directory test-subroutine
	@echo "=========================================="
	@echo "  All Tests Complete"
	@echo "=========================================="

# Utility targets
.PHONY: clean clean-all rebuild help

# Clean compiled files
clean:
	rm -f $(OBJECTS) $(EXECUTABLE) $(COM_FILES) $(LST_FILES) test.com

# Deep clean including any backups
clean-all: clean
	rm -f *~ *.bak

# Rebuild from scratch
rebuild: clean all

# Show help
help:
	@echo "Z80 Emulator Makefile"
	@echo "====================="
	@echo ""
	@echo "Build targets:"
	@echo "  all          - Build emulator and assemble all test programs (default)"
	@echo "  $(EXECUTABLE)     - Build only the emulator executable"
	@echo "  %.com        - Assemble specific Z80 program (e.g., make hello.com)"
	@echo ""
	@echo "Test targets:"
	@echo "  test           - Run default test (hello)"
	@echo "  test-hello     - Run hello.z80 test (Hello World)"
	@echo "  test-math      - Run math.z80 test (arithmetic operations)"
	@echo "  test-loop      - Run loop.z80 test (loop counter 0-9)"
	@echo "  test-registers - Run registers.z80 test (register operations)"
	@echo "  test-stack     - Run stack.z80 test (PUSH/POP operations)"
	@echo "  test-subroutine- Run subroutine.z80 test (CALL/RET)"
	@echo "  test-all       - Run all tests sequentially"
	@echo ""
	@echo "Utility targets:"
	@echo "  clean        - Remove compiled and assembled files"
	@echo "  clean-all    - Remove all generated files including backups"
	@echo "  rebuild      - Clean and rebuild everything"
	@echo "  debug        - Show Makefile variables"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Available test programs:"
	@echo "  $(Z80_SOURCES)"

# Show variables (for debugging the Makefile)
.PHONY: debug
debug:
	@echo "CC         = $(CC)"
	@echo "CFLAGS     = $(CFLAGS)"
	@echo "ASM        = $(ASM)"
	@echo "ASMFLAGS   = $(ASMFLAGS)"
	@echo "C_SOURCES  = $(C_SOURCES)"
	@echo "OBJECTS    = $(OBJECTS)"
	@echo "Z80_SOURCES= $(Z80_SOURCES)"
	@echo "COM_FILES  = $(COM_FILES)"
	@echo "LST_FILES  = $(LST_FILES)"
	@echo "EXECUTABLE = $(EXECUTABLE)"

# Prevent deletion of intermediate files
.PRECIOUS: %.o %.com

# Dependencies
run_test.o: run_test.c z80.h
z80.o: z80.c z80.h
