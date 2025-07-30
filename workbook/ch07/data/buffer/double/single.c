#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <termios.h>

#define WIDTH  40
#define HEIGHT 20
#define DELAY  50000  // microseconds

// ANSI escape codes
#define CLEAR_SCREEN  "\x1b[2J"
#define HIDE_CURSOR   "\x1b[?25l"
#define SHOW_CURSOR   "\x1b[?25h"
#define MOVE_CURSOR_TOP_LEFT "\x1b[H"

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

void draw_frame(int x, int y) {
    printf(CLEAR_SCREEN);
    printf(MOVE_CURSOR_TOP_LEFT);

    for (int row = 0; row < HEIGHT; ++row) {
        for (int col = 0; col < WIDTH; ++col) {
            if (row == y && col == x)
                putchar('O');
            else
                putchar(' ');
        }
        putchar('\n');
    }

    fflush(stdout);
}

int main() {
    int x = 2, y = 2;
    int dx = 1, dy = 1;

    printf(HIDE_CURSOR);
    enable_raw_mode();

    for (int frame = 0; frame < 500; ++frame) {
        draw_frame(x, y);

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