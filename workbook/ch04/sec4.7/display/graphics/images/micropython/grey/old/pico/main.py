import machine
import framebuf
import time

# === HARDWARE SETUP ===
spi = machine.SPI(0,
                  baudrate=60_000_000,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19))
cs  = machine.Pin(17, machine.Pin.OUT)
dc  = machine.Pin(16, machine.Pin.OUT)
rst = machine.Pin(20, machine.Pin.OUT)
bl  = machine.Pin(21, machine.Pin.OUT)
bl.value(1)  # Backlight on

WIDTH, HEIGHT = 320, 240

# === LOW-LEVEL SPI HELPERS ===
def write_cmd(cmd, data=None):
    cs.value(0)
    dc.value(0)
    spi.write(bytearray([cmd]))
    if data is not None:
        dc.value(1)
        spi.write(data)
    cs.value(1)

def set_window(x0=0, y0=0, x1=WIDTH-1, y1=HEIGHT-1):
    write_cmd(0x2A, bytearray([x0>>8, x0&0xFF, x1>>8, x1&0xFF]))
    write_cmd(0x2B, bytearray([y0>>8, y0&0xFF, y1>>8, y1&0xFF]))
    write_cmd(0x2C)  # RAMWR - ready for pixel data

# === DISPLAY INIT ===
def st7789_init():
    rst.value(0); time.sleep_ms(100)
    rst.value(1); time.sleep_ms(100)

    write_cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    write_cmd(0x36, b'\x00')  # MADCTL: portrait
    write_cmd(0x3A, b'\x05')  # 16-bit color
    write_cmd(0x21)          # Inversion on (optional)
    write_cmd(0x29)          # Display on
    time.sleep_ms(120)

# === PPM P5 LOADER (ROBUST) ===
def load_ppm_p5(filename):
    with open(filename, 'rb') as f:
        if f.read(2) != b'P5':
            raise ValueError("Not a P5 PPM file")

        # Skip comments and whitespace
        def read_token():
            token = b''
            while True:
                c = f.read(1)
                if not c:
                    raise EOFError("Unexpected end of file")
                if c in b' \t\n\r':
                    if token: return token
                elif c == b'#':
                    f.readline()  # skip comment
                else:
                    token += c

        w = int(read_token())
        h = int(read_token())
        maxval = int(read_token())

        if maxval != 255:
            raise ValueError("Only 8-bit (maxval 255) supported")

        pixels = f.read(w * h)
        if len(pixels) != w * h:
            raise ValueError("Image data truncated")

    # Create framebuffer
    fb = framebuf.FrameBuffer(bytearray(w * h * 2), w, h, framebuf.RGB565)

    for i in range(w * h):
        gray = pixels[i]
        # Convert 8-bit gray → 16-bit RGB565
        color = ((gray & 0xF8) << 8) | ((gray & 0xFC) << 3) | (gray >> 3)
        x = i % w
        y = i // w
        fb.pixel(x, y, color)

    return fb

# === MAIN ===
st7789_init()
print("Display initialized")

try:
    print("Loading /image.ppm...")
    fb = load_ppm_p5('/image.ppm')
    print(f"Loaded {fb.width()}x{fb.height()} grayscale image")
except Exception as e:
    print("Failed to load image:", e)
    raise

# === DISPLAY IMAGE ===
cs.value(0)
set_window()
dc.value(1)
spi.write(fb.buffer)
cs.value(1)

print("Image displayed!")

# Keep running
while True:
    time.sleep(1)