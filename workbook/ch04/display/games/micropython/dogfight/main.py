"""
Dogfight Game for Raspberry Pi Pico with Pimoroni Display Pack 2.0
Player vs AI opponent

Controls:
- A (GP12): Turn left
- B (GP13): Turn right  
- X (GP14): Fire (OR A+B together)
- Y (GP15): Reset game
"""

import time
import random
import math
from machine import Pin, SPI
from pimoroni import RGBLED
import st7789

# Init display (320x240)
spi = SPI(0, baudrate=62500000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
display = st7789.ST7789(spi, 320, 240, 
                        cs=Pin(17), dc=Pin(16), 
                        bl=Pin(20), rst=Pin(21),
                        rotate180=False)

# Init buttons
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# Init RGB LED
led = RGBLED(6, 7, 8)

# Colors
BLACK = display.BLACK
WHITE = display.WHITE
RED = display.RED
GREEN = display.GREEN
BLUE = display.BLUE
YELLOW = display.YELLOW

# Game constants
GAME_WIDTH = 80
GAME_HEIGHT = 72
PIXEL_SIZE = 3
SCREEN_WIDTH = GAME_WIDTH * PIXEL_SIZE
SCREEN_HEIGHT = GAME_HEIGHT * PIXEL_SIZE

# Directions (0-7)
DIR_N, DIR_NE, DIR_E, DIR_SE = 0, 1, 2, 3
DIR_S, DIR_SW, DIR_W, DIR_NW = 4, 5, 6, 7

# Direction deltas
DIR_DX = [0, 1, 1, 1, 0, -1, -1, -1]
DIR_DY = [-1, -1, 0, 1, 1, 1, 0, -1]

# Plane shapes (3x3 grid for each of 8 directions)
PLANE0_SHAPES = [
    [0,1,0, 1,1,1, 0,0,0],  # N
    [1,0,1, 0,1,0, 1,0,0],  # NE
    [0,1,0, 1,1,0, 0,1,0],  # E
    [1,0,0, 0,1,0, 1,0,1],  # SE
    [0,0,0, 1,1,1, 0,1,0],  # S
    [0,0,1, 0,1,0, 1,0,1],  # SW
    [0,1,0, 0,1,1, 0,1,0],  # W
    [1,0,1, 0,1,0, 0,0,1],  # NW
]

PLANE1_SHAPES = [
    [0,1,0, 1,1,1, 1,0,1],  # N
    [1,1,1, 1,1,0, 1,0,0],  # NE
    [0,1,1, 1,1,0, 0,1,1],  # E
    [1,0,0, 1,1,0, 1,1,1],  # SE
    [1,0,1, 1,1,1, 0,1,0],  # S
    [0,0,1, 0,1,1, 1,1,1],  # SW
    [1,1,0, 0,1,1, 1,1,0],  # W
    [1,1,1, 0,1,1, 0,0,1],  # NW
]

class Shot:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.dir = direction
        self.range = 15
        self.active = True
    
    def update(self):
        if not self.active:
            return
        
        # Move shot (3x speed of plane)
        self.x += DIR_DX[self.dir] * 3
        self.y += DIR_DY[self.dir] * 3
        
        # Wrap around screen
        if self.x < 0: self.x = GAME_WIDTH - 1
        if self.x >= GAME_WIDTH: self.x = 0
        if self.y < 0: self.y = GAME_HEIGHT - 1
        if self.y >= GAME_HEIGHT: self.y = 0
        
        # Decrement range
        self.range -= 1
        if self.range <= 0:
            self.active = False

class Plane:
    def __init__(self, x, y, direction, plane_type, is_ai=False):
        self.x = x
        self.y = y
        self.dir = direction
        self.type = plane_type
        self.is_ai = is_ai
        self.shots = []
        self.fire_cooldown = 0
        self.alive = True
        
        # AI state
        self.ai_timer = 0
        self.ai_state = "chase"  # chase, evade, fire
        self.ai_turn_delay = 0
    
    def get_shape(self):
        shapes = PLANE1_SHAPES if self.type == 1 else PLANE0_SHAPES
        return shapes[self.dir]
    
    def update(self):
        if not self.alive:
            return
        
        # Move plane
        self.x += DIR_DX[self.dir]
        self.y += DIR_DY[self.dir]
        
        # Wrap around
        if self.x < 1: self.x = GAME_WIDTH - 2
        if self.x >= GAME_WIDTH - 1: self.x = 1
        if self.y < 1: self.y = GAME_HEIGHT - 2
        if self.y >= GAME_HEIGHT - 1: self.y = 1
        
        # Update shots
        for shot in self.shots[:]:
            shot.update()
            if not shot.active:
                self.shots.remove(shot)
        
        # Update cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def fire(self):
        if self.fire_cooldown == 0 and len(self.shots) < 2:
            self.shots.append(Shot(self.x, self.y, self.dir))
            self.fire_cooldown = 10
    
    def turn_left(self):
        self.dir = (self.dir - 1) % 8
    
    def turn_right(self):
        self.dir = (self.dir + 1) % 8
    
    def check_hit(self, other_plane):
        shape = other_plane.get_shape()
        for shot in self.shots:
            if not shot.active:
                continue
            
            # Check all 3x3 positions of the plane
            for dy in range(3):
                for dx in range(3):
                    if shape[dy * 3 + dx]:
                        px = other_plane.x + dx - 1
                        py = other_plane.y + dy - 1
                        if shot.x == px and shot.y == py:
                            shot.active = False
                            return True
        return False
    
    def ai_update(self, player):
        if not self.alive:
            return
        
        self.ai_timer += 1
        
        # Calculate angle to player
        dx = player.x - self.x
        dy = player.y - self.y
        
        # Wrap-around distance (find shortest path)
        if abs(dx) > GAME_WIDTH / 2:
            dx = dx - GAME_WIDTH if dx > 0 else dx + GAME_WIDTH
        if abs(dy) > GAME_HEIGHT / 2:
            dy = dy - GAME_HEIGHT if dy > 0 else dy + GAME_HEIGHT
        
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Determine target direction
        target_angle = math.atan2(dy, dx)
        target_dir = int((target_angle / (2 * math.pi) * 8 + 2) % 8)
        
        # Simple state machine
        if distance < 20:
            # Close range - try to evade and fire
            self.ai_state = "evade"
            if self.ai_timer % 5 == 0:
                # Turn away from player occasionally
                if random.random() < 0.3:
                    self.turn_left() if random.random() < 0.5 else self.turn_right()
            
            # Fire if roughly aimed at player
            dir_diff = abs(self.dir - target_dir)
            if dir_diff <= 1 or dir_diff >= 7:
                if random.random() < 0.4:
                    self.fire()
        
        elif distance < 40:
            # Medium range - chase and fire
            self.ai_state = "chase"
            # Turn towards player
            if self.ai_turn_delay <= 0:
                dir_diff = (target_dir - self.dir) % 8
                if dir_diff <= 4 and dir_diff != 0:
                    self.turn_right()
                    self.ai_turn_delay = 2
                elif dir_diff > 4:
                    self.turn_left()
                    self.ai_turn_delay = 2
                else:
                    # Aimed correctly, try to fire
                    if random.random() < 0.3:
                        self.fire()
            else:
                self.ai_turn_delay -= 1
        
        else:
            # Far range - just chase
            self.ai_state = "chase"
            if self.ai_turn_delay <= 0:
                dir_diff = (target_dir - self.dir) % 8
                if dir_diff <= 4 and dir_diff != 0:
                    self.turn_right()
                    self.ai_turn_delay = 3
                elif dir_diff > 4:
                    self.turn_left()
                    self.ai_turn_delay = 3
            else:
                self.ai_turn_delay -= 1

class Game:
    def __init__(self):
        self.player = None
        self.ai = None
        self.game_over = False
        self.winner = None
        self.frame_buffer = [[0 for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
        self.reset()
    
    def reset(self):
        # Player starts bottom right
        self.player = Plane(GAME_WIDTH - 10, GAME_HEIGHT - 10, DIR_W, 0, is_ai=False)
        
        # AI starts top left
        self.ai = Plane(10, 10, DIR_E, 1, is_ai=True)
        
        self.game_over = False
        self.winner = None
        
        # Clear frame buffer
        for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                self.frame_buffer[y][x] = 0
    
    def update(self):
        if self.game_over:
            return
        
        # Update both planes
        self.player.update()
        self.ai.ai_update(self.player)
        self.ai.update()
        
        # Check collisions
        if self.player.check_hit(self.ai):
            self.game_over = True
            self.winner = "Player"
            self.ai.alive = False
        
        if self.ai.check_hit(self.player):
            self.game_over = True
            self.winner = "AI"
            self.player.alive = False
    
    def draw_plane(self, plane, color):
        shape = plane.get_shape()
        for dy in range(3):
            for dx in range(3):
                if shape[dy * 3 + dx]:
                    px = plane.x + dx - 1
                    py = plane.y + dy - 1
                    if 0 <= px < GAME_WIDTH and 0 <= py < GAME_HEIGHT:
                        self.frame_buffer[py][px] = color
    
    def render(self):
        # Clear frame buffer
        for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                self.frame_buffer[y][x] = 0
        
        # Draw player (white)
        if self.player.alive:
            self.draw_plane(self.player, 1)
        
        # Draw AI (red indicator in framebuffer, but we'll color it differently)
        if self.ai.alive:
            self.draw_plane(self.ai, 2)
        
        # Draw player shots (white)
        for shot in self.player.shots:
            if shot.active:
                if 0 <= shot.x < GAME_WIDTH and 0 <= shot.y < GAME_HEIGHT:
                    self.frame_buffer[shot.y][shot.x] = 1
        
        # Draw AI shots (red indicator)
        for shot in self.ai.shots:
            if shot.active:
                if 0 <= shot.x < GAME_WIDTH and 0 <= shot.y < GAME_HEIGHT:
                    self.frame_buffer[shot.y][shot.x] = 3
        
        # Render to display
        for y in range(GAME_HEIGHT):
            for x in range(GAME_WIDTH):
                pixel = self.frame_buffer[y][x]
                if pixel == 1:  # Player and shots
                    color = WHITE
                elif pixel == 2:  # AI plane
                    color = RED
                elif pixel == 3:  # AI shots
                    color = YELLOW
                else:
                    color = BLACK
                
                # Draw 3x3 block for each game pixel
                display.set_pen(color)
                display.rectangle(x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
        
        # Draw game over message
        if self.game_over:
            display.set_pen(BLACK)
            display.rectangle(40, 100, 160, 40)
            display.set_pen(GREEN if self.winner == "Player" else RED)
            msg = f"{self.winner} WINS!"
            display.text(msg, 60, 115, scale=2)
        
        display.update()

# Main game loop
def main():
    game = Game()
    display.set_pen(BLACK)
    display.clear()
    
    # Show startup message
    display.set_pen(WHITE)
    display.text("DOGFIGHT", 100, 100, scale=3)
    display.text("A/B: Turn  X: Fire  Y: Reset", 30, 140, scale=1)
    display.update()
    time.sleep(2)
    
    prev_fire = False
    
    while True:
        # Read buttons (inverted logic - pulled up)
        btn_a = not button_a.value()
        btn_b = not button_b.value()
        btn_x = not button_x.value()
        btn_y = not button_y.value()
        
        # Reset game
        if btn_y:
            game.reset()
            led.set_rgb(0, 0, 0)
            time.sleep(0.2)
            continue
        
#        # Player controls
#        if btn_a and not btn_b:
#            game.player.turn_left()
#        elif btn_b and not btn_a:
#            game.player.turn_right()
        
#        # Fire with edge detection
#        if btn_x and not prev_fire:
#            game.player.fire()
#        prev_fire = btn_x

        # Player controls
        if btn_a and btn_b:
            # Both pressed = fire
            if not prev_fire:
                game.player.fire()
            prev_fire = True
        else:
            # Only one pressed = turn
            if btn_a:
                game.player.turn_left()
            elif btn_b:
                game.player.turn_right()
            prev_fire = False

        # Update LED based on game state
        if game.game_over:
            if game.winner == "Player":
                led.set_rgb(0, 255, 0)  # Green
            else:
                led.set_rgb(255, 0, 0)  # Red
        else:
            # Pulse LED based on activity
            intensity = 50 if game.player.fire_cooldown > 0 else 10
            led.set_rgb(0, intensity, intensity)
        
        # Update game logic
        game.update()
        
        # Render
        game.render()
        
        # Frame delay (~10 FPS)
        time.sleep(0.1)

# Run game
if __name__ == "__main__":
    main()
