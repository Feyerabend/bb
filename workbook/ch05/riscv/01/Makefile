# RISC-V Assembler and VM Makefile

# Find all .asm files
ASM_SOURCES := $(wildcard *.asm)
BIN_TARGETS := $(ASM_SOURCES:.asm=.bin)

# Python interpreter
PYTHON := python3

# Assembler and VM scripts
ASM := ./asm.py
VM := ./vm.py

# Default target: build all .bin files
.PHONY: all
all: $(BIN_TARGETS)

# Rule to assemble .asm files to .bin files
%.bin: %.asm $(ASM)
	$(PYTHON) $(ASM) $< $@

# Run a specific .bin file (usage: make run BIN=program.bin)
.PHONY: run
run:
ifndef BIN
	@echo "Usage: make run BIN=program.bin"
	@exit 1
endif
	$(PYTHON) $(VM) $(BIN)

# Run with debug output
.PHONY: debug
debug:
ifndef BIN
	@echo "Usage: make debug BIN=program.bin"
	@exit 1
endif
	$(PYTHON) $(VM) $(BIN) -d

# Clean all generated .bin files
.PHONY: clean
clean:
	rm -f *.bin

# Run all .bin files
.PHONY: run-all
run-all: $(BIN_TARGETS)
	@for bin in $(BIN_TARGETS); do \
		echo "=== Running $$bin ==="; \
		$(PYTHON) $(VM) $$bin || true; \
		echo ""; \
	done

# Help target
.PHONY: help
help:
	@echo "RISC-V Assembler Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Assemble all .asm files to .bin (default)"
	@echo "  %.bin        - Assemble specific .asm file to .bin"
	@echo "  run          - Run a .bin file (usage: make run BIN=program.bin)"
	@echo "  debug        - Run with debug output (usage: make debug BIN=program.bin)"
	@echo "  run-all      - Run all .bin files"
	@echo "  clean        - Remove all .bin files"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make                    # Build all .asm files"
	@echo "  make program.bin        # Build program.asm to program.bin"
	@echo "  make run BIN=prog.bin   # Run prog.bin"
	@echo "  make debug BIN=prog.bin # Run prog.bin with debug output"
