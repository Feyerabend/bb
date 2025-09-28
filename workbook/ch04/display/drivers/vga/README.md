
## VGA

The Raspberry Pi Pico's Programmable I/O (PIO) is a versatile hardware feature on the
RP2040 microcontroller that allows for custom digital interfaces by executing small
assembly-like programs on dedicated state machines. PIO is particularly useful for
generating precise timing signals required for video standards like VGA, which demands
stable horisontal and vertical sync pulses alongside RGB pixel data. By offloading
these tasks to PIO, the CPU cores can focus on higher-level operations like rendering
graphics or handling inputs, enabling applications such as simple games, data visualisation,
or even video playback on a VGA monitor.

This section assumes that you have some experience with, or have read about,
VGA and the way older monitors worked.


### Hardware Requirements for VGA Output

To implement VGA on the Pico, you'll need:
- A Raspberry Pi Pico (or Pico 2) board.
- A VGA monitor supporting 640x480 resolution at 60Hz (many modern LCD screens are tolerant, but not all).
- A simple resistor-based digital-to-analog converter (DAC) for the RGB signals,
  typically using 5 bits per color channel (e.g., resistors in a weighted ladder
  like 8.06kΩ, 4.02kΩ, 2.00kΩ, 1.00kΩ, 510Ω for red, green, and blue).
  This reduces the 3.3V GPIO output to the VGA-standard 0-0.7V range.
- GPIO pins allocated for RGB (e.g., 0-4 for each color, totaling 15 pins for 5:6:5 RGB),
  HSYNC, and VSYNC (e.g., pins 5 and 6).
- Optionally, a pre-built board like the Pimoroni Pico VGA Demo Board or similar for
  easier wiring, which may include additional features like SD card support for loading assets.

The total pin count can be up to 17 for full-color VGA, but simpler 3-bit color
implementations (8 colors) use fewer pins and less memory.


### PIO Implementation Overview

PIO programs run on up to 8 state machines (4 per PIO block on the RP2040),
each capable of executing instructions at up to 133MHz. For VGA, multiple
state machines are synchronized via interrupts to handle:
- *HSYNC (Horizontal Sync):* Generates line timing.
- *VSYNC (Vertical Sync):* Generates frame timing, paced by HSYNC.
- *RGB Pixel Output:* Streams color data during active video periods.

A common resolution is 640x480 @ 60Hz, requiring a 25MHz pixel clock for HSYNC/VSYNC
and 125MHz for RGB to achieve sub-pixel precision. Pixel data is often stored in a
framebuffer (e.g., a char array for 8-color mode, using 1.5KB for 640x480) and transferred
via DMA to the PIO FIFO without CPU intervention.


#### Key PIO Code Snippets

Here's a summarized example from a detailed PIO VGA driver, using three state machines on
PIO0, clocked appropriately (HSYNC/VSYNC at 25MHz, RGB at 125MHz). The code uses PIO
assembly for timing-critical operations.

*HSYNC PIO Program (Generates horizontal timing, clocked at 25MHz):*
```
.program vga_hsync
.side_set 1
pull block              ; Load active + front porch length (656 cycles) into OSR
mov x osr               ; Copy to X scratch
activeporch:
jmp x-- activeporch     ; Loop for active + front porch (high)
set pins, 0 [31]        ; Sync pulse low (96 cycles total)
set pins, 0 [31]
set pins, 0 [31]
set pins, 0             ; End of sync pulse
set pins, 1 [31]        ; Back porch high (48 cycles)
set pins, 1 [31]
set pins, 1 [12]
irq 0 [1]               ; Signal to VSYNC/RGB, then wrap
wrap
```
- *Timing Explanation:* Active video (640 cycles) + front porch (16 cycles) = 656 high.
  Sync pulse: 96 low. Back porch: 48 high. Total line: 800 cycles (~31.77µs at
  25.175MHz for standard VGA).

*VSYNC PIO Program (Generates vertical timing, paced by HSYNC interrupts):*
```
.program vga_vsync
.side_set 1
pull block              ; Load active lines (480) into OSR
mov x osr
active:
wait 1 irq 0            ; Wait for HSYNC IRQ
jmp x-- active          ; Loop for 480 active lines
set y, 9                ; Front porch (10 lines)
frontporch:
wait 1 irq 0 side 1     ; High during front porch
jmp y-- frontporch
set pins, 0             ; Sync pulse low (2 lines)
wait 1 irq 0
wait 1 irq 0
set y, 31               ; Back porch (33 lines)
set pins, 1             ; High during back porch
backporch:
wait 1 irq 0 side 1
jmp y-- backporch
irq 1 [3]               ; Signal RGB active, then wrap
wrap
```
- *Timing Explanation:* Active: 480 lines. Front porch: 10 lines high.
  Sync: 2 lines low. Back porch: 33 lines high. Synchronized to HSYNC via IRQ 0.

*RGB PIO Program (Outputs pixel data, clocked at 125MHz):*
```
.program vga_rgb
.side_set 1 opt
pull block              ; Load counter (e.g., 640 pixels)
mov y osr
set pins, 0             ; Zero pins during blanking
blanking:
wait 1 irq 1 [3]        ; Wait for VSYNC active IRQ
pull block              ; Pull color data
mov x osr               ; Load loop counter
colorout:
out pins, 3 [4]         ; Output 3 bits (color) with delay
jmp x-- colorout [2]    ; Loop for row, with fine delay
wrap
```
- *Timing Explanation:* Outputs 640 pixels per line at 5x HSYNC clock for
  precision. Uses `out` to shift color bits from FIFO, with delays for stable signal.

These programs are compiled and loaded using the Pico SDK's `pio_sm_put_blocking`
and `pio_add_program` functions.



### DMA Integration for Pixel Data

DMA handles efficient transfer of framebuffer data (e.g., `uint8_t vga_data_array[153600]`)
to the RGB PIO FIFO. Two channels are chained:
- Channel 0: Transfers 8-bit data from array to PIO TX FIFO, paced by PIO DREQ.
- Channel 1: Reconfigures Channel 0's read address after each frame, chaining back.

Example C setup:
```c
dma_channel_config c0 = dma_channel_get_default_config(rgb_chan_0);
channel_config_set_transfer_data_size(&c0, DMA_SIZE_8);
channel_config_set_read_increment(&c0, true);
channel_config_set_write_increment(&c0, false);
channel_config_set_dreq(&c0, DREQ_PIO0_TX2);
channel_config_set_chain_to(&c0, rgb_chan_1);
dma_channel_configure(rgb_chan_0, &c0, &pio->txf[2], vga_data_array, TXCOUNT, false);

dma_channel_config c1 = dma_channel_get_default_config(rgb_chan_1);
channel_config_set_transfer_data_size(&c1, DMA_SIZE_32);
channel_config_set_read_increment(&c1, false);
channel_config_set_write_increment(&c1, false);
channel_config_set_chain_to(&c1, rgb_chan_0);
dma_channel_configure(rgb_chan_1, &c1, &dma_hw->ch[rgb_chan_0].al2_read_addr_trig, &address_pointer, 1, false);
```
This loop ensures continuous refresh without CPU overhead.


### Setup Tutorial Steps

1. *Prepare Hardware:* Wire the DAC resistors to GPIO pins for RGB,
   connect HSYNC/VSYNC to VGA pins 13/14. Use a breadboard or demo board.
2. *Install SDK:* Set up the Pico C/C++ SDK. Include `pico/stdlib.h`,
   `hardware/pio.h`, `hardware/dma.h`.
3. *Load PIO Programs:* Use `pio_add_program` to load assembled PIO code.
4. *Configure State Machines:* Set clocks, pins, and start machines with
   `pio_sm_init`, `pio_sm_set_enabled`.
5. *Set Up DMA:* As above, for framebuffer transfer.
6. *Render Graphics:* Modify the framebuffer array (e.g., draw lines or
   patterns), which auto-updates via DMA.
7. *Compile and Flash:* Use CMake with Pico SDK, flash via UF2.


### Advanced Examples and Libraries

- For higher-color modes (e.g., 16-bit RGB565), use the `pico_scanvideo`
  library from `pico-extras` for scanline-based rendering.
- GitHub repos like raspberrypi/pico-playground include demos like video
  playback or test patterns.
- Other libraries: PicoVGA for TV/VGA support, or MicroPython versions
  for scripting.
- Community tutorials on YouTube cover PIO coding and debugging.

This setup can be extended to DVI/HDMI with faster clocks or additional
hardware, but VGA remains accessible for retro computing or embedded displays.

