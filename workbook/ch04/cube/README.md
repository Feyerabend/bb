
### 2. 3D Spinning Cube

An interactive 3D wireframe cube with smooth rotation and depth sorting:
- *Real-time 3D rendering*: Full perspective projection
- *Depth-based coloring*: Back edges appear darker, front edges brighter
- *Painter's algorithm*: Edges drawn in correct depth order
- *Xiaolin Wu anti-aliasing*: Smooth, thin lines with sub-pixel precision
- *Interactive controls*: Adjust rotation, speed, and zoom on the fly

*Controls:*
- *Button A*: Toggle auto-rotation (play/pause)
- *Button B*: Reset to default view (angle and zoom)
- *Button X*: Increase rotation speed (up to max)
- *Button Y*: Cycle through zoom levels (0.8x to 3.0x)


### Rendering Engine
- *Xiaolin Wu line algorithm*: Anti-aliased lines with sub-pixel accuracy
- *RGB565 color*: Full 16-bit color support
- *DMA acceleration*: Fast display updates via SPI DMA
- *Button debouncing*: Reliable 50ms debounced button handling
- *Efficient rendering*: Minimal screen clearing, smart redrawing

### 3D Cube Technical Details
- *3D Transformations*: Full rotation matrices (X, Y, Z axes)
- *Perspective projection*: Simple but effective depth perspective
- *Depth sorting*: Painter's algorithm for correct edge ordering
- *Smooth animation*: ~30 FPS with adaptive rotation speeds
- *Visual depth cues*: Color gradient based on Z-depth




The `display.h` API provides:

- *Display functions*: Clear, fill rectangles, draw pixels, text rendering
- *Button handling*: Polled state, edge detection, callbacks
- *Error handling*: Comprehensive error codes and messages
- *DMA support*: Fast bulk transfers with interrupt handling
- *Color constants*: Predefined RGB565 colors

Example usage:
```c
display_pack_init();
display_clear(COLOR_BLACK);
display_draw_string(10, 10, "Hello", COLOR_WHITE, COLOR_BLACK);
display_set_backlight(true);

button_set_callback(BUTTON_A, my_callback);
while(1) {
    buttons_update();
    // ... rendering code ...
}
```


- *Frame rate*: ~20 FPS (clock), ~30 FPS (cube)
- *Line rendering*: Xiaolin Wu is slower but much prettier than Bresenham
- *DMA usage*: Large fills and blits use DMA for speed
- *Memory*: Display buffer not kept in RAM (streaming mode)



### Cube Extensions

- Add more complex 3D shapes (pyramid, octahedron, etc.)
- Implement face filling with colors
- Add lighting/shading effects
- Create a 3D model viewer

