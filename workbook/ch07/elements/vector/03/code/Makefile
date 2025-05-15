# Makefile for Lisp interpreter operations

.PHONY: run test clean help

run:
	@python3 lisp.py

test:
	@echo "Running unit tests .."
	@python3 -m unittest test_lisp.py -v

clean:
	@echo "Cleaning up .."
	@rm -rf __pycache__
	@rm -f *.pyc

help:
	@echo "Available targets:"
	@echo "  run    - Start the Lisp REPL"
	@echo "  test   - Run unit tests with verbose output"
	@echo "  clean  - Remove Python cache files"
	@echo "  help   - Show this help message"
