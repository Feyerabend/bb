import time
import math
import gc
from machine import Pin, SPI
import framebuf

# Test code for Pimoroni Pico Display Pack 2.0
def test_display():
    print("Running DISPLAY_PICO_DISPLAY_2 test...")
    cs = Pin(17, Pin.OUT, value=1)
    dc = Pin(16, Pin.OUT, value=1)
    rst = Pin(15, Pin.OUT, value=1)
    bl = Pin(20, Pin.OUT, value=0)
    spi = SPI(0, baudrate=10000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19))
    
    # Optional: Lock CS low (uncomment if screen remains black)
    # cs.value(0)
    
    def write_cmd(cmd):
        dc.value(0)
        cs.value(0)
        spi.write(bytes([cmd]))
        cs.value(1)
    
    def write_data(data):
        dc.value(1)
        # cs.value(0)
        if isinstance(data, (list, tuple)):
            spi.write(bytes(data))
        else:
            spi.write(bytes([data]))
        # cs.value(1)
    
    # Reset
    rst.value(1)
    time.sleep_ms(10)
    rst.value(0)
    time.sleep_ms(10)
    rst.value(1)
    time.sleep_ms(120)
    
    # Minimal init
    write_cmd(0x01)  # SWRESET
    time.sleep_ms(150)
    write_cmd(0x11)  # SLPOUT
    time.sleep_ms(120)
    write_cmd(0x3A)  # COLMOD
    write_data(0x55)  # 16-bit RGB565
    write_cmd(0x36)  # MADCTL
    write_data(0x70)  # RGB, row/col exchange
    write_cmd(0x2A)  # CASET
    write_data([0x00, 0x00, 0x01, 0x3F])  # 0-319
    write_cmd(0x2B)  # RASET
    write_data([0x00, 0x00, 0x00, 0xEF])  # 0-239
    write_cmd(0x29)  # DISPON
    time.sleep_ms(100)
    bl.value(1)
    print("Test: Backlight on")
    
    def set_window(x0, y0, x1, y1):
        write_cmd(0x2A)
        write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        write_cmd(0x2B)
        write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        write_cmd(0x2C)
    
    def fill_rect(x, y, w, h, color):
        if x >= 320 or y >= 240 or w <= 0 or h <= 0:
            return
        if x + w > 320:
            w = 320 - x
        if y + h > 240:
            h = 240 - y
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if w <= 0 or h <= 0:
            return
        set_window(x, y, x + w - 1, y + h - 1)
        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        dc.value(1)
        # cs.value(0)
        chunk_size = 100
        pixel_chunk = bytes([color_hi, color_lo] * chunk_size)
        remaining = w * h
        while remaining > 0:
            pixels_to_send = min(chunk_size, remaining)
            if pixels_to_send == chunk_size:
                spi.write(pixel_chunk)
            else:
                spi.write(bytes([color_hi, color_lo] * pixels_to_send))
            remaining -= pixels_to_send
        # cs.value(1)
    
    # Test 1: Full-screen white
    fill_rect(0, 0, 320, 240, 0xFFFF)
    print("Test: Full-screen white drawn")
    time.sleep_ms(2000)
    
    # Test 2: Red square at (0,0)
    fill_rect(0, 0, 20, 20, 0xF800)
    print("Test: Red square at (0,0) drawn")
    time.sleep_ms(2000)
    
    print("Test complete")

# Run test
test_display()

# Original game code
class ST7789:
    def __init__(self):
        self.cs = Pin(17, Pin.OUT, value=1)
        self.dc = Pin(16, Pin.OUT, value=1)
        self.reset = Pin(15, Pin.OUT, value=1)
        self.bl = Pin(20, Pin.OUT, value=0)
        self.spi = SPI(0, baudrate=10000000, polarity=1, phase=1,
                      sck=Pin(18), mosi=Pin(19))
        self.width = 320
        self.height = 240
        # Optional: Lock CS low
        # self.cs.value(0)
        self._init_display()
        self._test_display()
        
    def _write_cmd(self, cmd):
        self.dc.value(0)
        # self.cs.value(0)
        self.spi.write(bytes([cmd]))
        # self.cs.value(1)
        
    def _write_data(self, data):
        self.dc.value(1)
        # self.cs.value(0)
        if isinstance(data, (list, tuple)):
            self.spi.write(bytes(data))
        elif isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        # self.cs.value(1)
        
    def _init_display(self):
        print("Initializing ST7789 display...")
        self.reset.value(1)
        time.sleep_ms(10)
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(120)
        self._write_cmd(0x01)
        time.sleep_ms(150)
        self._write_cmd(0x11)
        time.sleep_ms(120)
        self._write_cmd(0x3A)
        self._write_data(0x55)
        self._write_cmd(0x36)
        self._write_data(0x70)
        self._write_cmd(0x2A)
        self._write_data([0x00, 0x00, 0x01, 0x3F])
        self._write_cmd(0x2B)
        self._write_data([0x00, 0x00, 0x00, 0xEF])
        self._write_cmd(0xB2)
        self._write_data([0x0C, 0x0C, 0x00, 0x33, 0x33])
        self._write_cmd(0xB7)
        self._write_data(0x35)
        self._write_cmd(0xBB)
        self._write_data(0x19)
        self._write_cmd(0xC0)
        self._write_data(0x2C)
        self._write_cmd(0xC2)
        self._write_data(0x01)
        self._write_cmd(0xC3)
        self._write_data(0x12)
        self._write_cmd(0xC4)
        self._write_data(0x20)
        self._write_cmd(0xC6)
        self._write_data(0x0F)
        self._write_cmd(0xD0)
        self._write_data([0xA4, 0xA1])
        self._write_cmd(0xE0)
        self._write_data([0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54,
                         0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23])
        self._write_cmd(0xE1)
        self._write_data([0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44,
                         0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23])
        self._write_cmd(0x21)
        self._write_cmd(0x13)
        time.sleep_ms(10)
        self._write_cmd(0x29)
        time.sleep_ms(100)
        self.bl.value(1)
        print("Display initialized, backlight on")
        
    def _test_display(self):
        print("Testing display with colors...")
        self.clear(0xF800)
        time.sleep_ms(500)
        self.clear(0x07E0)
        time.sleep_ms(500)
        self.clear(0x001F)
        time.sleep_ms(500)
        self.clear(0xFFFF)
        print("Display test complete")
        
    def set_window(self, x0, y0, x1, y1):
        x0 = max(0, min(x0, self.width - 1))
        x1 = max(0, min(x1, self.width - 1))
        y0 = max(0, min(y0, self.height - 1))
        y1 = max(0, min(y1, self.height - 1))
        self._write_cmd(0x2A)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self._write_cmd(0x2B)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self._write_cmd(0x2C)
        
    def fill_rect(self, x, y, w, h, color):
        if x >= self.width or y >= self.height or w <= 0 or h <= 0:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if w <= 0 or h <= 0:
            return
        self.set_window(x, y, x + w - 1, y + h - 1)
        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        self.dc.value(1)
        # self.cs.value(0)
        chunk_size = 100
        pixel_chunk = bytes([color_hi, color_lo] * chunk_size)
        remaining = w * h
        while remaining > 0:
            pixels_to_send = min(chunk_size, remaining)
            if pixels_to_send == chunk_size:
                self.spi.write(pixel_chunk)
            else:
                self.spi.write(bytes([color_hi, color_lo] * pixels_to_send))
            remaining -= pixels_to_send
        # self.cs.value(1)
        
    def clear(self, color=0x0000):
        self.fill_rect(0, 0, self.width, self.height, color)
        
    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fill_rect(x, y, 1, 1, color)

class Buttons:
    def __init__(self):
        self.btn_a = Pin(12, Pin.IN, Pin.PULL_UP)
        self.btn_b = Pin(13, Pin.IN, Pin.PULL_UP)
        self.btn_x = Pin(14, Pin.IN, Pin.PULL_UP)
        self.btn_y = Pin(15, Pin.IN, Pin.PULL_UP)
        self.current_state = [False, False, False, False]
        self.last_state = [False, False, False, False]
        self.last_check = 0
        print("Buttons initialized")
        
    def update(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_check) < 20:
            return
        self.last_check = now
        self.last_state = self.current_state.copy()
        self.current_state[0] = not self.btn_a.value()
        self.current_state[1] = not self.btn_b.value()
        self.current_state[2] = not self.btn_x.value()
        self.current_state[3] = not self.btn_y.value()
        
    def is_pressed(self, button):
        return self.current_state[button]
        
    def just_pressed(self, button):
        return self.current_state[button] and not self.last_state[button]

class Mario:
    def __init__(self):
        self.x = 160
        self.y = 100
        self.x_speed = 0
        self.y_speed = 0
        self.on_ground = False
        self.facing_left = False
        self.walk_speed = 2
        self.run_speed = 4
        self.jump_speed = 8
        self.gravity = 0.5
        self.max_fall_speed = 10
        print("Mario initialized at", self.x, self.y)

class Level:
    def __init__(self):
        self.width = 50
        self.height = 15
        self.data = [0] * (self.width * self.height)
        for x in range(self.width):
            for y in range(12, 15):
                self.data[y * self.width + x] = 1
        for x in range(10, 20):
            self.data[8 * self.width + x] = 2
        for x in range(25, 35):
            self.data[6 * self.width + x] = 2
        print("Level created")
        
    def get_tile(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 0
        return self.data[y * self.width + x]
    
    def is_solid(self, x, y):
        tile_x = int(x // 16)
        tile_y = int(y // 16)
        return self.get_tile(tile_x, tile_y) > 0

class MarioGame:
    def __init__(self):
        print("Initializing Mario Game...")
        self.display = ST7789()
        self.buttons = Buttons()
        self.mario = Mario()
        self.level = Level()
        self.camera_x = 0
        self.SKY_COLOR = 0x87CEEB
        self.GROUND_COLOR = 0x8B4513
        self.PLATFORM_COLOR = 0xA0522D
        self.MARIO_COLOR = 0xF800
        print("Game initialized!")
        
    def update_mario(self):
        if self.buttons.is_pressed(0):
            speed = -self.mario.run_speed if self.buttons.is_pressed(3) else -self.mario.walk_speed
            self.mario.x_speed = speed
            self.mario.facing_left = True
        elif self.buttons.is_pressed(1):
            speed = self.mario.run_speed if self.buttons.is_pressed(3) else self.mario.walk_speed
            self.mario.x_speed = speed
            self.mario.facing_left = False
        else:
            self.mario.x_speed = 0
        if self.buttons.just_pressed(2) and self.mario.on_ground:
            self.mario.y_speed = -self.mario.jump_speed
            self.mario.on_ground = False
        if not self.mario.on_ground:
            self.mario.y_speed += self.mario.gravity
            if self.mario.y_speed > self.mario.max_fall_speed:
                self.mario.y_speed = self.mario.max_fall_speed
        self.mario.x += self.mario.x_speed
        self.mario.y += self.mario.y_speed
        if self.mario.y > 180:
            self.mario.y = 180
            self.mario.y_speed = 0
            self.mario.on_ground = True
        else:
            self.mario.on_ground = False
        self.mario.x = max(8, min(self.mario.x, self.level.width * 16 - 8))
        target_camera = self.mario.x - 160
        self.camera_x += (target_camera - self.camera_x) * 0.1
        self.camera_x = max(0, min(self.camera_x, self.level.width * 16 - 320))
        
    def render(self):
        self.display.clear(self.SKY_COLOR)
        self.display.fill_rect(0, 192, 320, 48, self.GROUND_COLOR)
        start_tile = max(0, int(self.camera_x // 16))
        end_tile = min(self.level.width, start_tile + 21)
        for tile_x in range(start_tile, end_tile):
            for tile_y in range(self.level.height):
                tile = self.get_tile(tile_x, tile_y)
                if tile > 0:
                    screen_x = int(tile_x * 16 - self.camera_x)
                    screen_y = tile_y * 16
                    color = self.GROUND_COLOR if tile == 1 else self.PLATFORM_COLOR
                    self.display.fill_rect(screen_x, screen_y, 16, 16, color)
        mario_screen_x = int(self.mario.x - self.camera_x - 8)
        mario_screen_y = int(self.mario.y - 8)
        self.display.fill_rect(mario_screen_x, mario_screen_y, 16, 16, self.MARIO_COLOR)
        self.display.fill_rect(0, 0, 100, 20, 0x0000)
        
    def run(self):
        print("Starting game loop...")
        frame_count = 0
        while True:
            try:
                self.buttons.update()
                self.update_mario()
                self.render()
                frame_count += 1
                if frame_count % 60 == 0:
                    print(f"Mario at ({self.mario.x:.1f}, {self.mario.y:.1f}), Camera: {self.camera_x:.1f}")
                    gc.collect()
                time.sleep_ms(16)
            except KeyboardInterrupt:
                print("Game stopped by user")
                break
            except Exception as e:
                print(f"Game error: {e}")
                import sys
                sys.print_exception(e)
                break

def main():
    print("Starting Mario Game for Pico 2...")
    try:
        game = MarioGame()
        game.run()
    except Exception as e:
        print(f"Failed to start game: {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    main()