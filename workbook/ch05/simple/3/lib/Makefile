PYTHON := python3
TEST_FILE := test_fixed.py
LIB_FILE := fixed.py

.PHONY: all test clean

all: test

test:
	$(PYTHON) -m unittest $(TEST_FILE)

clean:
	rm -rf __pycache__ *.pyc *.pyo
