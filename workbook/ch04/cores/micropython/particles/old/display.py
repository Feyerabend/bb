# Ported to MicroPython from display.c .. untested
import machine
import time
import framebuf
import utime

# Display Pack 2.0 specifications
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

# Colors (RGB565 format)
COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_YELLOW = 0xFFE0
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F

# Button definitions
BUTTON_A = 0
BUTTON_B = 1
BUTTON_X = 2
BUTTON_Y = 3
BUTTON_COUNT = 4

# Error codes
DISPLAY_OK = 0
DISPLAY_ERROR_INIT_FAILED = 1
DISPLAY_ERROR_INVALID_PARAM = 2
DISPLAY_ERROR_NOT_INITIALIZED = 3

# Display Pack pin defs
DISPLAY_CS_PIN = 17
DISPLAY_CLK_PIN = 18
DISPLAY_MOSI_PIN = 19
DISPLAY_DC_PIN = 16
DISPLAY_RESET_PIN = 21
DISPLAY_BL_PIN = 20

# Button pins
BUTTON_A_PIN = 12
BUTTON_B_PIN = 13
BUTTON_X_PIN = 14
BUTTON_Y_PIN = 15

# Fixed 5x8 font (from display.c)
font5x8 = [
    [0x00, 0x00, 0x00, 0x00, 0x00], [0x00, 0x00, 0x5F, 0x00, 0x00],
    [0x00, 0x07, 0x00, 0x07, 0x00], [0x14, 0x7F, 0x14, 0x7F, 0x14],
    [0x12, 0x2A, 0x7F, 0x2A, 0x24], [0x62, 0x64, 0x08, 0x13, 0x23],
    [0x50, 0x22, 0x55, 0x49, 0x36], [0x00, 0x00, 0x07, 0x00, 0x00],
    [0x00, 0x41, 0x22, 0x1C, 0x00], [0x00, 0x1C, 0x22, 0x41, 0x00],
    [0x14, 0x08, 0x3E, 0x08, 0x14], [0x08, 0x08, 0x3E, 0x08, 0x08],
    [0x00, 0x30, 0x50, 0x00, 0x00], [0x08, 0x08, 0x08, 0x08, 0x08],
    [0x00, 0x60, 0x60, 0x00, 0x00], [0x02, 0x04, 0x08, 0x10, 0x20],
    [0x3E, 0x45, 0x49, 0x51, 0x3E], [0x00, 0x40, 0x7F, 0x42, 0x00],
    [0x46, 0x49, 0x51, 0x61, 0x42], [0x31, 0x4B, 0x45, 0x41, 0x21],
    [0x10, 0x7F, 0x12, 0x14, 0x18], [0x39, 0x49, 0x49, 0x49, 0x2F],
    [0x30, 0x49, 0x49, 0x4A, 0x3C], [0x07, 0x0D, 0x09, 0x71, 0x01],
    [0x36, 0x49, 0x49, 0x49, 0x36], [0x1E, 0x29, 0x49, 0x49, 0x0E],
    [0x00, 0x36, 0x36, 0x00, 0x00], [0x00, 0x36, 0x76, 0x00, 0x00],
    [0x00, 0x41, 0x22, 0x14, 0x08], [0x14, 0x14, 0x14, 0x14, 0x14],
    [0x08, 0x14, 0x22, 0x41, 0x00], [0x06, 0x09, 0x51, 0x01, 0x06],
    [0x3E, 0x41, 0x79, 0x49, 0x32], [0x7E, 0x11, 0x11, 0x11, 0x7E],
    [0x36, 0x49, 0x49, 0x49, 0x7F], [0x22, 0x41, 0x41, 0x41, 0x3E],
    [0x1C, 0x22, 0x41, 0x41, 0x7F], [0x41, 0x49, 0x49, 0x49, 0x7F],
    [0x01, 0x09, 0x09, 0x09, 0x7F], [0x7A, 0x49, 0x49, 0x41, 0x3E],
    [0x7F, 0x08, 0x08, 0x08, 0x7F], [0x00, 0x41, 0x7F, 0x41, 0x00],
    [0x01, 0x3F, 0x41, 0x40, 0x20], [0x41, 0x22, 0x14, 0x08, 0x7F],
    [0x40, 0x40, 0x40, 0x40, 0x7F], [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    [0x7F, 0x10, 0x0C, 0x02, 0x7F], [0x3E, 0x41, 0x41, 0x41, 0x3E],
    [0x06, 0x09, 0x09, 0x09, 0x7F], [0x5E, 0x21, 0x51, 0x41, 0x3E],
    [0x46, 0x29, 0x19, 0x09, 0x7F], [0x31, 0x49, 0x49, 0x49, 0x46],
    [0x01, 0x01, 0x7F, 0x01, 0x01], [0x3F, 0x40, 0x40, 0x40, 0x3F],
    [0x1F, 0x20, 0x40, 0x20, 0x1F], [0x3F, 0x40, 0x38, 0x40, 0x3F],
    [0x63, 0x14, 0x08, 0x14, 0x63], [0x07, 0x08, 0x70, 0x08, 0x07],
    [0x43, 0x45, 0x49, 0x51, 0x61]
]

# Error strings
error_strings = ["OK", "Init failed", "Invalid parameter", "Display not initialized"]

# Internal state
_display_initialized = False
_buttons_initialized = False
_button_state = [True] * BUTTON_COUNT  # Pulled high = True
_button_last_state = [True] * BUTTON_COUNT
_button_callbacks = [None] * BUTTON_COUNT
_last_button_check = 0
_button_pins = [BUTTON_A_PIN, BUTTON_B_PIN, BUTTON_X_PIN, BUTTON_Y_PIN]

# Framebuffer
_framebuffer = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT * 2)
_fb = framebuf.FrameBuffer(_framebuffer, DISPLAY_WIDTH, DISPLAY_HEIGHT, framebuf.RGB565)

# SPI and GPIO setup
_spi = None
_cs = None
_dc = None
_reset = None
_bl = None
_buttons = None

def get_time_ms():
    return utime.ticks_ms()

def display_pack_init():
    global _display_initialized, _spi, _cs, _dc, _reset, _bl
    if _display_initialized:
        return DISPLAY_OK

    try:
        # SPI setup
        _spi = machine.SPI(0, baudrate=31250000, polarity=0, phase=0,
                          sck=machine.Pin(DISPLAY_CLK_PIN), mosi=machine.Pin(DISPLAY_MOSI_PIN))
        _cs = machine.Pin(DISPLAY_CS_PIN, machine.Pin.OUT, value=1)
        _dc = machine.Pin(DISPLAY_DC_PIN, machine.Pin.OUT, value=1)
        _reset = machine.Pin(DISPLAY_RESET_PIN, machine.Pin.OUT, value=1)
        _bl = machine.Pin(DISPLAY_BL_PIN, machine.Pin.OUT, value=0)

        # Reset sequence
        _reset.value(1)
        time.sleep_ms(10)
        _reset.value(0)
        time.sleep_ms(10)
        _reset.value(1)
        time.sleep_ms(120)

        # ST7789 initialization sequence (from display.c)
        def write_cmd(cmd):
            _dc.value(0)
            _cs.value(0)
            _spi.write(bytes([cmd]))
            _cs.value(1)

        def write_data(data):
            _dc.value(1)
            _cs.value(0)
            _spi.write(bytes(data) if isinstance(data, list) else bytes([data]))
            _cs.value(1)

        write_cmd(0x01)  # Software reset
        time.sleep_ms(150)
        write_cmd(0x11)  # Sleep out
        time.sleep_ms(120)
        write_cmd(0x3A)
        write_data(0x55)  # Pixel format: RGB565
        write_cmd(0x36)
        write_data(0x70)  # Memory access control
        write_cmd(0x2A)
        write_data([0x00, 0x00, 0x01, 0x3F])  # Column address
        write_cmd(0x2B)
        write_data([0x00, 0x00, 0x00, 0xEF])  # Row address
        write_cmd(0xB2)
        write_data([0x0C, 0x0C, 0x00, 0x33, 0x33])
        write_cmd(0xB7)
        write_data(0x35)
        write_cmd(0xBB)
        write_data(0x19)
        write_cmd(0xC0)
        write_data(0x2C)
        write_cmd(0xC2)
        write_data(0x01)
        write_cmd(0xC3)
        write_data(0x12)
        write_cmd(0xC4)
        write_data(0x20)
        write_cmd(0xC6)
        write_data(0x0F)
        write_cmd(0xD0)
        write_data([0xA4, 0xA1])
        write_cmd(0xE0)
        write_data([0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54, 0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23])
        write_cmd(0xE1)
        write_data([0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44, 0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23])
        write_cmd(0x21)  # Display inversion
        write_cmd(0x13)  # Normal display
        time.sleep_ms(10)
        write_cmd(0x29)  # Display on
        time.sleep_ms(100)

        _bl.value(1)  # Backlight on
        _display_initialized = True
        return DISPLAY_OK
    except Exception:
        _display_initialized = False
        return DISPLAY_ERROR_INIT_FAILED

def display_set_window(x0, y0, x1, y1):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    try:
        _dc.value(0)
        _cs.value(0)
        _spi.write(b'\x2A')
        _cs.value(1)
        _dc.value(1)
        _cs.value(0)
        _spi.write(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        _cs.value(1)

        _dc.value(0)
        _cs.value(0)
        _spi.write(b'\x2B')
        _cs.value(1)
        _dc.value(1)
        _cs.value(0)
        _spi.write(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        _cs.value(1)

        _dc.value(0)
        _cs.value(0)
        _spi.write(b'\x2C')
        _cs.value(1)
        return DISPLAY_OK
    except Exception:
        return DISPLAY_ERROR_INVALID_PARAM

def display_clear(color):
    return display_fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color)

def display_fill_rect(x, y, width, height, color):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    if x >= DISPLAY_WIDTH or y >= DISPLAY_HEIGHT:
        return DISPLAY_ERROR_INVALID_PARAM
    if x + width > DISPLAY_WIDTH:
        width = DISPLAY_WIDTH - x
    if y + height > DISPLAY_HEIGHT:
        height = DISPLAY_HEIGHT - y
    if width == 0 or height == 0:
        return DISPLAY_OK

    try:
        # Update framebuffer
        _fb.fill_rect(x, y, width, height, color)
        # Blit to display
        result = display_set_window(x, y, x + width - 1, y + height - 1)
        if result != DISPLAY_OK:
            return result
        _dc.value(1)
        _cs.value(0)
        pixel_count = width * height
        color_bytes = bytes([color >> 8, color & 0xFF])
        # Write in chunks to avoid memory issues
        chunk_size = 4096  # 2KB at a time
        for _ in range(0, pixel_count, chunk_size // 2):
            count = min(chunk_size // 2, pixel_count)
            _spi.write(color_bytes * count)
            pixel_count -= count
        _cs.value(1)
        return DISPLAY_OK
    except Exception:
        return DISPLAY_ERROR_INVALID_PARAM

def display_draw_pixel(x, y, color):
    if x >= DISPLAY_WIDTH or y >= DISPLAY_HEIGHT:
        return DISPLAY_ERROR_INVALID_PARAM
    return display_fill_rect(x, y, 1, 1, color)

def display_blit_full(pixels):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    if not pixels:
        return DISPLAY_ERROR_INVALID_PARAM

    try:
        # Update framebuffer
        _fb.blit(framebuf.FrameBuffer(pixels, DISPLAY_WIDTH, DISPLAY_HEIGHT, framebuf.RGB565), 0, 0)
        # Blit to display
        result = display_set_window(0, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1)
        if result != DISPLAY_OK:
            return result
        _dc.value(1)
        _cs.value(0)
        total_bytes = DISPLAY_WIDTH * DISPLAY_HEIGHT * 2
        chunk_size = 32768  # 16K pixels
        offset = 0
        while offset < total_bytes:
            bytes_to_send = min(chunk_size, total_bytes - offset)
            _spi.write(pixels[offset:offset + bytes_to_send])
            offset += bytes_to_send
        _cs.value(1)
        return DISPLAY_OK
    except Exception:
        return DISPLAY_ERROR_INVALID_PARAM

def display_draw_char(x, y, c, color, bg_color):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    if x >= DISPLAY_WIDTH or y >= DISPLAY_HEIGHT:
        return DISPLAY_ERROR_INVALID_PARAM
    if ord(c) < 32 or ord(c) > 90:
        c = chr(32)

    char_data = font5x8[ord(c) - 32]
    for col in range(5):
        if x + col >= DISPLAY_WIDTH:
            break
        line = char_data[4 - col]
        for row in range(8):
            if y + row >= DISPLAY_HEIGHT:
                break
            pixel_color = color if (line & (1 << row)) else bg_color
            result = display_draw_pixel(x + col, y + row, pixel_color)
            if result != DISPLAY_OK:
                return result
    return DISPLAY_OK

def display_draw_string(x, y, s, color, bg_color):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    if not s:
        return DISPLAY_ERROR_INVALID_PARAM
    if x >= DISPLAY_WIDTH or y >= DISPLAY_HEIGHT:
        return DISPLAY_ERROR_INVALID_PARAM

    offset_x = 0
    for c in s:
        if x + offset_x >= DISPLAY_WIDTH:
            break
        result = display_draw_char(x + offset_x, y, c, color, bg_color)
        if result != DISPLAY_OK:
            return result
        offset_x += 6
    return DISPLAY_OK

def display_set_backlight(on):
    if not _display_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    _bl.value(1 if on else 0)
    return DISPLAY_OK

def buttons_init():
    global _buttons_initialized, _buttons
    if _buttons_initialized:
        return DISPLAY_OK

    try:
        _buttons = [
            machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
            for pin in _button_pins
        ]
        global _button_state, _button_last_state, _button_callbacks
        _button_state = [True] * BUTTON_COUNT
        _button_last_state = [True] * BUTTON_COUNT
        _button_callbacks = [None] * BUTTON_COUNT
        _buttons_initialized = True
        return DISPLAY_OK
    except Exception:
        return DISPLAY_ERROR_INIT_FAILED

def buttons_update():
    global _last_button_check
    if not _buttons_initialized:
        return
    now = get_time_ms()
    if now - _last_button_check < 50:
        return
    _last_button_check = now

    for i in range(BUTTON_COUNT):
        _button_last_state[i] = _button_state[i]
        _button_state[i] = _buttons[i].value()
        if _button_last_state[i] and not _button_state[i] and _button_callbacks[i]:
            _button_callbacks[i](i)

def button_pressed(button):
    if not _buttons_initialized or button >= BUTTON_COUNT:
        return False
    return not _button_state[button]

def button_just_pressed(button):
    if not _buttons_initialized or button >= BUTTON_COUNT:
        return False
    return _button_last_state[button] and not _button_state[button]

def button_just_released(button):
    if not _buttons_initialized or button >= BUTTON_COUNT:
        return False
    return not _button_last_state[button] and _button_state[button]

def button_set_callback(button, callback):
    if not _buttons_initialized:
        return DISPLAY_ERROR_NOT_INITIALIZED
    if button >= BUTTON_COUNT:
        return DISPLAY_ERROR_INVALID_PARAM
    _button_callbacks[button] = callback
    return DISPLAY_OK

def display_is_initialized():
    return _display_initialized

def display_error_string(error):
    if error < 0 or error >= len(error_strings):
        return "Unknown error"
    return error_strings[error]

def display_cleanup():
    global _display_initialized, _buttons_initialized
    if _display_initialized:
        _spi.deinit()
        _bl.value(0)
        _display_initialized = False
    _buttons_initialized = False
    global _button_callbacks
    _button_callbacks = [None] * BUTTON_COUNT