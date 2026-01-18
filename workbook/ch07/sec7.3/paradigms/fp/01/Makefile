# Makefile for Lisp interpreter project

PYTHON = python3

LISP_SRC = lisp.py
TEST_SRC = test_lisp.py

all: test

test:
	@echo "Running unit tests .."
	@$(PYTHON) -m unittest $(TEST_SRC) -v

repl:
	@echo "Starting Lisp REPL .."
	@$(PYTHON) $(LISP_SRC)

clean:
	@echo "Cleaning up..."
	@rm -f *.pyc __pycache__/* 2>/dev/null || true
	@rmdir __pycache__ 2>/dev/null || true

.PHONY: all test repl clean
