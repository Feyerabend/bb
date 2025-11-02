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

# Button pins (Display Pack 2.0)
btn_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
btn_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
btn_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
btn_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Display dimensions
WIDTH = 320
HEIGHT = 240

# ST7789 init sequence
def st7789_init():
    rst.value(0); time.sleep_ms(100); rst.value(1); time.sleep_ms(100)
    def cmd(c, d=None):
        dc.value(0); cs.value(0); spi.write(bytearray([c]))
        if d: dc.value(1); spi.write(bytearray(d))
        cs.value(1)
    cmd(0x11)  # Sleep out
    time.sleep_ms(120)
    cmd(0x36, b'\x00')  # Memory access control
    cmd(0x3A, b'\x05')  # Pixel format 16-bit RGB565
    cmd(0x21)  # Inversion on
    cmd(0x29)  # Display on
    time.sleep_ms(120)

# Set window for full screen
def set_window(x0=0, y0=0, x1=319, y1=239):
    dc.value(0); cs.value(0)
    spi.write(bytearray([0x2A]))
    dc.value(1); spi.write(bytearray([x0>>8, x0&0xFF, x1>>8, x1&0xFF]))
    dc.value(0); spi.write(bytearray([0x2B]))
    dc.value(1); spi.write(bytearray([y0>>8, y0&0xFF, y1>>8, y1&0xFF]))
    dc.value(0); spi.write(bytearray([0x2C]))
    dc.value(1)

# Load PPM P6 (color) image
def load_ppm(filename):
    with open(filename, 'rb') as f:
        magic = f.read(2)
        if magic not in [b'P5', b'P6']:
            raise ValueError("Not P5/P6 PPM")
        is_color = (magic == b'P6')
        
        # Skip comments and whitespace
        def read_token():
            token = b''
            while True:
                c = f.read(1)
                if c == b'#':
                    f.readline()  # Skip comment
                elif c in b' \t\n\r':
                    if token: return token
                else:
                    token += c
        
        w = int(read_token())
        h = int(read_token())
        maxval = int(read_token())
        
        if maxval != 255:
            raise ValueError("Only 8-bit supported")
        
        # Read pixel data
        bytes_per_pixel = 3 if is_color else 1
        pixel_data = f.read(w * h * bytes_per_pixel)
    
    return w, h, pixel_data, is_color

# Convert RGB888 to RGB565
def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

# Create framebuffer from pixel data
def create_framebuffer(w, h, pixel_data, is_color):
    fb = framebuf.FrameBuffer(bytearray(w * h * 2), w, h, framebuf.RGB565)
    
    if is_color:
        for y in range(h):
            for x in range(w):
                idx = (y * w + x) * 3
                r, g, b = pixel_data[idx], pixel_data[idx+1], pixel_data[idx+2]
                color = rgb888_to_rgb565(r, g, b)
                fb.pixel(x, y, color)
    else:
        for y in range(h):
            for x in range(w):
                gray = pixel_data[y * w + x]
                color = rgb888_to_rgb565(gray, gray, gray)
                fb.pixel(x, y, color)
    
    return fb

# Extract RGB channels from pixel data
def get_rgb_channels(w, h, pixel_data, is_color):
    r_ch = bytearray(w * h)
    g_ch = bytearray(w * h)
    b_ch = bytearray(w * h)
    
    if is_color:
        for i in range(w * h):
            r_ch[i] = pixel_data[i * 3]
            g_ch[i] = pixel_data[i * 3 + 1]
            b_ch[i] = pixel_data[i * 3 + 2]
    else:
        for i in range(w * h):
            gray = pixel_data[i]
            r_ch[i] = g_ch[i] = b_ch[i] = gray
    
    return r_ch, g_ch, b_ch

# Apply 3x3 convolution kernel to single channel
def convolve_channel(channel, w, h, kernel):
    result = bytearray(w * h)
    
    for y in range(h):
        for x in range(w):
            acc = 0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    px = min(max(x + kx, 0), w - 1)
                    py = min(max(y + ky, 0), h - 1)
                    acc += channel[py * w + px] * kernel[(ky + 1) * 3 + (kx + 1)]
            
            # Clamp to 0-255
            result[y * w + x] = max(0, min(255, acc))
    
    return result

# Convolution filters
FILTERS = {
    'original': [0, 0, 0, 0, 1, 0, 0, 0, 0],  # Identity
    'sharpen': [0, -1, 0, -1, 5, -1, 0, -1, 0],  # Sharpen
    'edge': [-1, -1, -1, -1, 8, -1, -1, -1, -1],  # Edge detect
    'emboss': [-2, -1, 0, -1, 1, 1, 0, 1, 2],  # Emboss
}

FILTER_NAMES = ['original', 'sharpen', 'edge', 'emboss']

# Apply filter to all channels
def apply_filter(w, h, r_ch, g_ch, b_ch, kernel):
    if kernel == FILTERS['original']:
        return r_ch, g_ch, b_ch
    
    r_out = convolve_channel(r_ch, w, h, kernel)
    g_out = convolve_channel(g_ch, w, h, kernel)
    b_out = convolve_channel(b_ch, w, h, kernel)
    
    return r_out, g_out, b_out

# Create framebuffer from RGB channels
def channels_to_framebuffer(w, h, r_ch, g_ch, b_ch):
    fb = framebuf.FrameBuffer(bytearray(w * h * 2), w, h, framebuf.RGB565)
    
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            color = rgb888_to_rgb565(r_ch[idx], g_ch[idx], b_ch[idx])
            fb.pixel(x, y, color)
    
    return fb

# Display framebuffer
def display_fb(fb):
    cs.value(0)
    set_window()
    spi.write(fb.buffer)
    cs.value(1)

# Main program
st7789_init()

# Load image
print("Loading image...")
w, h, pixel_data, is_color = load_ppm('/image.ppm')
print(f"Loaded: {w}x{h}, color={is_color}")

# Extract RGB channels
r_orig, g_orig, b_orig = get_rgb_channels(w, h, pixel_data, is_color)

# Initial display
current_filter = 0
print(f"Filter: {FILTER_NAMES[current_filter]}")
fb = create_framebuffer(w, h, pixel_data, is_color)
display_fb(fb)

# Button state tracking
btn_states = [True, True, True, True]  # Start as not pressed

print("Controls:")
print("  A: Original")
print("  B: Sharpen")
print("  X: Edge Detect")
print("  Y: Emboss")

# Main loop
while True:
    # Read buttons (active low)
    btns = [btn_a.value(), btn_b.value(), btn_x.value(), btn_y.value()]
    
    # Detect button press (transition from high to low)
    for i, (prev, curr) in enumerate(zip(btn_states, btns)):
        if prev == 1 and curr == 0:  # Button pressed
            if i != current_filter:
                current_filter = i
                filter_name = FILTER_NAMES[current_filter]
                print(f"Applying filter: {filter_name}")
                
                # Apply filter
                kernel = FILTERS[filter_name]
                r_out, g_out, b_out = apply_filter(w, h, r_orig, g_orig, b_orig, kernel)
                
                # Create and display
                fb = channels_to_framebuffer(w, h, r_out, g_out, b_out)
                display_fb(fb)
                print("Done!")
    
    btn_states = btns
    time.sleep_ms(50)  # Debounce delay
