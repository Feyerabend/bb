#include <stdio.h>
#include <string.h>

#define BUFFER_SIZE 64

typedef struct {
    char buffer[BUFFER_SIZE];
    int gap_start;
    int gap_end;
} GapBuffer;

void gb_init(GapBuffer* gb) {
    gb->gap_start = 0;
    gb->gap_end = BUFFER_SIZE;
}

void gb_print(GapBuffer* gb) {
    printf("Buffer: \"");
    for (int i = 0; i < gb->gap_start; i++)
        putchar(gb->buffer[i]);
    printf("[");
    for (int i = gb->gap_start; i < gb->gap_end; i++)
        putchar('_');
    printf("]");
    for (int i = gb->gap_end; i < BUFFER_SIZE; i++)
        putchar(gb->buffer[i]);
    printf("\"\n");
}

void gb_insert(GapBuffer* gb, char c) {
    if (gb->gap_start < gb->gap_end) {
        gb->buffer[gb->gap_start++] = c;
    }
}

void gb_delete(GapBuffer* gb) {
    if (gb->gap_start > 0)
        gb->gap_start--;
}

void gb_move_cursor_left(GapBuffer* gb) {
    if (gb->gap_start > 0) {
        gb->gap_end--;
        gb->buffer[gb->gap_end] = gb->buffer[--gb->gap_start];
    }
}

void gb_move_cursor_right(GapBuffer* gb) {
    if (gb->gap_end < BUFFER_SIZE) {
        gb->buffer[gb->gap_start++] = gb->buffer[gb->gap_end];
        gb->gap_end++;
    }
}

int main() {
    GapBuffer gb;
    gb_init(&gb);

    gb_insert(&gb, 'H');
    gb_insert(&gb, 'e');
    gb_insert(&gb, 'l');
    gb_insert(&gb, 'l');
    gb_insert(&gb, 'o');

    gb_print(&gb);

    gb_move_cursor_left(&gb);
    gb_move_cursor_left(&gb);
    gb_insert(&gb, '_');

    gb_print(&gb);

    gb_delete(&gb);
    gb_print(&gb);

    return 0;
}