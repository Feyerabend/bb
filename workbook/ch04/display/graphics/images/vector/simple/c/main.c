#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#include "pico/stdlib.h"
#include "display.h"

// Framebuffer
static uint16_t framebuffer[DISPLAY_WIDTH * DISPLAY_HEIGHT];

// Vector math
typedef struct { float x, y; } vec2_t;
typedef struct { float m[3][3]; } matrix3_t;

typedef struct {
    vec2_t* vertices;
    int vertex_count;
    uint16_t color;
} shape_t;

// Demo state
static float rotation = 0.0f;
static float scale = 1.0f;
static vec2_t translation = {160.0f, 120.0f};
static int current_shape = 0;
static bool auto_rotate = true;

// Matrix helpers
static matrix3_t matrix_identity(void) { matrix3_t m = {{{1,0,0},{0,1,0},{0,0,1}}}; return m; }
static matrix3_t matrix_translate(float x, float y) { matrix3_t m = matrix_identity(); m.m[0][2]=x; m.m[1][2]=y; return m; }
static matrix3_t matrix_rotate(float a) { matrix3_t m = matrix_identity(); float c=cosf(a), s=sinf(a); m.m[0][0]=c; m.m[0][1]=-s; m.m[1][0]=s; m.m[1][1]=c; return m; }
static matrix3_t matrix_scale(float sx, float sy) { matrix3_t m = matrix_identity(); m.m[0][0]=sx; m.m[1][1]=sy; return m; }

static matrix3_t matrix_multiply(matrix3_t a, matrix3_t b) {
    matrix3_t r = {{{0}}};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            for (int k = 0; k < 3; k++)
                r.m[i][j] += a.m[i][k] * b.m[k][j];
    return r;
}

static vec2_t matrix_transform_point(matrix3_t m, vec2_t p) {
    return (vec2_t){
        m.m[0][0]*p.x + m.m[0][1]*p.y + m.m[0][2],
        m.m[1][0]*p.x + m.m[1][1]*p.y + m.m[1][2]
    };
}

// Bresenham line
static void draw_line(int x0, int y0, int x1, int y1, uint16_t color) {
    int dx = abs(x1-x0), sx = x0 < x1 ? 1 : -1;
    int dy = abs(y1-y0), sy = y0 < y1 ? 1 : -1;
    int err = dx - dy;
    while (1) {
        if (x0 >= 0 && x0 < DISPLAY_WIDTH && y0 >= 0 && y0 < DISPLAY_HEIGHT)
            framebuffer[y0 * DISPLAY_WIDTH + x0] = color;
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 > -dy) { err -= dy; x0 += sx; }
        if (e2 < dx)  { err += dx; y0 += sy; }
    }
}

static void draw_shape(shape_t* s, matrix3_t t) {
    for (int i = 0; i < s->vertex_count; i++) {
        vec2_t p0 = matrix_transform_point(t, s->vertices[i]);
        vec2_t p1 = matrix_transform_point(t, s->vertices[(i+1)%s->vertex_count]);
        draw_line((int)p0.x, (int)p0.y, (int)p1.x, (int)p1.y, s->color);
    }
}

// === TEXT IN FRAMEBUFFER ===
static void draw_string_to_framebuffer(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg) {
    int offset_x = 0;
    while (*str && x + offset_x < DISPLAY_WIDTH) {
        const uint8_t* glyph = display_get_font_char(*str);
        for (int col = 0; col < 5 && x + offset_x + col < DISPLAY_WIDTH; col++) {
            uint8_t line = glyph[4 - col];
            for (int row = 0; row < 8 && y + row < DISPLAY_HEIGHT; row++) {
                uint16_t px = (line & (1 << row)) ? color : bg;
                framebuffer[(y + row) * DISPLAY_WIDTH + (x + offset_x + col)] = px;
            }
        }
        offset_x += 6;
        str++;
    }
}

// Shapes
static vec2_t triangle_verts[] = {{0,-30},{26,15},{-26,15}};
static vec2_t square_verts[] = {{-25,-25},{25,-25},{25,25},{-25,25}};
static vec2_t pentagon_verts[] = {{0,-30},{28,-9},{17,24},{-17,24},{-28,-9}};
static vec2_t hexagon_verts[] = {{0,-30},{26,-15},{26,15},{0,30},{-26,15},{-26,-15}};
static vec2_t star_verts[] = {{0,-30},{7,-10},{28,-10},{11,5},{18,25},{0,15},{-18,25},{-11,5},{-28,-10},{-7,-10}};
static shape_t shapes[] = {
    {triangle_verts, 3, COLOR_CYAN},
    {square_verts, 4, COLOR_YELLOW},
    {pentagon_verts, 5, COLOR_MAGENTA},
    {hexagon_verts, 6, COLOR_GREEN},
    {star_verts, 10, COLOR_RED}
};
static const int shape_count = 5;

// Button callbacks
static void button_a_pressed(button_t b) { (void)b; current_shape = (current_shape + 1) % shape_count; }
static void button_b_pressed(button_t b) { (void)b; auto_rotate = !auto_rotate; }
static void button_x_pressed(button_t b) { (void)b; scale = fminf(scale + 0.2f, 3.0f); }
static void button_y_pressed(button_t b) { (void)b; scale = fmaxf(scale - 0.2f, 0.2f); }

// UI
static void draw_ui(void) {
    char buf[64];
    snprintf(buf, sizeof(buf), "SHAPE: %d/%d", current_shape + 1, shape_count);
    draw_string_to_framebuffer(10, 10, buf, COLOR_WHITE, COLOR_BLACK);
    snprintf(buf, sizeof(buf), "ROT: %.1f", rotation * 180.0f / M_PI);
    draw_string_to_framebuffer(10, 20, buf, COLOR_WHITE, COLOR_BLACK);
    snprintf(buf, sizeof(buf), "SCALE: %.2f", scale);
    draw_string_to_framebuffer(10, 30, buf, COLOR_WHITE, COLOR_BLACK);
    snprintf(buf, sizeof(buf), "AUTO: %s", auto_rotate ? "ON" : "OFF");
    draw_string_to_framebuffer(10, 40, buf, COLOR_WHITE, COLOR_BLACK);
    draw_string_to_framebuffer(10, 220, "A:SHAPE B:AUTO X:+ Y:-", COLOR_YELLOW, COLOR_BLACK);
}

int main() {
    stdio_init_all();
    display_error_t r = display_pack_init();
    if (r != DISPLAY_OK) { printf("Init failed: %s\n", display_error_string(r)); return 1; }
    buttons_init();
    button_set_callback(BUTTON_A, button_a_pressed);
    button_set_callback(BUTTON_B, button_b_pressed);
    button_set_callback(BUTTON_X, button_x_pressed);
    button_set_callback(BUTTON_Y, button_y_pressed);

    while (1) {
        buttons_update();

        // Clear framebuffer
        for (int i = 0; i < DISPLAY_WIDTH * DISPLAY_HEIGHT; i++) framebuffer[i] = COLOR_BLACK;

        // Update rotation
        if (auto_rotate) {
            rotation += 0.02f;
            if (rotation > 2 * M_PI) rotation -= 2 * M_PI;
        }

        // Transform
        matrix3_t m_scale = matrix_scale(scale, scale);
        matrix3_t m_rotate = matrix_rotate(rotation);
        matrix3_t m_translate = matrix_translate(translation.x, translation.y);
        matrix3_t transform = matrix_multiply(m_translate, matrix_multiply(m_rotate, m_scale));

        // Draw shape
        draw_shape(&shapes[current_shape], transform);

        // Draw axes
        matrix3_t axis_t = m_translate;
        vec2_t o = matrix_transform_point(axis_t, (vec2_t){0,0});
        vec2_t x = matrix_transform_point(axis_t, (vec2_t){40,0});
        vec2_t y = matrix_transform_point(axis_t, (vec2_t){0,40});
        draw_line((int)o.x, (int)o.y, (int)x.x, (int)x.y, COLOR_RED);
        draw_line((int)o.x, (int)o.y, (int)y.x, (int)y.y, COLOR_GREEN);

        // Draw UI into framebuffer
        draw_ui();

        // Blit once
        display_blit_full(framebuffer);

        sleep_ms(16);
    }
    return 0;
}
