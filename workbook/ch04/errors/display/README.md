
## Pimoroni Display Pack 2.0 Driver

This is a complete, battle-tested driver for the *Pimoroni Display Pack 2.0*
(ST7789 320×240 IPS + 4 tactile buttons) on the *Raspberry Pi Pico (C/C++ SDK)*.
It also __requires__ the more capable Raspberry Pi Pico 2 or 2W to work.

The primary design goal is *zero silent failures*. Every public function returns
a detailed error code, tracks full context, validates parameters, and gracefully
degrades when resources (e.g. DMA) are unavailable.

| File | Purpose |
|-----|----|
| `display.h` | Complete public API, types, error codes, colours |
| `display.c` | Full implementation (init, drawing, DMA, buttons) |
| `main.c`    | Comprehensive demo + error-handling showcase |


### Features

- 320×240 landscape mode (90° rotation built-in)
- Full 16-bit RGB565 colour
- High-speed DMA transfers (≈40 ms full-screen clear)
- Automatic fallback to blocking SPI if DMA unavailable
- Configurable DMA timeout with automatic abort & recovery
- Bounds-checked & clamped drawing primitives
- Complete 5×8 bitmap font (ASCII 32-127)
- 4-button support with debounced press detection & callbacks
- Rich error system with function/line/message context
- Init/deinit state protection (double-init / use-after-free safe)
- Optional full-screen framebuffer for flicker-free updates


### Quick Start

```c
#include "display.h"

int main() {
    stdio_init_all();

    // Initialise with defaults (DMA enabled, backlight on)
    if (disp_init(NULL) != DISP_OK) {
        printf("Display init failed: %s\n", disp_error_string(disp_get_last_error().code));
        return -1;
    }

    disp_clear(COLOR_BLACK);
    disp_draw_text(50, 100, "Hello Pico!", COLOR_WHITE, COLOR_BLACK);

    // Button test
    buttons_init();
    button_set_callback(BUTTON_A, [](button_t b){ printf("A pressed!\n"); });

    while (1) {
        buttons_update();
        sleep_ms(10);
    }
}
```

### Core API Summary

```c
// Configuration
disp_config_t disp_get_default_config(void);
disp_error_t  disp_init(const disp_config_t *cfg);
disp_error_t  disp_deinit(void);
bool          disp_is_initialized(void);

// Drawing
disp_error_t disp_clear(uint16_t color);
disp_error_t disp_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
disp_error_t disp_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
disp_error_t disp_blit(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t *pixels);

disp_error_t disp_draw_char(uint16_t x, uint16_t y, char c, uint16_t fg, uint16_t bg);
disp_error_t disp_draw_text(uint16_t x, uint16_t y, const char *txt, uint16_t fg, uint16_t bg);

// Framebuffer (for smooth, flicker-free updates)
disp_error_t disp_framebuffer_alloc(void);
void disp_framebuffer_free(void);
uint16_t* disp_get_framebuffer(void);
disp_error_t disp_framebuffer_flush(void);
disp_error_t disp_framebuffer_clear(uint16_t color);
void disp_framebuffer_set_pixel(uint16_t x, uint16_t y, uint16_t color);

// Control
disp_error_t disp_set_backlight(bool on);
disp_error_t disp_wait_complete(uint32_t timeout_ms);

// Buttons (A, B, X, Y)
disp_error_t buttons_init(void);
void         buttons_update(void);                     // call often
bool         button_pressed(button_t b);
bool         button_just_pressed(button_t b);
bool         button_just_released(button_t b);
disp_error_t button_set_callback(button_t b, button_callback_t cb);
```


### Error Handling – Never Silent Again

Every function returns `disp_error_t`. On failure you can:

```c
disp_error_t err = disp_some_function(...);
if (err != DISP_OK) {
    disp_error_context_t ctx = disp_get_last_error();
    printf("ERROR %d (%s) in %s():%d – %s\n",
           err,
           disp_error_string(err),
           ctx.function, ctx.line,
           ctx.message ? ctx.message : "no details");
}
```

Convenient macro (perfect for development):

```c
#define CHECK(call) do {                           \
    disp_error_t e = (call);                       \
    if (e != DISP_OK) {                            \
        disp_error_context_t ctx = disp_get_last_error(); \
        printf("FAIL %s:%d → %s (%s)\n",           \
               ctx.function, ctx.line,             \
               disp_error_string(e), ctx.message); \
        return e;                                  \
    }                                              \
} while(0)
```


### Graceful Degradation Examples

```c
// Try with DMA first
disp_config_t cfg = disp_get_default_config();
cfg.use_dma = true;

if (disp_init(&cfg) != DISP_OK) {
    printf("DMA unavailable – falling back to blocking mode\n");
    cfg.use_dma = false;
    disp_init(&cfg);               // should now succeed
}
```

```c
// Recover from DMA timeout
cfg.dma_timeout_ms = 5;
disp_init(&cfg);
disp_clear(COLOR_RED);         // will timeout → DISP_ERR_DMA_TIMEOUT
disp_wait_complete(2000);      // let hardware settle
cfg.dma_timeout_ms = 1000;
disp_deinit();
disp_init(&cfg);               // back to normal
```


### Performance

| Operation                   | DMA enabled      | DMA disabled |
|-----------------------------|------------------|--------------|
| Full-screen clear           | ~40 ms           | ~200 ms      |
| 80×80 blit                  | ~6 ms            | ~25 ms       |
| Text character (5×8)        | ~1–2 ms          | unchanged    |
| Small rectangles (<100 px)  | blocking SPI faster (auto fallback) |


### Building

Standard Pico SDK project:

```bash
mkdir build
cd build
cmake ..
make
```

Copy the resulting `.uf2` to the Pico.


### Contributing & Extending

- Always return `disp_error_t` from new public functions
- Use the `DISP_ERROR(code, "msg")` macro to set context
- Validate coordinates, pointers, and state
- Add new error strings to `err_str[]` in `display.c`