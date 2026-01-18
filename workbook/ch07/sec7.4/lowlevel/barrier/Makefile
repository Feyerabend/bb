CC = gcc
CFLAGS = -Wall -Wextra -pedantic -std=c11

all: barrier primes square

barrier: barrier.c
	$(CC) $(CFLAGS) -o $@ $<

primes: primes.c
	$(CC) $(CFLAGS) -o $@ $<

square: square.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f barrier primes square

