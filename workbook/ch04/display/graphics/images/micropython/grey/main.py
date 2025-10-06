import machine
import framebuf
import time

# Pins for Pimoroni Display Pack 2.0 (ST7789 SPI)
spi = machine.SPI(0, baudrate=60000000, sck=machine.Pin(18), mosi=machine.Pin(19))
cs = machine.Pin(17, machine.Pin.OUT)
dc = machine.Pin(16, machine.Pin.OUT)
rst = machine.Pin(20, machine.Pin.OUT)
bl = machine.Pin(21, machine.Pin.OUT)
bl.value(1)  # Backlight on

# ST7789 init sequence
def st7789_init():
    rst.value(0); time.sleep_ms(100); rst.value(1); time.sleep_ms(100)
    def cmd(c, d=None):
        dc.value(0); spi.write(bytearray([c]))
        if d: dc.value(1); spi.write(bytearray(d))
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    cmd(0x36, b'\x00')  # Memory access control (landscape)
    cmd(0x3A, b'\x05')  # Pixel format 16-bit RGB565
    cmd(0x21)  # Inversion on
    cmd(0x29)  # Display on
    time.sleep_ms(120)

# Set window for full screen
def set_window(x0=0, y0=0, x1=319, y1=239):
    dc.value(0); spi.write(bytearray([0x2A]))
    dc.value(1); spi.write(bytearray([x0>>8, x0&0xFF, x1>>8, x1&0xFF]))
    dc.value(0); spi.write(bytearray([0x2B]))
    dc.value(1); spi.write(bytearray([y0>>8, y0&0xFF, y1>>8, y1&0xFF]))
    dc.value(0); spi.write(bytearray([0x2C]))

# Load and display PPM P5
def load_ppm(filename):
    with open(filename, 'rb') as f:
        if f.read(2) != b'P5':
            raise ValueError("Not P5 PPM")
        # Skip whitespace/comments to width/height
        line = b''
        while b' ' not in line: line = f.readline()
        w, h = map(int, line.split())
        # Read maxval
        maxval = int(f.readline())
        if maxval != 255:
            raise ValueError("Not 8-bit")
        # Read raw bytes
        pixels = f.read(w * h)
    
    # Create framebuf (RGB565)
    fb = framebuf.FrameBuffer(bytearray(w * h * 2), w, h, framebuf.RGB565)
    for i in range(w * h):
        gray = pixels[i]
        color = ((gray & 0xF8) << 8) | ((gray & 0xFC) << 3) | (gray >> 3)  # RGB565 grayscale
        fb.pixel(i % w, i // w, color)
    
    return fb

# Main
st7789_init()
fb = load_ppm('/image.ppm')  # Adjust path if needed

cs.value(0)
set_window()
dc.value(1)
spi.write(fb.buffer)
cs.value(1)

while True:
    time.sleep(1)  # Keep alive
