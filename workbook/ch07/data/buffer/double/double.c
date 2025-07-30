#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>   // For usleep()
#include <termios.h>
#include <fcntl.h>

#define WIDTH  40
#define HEIGHT 20
#define DELAY  50000  // microseconds

char buffer1[HEIGHT][WIDTH + 1];
char buffer2[HEIGHT][WIDTH + 1];
char (*draw_buffer)[WIDTH + 1] = buffer1;
char (*disp_buffer)[WIDTH + 1] = buffer2;

// Simple ANSI control codes
#define CLEAR_SCREEN  "\x1b[2J"
#define HIDE_CURSOR   "\x1b[?25l"
#define SHOW_CURSOR   "\x1b[?25h"
#define MOVE_CURSOR_TOP_LEFT "\x1b[H"

void clear_buffer(char buf[HEIGHT][WIDTH + 1]) {
    for (int i = 0; i < HEIGHT; ++i) {
        memset(buf[i], ' ', WIDTH);
        buf[i][WIDTH] = '\0';
    }
}

void draw_ball(int x, int y) {
    if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT) {
        draw_buffer[y][x] = 'O';
    }
}

void swap_buffers() {
    char (*temp)[WIDTH + 1] = draw_buffer;
    draw_buffer = disp_buffer;
    disp_buffer = temp;
}

void flush_to_terminal() {
    printf(MOVE_CURSOR_TOP_LEFT);
    for (int i = 0; i < HEIGHT; ++i) {
        printf("%s\n", disp_buffer[i]);
    }
    fflush(stdout);
}

void enable_raw_mode() {
    struct termios t;
    tcgetattr(0, &t);
    t.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(0, TCSANOW, &t);
}

void restore_terminal() {
    struct termios t;
    tcgetattr(0, &t);
    t.c_lflag |= ICANON | ECHO;
    tcsetattr(0, TCSANOW, &t);
}

int main() {
    int x = 2, y = 2;
    int dx = 1, dy = 1;

    printf(CLEAR_SCREEN HIDE_CURSOR);
    enable_raw_mode();

    for (int frame = 0; frame < 500; ++frame) {
        clear_buffer(draw_buffer);
        draw_ball(x, y);

        swap_buffers();
        flush_to_terminal();

        x += dx;
        y += dy;

        if (x <= 0 || x >= WIDTH - 1) dx = -dx;
        if (y <= 0 || y >= HEIGHT - 1) dy = -dy;

        usleep(DELAY);
    }

    restore_terminal();
    printf(SHOW_CURSOR);
    printf("\n");
    return 0;
}
