.PHONY: all clean

CC = gcc
SRC = array.c

all: array array_opt

array: $(SRC)
	$(CC) -O0 -o array $(SRC)

array_opt: $(SRC)
	$(CC) -O3 -o array_opt $(SRC)

clean:
	rm -f array array_opt