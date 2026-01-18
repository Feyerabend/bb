# Makefile for Half/Full Adder Factory Pattern Example

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
OBJ = main.o gates.o half_adder.o full_adder.o
TARGET = adder

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)

main.o: main.c gates.h half_adder.h full_adder.h
	$(CC) $(CFLAGS) -c main.c

gates.o: gates.c gates.h logical_gate.h
	$(CC) $(CFLAGS) -c gates.c

half_adder.o: half_adder.c half_adder.h logical_gate.h
	$(CC) $(CFLAGS) -c half_adder.c

full_adder.o: full_adder.c full_adder.h logical_gate.h
	$(CC) $(CFLAGS) -c full_adder.c

clean:
	rm -f $(OBJ) $(TARGET)