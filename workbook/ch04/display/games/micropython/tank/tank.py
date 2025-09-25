from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_PACK, PEN_P3
# Simple tank game for Raspberry Pi Pico with Display Pack 2.0:
# DISPLAY_PICO_DISPLAY_PACK2
# from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_PACK2, PEN_P3
# import picodisplay2 as display  # Uncomment if using Display Pack 2.0
import time
import random
import math

# Setup display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_PACK, rotate=0, pen_type=PEN_P3)
#display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_PACK2, rotate=0, pen_type=PEN_P3)
# display = picodisplay.PicoDisplay2()
WIDTH, HEIGHT = 240, 135

# Colors (RGB888)
BLACK = display.create_pen(0, 0, 0)
GREEN = display.create_pen(0, 255, 0)  # Ground
BLUE = display.create_pen(0, 0, 255)    # Sky
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GRAY = display.create_pen(128, 128, 128)

# Button pins for Display Pack 2.0
button_a = 12  # Left
button_b = 13  # Down (right move)
button_x = 14  # Up (shoot)
button_y = 15  # Right (unused)

def read_button(pin):
    import machine
    return machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP).value() == 0

# Game state
class Tank:
    def __init__(self, x, color, is_player=False):
        self.x = x
        self.y = HEIGHT - 15  # Ground level
        self.color = color
        self.health = 3
        self.missiles = []
        self.is_player = is_player
        self.dx = 0  # Movement speed
        self.shoot_timer = 0

    def update(self, dt):
        if self.is_player:
            self.dx = 0
            if read_button(button_a):
                self.dx = -2
            if read_button(button_b):
                self.dx = 2
            if read_button(button_x) and self.shoot_timer <= 0:
                self.missiles.append(Missile(self.x, self.y - 5, -1))  # Upward
                self.shoot_timer = 30  # Cooldown frames
        else:
            # Enemy AI: random wander and occasional shoot
            if random.random() < 0.02:
                self.dx = random.choice([-1, 1])
            if random.random() < 0.01 and self.shoot_timer <= 0:  # Rare shot
                self.missiles.append(Missile(self.x, self.y - 5, -1))
                self.shoot_timer = 60
            self.dx *= 0.95  # Friction

        self.x += self.dx
        self.x = max(5, min(WIDTH - 5, self.x))  # Boundaries
        self.shoot_timer -= 1

        # Update missiles
        for m in self.missiles[:]:
            m.update(dt)
            if m.y < 0 or m.y > HEIGHT:
                self.missiles.remove(m)

    def draw(self):
        # Tank body (rectangle)
        display.set_pen(self.color)
        display.rectangle(self.x - 5, self.y - 10, 10, 10)
        # Turret (small circle)
        display.set_pen(WHITE)
        display.circle(self.x, self.y - 12, 3)
        # Missiles
        for m in self.missiles:
            m.draw()

    def check_hit(self, other_missiles):
        for m in other_missiles:
            if abs(m.x - self.x) < 8 and abs(m.y - self.y) < 8:
                self.health -= 1
                other_missiles.remove(m)
                return True
        return False

class Missile:
    def __init__(self, x, y, dy):
        self.x = x
        self.y = y
        self.dy = dy
        self.speed = 3

    def update(self, dt):
        self.y += self.dy * self.speed

    def draw(self):
        display.set_pen(WHITE)
        display.rectangle(self.x - 1, self.y - 2, 2, 4)

# Init game
player = Tank(50, GREEN, True)
enemy = Tank(190, RED, False)
score_p = 0
score_e = 0
clock = 0
running = True

while running:
    dt = 1 / 60  # Fake 60 FPS
    clock += 1

    # Update
    player.update(dt)
    enemy.update(dt)

    # Check collisions
    if player.check_hit(enemy.missiles):
        score_e += 1
    if enemy.check_hit(player.missiles):
        score_p += 1

    # Check win
    if score_p >= 3:
        display.set_pen(GREEN)
        display.text("YOU WIN!", 80, 60, scale=2)
        display.update()
        time.sleep(3)
        running = False
    elif score_e >= 3:
        display.set_pen(RED)
        display.text("YOU LOSE!", 80, 60, scale=2)
        display.update()
        time.sleep(3)
        running = False

    # Draw
    display.set_pen(BLUE)
    display.rectangle(0, 0, WIDTH, HEIGHT - 15)  # Sky
    display.set_pen(GREEN)
    display.rectangle(0, HEIGHT - 15, WIDTH, 15)  # Ground

    player.draw()
    enemy.draw()

    # Scores
    display.set_pen(WHITE)
    display.text(f"P: {score_p}", 10, 10, scale=1)
    display.text(f"E: {score_e}", WIDTH - 40, 10, scale=1)

    display.update()
    time.sleep(1/60)  # ~60 FPS

print("Game over!")
