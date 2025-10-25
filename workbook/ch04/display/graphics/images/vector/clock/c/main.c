#include "display.h"
#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "pico/time.h"

// Fixed-point (8.8) helpers
#define FIXED_SHIFT      8
#define FIXED_ONE        (1 << FIXED_SHIFT)

static inline int16_t fixed_mul(int16_t a, int16_t b) {
    return (int16_t)((int32_t)a * b >> FIXED_SHIFT);
}

// Path primitives
typedef enum { PATH_MOVE = 0, PATH_LINE, PATH_CLOSE, PATH_END } path_cmd_t;
typedef struct { int16_t x, y; } vec_pt_t;
typedef struct { path_cmd_t cmd; vec_pt_t pt; } path_entry_t;


// Bresenham line drawer (fixed-point → pixel)
static void draw_line_fixed(int16_t x0, int16_t y0,
                            int16_t x1, int16_t y1,
                            uint16_t color) {
    int16_t ix0 = (x0 + (1 << (FIXED_SHIFT-1))) >> FIXED_SHIFT;
    int16_t iy0 = (y0 + (1 << (FIXED_SHIFT-1))) >> FIXED_SHIFT;
    int16_t ix1 = (x1 + (1 << (FIXED_SHIFT-1))) >> FIXED_SHIFT;
    int16_t iy1 = (y1 + (1 << (FIXED_SHIFT-1))) >> FIXED_SHIFT;

    int16_t dx = abs(ix1 - ix0), sx = ix0 < ix1 ? 1 : -1;
    int16_t dy = -abs(iy1 - iy0), sy = iy0 < iy1 ? 1 : -1;
    int16_t err = dx + dy;

    while (1) {
        if (ix0 >= 0 && ix0 < DISPLAY_WIDTH && iy0 >= 0 && iy0 < DISPLAY_HEIGHT)
            display_draw_pixel((uint16_t)ix0, (uint16_t)iy0, color);
        if (ix0 == ix1 && iy0 == iy1) break;
        int16_t e2 = 2 * err;
        if (e2 >= dy) { err += dy; ix0 += sx; }
        if (e2 <= dx) { err += dx; iy0 += sy; }
    }
}


// Path renderer
static void draw_path(const path_entry_t *path, uint16_t color) {
    vec_pt_t cur = {0,0}, start = {0,0};
    bool have_start = false;

    for (const path_entry_t *p = path; p->cmd != PATH_END; ++p) {
        switch (p->cmd) {
            case PATH_MOVE: cur = start = p->pt; have_start = true; break;
            case PATH_LINE:
                if (!have_start) break;
                draw_line_fixed(cur.x, cur.y, p->pt.x, p->pt.y, color);
                cur = p->pt; break;
            case PATH_CLOSE:
                if (!have_start) break;
                draw_line_fixed(cur.x, cur.y, start.x, start.y, color);
                cur = start; break;
            default: break;
        }
    }
}


// Clock geometry helpers
#define CLOCK_CENTER_X   (160 << FIXED_SHIFT)
#define CLOCK_CENTER_Y   (120 << FIXED_SHIFT)
#define CLOCK_RADIUS     (100 << FIXED_SHIFT)   // 100 pixels

static void hand_path(path_entry_t *buf, int16_t length, int16_t angle_deg, uint16_t color) {
    int16_t rad = (int16_t)(angle_deg * 182) >> 8; // 360° → 2π → 182*256
    int16_t cosA = (int16_t)(cosf(rad * 3.14159265f / 180.0f) * FIXED_ONE);
    int16_t sinA = (int16_t)(sinf(rad * 3.14159265f / 180.0f) * FIXED_ONE);

    int16_t tip_x = CLOCK_CENTER_X + fixed_mul(length, cosA);
    int16_t tip_y = CLOCK_CENTER_Y - fixed_mul(length, sinA); // Y down

    buf[0] = (path_entry_t){PATH_MOVE, {CLOCK_CENTER_X, CLOCK_CENTER_Y}};
    buf[1] = (path_entry_t){PATH_LINE, {tip_x, tip_y}};
    buf[2] = (path_entry_t){PATH_END, {0,0}};
}

//  Tick marks (12 hour marks)
static void draw_clock_face(void) {
    path_entry_t path[64];
    int idx = 0;

    for (int i = 0; i < 12; ++i) {
        float a = i * 30.0f; // 360/12
        int16_t rad = (int16_t)(a * 182) >> 8;
        int16_t c = (int16_t)(cosf(rad * 3.14159265f / 180.0f) * FIXED_ONE);
        int16_t s = (int16_t)(sinf(rad * 3.14159265f / 180.0f) * FIXED_ONE);

        int16_t inner = CLOCK_RADIUS - (15 << FIXED_SHIFT);
        int16_t outer = CLOCK_RADIUS;

        int16_t x1 = CLOCK_CENTER_X + fixed_mul(inner, c);
        int16_t y1 = CLOCK_CENTER_Y - fixed_mul(inner, s);
        int16_t x2 = CLOCK_CENTER_X + fixed_mul(outer, c);
        int16_t y2 = CLOCK_CENTER_Y - fixed_mul(outer, s);

        path[idx++] = (path_entry_t){PATH_MOVE, {x1, y1}};
        path[idx++] = (path_entry_t){PATH_LINE, {x2, y2}};
    }
    path[idx++] = (path_entry_t){PATH_END, {0,0}};
    draw_path(path, COLOR_WHITE);
}


// Stopwatch state
static bool stopwatch_running = false;
static absolute_time_t stopwatch_start;
static int64_t stopwatch_elapsed_ms = 0;

// Button callbacks
static void btn_a_callback(button_t btn) {
    (void)btn;
    if (stopwatch_running) {
        stopwatch_running = false;
        stopwatch_elapsed_ms = absolute_time_diff_us(stopwatch_start, get_absolute_time()) / 1000;
    } else {
        stopwatch_running = true;
        stopwatch_start = get_absolute_time();
    }
}

static void btn_b_callback(button_t btn) {
    (void)btn;
    stopwatch_running = false;
    stopwatch_elapsed_ms = 0;
}


int main(void) {
    stdio_init_all();

    if (display_pack_init() != DISPLAY_OK) { printf("display init failed\n"); return 1; }
    if (buttons_init()      != DISPLAY_OK) { printf("buttons init failed\n"); return 1; }

    button_set_callback(BUTTON_A, btn_a_callback);
    button_set_callback(BUTTON_B, btn_b_callback);

    display_clear(COLOR_BLACK);
    display_set_backlight(true);

    /* Draw static face once */
    draw_clock_face();

    path_entry_t hand_buf[3];

    while (1) {
        buttons_update();

        // Get current time (or stopwatch time)
        int h, m, s, ms;
        if (stopwatch_running) {
            int64_t elapsed = absolute_time_diff_us(stopwatch_start, get_absolute_time()) / 1000;
            s  = (elapsed / 1000) % 60;
            m  = (elapsed / 60000) % 60;
            h  = (elapsed / 3600000) % 12;
            ms = elapsed % 1000;
        } else {
            datetime_t t;
            rtc_get_datetime(&t);
            h  = t.hour % 12;
            m  = t.min;
            s  = t.sec;
            ms = 0;
        }

        // Redraw hands (clear old ones by drawing over in black)
        display_clear(COLOR_BLACK);
        draw_clock_face();

        /* Second hand – thin red */
        hand_path(hand_buf, (90 << FIXED_SHIFT), (s * 6) + (ms * 6 / 1000), COLOR_RED);
        draw_path(hand_buf, COLOR_RED);

        /* Minute hand – medium white */
        hand_path(hand_buf, (80 << FIXED_SHIFT), m * 6 + s * 0.1f, COLOR_WHITE);
        draw_path(hand_buf, COLOR_WHITE);

        /* Hour hand – short thick cyan */
        hand_path(hand_buf, (60 << FIXED_SHIFT), h * 30 + m * 0.5f, COLOR_CYAN);
        draw_path(hand_buf, COLOR_CYAN);

        /* Center dot */
        display_draw_pixel(160, 120, COLOR_WHITE);

        // Mode indicator
        const char *mode = stopwatch_running ? "STOPWATCH (A=stop)" : "CLOCK (A=start)";
        display_draw_string(10, 220, mode, COLOR_GREEN, COLOR_BLACK);

        sleep_ms(100);
    }

    display_cleanup();
    return 0;
}
