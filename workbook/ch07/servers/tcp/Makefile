# Makefile for TCP/IP Stack Projects
# Supports both basic TCP/IP stack and custom MyNet protocol implementation

# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -g
LDFLAGS = 
LIBS = 

# Target executables
TARGETS = regtcp custom

# Source files
REGTCP_SOURCES = regtcp.c
CUSTOM_SOURCES = custom.c

# Object files
REGTCP_OBJECTS = $(REGTCP_SOURCES:.c=.o)
CUSTOM_OBJECTS = $(CUSTOM_SOURCES:.c=.o)

# Default target
all: $(TARGETS)

# Build basic TCP/IP stack
regtcp: $(REGTCP_OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

# Build custom MyNet protocol stack
custom: $(CUSTOM_OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

# Compile source files to object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(TARGETS) $(REGTCP_OBJECTS) $(CUSTOM_OBJECTS)

# Clean everything including backup files
distclean: clean
	rm -f *~ *.bak

# Install targets (optional)
install: $(TARGETS)
	mkdir -p $(DESTDIR)/usr/local/bin
	cp $(TARGETS) $(DESTDIR)/usr/local/bin/

# Uninstall targets
uninstall:
	rm -f $(DESTDIR)/usr/local/bin/regtcp
	rm -f $(DESTDIR)/usr/local/bin/custom

# Run basic TCP/IP stack demo
run-basic: regtcp
	./regtcp

# Run custom MyNet protocol demo
run-custom: custom
	./custom

# Run both demos
run-all: run-basic run-custom

# Debug builds with additional flags
debug: CFLAGS += -DDEBUG -fsanitize=address -fsanitize=undefined
debug: clean $(TARGETS)

# Release builds with optimization
release: CFLAGS += -O3 -DNDEBUG
release: clean $(TARGETS)

# Static analysis with various tools (if available)
analyze:
	@which cppcheck >/dev/null 2>&1 && cppcheck --enable=all $(REGTCP_SOURCES) $(CUSTOM_SOURCES) || echo "cppcheck not found"
	@which clang-tidy >/dev/null 2>&1 && clang-tidy $(REGTCP_SOURCES) $(CUSTOM_SOURCES) -- $(CFLAGS) || echo "clang-tidy not found"

# Format code (if clang-format is available)
format:
	@which clang-format >/dev/null 2>&1 && clang-format -i $(REGTCP_SOURCES) $(CUSTOM_SOURCES) || echo "clang-format not found"

# Show help
help:
	@echo "Available targets:"
	@echo "  all          - Build all targets (default)"
	@echo "  regtcp       - Build basic TCP/IP stack"
	@echo "  custom       - Build custom MyNet protocol stack"
	@echo "  clean        - Remove build artifacts"
	@echo "  distclean    - Remove all generated files"
	@echo "  run-basic    - Run basic TCP/IP stack demo"
	@echo "  run-custom   - Run custom MyNet protocol demo"
	@echo "  run-all      - Run both demos"
	@echo "  debug        - Build with debug flags"
	@echo "  release      - Build optimized release version"
	@echo "  analyze      - Run static analysis tools"
	@echo "  format       - Format source code"
	@echo "  install      - Install binaries to system"
	@echo "  uninstall    - Remove installed binaries"
	@echo "  help         - Show this help message"

# Dependency tracking (automatically generate dependencies)
depend: $(REGTCP_SOURCES) $(CUSTOM_SOURCES)
	$(CC) -MM $(CFLAGS) $^ > .depend

# Include dependencies if they exist
-include .depend

# Declare phony targets
.PHONY: all clean distclean install uninstall run-basic run-custom run-all debug release analyze format help depend