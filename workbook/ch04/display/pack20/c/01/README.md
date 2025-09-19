

### Colour Representation

```c
// Colours (RGB565 format)
#define COLOR_BLACK     0x0000
#define COLOR_WHITE     0xFFFF
#define COLOR_RED       0xF800
#define COLOR_GREEN     0x07E0
#define COLOR_BLUE      0x001F
#define COLOR_YELLOW    0xFFE0
#define COLOR_CYAN      0x07FF
#define COLOR_MAGENTA   0xF81F
```

This C/C++ code defines color constants in *RGB565 format*—a 16-bit color scheme used
in embedded graphics (e.g., TFT displays on microcontrollers). It packs color data
efficiently:
- *Red*: 5 bits (0-31 intensity levels, where 0 = off, 31 = max brightness).
- *Green*: 6 bits (0-63 intensity levels, for finer shades).
- *Blue*: 5 bits (0-31 intensity levels).

The hex values are bit-packed as *RRRRRGGG GGGBBBBB*. It's memory-efficient (2 bytes per
pixel) but has fewer shades than full 24-bit RGB (~65K vs. 16M colors).

*Intensity Reference Table:*

| Color Name | Hex Value | Red Intensity (0-31) | Green Intensity (0-63) | Blue Intensity (0-31) | Visual Description  |
|------------|-----------|----------------------|------------------------|-----------------------|---------------------|
| Black      | 0x0000    | 0 (off)              | 0 (off)                | 0 (off)               | Pure darkness       |
| White      | 0xFFFF    | 31 (full)            | 63 (full)              | 31 (full)             | Bright white        |
| Red        | 0xF800    | 31 (full)            | 0 (off)                | 0 (off)               | Pure red            |
| Green      | 0x07E0    | 0 (off)              | 63 (full)              | 0 (off)               | Pure green          |
| Blue       | 0x001F    | 0 (off)              | 0 (off)                | 31 (full)             | Pure blue           |
| Yellow     | 0xFFE0    | 31 (full)            | 63 (full)              | 0 (off)               | Bright yellow (R+G) |
| Cyan       | 0x07FF    | 0 (off)              | 63 (full)              | 31 (full)             | Bright cyan (G+B)   |
| Magenta    | 0xF81F    | 31 (full)            | 0 (off)                | 31 (full)             | Bright magenta (R+B)|
