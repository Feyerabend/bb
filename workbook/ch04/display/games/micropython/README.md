
## ..

### Pimoroni Pico Display Pack 2.0

The *Pico Display Pack 2.0* is a compact add-on board from Pimoroni designed specifically
for the Raspberry Pi Pico (or Pico W). It's essentially a "backpack" that snaps onto the
underside of your Pico, turning it into a portable display-equipped device perfect for
embedded projects, games, or interfaces. Released around mid-2024, it's an upgraded version
of the original Pico Display Pack, offering a larger, higher-resolution screen while keeping
the same easy-to-use form factor.


#### Key Features

| Feature | Details |
|---------|---------|
| *Display* | 2.0-inch (50.8mm) IPS LCD, 320 x 240 pixels (~220 PPI), 18-bit color (65K colors), wide viewing angles, and vibrant backlighting. Communicates via SPI (pins: CS, DC, SCLK, MOSI) with PWM-controlled brightness. |
| *Input/Output* | Four tactile buttons (labeled A/B/X/Y, connected to GPIO 12-15 by default) for user interaction. Includes a single RGB LED for status indicators. |
| *Compatibility* | - Raspberry Pi Pico/Pico W (requires male headers soldered on the Pico).<br>- Works with MicroPython (Pimoroni's custom UF2 build), CircuitPython (via Adafruit DisplayIO), or C/C++.<br>- Stackable with other Pico add-ons like Pico Omnibus or Pico Decker (though it may overhang slightly). |
| *Dimensions & Build* | Approx. 53mm x 25mm x 9mm (L x W x H). No soldering needed if your Pico has headers. The screen protrudes slightly above the buttons, so use gentle fingertip presses to avoid accidental touches. |
| *Power* | Draws from the Pico (3.3V logic), low power for battery projects. |


#### What's New vs. Original Pico Display Pack?

- *Bigger Screen*: Original is 1.14-inch at 240x135; 2.0 is double the diagonal and resolution
  for sharper graphics and more real estate.
- *Code Migration*: Super simple— in MicroPython, swap `import picodisplay` to `import picodisplay2`
  or use `DISPLAY_PICO_DISPLAY_2` constant.
- Same button layout and RGB LED, but more space for custom Pico projects (e.g., mounting on larger bases).



#### Getting Started

1. *Hardware Setup*: Buy a Pico with headers (or solder your own). Snap the pack onto the Pico's
   underside—pins align automatically.

2. *Software*:
   - *MicroPython*: Flash Pimoroni's custom UF2 from their GitHub (includes `picographics` library).
     Example code for basics:
     ```python
     import picodisplay2 as picodisplay
     import time

     display = picodisplay.PicoDisplay2()
     display.set_backlight(1.0)  # Full brightness

     while True:
         display.set_pen(picodisplay.WHITE)
         display.clear()
         display.text("Hello, Pico Display 2.0!", 10, 100, scale=2)
         display.update()
         time.sleep(1)
     ```
     Tutorials and full examples are on Pimoroni's site.
   - *CircuitPython*: Use Adafruit's bundle; look for the ST7789 driver example.

3. *Projects Ideas*: Retro games (like the Atari-style tank combat I coded
   earlier--just update the display init to `DISPLAY_PICO_DISPLAY_2` and scale
   graphics to 320x240), sensors dashboards, portable music players,
   or even a mini weather station.

Upgrade is trivial from the original to the newer: Change `DISPLAY_PICO_DISPLAY_PACK`
to `DISPLAY_PICO_DISPLAY_2`, bump WIDTH/HEIGHT to 320/240, and adjust coordinates/scaling.

