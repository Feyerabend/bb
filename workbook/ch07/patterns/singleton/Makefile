all: singleton

singleton: main.o logger.o
	$(CC) main.o logger.o -o singleton

main.o: main.c logger.h
	$(CC) -c main.c

logger.o: logger.c logger.h
	$(CC) -c logger.c

clean:
	rm -f *.o singleton