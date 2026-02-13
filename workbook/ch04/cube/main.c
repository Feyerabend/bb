#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#include "pico/stdlib.h"
#include "pico/time.h"
#include "display.h"

#define CENTER_X 160.0f
#define CENTER_Y 120.0f
#define CUBE_SIZE 60.0f

// Cube vertices in 3D space (local coordinates)
static float vertices[8][3] = {
    {-1, -1, -1}, {1, -1, -1}, {1, 1, -1}, {-1, 1, -1},  // Back face
    {-1, -1,  1}, {1, -1,  1}, {1, 1,  1}, {-1, 1,  1}   // Front face
};

// Cube edges (pairs of vertex indices)
static const int edges[12][2] = {
    {0, 1}, {1, 2}, {2, 3}, {3, 0},  // Back face
    {4, 5}, {5, 6}, {6, 7}, {7, 4},  // Front face
    {0, 4}, {1, 5}, {2, 6}, {3, 7}   // Connecting edges
};

// Rotation angles
static float angle_x = 0.3f;
static float angle_y = 0.5f;
static float angle_z = 0.0f;

// Rotation speeds
static float speed_x = 0.01f;
static float speed_y = 0.015f;
static float speed_z = 0.008f;

// Control state
static bool auto_rotate = true;
static bool wireframe = true;
static float zoom = 1.5f;

// Projected 2D vertices
static float projected[8][2];

/* Xiaolin Wu anti-aliased line (from your clock code) */
static void wu_plot(int x, int y, uint8_t brightness, uint16_t color) {
    if (x < 0 || x >= 320 || y < 0 || y >= 240) return;

    uint8_t r5 = (color >> 11) & 0x1F;
    uint8_t g6 = (color >>  5) & 0x3F;
    uint8_t b5 =  color        & 0x1F;

    uint8_t r = (r5 * brightness) >> 8;
    uint8_t g = (g6 * brightness) >> 8;
    uint8_t b = (b5 * brightness) >> 8;

    uint16_t blended = (r << 11) | (g << 5) | b;
    display_draw_pixel(x, y, blended);
}

static void draw_line(float x0, float y0, float x1, float y1, uint16_t color) {
    bool steep = fabsf(y1 - y0) > fabsf(x1 - x0);

    if (steep) {
        float t; t = x0; x0 = y0; y0 = t; t = x1; x1 = y1; y1 = t;
    }
    if (x0 > x1) {
        float t; t = x0; x0 = x1; x1 = t; t = y0; y0 = y1; y1 = t;
    }

    float dx = x1 - x0;
    float dy = y1 - y0;
    float gradient = (dx == 0.0f) ? 1.0f : dy / dx;

    int   xend = (int)(x0 + 0.5f);
    float yend = y0 + gradient * (xend - x0);
    float xgap = 1.0f - (x0 + 0.5f - (int)(x0 + 0.5f));
    int   xpxl1 = xend;
    int   ypxl1 = (int)yend;

    if (steep) {
        wu_plot(ypxl1,     xpxl1,     (uint8_t)(255 * (1 - (yend - ypxl1)) * xgap), color);
        wu_plot(ypxl1 + 1, xpxl1,     (uint8_t)(255 * (yend - ypxl1) * xgap),       color);
    } else {
        wu_plot(xpxl1,     ypxl1,     (uint8_t)(255 * (1 - (yend - ypxl1)) * xgap), color);
        wu_plot(xpxl1,     ypxl1 + 1, (uint8_t)(255 * (yend - ypxl1) * xgap),       color);
    }
    float intery = yend + gradient;

    xend = (int)(x1 + 0.5f);
    yend = y1 + gradient * (xend - x1);
    xgap = x1 + 0.5f - (int)(x1 + 0.5f);
    int xpxl2 = xend;
    int ypxl2 = (int)yend;

    if (steep) {
        wu_plot(ypxl2,     xpxl2,     (uint8_t)(255 * (1 - (yend - ypxl2)) * xgap), color);
        wu_plot(ypxl2 + 1, xpxl2,     (uint8_t)(255 * (yend - ypxl2) * xgap),       color);
    } else {
        wu_plot(xpxl2,     ypxl2,     (uint8_t)(255 * (1 - (yend - ypxl2)) * xgap), color);
        wu_plot(xpxl2,     ypxl2 + 1, (uint8_t)(255 * (yend - ypxl2) * xgap),       color);
    }

    for (int x = xpxl1 + 1; x < xpxl2; ++x) {
        int y   = (int)intery;
        uint8_t frac = (uint8_t)(255 * (intery - y));

        if (steep) {
            wu_plot(y,     x, 255 - frac, color);
            wu_plot(y + 1, x, frac,       color);
        } else {
            wu_plot(x, y,     255 - frac, color);
            wu_plot(x, y + 1, frac,       color);
        }
        intery += gradient;
    }
}

// 3D rotation matrices
static void rotate_x(float v[3], float angle) {
    float y = v[1];
    float z = v[2];
    v[1] = y * cosf(angle) - z * sinf(angle);
    v[2] = y * sinf(angle) + z * cosf(angle);
}

static void rotate_y(float v[3], float angle) {
    float x = v[0];
    float z = v[2];
    v[0] = x * cosf(angle) + z * sinf(angle);
    v[2] = -x * sinf(angle) + z * cosf(angle);
}

static void rotate_z(float v[3], float angle) {
    float x = v[0];
    float y = v[1];
    v[0] = x * cosf(angle) - y * sinf(angle);
    v[1] = x * sinf(angle) + y * cosf(angle);
}

// Project 3D point to 2D screen
static void project(float v[3], float *x, float *y) {
    float perspective = 4.0f / (4.0f + v[2]);  // Simple perspective
    *x = CENTER_X + v[0] * CUBE_SIZE * zoom * perspective;
    *y = CENTER_Y + v[1] * CUBE_SIZE * zoom * perspective;
}

// Calculate depth for edge sorting
static float edge_depth(int edge_idx) {
    int v1 = edges[edge_idx][0];
    int v2 = edges[edge_idx][1];
    
    // Use average Z of both vertices
    float rotated1[3] = {vertices[v1][0], vertices[v1][1], vertices[v1][2]};
    float rotated2[3] = {vertices[v2][0], vertices[v2][1], vertices[v2][2]};
    
    rotate_x(rotated1, angle_x);
    rotate_y(rotated1, angle_y);
    rotate_z(rotated1, angle_z);
    
    rotate_x(rotated2, angle_x);
    rotate_y(rotated2, angle_y);
    rotate_z(rotated2, angle_z);
    
    return (rotated1[2] + rotated2[2]) / 2.0f;
}

// Render the cube
static void render_cube(void) {
    // Transform and project all vertices
    for (int i = 0; i < 8; i++) {
        float rotated[3] = {vertices[i][0], vertices[i][1], vertices[i][2]};
        
        rotate_x(rotated, angle_x);
        rotate_y(rotated, angle_y);
        rotate_z(rotated, angle_z);
        
        project(rotated, &projected[i][0], &projected[i][1]);
    }
    
    // Sort edges by depth (painter's algorithm - back to front)
    int sorted_edges[12];
    float depths[12];
    
    for (int i = 0; i < 12; i++) {
        sorted_edges[i] = i;
        depths[i] = edge_depth(i);
    }
    
    // Simple bubble sort by depth
    for (int i = 0; i < 11; i++) {
        for (int j = 0; j < 11 - i; j++) {
            if (depths[j] > depths[j + 1]) {
                float temp_d = depths[j];
                depths[j] = depths[j + 1];
                depths[j + 1] = temp_d;
                
                int temp_e = sorted_edges[j];
                sorted_edges[j] = sorted_edges[j + 1];
                sorted_edges[j + 1] = temp_e;
            }
        }
    }
    
    // Draw edges in sorted order with depth-based color
    for (int i = 0; i < 12; i++) {
        int edge_idx = sorted_edges[i];
        int v1 = edges[edge_idx][0];
        int v2 = edges[edge_idx][1];
        
        // Color based on depth (cyan to blue gradient)
        float depth_norm = (depths[i] + 2.0f) / 4.0f;  // Normalize to 0-1
        if (depth_norm < 0.0f) depth_norm = 0.0f;
        if (depth_norm > 1.0f) depth_norm = 1.0f;
        
        uint8_t blue_intensity = (uint8_t)(31 * depth_norm);
        uint8_t green_intensity = (uint8_t)(63 * (1.0f - depth_norm * 0.5f));
        uint16_t color = (blue_intensity) | (green_intensity << 5);
        
        draw_line(projected[v1][0], projected[v1][1],
                  projected[v2][0], projected[v2][1], color);
    }
    
    // Draw vertices as small dots
    for (int i = 0; i < 8; i++) {
        int x = (int)(projected[i][0] + 0.5f);
        int y = (int)(projected[i][1] + 0.5f);
        
        if (x >= 0 && x < 320 && y >= 0 && y < 240) {
            display_draw_pixel(x, y, COLOR_WHITE);
            // Make vertices slightly thicker
            if (x > 0) display_draw_pixel(x-1, y, COLOR_WHITE);
            if (x < 319) display_draw_pixel(x+1, y, COLOR_WHITE);
            if (y > 0) display_draw_pixel(x, y-1, COLOR_WHITE);
            if (y < 239) display_draw_pixel(x, y+1, COLOR_WHITE);
        }
    }
}

/* Button callbacks */
static void btn_a_callback(button_t btn) { 
    (void)btn;
    auto_rotate = !auto_rotate;
}

static void btn_b_callback(button_t btn) { 
    (void)btn;
    // Reset to default view
    angle_x = 0.3f;
    angle_y = 0.5f;
    angle_z = 0.0f;
    zoom = 1.5f;
}

static void btn_x_callback(button_t btn) { 
    (void)btn;
    // Increase rotation speed
    speed_x *= 1.5f;
    speed_y *= 1.5f;
    speed_z *= 1.5f;
    
    // Cap maximum speed
    if (speed_x > 0.1f) speed_x = 0.1f;
    if (speed_y > 0.1f) speed_y = 0.1f;
    if (speed_z > 0.1f) speed_z = 0.1f;
}

static void btn_y_callback(button_t btn) { 
    (void)btn;
    // Zoom in/out
    zoom += 0.3f;
    if (zoom > 3.0f) zoom = 0.8f;  // Cycle back
}

// Draw status information
static void draw_status(void) {
    char buf[50];
    
    snprintf(buf, sizeof(buf), "A:%s X:Speed Y:Zoom B:Reset", 
             auto_rotate ? "PAUSE" : "PLAY ");
    display_draw_string(5, 5, buf, COLOR_GREEN, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "Speed: %.3f  Zoom: %.1fx", 
             speed_y, zoom);
    display_draw_string(5, 225, buf, COLOR_CYAN, COLOR_BLACK);
}

int main(void) {
    stdio_init_all();
    
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed\n");
        return 1;
    }
    
    if (buttons_init() != DISPLAY_OK) {
        printf("Buttons init failed\n");
        return 1;
    }

    // Set up button callbacks
    button_set_callback(BUTTON_A, btn_a_callback);
    button_set_callback(BUTTON_B, btn_b_callback);
    button_set_callback(BUTTON_X, btn_x_callback);
    button_set_callback(BUTTON_Y, btn_y_callback);

    display_clear(COLOR_BLACK);
    display_set_backlight(true);
    
    printf("3D Cube Demo Started\n");
    printf("Controls:\n");
    printf("  A - Toggle rotation\n");
    printf("  B - Reset view\n");
    printf("  X - Increase speed\n");
    printf("  Y - Cycle zoom\n");

    while (1) {
        buttons_update();
        
        // Clear screen
        display_clear(COLOR_BLACK);
        
        // Update rotation angles if auto-rotating
        if (auto_rotate) {
            angle_x += speed_x;
            angle_y += speed_y;
            angle_z += speed_z;
            
            // Wrap angles to prevent overflow
            if (angle_x > 2 * M_PI) angle_x -= 2 * M_PI;
            if (angle_y > 2 * M_PI) angle_y -= 2 * M_PI;
            if (angle_z > 2 * M_PI) angle_z -= 2 * M_PI;
        }
        
        // Render the cube
        render_cube();
        
        // Draw UI
        draw_status();
        
        // Frame rate control (~30 fps)
        sleep_ms(33);
    }

    return 0;
}
