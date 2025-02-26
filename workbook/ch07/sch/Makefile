CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
TARGET = sch
OBJS = sch.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

sch.o: sch.c
	$(CC) $(CFLAGS) -c sch.c

clean:
	rm -f $(OBJS) $(TARGET)
