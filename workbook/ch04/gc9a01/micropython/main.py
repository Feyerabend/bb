"""
GC9A01 Display Driver for Raspberry Pi Pico / Pico W
240x240 Round LCD Display Driver with Hardware SPI
DIAGNOSTIC VERSION - Testing window settings and rotation
"""

from machine import Pin, SPI
from micropython import const
import framebuf
import time

# GC9A01 Commands
_SWRESET = const(0x01)
_SLPOUT  = const(0x11)
_INVOFF  = const(0x20)
_INVON   = const(0x21)
_DISPOFF = const(0x28)
_DISPON  = const(0x29)
_CASET   = const(0x2A)
_RASET   = const(0x2B)
_RAMWR   = const(0x2C)
_MADCTL  = const(0x36)
_COLMOD  = const(0x3A)
_TEON    = const(0x35)

# MADCTL bits
_MADCTL_MH  = const(0x04)
_MADCTL_RGB = const(0x00)
_MADCTL_BGR = const(0x08)
_MADCTL_ML  = const(0x10)
_MADCTL_MV  = const(0x20)
_MADCTL_MX  = const(0x40)
_MADCTL_MY  = const(0x80)


class GC9A01:
    def __init__(self, spi, dc, cs, rst=None, bl=None,
                 width=240, height=240, rotation=0):

        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.bl = bl
        self.width = width
        self.height = height

        # Configure pins
        self.dc.init(Pin.OUT, value=0)
        self.cs.init(Pin.OUT, value=1)

        if self.rst:
            self.rst.init(Pin.OUT, value=1)

        if self.bl:
            self.bl.init(Pin.OUT, value=1)

        # Framebuffer
        self.buffer = bytearray(width * height * 2)
        self.fbuf = framebuf.FrameBuffer(
            self.buffer, width, height, framebuf.RGB565
        )

        self._init_display()
        self.set_rotation(rotation)

    def _write_cmd(self, cmd):
        self.cs(0)
        self.dc(0)
        time.sleep_us(1)
        self.spi.write(bytearray([cmd]))
        time.sleep_us(1)
        self.cs(1)

    def _write_data(self, data):
        self.cs(0)
        self.dc(1)
        time.sleep_us(1)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        time.sleep_us(1)
        self.cs(1)

    def _init_display(self):
        if self.rst:
            self.rst(1)
            time.sleep_ms(10)
            self.rst(0)
            time.sleep_ms(50)
            self.rst(1)
            time.sleep_ms(150)

        self._write_cmd(_SWRESET)
        time.sleep_ms(150)

        # Inter Register Enable
        self._write_cmd(0xFE)
        self._write_cmd(0xEF)

        self._write_cmd(0xEB)
        self._write_data(0x14)

        self._write_cmd(0x84)
        self._write_data(0x40)

        self._write_cmd(0x85)
        self._write_data(0xFF)

        self._write_cmd(0x86)
        self._write_data(0xFF)

        self._write_cmd(0x87)
        self._write_data(0xFF)

        self._write_cmd(0x88)
        self._write_data(0x0A)

        self._write_cmd(0x89)
        self._write_data(0x21)

        self._write_cmd(0x8A)
        self._write_data(0x00)

        self._write_cmd(0x8B)
        self._write_data(0x80)

        self._write_cmd(0x8C)
        self._write_data(0x01)

        self._write_cmd(0x8D)
        self._write_data(0x01)

        self._write_cmd(0x8E)
        self._write_data(0xFF)

        self._write_cmd(0x8F)
        self._write_data(0xFF)

        self._write_cmd(0xB6)
        self._write_data(0x00)
        self._write_data(0x20)

        # Pixel Format Set - 16bit/pixel
        self._write_cmd(_COLMOD)
        self._write_data(0x05)

        # Gamma settings
        self._write_cmd(0xF0)
        self._write_data(bytearray([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]))

        self._write_cmd(0xF1)
        self._write_data(bytearray([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]))

        self._write_cmd(0xF2)
        self._write_data(bytearray([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]))

        self._write_cmd(0xF3)
        self._write_data(bytearray([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]))

        self._write_cmd(_TEON)
        self._write_data(0x00)

        self._write_cmd(_SLPOUT)
        time.sleep_ms(150)

        self._write_cmd(_INVON)
        time.sleep_ms(10)

        self._write_cmd(_DISPON)
        time.sleep_ms(50)

    def set_rotation(self, rotation):
        rotation %= 4
        self._write_cmd(_MADCTL)

        if rotation == 0:
            self._write_data(_MADCTL_MX | _MADCTL_BGR)
        elif rotation == 1:
            self._write_data(_MADCTL_MV | _MADCTL_BGR)
        elif rotation == 2:
            self._write_data(_MADCTL_MY | _MADCTL_BGR)
        elif rotation == 3:
            self._write_data(_MADCTL_MX | _MADCTL_MY | _MADCTL_MV | _MADCTL_BGR)

    def set_window(self, x0, y0, x1, y1):
        self._write_cmd(_CASET)
        self._write_data(bytearray([x0 >> 8, x0 & 0xFF,
                                    x1 >> 8, x1 & 0xFF]))

        self._write_cmd(_RASET)
        self._write_data(bytearray([y0 >> 8, y0 & 0xFF,
                                    y1 >> 8, y1 & 0xFF]))

    def show(self):
        """Send framebuffer to display"""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Send RAMWR command
        self.cs(0)
        self.dc(0)
        time.sleep_us(1)
        self.spi.write(bytearray([_RAMWR]))
        self.cs(1)
        time.sleep_us(1)
        
        # Send pixel data
        self.cs(0)
        self.dc(1)
        time.sleep_us(1)
        
        chunk_size = 4096
        for i in range(0, len(self.buffer), chunk_size):
            self.spi.write(self.buffer[i:i+chunk_size])
        
        self.cs(1)

    def fill(self, color):
        self.fbuf.fill(color)

    def pixel(self, x, y, color):
        self.fbuf.pixel(x, y, color)

    def hline(self, x, y, w, color):
        self.fbuf.hline(x, y, w, color)

    def vline(self, x, y, h, color):
        self.fbuf.vline(x, y, h, color)

    def line(self, x0, y0, x1, y1, color):
        self.fbuf.line(x0, y0, x1, y1, color)

    def rect(self, x, y, w, h, color):
        self.fbuf.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color):
        self.fbuf.fill_rect(x, y, w, h, color)

    def text(self, text, x, y, color):
        self.fbuf.text(text, x, y, color)

    def backlight(self, state):
        if self.bl:
            self.bl(state)

    def invert(self, state):
        self._write_cmd(_INVON if state else _INVOFF)

    def power(self, state):
        self._write_cmd(_DISPON if state else _DISPOFF)

    @staticmethod
    def rgb(r, g, b):
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def fill_circle(self, x, y, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(x - dx, y + dy, 2 * dx + 1, color)
    
    def draw_rect_direct(self, x, y, w, h, color):
        """Draw rectangle by directly setting window and writing color"""
        self.set_window(x, y, x + w - 1, y + h - 1)
        
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([_RAMWR]))
        self.cs(1)
        
        # Create color bytes
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF
        pixel_data = bytearray([color_high, color_low])
        
        self.cs(0)
        self.dc(1)
        for _ in range(w * h):
            self.spi.write(pixel_data)
        self.cs(1)


def diagnostic_test():
    print("=== GC9A01 DIAGNOSTIC TEST ===")
    
    spi = SPI(
        0,
        baudrate=10_000_000,
        polarity=0,
        phase=0,
        sck=Pin(2),
        mosi=Pin(3)
    )

    display = GC9A01(
        spi,
        dc=Pin(4),
        cs=Pin(5),
        rst=Pin(6),
        bl=None
    )

    RED     = 0xF800
    GREEN   = 0x07E0
    BLUE    = 0x001F
    WHITE   = 0xFFFF
    BLACK   = 0x0000

    print("\n1. Testing DIRECT rectangle draw (bypassing framebuffer)")
    print("Drawing RED rectangle at top-left corner (0,0,50,50)")
    display.draw_rect_direct(0, 0, 50, 50, RED)
    time.sleep(3)
    
    print("Drawing GREEN rectangle at (50,50,50,50)")
    display.draw_rect_direct(50, 50, 50, 50, GREEN)
    time.sleep(3)
    
    print("Drawing BLUE rectangle at (100,100,50,50)")
    display.draw_rect_direct(100, 100, 50, 50, BLUE)
    time.sleep(3)
    
    print("Drawing WHITE rectangle at center (95,95,50,50)")
    display.draw_rect_direct(95, 95, 50, 50, WHITE)
    time.sleep(3)
    
    print("\n2. Testing full screen colors with DIRECT draw")
    print("Full RED screen")
    display.draw_rect_direct(0, 0, 240, 240, RED)
    time.sleep(2)
    
    print("Full GREEN screen")
    display.draw_rect_direct(0, 0, 240, 240, GREEN)
    time.sleep(2)
    
    print("Full BLUE screen")
    display.draw_rect_direct(0, 0, 240, 240, BLUE)
    time.sleep(2)
    
    print("\n3. Testing with framebuffer")
    display.fill(BLACK)
    display.fill_rect(10, 10, 50, 50, RED)
    display.fill_rect(80, 80, 50, 50, GREEN)
    display.fill_rect(150, 150, 50, 50, BLUE)
    display.show()
    time.sleep(3)
    
    print("\n4. Testing different rotations")
    for rot in range(4):
        print(f"Rotation {rot}")
        display.set_rotation(rot)
        display.draw_rect_direct(0, 0, 50, 50, RED)
        display.draw_rect_direct(190, 0, 50, 50, GREEN)
        display.draw_rect_direct(0, 190, 50, 50, BLUE)
        display.draw_rect_direct(190, 190, 50, 50, WHITE)
        time.sleep(3)
    
    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    diagnostic_test()
