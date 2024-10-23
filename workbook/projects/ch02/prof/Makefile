CC		= gcc
CFLAGS		= -Wall
LDFLAGS		=
OBJFILES	= vm4.o profiler.o
TARGET		= vm4

all: $(TARGET)

$(TARGET): $(OBJFILES)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJFILES) $(LDFLAGS)

clean:
	rm -f $(OBJFILES) $(TARGET) *~
