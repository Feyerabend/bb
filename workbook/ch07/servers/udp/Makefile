# Makefile for Enhanced UDP Client/Server

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -pedantic -O2
DEBUG_FLAGS = -g -DDEBUG
TARGET_DIR = bin
TARGETS = $(TARGET_DIR)/udp_server $(TARGET_DIR)/udp_client

# Default target
all: $(TARGET_DIR) $(TARGETS)

# Create target directory
$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

# Build server
$(TARGET_DIR)/udp_server: udp_server.c | $(TARGET_DIR)
	$(CC) $(CFLAGS) -o $@ $<

# Build client
$(TARGET_DIR)/udp_client: udp_client.c | $(TARGET_DIR)
	$(CC) $(CFLAGS) -o $@ $<

# Debug builds
debug: CFLAGS += $(DEBUG_FLAGS)
debug: $(TARGETS)

# Clean build artifacts
clean:
	rm -rf $(TARGET_DIR)

# Install (copy to /usr/local/bin - requires sudo)
install: $(TARGETS)
	sudo cp $(TARGET_DIR)/udp_server /usr/local/bin/
	sudo cp $(TARGET_DIR)/udp_client /usr/local/bin/
	sudo chmod +x /usr/local/bin/udp_server
	sudo chmod +x /usr/local/bin/udp_client

# Uninstall
uninstall:
	sudo rm -f /usr/local/bin/udp_server
	sudo rm -f /usr/local/bin/udp_client

# Test targets
test-server: $(TARGET_DIR)/udp_server
	@echo "Starting test server on port 8888..."
	$(TARGET_DIR)/udp_server

test-client: $(TARGET_DIR)/udp_client
	@echo "Testing client with PING message..."
	$(TARGET_DIR)/udp_client 127.0.0.1 PING

test-interactive: $(TARGET_DIR)/udp_client
	@echo "Starting interactive client..."
	$(TARGET_DIR)/udp_client -i 127.0.0.1

test-stress: $(TARGET_DIR)/udp_client
	@echo "Running stress test with 50 messages..."
	$(TARGET_DIR)/udp_client -s 50 127.0.0.1

# Help target
help:
	@echo "Available targets:"
	@echo "  all           - Build both server and client (default)"
	@echo "  debug         - Build with debug flags"
	@echo "  clean         - Remove build artifacts"
	@echo "  install       - Install binaries to /usr/local/bin (requires sudo)"
	@echo "  uninstall     - Remove installed binaries"
	@echo "  test-server   - Start test server"
	@echo "  test-client   - Test client with PING"
	@echo "  test-interactive - Start interactive client"
	@echo "  test-stress   - Run stress test"
	@echo "  help          - Show this help"

.PHONY: all debug clean install uninstall test-server test-client test-interactive test-stress help
