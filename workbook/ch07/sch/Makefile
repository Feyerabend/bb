CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
TARGET = test_scheme
OBJS = scheme.o test_scheme.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

scheme.o: scheme.c scheme.h
	$(CC) $(CFLAGS) -c scheme.c

test_scheme.o: test_scheme.c scheme.h
	$(CC) $(CFLAGS) -c test_scheme.c

clean:
	rm -f $(OBJS) $(TARGET)