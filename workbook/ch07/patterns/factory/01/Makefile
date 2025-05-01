# Makefile for Half-Adder Factory Pattern Example

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
OBJ = main.o half_adder.o gates.o
TARGET = half_adder

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)

main.o: main.c half_adder.h
	$(CC) $(CFLAGS) -c main.c

half_adder.o: half_adder.c half_adder.h logical_gate.h gates.h
	$(CC) $(CFLAGS) -c half_adder.c

gates.o: gates.c gates.h
	$(CC) $(CFLAGS) -c gates.c

clean:
	rm -f $(OBJ) $(TARGET)