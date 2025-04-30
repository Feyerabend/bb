# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2

OBJS = main.o adder.o gate.o

all: adder

adder: $(OBJS)
	$(CC) $(CFLAGS) -o adder $(OBJS)

main.o: main.c adder.h gate.h
adder.o: adder.c adder.h gate.h
gate.o: gate.c gate.h

clean:
	rm -f adder $(OBJS)