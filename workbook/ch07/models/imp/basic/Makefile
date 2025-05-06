# Makefile
# Makefile for testing the BASIC interpreter with sample programs
# NOTE: Commands under targets must be indented with TABS, not spaces.

PYTHON = python3
INTERPRETER = basic_interpreter.py
SAMPLE_DIR = samples
SAMPLES = $(SAMPLE_DIR)/arithmetic.bas $(SAMPLE_DIR)/loops.bas $(SAMPLE_DIR)/conditionals.bas $(SAMPLE_DIR)/strings.bas $(SAMPLE_DIR)/functions.bas

.PHONY: all test clean check_interpreter

all: test

check_interpreter:
	@if [ ! -f $(INTERPRETER) ]; then \
		echo "Error: $(INTERPRETER) not found in current directory"; \
		exit 1; \
	fi

test: check_interpreter $(SAMPLES)
	@echo "Running all tests..."
	@for sample in $(SAMPLES); do \
		echo "\nTesting $$sample:"; \
		$(PYTHON) $(INTERPRETER) $$sample; \
	done

$(SAMPLE_DIR)/arithmetic.bas:
	@mkdir -p $(SAMPLE_DIR)
	@echo "Creating $@"
	@echo "10 REM Test arithmetic operations" > $@
	@echo "20 LET A = 10" >> $@
	@echo "30 LET B = 5" >> $@
	@echo "40 PRINT \"Sum: \"; A + B" >> $@
	@echo "50 PRINT \"Difference: \"; A - B" >> $@
	@echo "60 PRINT \"Product: \"; A * B" >> $@
	@echo "70 PRINT \"Quotient: \"; A / B" >> $@
	@echo "80 END" >> $@

$(SAMPLE_DIR)/loops.bas:
	@mkdir -p $(SAMPLE_DIR)
	@echo "Creating $@"
	@echo "10 REM Test loops" > $@
	@echo "20 FOR I = 1 TO 5" >> $@
	@echo "30 PRINT \"FOR Loop iteration: \"; I" >> $@
	@echo "40 NEXT I" >> $@
	@echo "50 LET X = 1" >> $@
	@echo "60 WHILE X <= 3" >> $@
	@echo "70 PRINT \"WHILE Loop iteration: \"; X" >> $@
	@echo "80 LET X = X + 1" >> $@
	@echo "90 WEND" >> $@
	@echo "100 END" >> $@

$(SAMPLE_DIR)/conditionals.bas:
	@mkdir -p $(SAMPLE_DIR)
	@echo "Creating $@"
	@echo "10 REM Test conditionals" > $@
	@echo "20 LET A = 10" >> $@
	@echo "30 IF A > 5 THEN PRINT \"A is greater than 5\" ELSE PRINT \"A is 5 or less\"" >> $@
	@echo "40 LET B = 3" >> $@
	@echo "50 IF B = 3 THEN 70" >> $@
	@echo "60 PRINT \"B is not 3\"" >> $@
	@echo "70 PRINT \"B is 3\"" >> $@
	@echo "80 END" >> $@

$(SAMPLE_DIR)/strings.bas:
	@mkdir -p $(SAMPLE_DIR)
	@echo "Creating $@"
	@echo "10 REM Test string operations" > $@
	@echo "20 LET S\$ = \"Hello, World!\"" >> $@
	@echo "30 PRINT \"Original: \"; S\$" >> $@
	@echo "40 PRINT \"Left 5: \"; LEFT(S\$, 5)" >> $@
	@echo "50 PRINT \"Right 6: \"; RIGHT(S\$, 6)" >> $@
	@echo "60 PRINT \"Mid 7,5: \"; MID(S\$, 7, 5)" >> $@
	@echo "70 PRINT \"Length: \"; LEN(S\$)" >> $@
	@echo "80 END" >> $@

$(SAMPLE_DIR)/functions.bas:
	@mkdir -p $(SAMPLE_DIR)
	@echo "Creating $@"
	@echo "10 REM Test mathematical functions" > $@
	@echo "20 LET X = 3.14159 / 2" >> $@
	@echo "30 PRINT \"Sine: \"; SIN(X)" >> $@
	@echo "40 PRINT \"Cosine: \"; COS(X)" >> $@
	@echo "50 PRINT \"Absolute: \"; ABS(-5)" >> $@
	@echo "60 PRINT \"Square root: \"; SQR(16)" >> $@
	@echo "70 PRINT \"Random: \"; RND" >> $@
	@echo "80 END" >> $@

clean:
	@echo "Cleaning up..."
	@rm -rf $(SAMPLE_DIR)