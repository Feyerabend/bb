# Default target (runs when you just type "make")
.PHONY: all
all: run

# Clean target to remove __pycache__ folders
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	@echo "All __pycache__ folders have been removed."

# Run target to execute main.py with python3
.PHONY: run
run:
	python3 main.py

# Help target to explain usage
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make          - Run main.py (default)"
	@echo "  make clean    - Remove all __pycache__ folders in the project"
	@echo "  make run      - Run main.py with python3"