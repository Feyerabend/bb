#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Simple error logger - stores last 10 errors with full context */
#define MAX_ERROR_LOG 10

typedef struct {
    disp_error_context_t ctx;
    uint32_t timestamp_ms;
} logged_error_t;

static struct {
    logged_error_t errors[MAX_ERROR_LOG];
    int count;
} error_log = {0};

static void log_error(disp_error_t err) {
    if (err == DISP_OK || error_log.count >= MAX_ERROR_LOG) return;

    error_log.errors[error_log.count].ctx = disp_get_last_error();
    error_log.errors[error_log.count].timestamp_ms = to_ms_since_boot(get_absolute_time());
    error_log.count++;
}

static void print_error_log(void) {
    if (error_log.count == 0) {
        printf("\nNo errors recorded.\n");
        return;
    }

    printf("\n=== ERROR LOG (%d recorded) ===\n", error_log.count);
    for (int i = 0; i < error_log.count; i++) {
        logged_error_t *e = &error_log.errors[i];
        printf("\n[%d] %s (at %lu ms)\n", i + 1,
               disp_error_string(e->ctx.code), (unsigned long)e->timestamp_ms);
        printf("    Function: %s (line %d)\n", e->ctx.function, e->ctx.line);
        printf("    Message : %s\n", e->ctx.message);
    }
    printf("\n");
}

static void button_a_cb(button_t b) { printf("Button A pressed!\n"); }
static void button_b_cb(button_t b) { printf("Button B pressed!\n"); }
static void button_x_cb(button_t b) { printf("Button X pressed!\n"); }
static void button_y_cb(button_t b) { printf("Button Y pressed!\n"); }

void demo_robust_init(void) {
    printf("\n--- Demo 1: Robust Init (DMA fallback) ---\n");

    disp_config_t cfg = disp_get_default_config();
    cfg.use_dma = true;

    disp_error_t err = disp_init(&cfg);
    if (err != DISP_OK) {
        printf("DMA init failed - falling back to software mode..\n");
        log_error(err);

        cfg.use_dma = false;
        err = disp_init(&cfg);
        if (err != DISP_OK) {
            printf("Init failed completely!\n");
            log_error(err);
            return;
        }
        printf("Init successfully without DMA\n");
    } else {
        printf("Init with DMA - perfect!\n");
    }

    disp_clear(COLOR_GREEN);
    disp_draw_text(40, 100, "INIT OK", COLOR_BLACK, COLOR_GREEN);
    sleep_ms(1500);
    disp_deinit();
}

void demo_batch_drawing(void) {
    printf("\n--- Demo 2: Batch drawing (50 rectangles) ---\n");

    disp_init(NULL);
    disp_clear(COLOR_BLACK);

    int ok = 0, failed = 0;
    for (int i = 0; i < 50; i++) {
        uint16_t x = rand() % (DISPLAY_WIDTH  - 40);
        uint16_t y = rand() % (DISPLAY_HEIGHT - 40);
        uint16_t col = rand() & 0xFFFF;

        disp_error_t err = disp_fill_rect(x, y, 38, 38, col);
        if (err != DISP_OK) {
            failed++;
            log_error(err);
            disp_clear_error();
        } else {
            ok++;
        }
    }

    char txt[64];
    snprintf(txt, sizeof(txt), "OK:%d  ERR:%d", ok, failed);
    disp_draw_text(10, 10, txt, failed ? COLOR_RED : COLOR_GREEN, COLOR_BLACK);

    printf("Batch complete - %d successful, %d failed\n", ok, failed);
    sleep_ms(3000);
    disp_deinit();
}

void demo_safe_blit(void) {
    printf("\n--- Demo 3: Safe buffer blit (out-of-bounds test) ---\n");

    disp_init(NULL);
    disp_clear(0x001F); // dark blue

    const int w = 80, h = 80;
    uint16_t *buf = malloc(w * h * 2);
    if (!buf) {
        printf("Failed to allocate buffer!\n");
        disp_deinit();
        return;
    }

    for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++)
            buf[y * w + x] = ((x * 31 / w) << 11) | ((y * 63 / h) << 5) | (31 - x * 31 / w);

    int positions[][2] = { {0,0}, {250,0}, {0,180}, {300,200}, {120,80} };

    for (int i = 0; i < 5; i++) {
        disp_error_t err = disp_blit(positions[i][0], positions[i][1], w, h, buf);
        if (err != DISP_OK) {
            printf("Blit %d failed (expected): %s\n", i, disp_error_string(err));
            log_error(err);
        } else {
            printf("Blit %d successful\n", i);
        }
    }

    free(buf);
    disp_draw_text(10, 10, "Blit Test Done", COLOR_YELLOW, COLOR_BLACK);
    sleep_ms(3000);
    disp_deinit();
}

void demo_timeout(void) {
    printf("\n--- Demo 4: DMA timeout test ---\n");

    disp_config_t cfg = disp_get_default_config();
    cfg.dma_timeout_ms = 5;

    disp_init(&cfg);
    printf("Trying large clear with 5ms timeout..\n");

    disp_error_t err = disp_clear(COLOR_MAGENTA);
    if (err == DISP_ERR_DMA_TIMEOUT) {
        printf("Timeout detected (expected)\n");
        log_error(err);
        disp_wait_complete(2000);
        printf("Recovered - reinit with normal timeout\n");
        cfg.dma_timeout_ms = 1000;
        disp_deinit();
        disp_init(&cfg);
        disp_clear(COLOR_CYAN);
        disp_draw_text(40, 100, "Recovered!", COLOR_BLACK, COLOR_CYAN);
    }

    sleep_ms(2000);
    disp_deinit();
}

void demo_state_validation(void) {
    printf("\n--- Demo 5: State validation tests ---\n");

    printf("Before init - initialised? %s\n", disp_is_initialized() ? "YES" : "NO");

    disp_init(NULL);
    printf("After init   - initialised? %s\n", disp_is_initialized() ? "YES" : "NO");

    disp_error_t err = disp_init(NULL);
    if (err == DISP_ERR_ALREADY_INIT) {
        printf("Double init correctly rejected\n");
        log_error(err);
        disp_clear_error();
    }

    disp_deinit();
    printf("After deinit - initialised? %s\n", disp_is_initialized() ? "YES" : "NO");

    err = disp_clear(COLOR_RED);
    if (err == DISP_ERR_NOT_INIT) {
        printf("Use after deinit correctly blocked\n");
        log_error(err);
    }
}

int main() {
    stdio_init_all();
    sleep_ms(2000);

    printf("\n");
    printf("  Pimoroni Display Pack 2.0 - Error Handling Demo\n");

    srand(12345);

    demo_robust_init();
    demo_batch_drawing();
    demo_safe_blit();
    demo_timeout();
    demo_state_validation();

    print_error_log();

    printf("Demo finished\n");
    printf("Now testing buttons A/B/X/Y.\n\n");

    /* ----- Final button test (pure C) ----- */
    buttons_init();
    button_set_callback(BUTTON_A, button_a_cb);
    button_set_callback(BUTTON_B, button_b_cb);
    button_set_callback(BUTTON_X, button_x_cb);
    button_set_callback(BUTTON_Y, button_y_cb);

    disp_init(NULL);
    disp_clear(COLOR_BLACK);
    disp_draw_text(20, 80,  "Everything should work", COLOR_WHITE, COLOR_BLACK);
    disp_draw_text(50, 120, "Press A B X Y for test", COLOR_CYAN, COLOR_BLACK);

    while (1) {
        buttons_update();
        sleep_ms(10);
    }

    return 0;
}
