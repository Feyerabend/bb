import time
import math
import gc
from machine import Pin, SPI
import framebuf

# Display driver for ST7789 (based on your C code)
class ST7789:
    def __init__(self):
        # Display Pack pin definitions
        self.cs = Pin(17, Pin.OUT, value=1)
        self.dc = Pin(16, Pin.OUT, value=1)
        self.reset = Pin(21, Pin.OUT, value=1)
        self.bl = Pin(20, Pin.OUT, value=0)
        
        # SPI setup
        self.spi = SPI(0, baudrate=31250000, 
                      sck=Pin(18), mosi=Pin(19))
        
        self.width = 320
        self.height = 240
        
        # Initialize display
        self._init_display()
        
    def _write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)
        
    def _write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
        
    def _init_display(self):
        # Hardware reset
        self.reset.value(1)
        time.sleep_ms(10)
        self.reset.value(0)
        time.sleep_ms(10)
        self.reset.value(1)
        time.sleep_ms(120)
        
        # ST7789 init sequence
        self._write_cmd(0x01)  # SWRESET
        time.sleep_ms(150)
        
        self._write_cmd(0x11)  # SLPOUT
        time.sleep_ms(120)
        
        self._write_cmd(0x3A)  # COLMOD
        self._write_data(0x55)  # 16-bit RGB565
        
        self._write_cmd(0x36)  # MADCTL
        self._write_data(0x70)  # Row/Column exchange, RGB order
        
        # Set display area
        self._write_cmd(0x2A)  # CASET
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x01)
        self._write_data(0x3F)
        
        self._write_cmd(0x2B)  # RASET
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0xEF)
        
        self._write_cmd(0x21)  # INVON
        self._write_cmd(0x13)  # NORON
        self._write_cmd(0x29)  # DISPON
        time.sleep_ms(100)
        
        # Turn on backlight
        self.bl.value(1)
        
    def set_window(self, x0, y0, x1, y1):
        self._write_cmd(0x2A)  # CASET
        self._write_data(x0 >> 8)
        self._write_data(x0 & 0xFF)
        self._write_data(x1 >> 8)
        self._write_data(x1 & 0xFF)
        
        self._write_cmd(0x2B)  # RASET
        self._write_data(y0 >> 8)
        self._write_data(y0 & 0xFF)
        self._write_data(y1 >> 8)
        self._write_data(y1 & 0xFF)
        
        self._write_cmd(0x2C)  # RAMWR
        
    def fill_rect(self, x, y, w, h, color):
        if x >= self.width or y >= self.height:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
            
        self.set_window(x, y, x + w - 1, y + h - 1)
        
        color_bytes = bytes([(color >> 8) & 0xFF, color & 0xFF])
        pixel_data = color_bytes * (w * h)
        
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(pixel_data)
        self.cs.value(1)
        
    def clear(self, color=0x0000):
        self.fill_rect(0, 0, self.width, self.height, color)

# Button handler
class Buttons:
    def __init__(self):
        self.btn_a = Pin(12, Pin.IN, Pin.PULL_UP)
        self.btn_b = Pin(13, Pin.IN, Pin.PULL_UP)
        self.btn_x = Pin(14, Pin.IN, Pin.PULL_UP)
        self.btn_y = Pin(15, Pin.IN, Pin.PULL_UP)
        
        self.last_state = [True, True, True, True]
        self.last_check = 0
        
    def update(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_check) < 50:
            return
        self.last_check = now
        
        self.last_state[0] = not self.btn_a.value()
        self.last_state[1] = not self.btn_b.value()
        self.last_state[2] = not self.btn_x.value()
        self.last_state[3] = not self.btn_y.value()
        
    def is_pressed(self, button):
        # 0=A(left), 1=B(right), 2=X(jump), 3=Y(run)
        return self.last_state[button]

# Sprite and tile data (simplified 8x8 patterns)
class SpriteData:
    @staticmethod
    def get_mario_idle():
        # 16x16 Mario idle sprite (RGB565 format)
        # Simplified as colored rectangles for demo
        return [
            0xF800, 0xF800, 0xF800, 0xF800, 0x0000, 0x0000, 0x0000, 0x0000,
            0xF800, 0xF800, 0xF800, 0xF800, 0x0000, 0x0000, 0x0000, 0x0000,
            0xF800, 0xF800, 0xF800, 0xF800, 0x0000, 0x0000, 0x0000, 0x0000,
            0xF800, 0xF800, 0xF800, 0xF800, 0x0000, 0x0000, 0x0000, 0x0000,
            0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0,
            0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0, 0x07E0,
            0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F,
            0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F, 0x001F
        ]
    
    @staticmethod
    def get_block():
        # 16x16 block sprite
        block = []
        for y in range(16):
            for x in range(16):
                if x == 0 or x == 15 or y == 0 or y == 15:
                    block.append(0x0000)  # Border
                else:
                    block.append(0xFFE0)  # Yellow interior
        return block

# Game physics and logic
class Mario:
    def __init__(self):
        self.x = 50
        self.y = 128
        self.x_speed = 0
        self.y_speed = 0
        
        self.facing_left = False
        self.skidding = False
        self.fast_jump = False
        self.faster_jump = False
        self.fast_v_jump = False
        self.faster_v_jump = False
        self.run_count = 0
        
        # Physics constants (from JS)
        self.min_walk_speed = 1/16 + 3/256
        self.walk_accel = 9/256 + 8/(16*16*16)
        self.max_walk_speed = 1 + 9/16
        self.release_decel = 13/256
        self.skid_decel = 1/16 + 10/256
        self.turn_speed = 9/16
        self.max_run_speed = 2 + 9/16
        self.run_accel = 14/256 + 4/(16*16*16)
        
        self.airspeed_cutoff = 1 + 13/16
        self.air_slow_gain = 9/256 + 8/(16*16*16)
        self.air_fast_gain = 14/256 + 4/(16*16*16)
        self.air_fast_drag = 13/256
        self.air_slow_drag = 9/256 + 8/(16*16*16)
        
        self.jump_speed = 4
        self.big_jump_speed = 5
        self.small_up_drag = 2/16
        self.medium_up_drag = 1/16 + 14/256
        self.big_up_drag = 2/16 + 8/256
        self.small_gravity = 7/16
        self.med_gravity = 6/16
        self.big_gravity = 9/16
        self.jump_cutoff1 = 1
        self.jump_cutoff2 = 2 + 5/16
        self.max_v_speed = 4

class Level:
    def __init__(self):
        # Simplified level data - 1=ground, 0=air, 2=breakable block
        self.width = 100
        self.height = 15
        self.data = [0] * (self.width * self.height)
        
        # Create simple ground level
        for x in range(self.width):
            for y in range(13, 15):  # Ground at bottom
                self.data[y * self.width + x] = 1
                
        # Add some platforms and blocks
        for x in range(20, 30):
            self.data[10 * self.width + x] = 1
        for x in range(40, 50):
            self.data[8 * self.width + x] = 1
        for x in range(60, 70):
            self.data[6 * self.width + x] = 2  # Breakable blocks
            
    def get_tile(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 0
        return self.data[y * self.width + x]
    
    def is_solid(self, x, y):
        tile_x = int(x // 16)
        tile_y = int(y // 16)
        tile = self.get_tile(tile_x, tile_y)
        return tile > 0 and tile < 9

# Main game class
class MarioGame:
    def __init__(self):
        self.display = ST7789()
        self.buttons = Buttons()
        self.mario = Mario()
        self.level = Level()
        self.scroll = 0
        self.frame = 0
        self.background_frame = 0
        
        # Colors
        self.sky_color = 0x5D9CEC    # Light blue
        self.ground_color = 0x8B4513  # Brown
        self.block_color = 0xFFE0     # Yellow
        self.mario_color = 0xF800     # Red
        
    def is_standing_on_ground(self):
        return (self.level.is_solid(self.mario.x, self.mario.y + 8) or
                (self.level.is_solid(self.mario.x + 4, self.mario.y + 8) and 
                 ((self.mario.y + 8) % 16) < 1 + self.mario.y_speed) or
                (self.level.is_solid(self.mario.x - 4, self.mario.y + 8) and 
                 ((self.mario.y + 8) % 16) < 1 + self.mario.y_speed))
    
    def update_physics(self):
        standing_on = self.is_standing_on_ground()
        
        if standing_on:
            # Ground physics
            self.mario.y = 16 * int((self.mario.y + 8) // 16) - 8
            self.mario.y_speed = 0
            
            # Determine acceleration
            if self.buttons.is_pressed(3):  # Y button = run
                self.mario.run_count = 10
                accel = self.mario.run_accel
            else:
                if self.mario.run_count > 0:
                    self.mario.run_count -= 1
                accel = self.mario.walk_accel
                
            # Horizontal movement
            if self.buttons.is_pressed(1):  # B button = right
                if self.mario.x_speed < 0:  # Skidding
                    self.mario.skidding = True
                    if self.mario.x_speed > -self.mario.turn_speed:
                        self.mario.x_speed = 0
                    else:
                        self.mario.x_speed += self.mario.skid_decel
                else:
                    self.mario.skidding = False
                    self.mario.facing_left = False
                    
                    if self.mario.x_speed == 0:
                        self.mario.x_speed = self.mario.min_walk_speed
                    else:
                        self.mario.x_speed += accel
                        
                    if self.mario.x_speed > self.mario.max_run_speed:
                        self.mario.x_speed = self.mario.max_run_speed
                    if (self.mario.x_speed > self.mario.max_walk_speed and 
                        self.mario.run_count == 0):
                        self.mario.x_speed = self.mario.max_walk_speed
                        
            elif self.buttons.is_pressed(0):  # A button = left
                if self.mario.x_speed > 0:  # Skidding
                    self.mario.skidding = True
                    if self.mario.x_speed < self.mario.turn_speed:
                        self.mario.x_speed = 0
                    else:
                        self.mario.x_speed -= self.mario.skid_decel
                else:
                    self.mario.skidding = False
                    self.mario.facing_left = True
                    
                    if self.mario.x_speed == 0:
                        self.mario.x_speed = -self.mario.min_walk_speed
                    else:
                        self.mario.x_speed -= accel
                        
                    if self.mario.x_speed < -self.mario.max_run_speed:
                        self.mario.x_speed = -self.mario.max_run_speed
                    if (self.mario.x_speed < -self.mario.max_walk_speed and 
                        self.mario.run_count == 0):
                        self.mario.x_speed = -self.mario.max_walk_speed
            else:
                # Decelerate
                decel = self.mario.skid_decel if self.mario.skidding else self.mario.release_decel
                
                if self.mario.x_speed > decel:
                    self.mario.x_speed -= decel
                elif self.mario.x_speed < -decel:
                    self.mario.x_speed += decel
                else:
                    self.mario.x_speed = 0
                    
            # Set jump flags based on speed
            abs_speed = abs(self.mario.x_speed)
            
            if abs_speed > self.mario.jump_cutoff2:
                self.mario.faster_v_jump = True
            elif abs_speed > self.mario.jump_cutoff1:
                self.mario.fast_v_jump = True
            else:
                self.mario.faster_v_jump = False
                self.mario.fast_v_jump = False
                
            self.mario.fast_jump = abs_speed > self.mario.max_walk_speed
            self.mario.faster_jump = abs_speed > self.mario.airspeed_cutoff
            
            # Jump
            if self.buttons.is_pressed(2):  # X button = jump
                if self.mario.faster_v_jump:
                    self.mario.y_speed = -self.mario.big_jump_speed
                else:
                    self.mario.y_speed = -self.mario.jump_speed
        else:
            # Air physics (simplified)
            if self.buttons.is_pressed(1):  # Right
                if (abs(self.mario.x_speed) >= self.mario.max_walk_speed):
                    self.mario.x_speed += self.mario.air_fast_gain
                else:
                    if self.mario.x_speed > 0:
                        self.mario.x_speed += self.mario.air_slow_gain
                    else:
                        if self.mario.faster_jump:
                            self.mario.x_speed += self.mario.air_fast_drag
                        else:
                            self.mario.x_speed += self.mario.air_slow_drag
                            
            elif self.buttons.is_pressed(0):  # Left
                if (abs(self.mario.x_speed) >= self.mario.max_walk_speed):
                    self.mario.x_speed -= self.mario.air_fast_gain
                else:
                    if self.mario.x_speed < 0:
                        self.mario.x_speed -= self.mario.air_slow_gain
                    else:
                        if self.mario.faster_jump:
                            self.mario.x_speed -= self.mario.air_fast_drag
                        else:
                            self.mario.x_speed -= self.mario.air_slow_drag
                            
            # Limit air speed
            if self.mario.fast_jump:
                self.mario.x_speed = max(-self.mario.max_run_speed, 
                                       min(self.mario.max_run_speed, self.mario.x_speed))
            else:
                self.mario.x_speed = max(-self.mario.max_walk_speed, 
                                       min(self.mario.max_walk_speed, self.mario.x_speed))
                
            # Vertical movement in air
            if self.mario.y_speed < 0 and self.buttons.is_pressed(2):  # Holding jump
                if self.mario.faster_v_jump:
                    self.mario.y_speed += self.mario.big_up_drag
                elif self.mario.fast_v_jump:
                    self.mario.y_speed += self.mario.medium_up_drag
                else:
                    self.mario.y_speed += self.mario.small_up_drag
            else:
                if self.mario.faster_v_jump:
                    self.mario.y_speed += self.mario.big_gravity
                elif self.mario.fast_v_jump:
                    self.mario.y_speed += self.mario.med_gravity
                else:
                    self.mario.y_speed += self.mario.small_gravity
                    
            if self.mario.y_speed > self.mario.max_v_speed:
                self.mario.y_speed = self.mario.max_v_speed
                
        # Apply movement
        self.mario.x += self.mario.x_speed
        self.mario.y += self.mario.y_speed
        
        # Wall collisions (simplified)
        solid_left = self.level.is_solid(self.mario.x - 7, self.mario.y)
        solid_right = self.level.is_solid(self.mario.x + 7, self.mario.y)
        
        if solid_left and not solid_right:
            if self.mario.facing_left:
                self.mario.x_speed = 0
            self.mario.x += 1
            
        if solid_right and not solid_left:
            if not self.mario.facing_left:
                self.mario.x_speed = 0
            self.mario.x -= 1
            
        # Head collision
        if self.level.is_solid(self.mario.x, self.mario.y - 4):
            self.mario.y_speed = 0
            self.mario.y = 16 * int((self.mario.y - 4) // 16 + 1) + 4
            
        # Camera scrolling
        if self.mario.x < 8:
            self.mario.x = 8
            self.mario.x_speed = 0
        if self.mario.x > 90:
            a = (self.mario.x - 90) / 2
            self.scroll += a
            self.mario.x -= a
            
    def draw_sprite(self, x, y, sprite_data, width=16, height=16):
        # Simple sprite drawing - just draw colored rectangles for now
        if sprite_data == self.mario_color:
            self.display.fill_rect(int(x), int(y), width, height, self.mario_color)
        elif sprite_data == self.block_color:
            self.display.fill_rect(int(x), int(y), width, height, self.block_color)
            
    def render(self):
        # Clear screen
        self.display.clear(self.sky_color)
        
        # Draw level tiles
        start_x = max(0, int(self.scroll // 16))
        end_x = min(self.level.width, start_x + 21)
        
        for tile_x in range(start_x, end_x):
            for tile_y in range(self.level.height):
                tile = self.level.get_tile(tile_x, tile_y)
                if tile > 0:
                    screen_x = tile_x * 16 - int(self.scroll)
                    screen_y = tile_y * 16
                    
                    if -16 <= screen_x <= 336:  # On screen
                        color = self.ground_color if tile == 1 else self.block_color
                        self.display.fill_rect(screen_x, screen_y, 16, 16, color)
                        
        # Draw Mario
        mario_screen_x = int(self.mario.x - 8)
        mario_screen_y = int(self.mario.y - 7)
        self.draw_sprite(mario_screen_x, mario_screen_y, self.mario_color)
        
    def run(self):
        print("Mario Game Starting!")
        last_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time)
            
            if dt >= 16:  # ~60 FPS
                self.buttons.update()
                self.update_physics()
                self.render()
                
                self.frame = (self.frame + 1) % 48
                self.background_frame = (self.background_frame + 1) % 80
                
                last_time = current_time
                
                # Garbage collection to prevent memory issues
                if self.frame % 60 == 0:
                    gc.collect()
                    
            time.sleep_ms(1)

# Main execution
if __name__ == "__main__":
    try:
        game = MarioGame()
        game.run()
    except KeyboardInterrupt:
        print("Game stopped")
    except Exception as e:
        print(f"Error: {e}")
