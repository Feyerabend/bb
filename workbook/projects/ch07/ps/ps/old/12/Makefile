
PYTHON = python3
TEST_FILES = $(wildcard test_*.py)

all: test

test: $(TEST_FILES)
	$(PYTHON) -m unittest $(TEST_FILES)

clean:
	rm -f *.pyc
	rm -rf __pycache__

help:
	@echo "Makefile for running Python unit tests"
	@echo "Targets:"
	@echo "  all      - Run all unit tests (default)"
	@echo "  test     - Run unit tests"
	@echo "  clean    - Remove bytecode files"
	@echo "  help     - Show this message"
