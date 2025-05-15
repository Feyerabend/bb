# Makefile for Lisp interpreter project

# Variables
PYTHON = python3
LINT = flake8
FORMAT = black
TEST_FILE = test_lisp.py
SRC_FILES = lisp.py test_lisp.py

# Default target
all: test lint format

# Run tests
test:
	$(PYTHON) -m unittest $(TEST_FILE) -v

# Lint code
lint:
	$(LINT) $(SRC_FILES)

# Format code
format:
	$(FORMAT) --check $(SRC_FILES)

# Clean up
clean:
	rm -rf __pycache__ *.pyc

# Install dependencies
install:
	pip install flake8 black

.PHONY: all test lint format clean install
