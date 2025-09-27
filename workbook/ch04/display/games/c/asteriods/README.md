
## Project

The goal is for you to experiment with different solutions to reduce/eliminate flickering
while respecting the Pico's constraints:
- *Memory limit*: Pico has ~264KB RAM. A full 320x240x16-bit frame buffer uses ~150KB,
  leaving ~114KB for code, stack, and game state—tight but doable.
- *Performance*: The Pico runs at 133MHz by default. SPI transfers for large data (e.g.,
  full-screen blits) can take time (~10-20ms at 31.25MHz SPI speed), so aim for 30-50 FPS.
  Overclocking (via `set_sys_clock_khz`) is an option but risks stability.

This project encourages trial-and-error: Start with the baseline (flickering) code,
then iterate on solutions like dirty rectangles, frame buffering, or optimisation.


### "Asteroids Pico - Fix the Flicker"

*Objective*: The game flickers during gameplay due to how the screen is updated
(incremental clears and draws). Improve the display handling to make it smoother.
Experiment with techniques, measure trade-offs (e.g., FPS, memory usage), and
document your choices.

*Baseline Behavior*:
- The game clears old object positions using bounding rectangles, then redraws new ones.
- Every 60 frames (~1-2 seconds), it does a full-screen clear to prevent artifacts.
- Flickering happens because clears and draws aren't atomic—the display shows partial updates.
- Controls: B (left turn), Y (right turn), A (thrust), X (shoot/restart).
- LEDs indicate state (e.g., blue for thrust, yellow for shooting).

*Constraints*:
- Don't add external libraries beyond the Pico SDK. But you sure should change the driver.
- Keep the game playable (30+ FPS target).
- Monitor memory: Use `printf` to report free heap (via `malloc` tricks) or check build output.
- Test on hardware: Emulators won't show real SPI timing/flicker.


*Suggested Experiments* (Pick 1-2 to Implement):

1. *Optimize Dirty Rectangles*: Improve bounding rect calculation and merging.
   Only clear/redraw changed areas more efficiently. (Low memory, medium complexity.)

2. *Partial Frame Buffer*: Use a small RAM buffer (e.g., 32KB) for "dirty" regions
   only. Composite changes, then send via SPI. (Balances memory/speed.)

3. *Full Frame Buffer*: Allocate a 320x240 uint16_t array in RAM. Redefine drawing
   functions (e.g., `draw_line_clipped`) to write to the buffer, then blit the whole
   screen each frame using `display_blit_full`. (High memory, simple, but measure
   FPS drop from full blits.)

4. *Double Buffering*: Use two full buffers, draw to one while blitting the other.
   (Uses ~300KB—over limit unless you compress or reduce resolution. Likely fails;
   good for learning why.)

5. *SPI/DMA Tweaks*: Increase SPI speed (up to 62.5MHz), overclock Pico to 200+ MHz,
   or chain DMA transfers for faster blits. (Low memory, but risks hardware instability.)

6. *Reduce Draw Complexity*: Simplify asteroids (fewer vertices), reduce max bullets/asteroids,
   or skip draws near edges. (Easy starter fix.)

7. *V-Sync Approximation*: Use timers to sync updates to ~50Hz, avoiding mid-frame SPI conflicts.


*Measurement Tips*:
- FPS: Add a counter in `main()` loop; `printf` every second.
- Memory: In code,
  `extern char __StackLimit; printf("Free RAM: %dKB\n", (uint32_t)&__StackLimit - (uint32_t)malloc(1));`
  (approximate).
- Flicker: Record video or observe on hardware.
- Profile: Use `absolute_time_t` to time sections (e.g., clear vs. draw vs. blit).


*Sample Build/Run Instructions*:
1. Clone Pico SDK if needed.
2. Create project dir with the four files + CMakeLists.txt.
3. `cd build; cmake ..; make`.
4. Flash `asteroids_pico.uf2` to Pico.
5. Connect via serial (e.g., minicom) for debug output.

*Example Improvement: Full Frame Buffer (Implement!)*

In `main.c`, add at top:
```c
uint16_t frame_buffer[SCREEN_WIDTH * SCREEN_HEIGHT];
```

Redefine drawing functions to target `frame_buffer` (e.g., for pixels):
```c
void buffer_draw_pixel(int x, int y, uint16_t color) {
    if (x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT) {
        frame_buffer[y * SCREEN_WIDTH + x] = color;
    }
}
```

Adapt `draw_line_clipped`, `draw_ship`, etc., to use `buffer_draw_pixel`. In `game_loop()`:
- Clear buffer to black: `memset(frame_buffer, 0, sizeof(frame_buffer));` (or optimised loop).
- Draw all objects to buffer.
- Call `display_blit_full(frame_buffer);`.
- Remove incremental clears.

*Trade-offs to Discuss*:
- Full buffer: No flicker, but slower (full blit every frame). If FPS drops below 30,
  optimise by blitting only dirty regions.
- If memory runs out: Reduce to 1bpp (bit-packed) buffer and convert on blit—complex
  but saves ~75% RAM.
- Failure Modes: Double buffering might crash (OOM); overclocking might cause heat/glitches.

*Deliverable*:
- Modified code.
- Report: What you tried, what tools you tried, why, measurements (FPS, memory, flicker before/after),
  and lessons (e.g., "Full buffering eliminated flicker but dropped FPS by 20%—fixed by overclocking.").

