


## NOTES: Roadmap

1. Hardware + driver: get the ST7789 talking to the Raspberry Pi Pico (SPI / DC / RST / BL).
   Verify wiring and a minimal init sequence; be able to draw pixels and filled rectangles.
2. Framebuffer & transfer: choose a buffering strategy (full framebuffer, partial updates,
   tiled updates), implement a fast transfer path (SPI + DMA, or PIO + DMA for maximal offload).
   Verify refresh rates and CPU load.
3. Graphics API: expose simple primitives (pixel, line, rect, blit, tilemap, text) implemented
   efficiently for the Pico’s constraints!
4. Scripting / VM: design and implement a small VM (bytecode) that exposes engine APIs
   (spawn, move, draw, wait, emit). Add coroutines, event dispatch, sandboxing and hot-reload.
5. Game runtime & tools: entity system, input handling, asset pipeline, simple level editor,
   and example game content.
6. Optimise & polish: reduce allocations, tune DMA/PIO usage, add profiler and debug hooks.


### Phase 1 — ST7789 on Raspberry Pi Pico: practical requirements and first driver

Goals
- Get a working driver that initialises the ST7789 and can draw pixels and rectangles.
- Measure time to fill screen and CPU load.

__Hardware basics (wiring & pins)__

Typical pins on a 240×240 ST7789 module:
- VCC → 3.3 V, GND → GND
- SCL / SCK → SPI SCK pin
- SDA / MOSI → SPI MOSI pin
- DC (Data/Command) → GPIO (controls whether byte is command or data)
- RST → Reset GPIO
- CS (Chip Select) → optional (can tie low)
- BL / LED → Backlight control (PWM or on)
(Examples and typical module specs: 240×240 ST7789 breakout modules, Waveshare?).

Important device facts (load-bearing)
- ST7789-based 240×240 modules commonly use SPI and accept 16-bit RGB565 data
  (other modes exist; COLMOD controls pixel format). See ST7789 datasheet for
  exact commands and COLMOD values.  ￼
- RP2040 (the Pico) has 264 kB SRAM in multiple banks and supports DMA and PIO;
  these features make frame buffering and DMA transfer practical on-device.  ￼

Minimal command flow (concept)
1. Hardware reset pulse (toggle RST low for X ms).
2. Send initialization commands (SWRESET, SLEEP OUT, COLMOD, MADCTL, RAMCTRL / GRAM settings,
   INVERSION ON/OFF, DISPLAY ON). The exact sequence varies by module and panel--use datasheet
   or your module vendor init array. Problems occur when a register in the init is omitted
   (e.g. RAMCTRL).

Framebuffer size math (digit-by-digit)
- Resolution: 240 × 240 = 57 600 pixels.
- Using 16-bit RGB565: bytes per pixel = 2.
- Framebuffer bytes = 57 600 × 2 = 115 200 bytes.
So a single full-screen 16-bit framebuffer is 115 200 bytes, which fits inside the Pico’s 264 kB SRAM,
but leaves space usage for code, stacks and other buffers — plan memory carefully. So we use RPI 2 instead!


CHECK Pico C

A compact sketch for initialising SPI and sending a single command/data byte.
```c
/* pico_st7789_min.c — schematic */
#include "pico/stdlib.h"
#include "hardware/spi.h"

/* pin assignment — adapt to your wiring */
#define PIN_SCK  18
#define PIN_MOSI 19
#define PIN_CS   17   /* optional */
#define PIN_DC   16
#define PIN_RST  20

static inline void st7789_cmd(uint8_t b) {
    gpio_put(PIN_DC, 0);
    gpio_put(PIN_CS, 0);
    spi_write_blocking(spi0, &b, 1);
    gpio_put(PIN_CS, 1);
}

static inline void st7789_data(const uint8_t *buf, size_t len) {
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    spi_write_blocking(spi0, buf, len);
    gpio_put(PIN_CS, 1);
}

void st7789_init(void) {
    /* reset pulse */
    gpio_put(PIN_RST, 0);
    sleep_ms(10);
    gpio_put(PIN_RST, 1);
    sleep_ms(120);

    /* Typical init sequence (example commands) */
    st7789_cmd(0x01); /* SWRESET */
    sleep_ms(150);
    st7789_cmd(0x11); /* SLEEP OUT */
    sleep_ms(120);
    uint8_t colmod[] = {0x05}; /* 16-bit/pixel = 0x05 */
    st7789_cmd(0x3A); /* COLMOD */
    st7789_data(colmod, 1);
    /* set MADCTL, RAMCTRL, inversion, etc, then DISPLAY ON */
    st7789_cmd(0x29); /* DISPLAY ON */
}
```

__Notes__
- Use spi_init(spi0, 20 * 1000 * 1000) for a fast clock (test module limit).
  Many modules are stable at 10–30 MHz; check module specs.
- Some modules/driver combinations require SPI mode 0 or mode 3; test and
  verify--libraries vary.  ￼



### Phase 2 — Efficient transfers: DMA, double-buffering, PIO

__Options (trade-offs)__
- Full framebuffer (single buffer): easy; prepare whole frame in RAM, push via DMA
  to the display. Memory: ~115 KB for 240×240 RGB565. Good when you can spare memory
  and want simple blits.
- Double-buffering: prepare next frame off-screen, swap, and DMA-transfer while
  engine continues. More memory (≈230 KB) but smoother.
  On Pico this may be tight but sometimes feasible. Check!
- Tiled / partial updates: keep smaller rectangles updated; stream only changed
  tiles to save bandwidth. Useful for HUDs or tile-based games.
- PIO + DMA offload: push pixel stream using PIO state machines and DMA so CPU
  is free for game logic.  ￼


### Why DMA?

Using DMA to stream the framebuffer to SPI or PIO reduces CPU interrupts and makes
it practical to maintain a gameplay update loop concurrently.
See spi_dma example in Pico examples for reference.  ￼

Practical approach on Pico
1. Start with a single framebuffer in SRAM and implement a DMA routine that streams
   the buffer to the TFT in row/column order. Confirm timing and observed FPS.
  (Simple and fast to implement.)
2. If you need less CPU load or higher refresh, consider PIO + multiple DMA channels
   to fully offload the refresh to hardware.

For a lot of this: See Dmitry Grinberg.


### Phase 3 — Graphics API you should implement (minimal set)

Implement and expose these primitives from C (fast) to the VM (scripted):
- clear(color)
- drawPixel(x,y,color)
- fillRect(x,y,w,h,color) — optimise to fill row by row into framebuffer using memset-like operations where possible.
- blit(sprite, x, y) — sprite blitting, with optional transparent colour key. Use small sprite atlases.
- drawText(x,y,string,font) — bitmap font rendering (monospace or variable width).
- Tilemap helpers: drawTilemap(map, tileset, camera_x, camera_y).

Implementation notes:
- Pre-convert loaded images into native RGB565 in your asset pipeline (no runtime conversion on Pico).
- Use batches: aggregate blits into contiguous memory streams to use fewer DMA transfers.
- Use vertical or horizontal strip transfers to match display memory layout.

Example: 32×32 sprite memory:
- 32 × 32 = 1024 pixels. At 2 bytes/pixel → 1024 × 2 = 2048 bytes per sprite.



### Phase 4 — VM design and integration: what the scripting language must provide

A compact bytecode VM is adequate for Pico-based games and gives you full control of
memory, coroutines and APIs. Below is a recommended design.

High-level requirements for the scripting VM
1. Small runtime footprint: must fit comfortably with framebuffer and engine code in Pico SRAM.
2. Coroutines / yields: a wait() primitive or yield must exist so scripts can pause between frames without busy-waiting.
3. Native bindings: direct, quick calls from script to C engine routines (draw, spawn, set_velocity, play_sound).
4. Controlled allocation & GC: keep GC simple, predictable, and with small heaps (or avoid GC-heavy patterns).
5. Determinism support (optional): seedable RNG and careful float use for synchronised multiplayer or deterministic replays.
6. Hot-reload / recompile of scripts: allow designers to tweak behaviours without rebooting.

VM architecture choices
- Stack-based VM: simpler to implement (push/pop), compact bytecode. Good for small embedded targets.
- Register-based VM: fewer instructions, faster on average, more complex to implement.

For a Pico project, a simple stack-based VM is usually the best balance of simplicity and size.


### Minimal instruction set (example)

```
OP_LOAD_CONST <u16 idx>
OP_LOAD_LOCAL <u8 idx>
OP_STORE_LOCAL <u8 idx>
OP_GET_GLOBAL <u16 idx>
OP_CALL <u8 nargs>
OP_RETURN
OP_JMP <s16>
OP_JMP_IF_FALSE <s16>
OP_PUSH_INT <s32>
OP_PUSH_FLOAT <f32>
OP_WAIT_TICKS <u16>   ; coroutine yield for N engine ticks
OP_SPAWN <u16 script_id>  ; spawn a new script/coroutine
OP_NATIVE <u16 native_id>  ; call an engine native function
```
Coroutines scheduler (concept)
- Each script runs as a coroutine with its own stack, PC and local storage.
- Scheduler runs all “ready” coroutines each frame (or until they yield).
- OP_WAIT_TICKS n sets coroutine->wake_at = ticks_now + n and yields back
  to scheduler. Scheduler checks wake times each frame. This yields deterministic
  timing based on engine ticks.


__Example of WAIT in interpreter (sketch)__
```
switch(instr) {
  case OP_WAIT_TICKS: {
    uint16_t n = fetch_u16();
    curr->wake_at = engine.ticks + n;
    curr->state = COROUTINE_SLEEPING;
    return; /* yield interpreter for this coroutine */
  }
  ...
}
```


Memory and GC strategy (recommendation)
- Option A: No GC / pool allocation — pre-allocate arrays of objects
  (entities, small object pools). This is fastest and most deterministic.
  Use free lists.
- Option B: Simple reference counting with careful cycle avoidance.
  Low overhead but must handle cycles.
- Option C: Tiny mark-and-sweep GC that you can trigger during non-critical times;
  keep heap small and predictable. For the Pico, pool-based allocation or ref-count
  are both sensible starting points.

Binding engine functions (native interface)
- Keep a native function table: native_funcs[native_id] = function pointer.
- From bytecode use OP_NATIVE native_id with arguments on the stack. Native
  functions pop arguments and return values via the VM stack. This is efficient and compact.



### Phase 5 — Bringing VM and graphics together (runtime loop)

Design your engine loop to manage both low-level tasks and the script VM:

```
while (true) {
  process_input();            // read buttons / ADC / USB
  engine.ticks++;
  run_scripts_for_budget();   // resume coroutines scheduled to run
  physics_step();             // simple discrete collision / movement
  update_game_state();        // process AI and events (can be in scripts)
  render_into_framebuffer();  // call draw primitives to compose the frame
  kick_dma_transfer();        // start DMA to refresh display (non-blocking)
  wait_for_next_frame();      // or do a coarse sleep/yield to scheduler
}
```
Key notes:
- Keep render_into_framebuffer() and kick_dma_transfer() decoupled—start DMA and
  return control to logic if PIO+DMA offload is used.
- Cap the script VM execution per frame (instruction budget) to avoid long script-induced frame hitches.



### Phase 6 — Tools, asset pipeline and workflow
- Asset pipeline: convert PNG / BMP sprites off-line to RGB565 arrays (tool on PC).
   Commit .h or binary assets into flash or serve from external storage.
- Sprite atlas & indices: pack sprites into atlases and store metadata (x,y,w,h) to speed blits.
- Level editor: simple CSV tilemap editor or a small GUI on PC that exports simple JSON or binary tilemaps.
- Hot reload: allow script bytecode files to be reloaded from USB mass storage or via a serial protocol.



### Phase 7 — Example: tiny bytecode + engine native (sketch)

Example bytecode pseudo and the corresponding native call to move a sprite.
```
/* pseudo bytecode for "move right 10 ticks" */
OP_PUSH_INT 100       ; speed
OP_PUSH_INT 10        ; duration
OP_NATIVE N_MOVE_SPRITE  ; native: move(sprite_id, speed, duration)
OP_WAIT_TICKS 10
OP_RETURN
```
Native binding table:
```
typedef int (*native_fn)(VMState *vm);
native_fn native_table[] = { native_move_sprite, native_play_sound, ... };

int native_move_sprite(VMState *vm) {
  int duration = vm_pop_int(vm);
  int speed = vm_pop_int(vm);
  int sprite_id = vm_pop_int(vm);
  engine_move_sprite(sprite_id, speed, duration);
  return 0; /* zero return values on VM stack */
}
```



### Phase 8 — Practical development milestones and checklist
1. Hardware test: wire ST7789 to Pico, implement minimal C driver, show "fill screen" in single colour.
   (Verify init sequence against datasheet.) DONE.
2. Framebuffer + SPI transfer: implement single-buffer transfer via spi_write_blocking, measure time
   to full-screen update.
3. DMA: refactor streaming to use DMA (reference pico-examples spi_dma). Measure improvement.
4. Simple graphics primitives: drawPixel, fillRect, blit. Create an art asset or tile set.
5. Minimal VM: implement stack-based interpreter with WAIT and NATIVE calls.
   Test a simple "enemy patrol" script.
6. Asset pipeline: PNG → RGB565 converter and sprite atlas exporter (PC tool).
7. Input & entity system: map buttons to player actions and spawn entities from VM scripts.
8. Optimise: if CPU saturates, consider PIO+DMA offload (Dmitry’s approach) and move non-real-time
   tasks to background.



Practical tips, pitfalls and suggestions
- Check the exact module datasheet for your ST7789 variant — init arrays differ between panel
  manufacturers and clones; leaving out one register can produce strange colour behaviour.  This on DP1?
- Test SPI mode if the module behaves oddly — some modules/libraries use mode 0, others mode 3.
  If you share the SPI bus with other devices (SD card), ensure you set the right mode before transfers.  ￼
- Keep runtime allocations small and prefer pool-based objects on RP2040. Full GC pauses can ruin frame timings.
- Instrument early: add simple cycle counters and measure frame times before micro-optimising.
- Start simple: prototype behaviour in MicroPython or Lua to iterate faster, then port hot parts to C when needed.



Quick MicroPython example — initialise and write a single pixel
```python
# micropython_st7789_min.py (schematic)
from machine import Pin, SPI
import time

spi = SPI(0, baudrate=20000000, sck=Pin(18), mosi=Pin(19))
dc = Pin(16, Pin.OUT)
cs = Pin(17, Pin.OUT)
rst = Pin(20, Pin.OUT)

def cmd(b):
    dc.value(0)
    cs.value(0)
    spi.write(bytes([b]))
    cs.value(1)

def data(b):
    dc.value(1)
    cs.value(0)
    spi.write(b if isinstance(b, bytes) else bytes([b]))
    cs.value(1)

# reset
rst.value(0); time.sleep_ms(10); rst.value(1); time.sleep_ms(120)
cmd(0x11)          # SLEEP OUT
time.sleep_ms(120)
cmd(0x3A); data(bytes([0x05])) # COLMOD = 16-bit
cmd(0x29)          # DISPLAY ON

# set a pixel by writing to a window and RAM
```



Final notes
- A language VM is adequate and standard practice for embedding gameplay logic on small platforms.
  For the Pico balance memory (framebuffer vs VM heap) and CPU (drawing vs script execution).
  Use C for the driver and VM core; expose a compact bytecode API to scripts.

- Sketch a small stack-based bytecode VM in C tuned to RP2040 memory constraints
  (coroutines, wait instruction, native binding table)!


#### Option A — Display Node + Logic Node

Pi A (Display Node)
- Talks directly to the ST7789 via SPI.
- Owns framebuffer, rendering pipeline, sprite blitting.
- Reads local input (buttons/joystick).
- Runs a lightweight VM for HUD/animation scripting.

Pi B (Logic Node)
- Runs the main game loop (AI, physics, entity management).
- Decides world state: positions, velocities, collisions, triggers.
- Sends periodic state updates to Display Node over UDP/TCP.

Data over Wi-Fi:
- From Logic → Display: compressed entity state (positions, sprites, animations).
- From Display → Logic: player input events (button presses, analog values).

This way, the Display Node only needs to worry about drawing
the current world state, and the Logic Node can run heavier
simulation or scripting.


Networking Considerations
- Protocol: Use UDP for fast, low-latency state packets; add your own reliability
  for critical events. TCP is simpler but may stall if a packet is dropped.
- Update rate: Don’t try to send updates every pixel/frame. Instead, send at 10–30
  Hz "world state" updates and let the Display Node interpolate between them.
- Data format: Binary, compact, little endian. Example packet:

[tick][num_entities][entity_id][x][y][sprite_id][flags]...

- Latency hiding: On the Display Node, run simple prediction (e.g. keep moving entity
  at last known velocity until update arrives).


Development Order
1. Get Pi A driving the ST7789 reliably (local rendering only).
2. Implement input loop on Pi A and echo button presses over UDP to Pi B.
3. Implement simple simulation loop on Pi B and send back entity positions.
4. Draw entities on Pi A using positions from Pi B.
5. Add interpolation/prediction so motion looks smooth even if Wi-Fi updates jitter.
6. Expand to multiple entities, collisions, scripting on Pi B.



"Analogy"

Think of it as “console + server”:
- The Display Node (Pi A) is like a thin client/console.
- The Logic Node (Pi B) is like the game server.

This scales if later multiplayer:
Pi B could be central “world authority” and multiple Pi A’s (each with screens + inputs) could connect.


