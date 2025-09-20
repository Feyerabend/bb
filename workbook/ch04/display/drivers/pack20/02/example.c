#include <stdio.h>
#include "pico/stdlib.h"
#include "display.h"

// Game constants
#define PADDLE_WIDTH 50
#define PADDLE_HEIGHT 8
#define PADDLE_SPEED 6
#define BALL_SIZE 4
#define BALL_SPEED 3
#define BRICK_ROWS 8
#define BRICK_COLS 20
#define BRICK_WIDTH (DISPLAY_WIDTH / BRICK_COLS)
#define BRICK_HEIGHT 8
#define BRICK_START_Y 20
#define INITIAL_LIVES 3

// Brick structure
typedef struct {
    bool active;
    uint16_t color;
    int score;
} brick_t;

// Game state
static int paddle_x = (DISPLAY_WIDTH - PADDLE_WIDTH) / 2;
static int ball_x = DISPLAY_WIDTH / 2;
static int ball_y = DISPLAY_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 10;
static int ball_vx = BALL_SPEED;
static int ball_vy = -BALL_SPEED;
static bool ball_launched = false;
static brick_t bricks[BRICK_ROWS][BRICK_COLS];
static int score = 0;
static int lives = INITIAL_LIVES;
static bool game_over = false;

// Brick colors and scores (inspired by original Breakout)
static const uint16_t row_colors[BRICK_ROWS] = {
    COLOR_YELLOW, COLOR_YELLOW,
    COLOR_GREEN, COLOR_GREEN,
    COLOR_MAGENTA, COLOR_MAGENTA,
    COLOR_RED, COLOR_RED
};
static const int row_scores[BRICK_ROWS] = {
    1, 1, 2, 2, 3, 3, 4, 4
};

// Function to init bricks
static void init_bricks(void) {
    for (int row = 0; row < BRICK_ROWS; row++) {
        for (int col = 0; col < BRICK_COLS; col++) {
            bricks[row][col].active = true;
            bricks[row][col].color = row_colors[row];
            bricks[row][col].score = row_scores[row];
        }
    }
}

// Function to draw all game elements
static void draw_game(void) {
    display_error_t result;

    // Clear screen
    if ((result = display_clear(COLOR_BLACK)) != DISPLAY_OK) {
        printf("Error clearing display: %s\n", display_error_string(result));
        return;
    }

    // Draw bricks
    for (int row = 0; row < BRICK_ROWS; row++) {
        for (int col = 0; col < BRICK_COLS; col++) {
            if (bricks[row][col].active) {
                uint16_t brick_x = col * BRICK_WIDTH;
                uint16_t brick_y = BRICK_START_Y + row * BRICK_HEIGHT;
                if ((result = display_fill_rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT, bricks[row][col].color)) != DISPLAY_OK) {
                    printf("Error drawing brick: %s\n", display_error_string(result));
                }
            }
        }
    }

    // Draw paddle
    if ((result = display_fill_rect(paddle_x, DISPLAY_HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, COLOR_WHITE)) != DISPLAY_OK) {
        printf("Error drawing paddle: %s\n", display_error_string(result));
    }

    // Draw ball
    if ((result = display_fill_rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE, COLOR_WHITE)) != DISPLAY_OK) {
        printf("Error drawing ball: %s\n", display_error_string(result));
    }

    // Draw score
    char score_str[32];
    sprintf(score_str, "SCORE: %d", score);
    if ((result = display_draw_string(10, 5, score_str, COLOR_WHITE, COLOR_BLACK)) != DISPLAY_OK) {
        printf("Error drawing score: %s\n", display_error_string(result));
    }

    // Draw lives
    char lives_str[32];
    sprintf(lives_str, "LIVES: %d", lives);
    if ((result = display_draw_string(DISPLAY_WIDTH - 100, 5, lives_str, COLOR_WHITE, COLOR_BLACK)) != DISPLAY_OK) {
        printf("Error drawing lives: %s\n", display_error_string(result));
    }

    // If game over, draw message
    if (game_over) {
        if ((result = display_draw_string(80, 100, "GAME OVER", COLOR_RED, COLOR_BLACK)) != DISPLAY_OK) {
            printf("Error drawing game over: %s\n", display_error_string(result));
        }
        if ((result = display_draw_string(50, 120, "PRESS X TO RESTART", COLOR_WHITE, COLOR_BLACK)) != DISPLAY_OK) {
            printf("Error drawing restart: %s\n", display_error_string(result));
        }
    } else if (!ball_launched) {
        if ((result = display_draw_string(50, 100, "PRESS X TO LAUNCH", COLOR_WHITE, COLOR_BLACK)) != DISPLAY_OK) {
            printf("Error drawing launch: %s\n", display_error_string(result));
        }
    }
}

// Function to update game logic
static void update_game(void) {
    if (game_over) {
        // Check for restart
        if (button_just_pressed(BUTTON_X)) {
            init_bricks();
            score = 0;
            lives = INITIAL_LIVES;
            paddle_x = (DISPLAY_WIDTH - PADDLE_WIDTH) / 2;
            ball_x = paddle_x + PADDLE_WIDTH / 2 - BALL_SIZE / 2;
            ball_y = DISPLAY_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 1;
            ball_vx = BALL_SPEED;
            ball_vy = -BALL_SPEED;
            ball_launched = false;
            game_over = false;
        }
        return;
    }

    // Paddle movement (use A for left, B for right)
    if (button_pressed(BUTTON_A) && paddle_x > 0) {
        paddle_x -= PADDLE_SPEED;
        if (paddle_x < 0) paddle_x = 0;
    }
    if (button_pressed(BUTTON_B) && paddle_x + PADDLE_WIDTH < DISPLAY_WIDTH) {
        paddle_x += PADDLE_SPEED;
        if (paddle_x + PADDLE_WIDTH > DISPLAY_WIDTH) paddle_x = DISPLAY_WIDTH - PADDLE_WIDTH;
    }

    // Launch ball with X
    if (!ball_launched) {
        ball_x = paddle_x + PADDLE_WIDTH / 2 - BALL_SIZE / 2;
        if (button_just_pressed(BUTTON_X)) {
            ball_launched = true;
        }
        return;
    }

    // Update ball position
    ball_x += ball_vx;
    ball_y += ball_vy;

    // Wall collisions
    if (ball_x <= 0 || ball_x + BALL_SIZE >= DISPLAY_WIDTH) {
        ball_vx = -ball_vx;
        ball_x = (ball_x <= 0) ? 0 : DISPLAY_WIDTH - BALL_SIZE;
    }
    if (ball_y <= 0) {
        ball_vy = -ball_vy;
        ball_y = 0;
    }

    // Bottom collision (lose life)
    if (ball_y + BALL_SIZE >= DISPLAY_HEIGHT) {
        lives--;
        if (lives <= 0) {
            game_over = true;
        } else {
            // Reset ball
            ball_x = paddle_x + PADDLE_WIDTH / 2 - BALL_SIZE / 2;
            ball_y = DISPLAY_HEIGHT - PADDLE_HEIGHT - BALL_SIZE - 1;
            ball_vx = BALL_SPEED;
            ball_vy = -BALL_SPEED;
            ball_launched = false;
        }
        return;
    }

    // Paddle collision
    if (ball_y + BALL_SIZE >= DISPLAY_HEIGHT - PADDLE_HEIGHT &&
        ball_y <= DISPLAY_HEIGHT &&
        ball_x + BALL_SIZE >= paddle_x &&
        ball_x <= paddle_x + PADDLE_WIDTH) {
        ball_vy = -ball_vy;
        // Adjust angle based on hit position
        int hit_pos = (ball_x + BALL_SIZE / 2) - paddle_x;
        ball_vx = (hit_pos - PADDLE_WIDTH / 2) / (PADDLE_WIDTH / (2 * BALL_SPEED));
        if (ball_vx == 0) ball_vx = (ball_vx > 0) ? 1 : -1; // Prevent straight down
        ball_y = DISPLAY_HEIGHT - PADDLE_HEIGHT - BALL_SIZE;
    }

    // Brick collisions
    for (int row = 0; row < BRICK_ROWS; row++) {
        for (int col = 0; col < BRICK_COLS; col++) {
            if (bricks[row][col].active) {
                uint16_t brick_x = col * BRICK_WIDTH;
                uint16_t brick_y = BRICK_START_Y + row * BRICK_HEIGHT;
                if (ball_x + BALL_SIZE >= brick_x &&
                    ball_x <= brick_x + BRICK_WIDTH &&
                    ball_y + BALL_SIZE >= brick_y &&
                    ball_y <= brick_y + BRICK_HEIGHT) {
                    bricks[row][col].active = false;
                    score += bricks[row][col].score;
                    ball_vy = -ball_vy;
                    // Only break one brick per update
                    return;
                }
            }
        }
    }
}

// Backlight toggle callback (using Y button)
static void on_button_y(button_t button) {
    static bool backlight_on = true;
    backlight_on = !backlight_on;
    display_error_t result = display_set_backlight(backlight_on);
    if (result != DISPLAY_OK) {
        printf("Error toggling backlight: %s\n", display_error_string(result));
    }
}

int main() {
    stdio_init_all();

    printf("-- Breakout Game --\n");

    // Initialize display
    display_error_t result;
    if ((result = display_pack_init()) != DISPLAY_OK) {
        printf("Failed to initialize display: %s\n", display_error_string(result));
        return 1;
    }

    // Initialize buttons
    if ((result = buttons_init()) != DISPLAY_OK) {
        printf("Failed to initialize buttons: %s\n", display_error_string(result));
        return 1;
    }

    // Set callback for Y button (backlight toggle)
    if ((result = button_set_callback(BUTTON_Y, on_button_y)) != DISPLAY_OK) {
        printf("Failed to set callback for Y: %s\n", display_error_string(result));
    }

    // Init game
    init_bricks();

    while (true) {
        buttons_update();

        update_game();
        draw_game();

        // Wait for DMA if busy
        if (display_dma_busy()) {
            display_wait_for_dma();
        }

        sleep_ms(20); // ~50 FPS
    }

    // Cleanup (unreachable)
    display_cleanup();
    return 0;
}

