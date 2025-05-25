PYTHON = python3
MAIN = main.py
SOURCES = soundex.py database.py adapter.py main.py
CSV_FILE = names.csv

.PHONY: all run clean lint

all: run

run: $(CSV_FILE)
	$(PYTHON) $(MAIN)

clean:
	rm -rf __pycache__ *.pyc

$(CSV_FILE):
	@echo "Error: $(CSV_FILE) not found. Please create the CSV file."
	@exit 1
