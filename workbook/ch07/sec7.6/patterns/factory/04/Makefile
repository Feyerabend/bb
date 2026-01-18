CC = gcc
CFLAGS = -Wall -Wextra -O2

all: adder

adder: main.o adder.o
	$(CC) $(CFLAGS) -o adder main.o adder.o

main.o: main.c adder.h
	$(CC) $(CFLAGS) -c main.c

adder.o: adder.c adder.h
	$(CC) $(CFLAGS) -c adder.c

clean:
	rm -f *.o adder