CC = gcc
CFLAGS = -Iinclude -Isrc -Wall -Wextra -Werror -pedantic -std=c11 -g
LDFLAGS = -lm

SRC_DIR = src
BUILD_DIR = build
BIN_DIR = bin
LIB_DIR = lib

# source files by component
CORE_SRCS = $(wildcard $(SRC_DIR)/core/*.c)
UI_SRCS = $(wildcard $(SRC_DIR)/ui/*.c)
UTILS_SRCS = $(wildcard $(SRC_DIR)/utils/*.c)
APP_SRC = $(SRC_DIR)/app.c

# object files
CORE_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(CORE_SRCS))
UI_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(UI_SRCS))
UTILS_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(UTILS_SRCS))
APP_OBJ = $(BUILD_DIR)/app.o

# library and executable targets
LIB_TARGET = $(LIB_DIR)/libccalc.a
EXE_TARGET = $(BIN_DIR)/ccalc

# test files
TEST_SRCS = $(wildcard tests/*.c)
TEST_OBJS = $(patsubst tests/%.c,$(BUILD_DIR)/tests/%.o,$(TEST_SRCS))
TEST_BINS = $(patsubst tests/%.c,$(BIN_DIR)/tests/%,$(TEST_SRCS))

# all targets
.PHONY: all clean test dirs

all: dirs $(LIB_TARGET) $(EXE_TARGET) test

# create necessary directories
dirs:
	mkdir -p $(BUILD_DIR)/core $(BUILD_DIR)/ui $(BUILD_DIR)/utils $(BUILD_DIR)/tests $(BIN_DIR)/tests $(LIB_DIR)

# rules for building object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/tests/%.o: tests/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# build the static library
$(LIB_TARGET): $(CORE_OBJS) $(UTILS_OBJS)
	ar rcs $@ $^

# build the executable
$(EXE_TARGET): $(APP_OBJ) $(UI_OBJS) $(LIB_TARGET)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# build and run tests
test: $(TEST_BINS)
	@echo "Running tests..."
	@for test in $(TEST_BINS); do \
		echo "Running $$test..."; \
		$$test; \
	done

$(BIN_DIR)/tests/%: $(BUILD_DIR)/tests/%.o $(LIB_TARGET)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) $(LIB_DIR)
