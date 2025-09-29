
## HSTX

The RP2350, featured in the Raspberry Pi Pico 2, introduces the HSTX peripheral--a
high-speed serial interface capable of streaming data at up to 2.4 Gbps across 8 GPIO
pins. This feature is particularly advantageous for applications like video output,
such as DVI or DSI, without burdening the CPU cores or PIO blocks. The HSTX operates
independently of the system clock, running at 150 MHz, and is accessible via GPIOs 12 to 19.

HSTX (High-Speed Transmit) on the RP2350 is not a generic UART/SPI/I²C controller;
rather, it’s designed for streaming out waveforms at high speed with precise control
over pins and timing.

At a high level:
- Purpose: It allows the RP2350 to offload high-bandwidth bit-pushing tasks that would
  otherwise eat CPU cycles or push PIO to its limits.
- How it works:
  - You load words into an HSTX FIFO.
  - Each word encodes the waveform on multiple HSTX pins for a given number of cycles.
  - The HSTX block then serialises this out continuously with almost no CPU overhead.
- Use cases: Driving high-speed RGB displays (like ST7789/ST7735), generating LVDS/DDR-style
  signals, or other custom synchronous protocols.
- Flexibility: Instead of hardwired "SPI mode," you get a bit crossbar (remap logical
  bit streams to physical GPIOs) and can choose SDR or DDR. This makes it possible to
  mimic an SPI-like bus while actually running on the dedicated HSTX hardware.


The code is essentially a display driver for the Pimoroni Display Pack 2.0 (ST7789V2
controller), but instead of using the RP2350’s standard spi0/spi1 peripheral, it builds
a custom interface on top of HSTX:

1. Pin mapping & crossbar setup:
- gpio_set_function(..., GPIO_FUNC_HSTX) puts the display pins under HSTX control.
- Then hstx_ctrl_hw->bit[...] remaps logical HSTX streams to MOSI, SCK, CS, DC.
- Notably, DC is inverted in hardware, so the driver compensates.

2. FIFO-based transmission:
- Functions like hstx_put_word() and hstx_put_dc_cs_data() pack CS/DC/data into
  32-bit words that HSTX will stream.
- This simulates “chip-select low, clock eight cycles, MOSI sends data” entirely in hardware.

3. Display initialisation sequence:
- Mirrors what you’d see in a SPI display driver: reset the ST7789, issue commands
  (SWRESET, SLPOUT, COLMOD, etc.), set address window, then turn the display on.
- The key difference: instead of spi_write_blocking(), everything is passed through HSTX.

4. Drawing API:
- Provides fill_rect, draw_pixel, draw_string, blit_full. These functions just break
  down higher-level operations into HSTX byte pushes.
- This is CPU-driven (polling loop), no DMA (yet), but still much faster than bit-banging GPIO.

5. Buttons:
- Completely separate from HSTX, just GPIO inputs with callbacks and debounce logic.



### Summary
- The code is using HSTX as a hardware-accelerated SPI replacement.
- Instead of sending data byte-by-byte through SPI, the driver encodes
  CS, DC, and MOSI states into HSTX words and streams them out.
- This makes the display driver faster and more flexible, while leaving
  the RP2350’s regular SPI peripherals free for other tasks.

So, it’s a clean example of why HSTX exists: offloading "fast serial output"
that would normally burn CPU or PIO resources.

