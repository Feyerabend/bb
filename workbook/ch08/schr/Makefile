CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
TARGET = schr
OBJS = schr.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

schr.o: schr.c
	$(CC) $(CFLAGS) -c schr.c

clean:
	rm -f $(OBJS) $(TARGET)
