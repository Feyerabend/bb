#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "display.h"

// Vector graphics structures
typedef struct {
    float x, y;
} vec2_t;

typedef struct {
    float m[3][3];  // 3x3 transformation matrix for 2D homogeneous coordinates
} matrix3_t;

typedef struct {
    vec2_t* vertices;
    int vertex_count;
    uint16_t color;
} shape_t;

// Framebuffer for double buffering
static uint16_t framebuffer[DISPLAY_WIDTH * DISPLAY_HEIGHT];

// Demo state
static float rotation = 0.0f;
static float scale = 1.0f;
static vec2_t translation = {160.0f, 120.0f};
static int current_shape = 0;
static bool auto_rotate = true;

// Matrix operations
static matrix3_t matrix_identity(void) {
    matrix3_t m = {{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}};
    return m;
}

static matrix3_t matrix_translate(float x, float y) {
    matrix3_t m = matrix_identity();
    m.m[0][2] = x;
    m.m[1][2] = y;
    return m;
}

static matrix3_t matrix_rotate(float angle) {
    matrix3_t m = matrix_identity();
    float c = cosf(angle);
    float s = sinf(angle);
    m.m[0][0] = c;
    m.m[0][1] = -s;
    m.m[1][0] = s;
    m.m[1][1] = c;
    return m;
}

static matrix3_t matrix_scale(float sx, float sy) {
    matrix3_t m = matrix_identity();
    m.m[0][0] = sx;
    m.m[1][1] = sy;
    return m;
}

// CRITICAL: Matrix multiplication order matters!
// To transform a point: First scale, then rotate, then translate
// This means: M_final = M_translate * M_rotate * M_scale
static matrix3_t matrix_multiply(matrix3_t a, matrix3_t b) {
    matrix3_t result = {{{0}}};
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            for (int k = 0; k < 3; k++) {
                result.m[i][j] += a.m[i][k] * b.m[k][j];
            }
        }
    }
    return result;
}

static vec2_t matrix_transform_point(matrix3_t m, vec2_t p) {
    vec2_t result;
    result.x = m.m[0][0] * p.x + m.m[0][1] * p.y + m.m[0][2];
    result.y = m.m[1][0] * p.x + m.m[1][1] * p.y + m.m[1][2];
    return result;
}

// Drawing primitives
static void draw_line(int x0, int y0, int x1, int y1, uint16_t color) {
    // Bresenham's line algorithm
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = x0 < x1 ? 1 : -1;
    int sy = y0 < y1 ? 1 : -1;
    int err = dx - dy;
    
    while (1) {
        if (x0 >= 0 && x0 < DISPLAY_WIDTH && y0 >= 0 && y0 < DISPLAY_HEIGHT) {
            framebuffer[y0 * DISPLAY_WIDTH + x0] = color;
        }
        
        if (x0 == x1 && y0 == y1) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

static void draw_shape(shape_t* shape, matrix3_t transform) {
    if (shape->vertex_count < 2) return;
    
    // Transform and draw each edge
    for (int i = 0; i < shape->vertex_count; i++) {
        vec2_t p0 = matrix_transform_point(transform, shape->vertices[i]);
        vec2_t p1 = matrix_transform_point(transform, shape->vertices[(i + 1) % shape->vertex_count]);
        
        draw_line((int)p0.x, (int)p0.y, (int)p1.x, (int)p1.y, shape->color);
    }
}

// Shape definitions
static vec2_t triangle_verts[] = {
    {0, -30}, {26, 15}, {-26, 15}
};

static vec2_t square_verts[] = {
    {-25, -25}, {25, -25}, {25, 25}, {-25, 25}
};

static vec2_t pentagon_verts[] = {
    {0, -30}, {28, -9}, {17, 24}, {-17, 24}, {-28, -9}
};

static vec2_t hexagon_verts[] = {
    {0, -30}, {26, -15}, {26, 15}, {0, 30}, {-26, 15}, {-26, -15}
};

static vec2_t star_verts[] = {
    {0, -30}, {7, -10}, {28, -10}, {11, 5}, {18, 25},
    {0, 15}, {-18, 25}, {-11, 5}, {-28, -10}, {-7, -10}
};

static shape_t shapes[] = {
    {triangle_verts, 3, COLOR_CYAN},
    {square_verts, 4, COLOR_YELLOW},
    {pentagon_verts, 5, COLOR_MAGENTA},
    {hexagon_verts, 6, COLOR_GREEN},
    {star_verts, 10, COLOR_RED}
};
static const int shape_count = 5;

// Button callbacks
static void button_a_pressed(button_t button) {
    (void)button;
    current_shape = (current_shape + 1) % shape_count;
}

static void button_b_pressed(button_t button) {
    (void)button;
    auto_rotate = !auto_rotate;
}

static void button_x_pressed(button_t button) {
    (void)button;
    scale += 0.2f;
    if (scale > 3.0f) scale = 3.0f;
}

static void button_y_pressed(button_t button) {
    (void)button;
    scale -= 0.2f;
    if (scale < 0.2f) scale = 0.2f;
}

// UI rendering
static void draw_ui(void) {
    char buf[64];
    
    snprintf(buf, sizeof(buf), "SHAPE: %d/%d", current_shape + 1, shape_count);
    display_draw_string(10, 10, buf, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "ROT: %.1f", rotation * 180.0f / M_PI);
    display_draw_string(10, 20, buf, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "SCALE: %.2f", scale);
    display_draw_string(10, 30, buf, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "AUTO: %s", auto_rotate ? "ON" : "OFF");
    display_draw_string(10, 40, buf, COLOR_WHITE, COLOR_BLACK);
    
    // Instructions
    display_draw_string(10, 220, "A:SHAPE B:AUTO X:+ Y:-", COLOR_YELLOW, COLOR_BLACK);
}

int main() {
    stdio_init_all();
    
    // Init display and buttons
    display_error_t result = display_pack_init();
    if (result != DISPLAY_OK) {
        printf("Display init failed: %s\n", display_error_string(result));
        return 1;
    }
    
    result = buttons_init();
    if (result != DISPLAY_OK) {
        printf("Buttons init failed: %s\n", display_error_string(result));
        return 1;
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, button_a_pressed);
    button_set_callback(BUTTON_B, button_b_pressed);
    button_set_callback(BUTTON_X, button_x_pressed);
    button_set_callback(BUTTON_Y, button_y_pressed);
    
    display_clear(COLOR_BLACK);
    printf("Vector Graphics Demo Started\n");
    
    // Main loop
    while (1) {
        buttons_update();
        
        // Clear framebuffer
        for (int i = 0; i < DISPLAY_WIDTH * DISPLAY_HEIGHT; i++) {
            framebuffer[i] = COLOR_BLACK;
        }
        
        // Update rotation
        if (auto_rotate) {
            rotation += 0.02f;
            if (rotation > 2 * M_PI) rotation -= 2 * M_PI;
        }
        
        // IMPORTANT: Transformation composition order!
        // We want to: scale the shape, rotate it, then move it to position
        // Matrix multiplication is right-to-left, so: T * R * S
        matrix3_t m_scale = matrix_scale(scale, scale);
        matrix3_t m_rotate = matrix_rotate(rotation);
        matrix3_t m_translate = matrix_translate(translation.x, translation.y);
        
        // Compose transformations: first apply scale, then rotation, then translation
        matrix3_t transform = matrix_multiply(m_translate, 
                             matrix_multiply(m_rotate, m_scale));
        
        // Draw the current shape with composed transformation
        draw_shape(&shapes[current_shape], transform);
        
        // Draw coordinate axes at origin (after translation only)
        matrix3_t axis_transform = m_translate;
        vec2_t x_axis_end = {40, 0};
        vec2_t y_axis_end = {0, 40};
        vec2_t origin = {0, 0};
        
        vec2_t o = matrix_transform_point(axis_transform, origin);
        vec2_t x = matrix_transform_point(axis_transform, x_axis_end);
        vec2_t y = matrix_transform_point(axis_transform, y_axis_end);
        
        draw_line((int)o.x, (int)o.y, (int)x.x, (int)x.y, COLOR_RED);
        draw_line((int)o.x, (int)o.y, (int)y.x, (int)y.y, COLOR_GREEN);
        
        // Blit framebuffer to display
        display_blit_full(framebuffer);
        
        // Draw UI on top
        draw_ui();
        
        sleep_ms(16); // ~60 FPS
    }
    
    return 0;
}

