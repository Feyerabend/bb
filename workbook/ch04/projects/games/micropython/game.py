"""
Simple Game for Pimoroni Display Pack 2.0 + Raspberry Pi Pico 2
Using simplified Entity-Manager pattern with basic AI and collision detection.

Hardware: 320x240 IPS LCD, 4 buttons (A, B, X, Y)
Libraries: picographics, pimoroni
"""

from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
from pimoroni import Button
import time
import math
import random

# Init display and buttons
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
WIDTH, HEIGHT = display.get_bounds()

btn_a = Button(12)  # Left
btn_b = Button(13)  # Right
btn_x = Button(14)  # Jump
btn_y = Button(15)  # Action

# Colors
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 100, 255)
YELLOW = display.create_pen(255, 255, 0)


# INPUT HANDLER
class InputHandler:
    def __init__(self):
        self.left = False
        self.right = False
        self.jump = False
        self.action = False
    
    def poll(self):
        self.left = btn_a.is_pressed
        self.right = btn_b.is_pressed
        self.jump = btn_x.is_pressed
        self.action = btn_y.is_pressed
        return self


# ENTITY BASE CLASS
class Entity:
    _next_id = 0
    
    def __init__(self, x, y):
        self.id = Entity._next_id
        Entity._next_id += 1
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.active = True
    
    def update(self, dt, input_handler):
        # Apply velocity to position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Simple boundary check
        self.x = max(5, min(WIDTH - 5, self.x))
        self.y = max(5, min(HEIGHT - 5, self.y))
    
    def render(self, display):
        pass  # Override in subclasses


# PLAYER
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 100
        self.size = 8
        self.score = 0
    
    def update(self, dt, input_handler):
        # Process input → set velocity
        self.vx = 0
        if input_handler.left:
            self.vx = -self.speed
        if input_handler.right:
            self.vx = self.speed
        
        # Jump (simple vertical movement)
        if input_handler.jump:
            self.vy = -80
        else:
            self.vy = 80
        
        # Call parent to apply movement
        super().update(dt, input_handler)
    
    def render(self, display):
        display.set_pen(GREEN)
        # Draw player as square
        display.rectangle(int(self.x - self.size), int(self.y - self.size), 
                         self.size * 2, self.size * 2)


# ENEMY
class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 60
        self.size = 6
        self.time = random.random() * 6.28  # Random phase
    
    def update(self, dt, input_handler):
        # AI: Sine wave patrol
        self.time += dt
        self.vx = -self.speed
        self.vy = math.sin(self.time * 2) * 40
        
        # Wrap around screen
        if self.x < -10:
            self.x = WIDTH + 10
            self.y = random.randint(20, HEIGHT - 20)
        
        super().update(dt, input_handler)
    
    def render(self, display):
        display.set_pen(RED)
        display.circle(int(self.x), int(self.y), self.size)


# COLLECTIBLE (Sprite)
class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 4
        self.time = random.random() * 6.28
    
    def update(self, dt, input_handler):
        # Gentle floating animation
        self.time += dt * 3
        self.y += math.sin(self.time) * 0.5
        super().update(dt, input_handler)
    
    def render(self, display):
        display.set_pen(YELLOW)
        display.circle(int(self.x), int(self.y), self.size)


# ENTITY MANAGER
class EntityManager:
    def __init__(self):
        self.entities = []
    
    def create_entity(self, entity_type, x, y):
        entity = entity_type(x, y)
        self.entities.append(entity)
        return entity
    
    def update(self, dt, input_handler):
        for entity in self.entities:
            if entity.active:
                entity.update(dt, input_handler)
    
    def render(self, display):
        for entity in self.entities:
            if entity.active:
                entity.render(display)
    
    def get_by_type(self, entity_type):
        return [e for e in self.entities if isinstance(e, entity_type) and e.active]
    
    def remove_inactive(self):
        self.entities = [e for e in self.entities if e.active]


# COLLISION SYSTEM (simple circle-based)
def check_collision(e1, e2):
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    dist = math.sqrt(dx*dx + dy*dy)
    return dist < (getattr(e1, 'size', 5) + getattr(e2, 'size', 5))


# GAME
class Game:
    def __init__(self):
        self.entity_manager = EntityManager()
        self.input_handler = InputHandler()
        self.player = None
        self.running = True
        self.last_time = time.ticks_ms()
        
    def setup(self):
        # Create player
        self.player = self.entity_manager.create_entity(Player, WIDTH // 2, HEIGHT // 2)
        
        # Create enemies
        for i in range(3):
            x = WIDTH + i * 80
            y = random.randint(30, HEIGHT - 30)
            self.entity_manager.create_entity(Enemy, x, y)
        
        # Create coins
        for i in range(5):
            x = random.randint(40, WIDTH - 40)
            y = random.randint(40, HEIGHT - 40)
            self.entity_manager.create_entity(Coin, x, y)
    
    def loop(self):
        # Calculate delta time
        current_time = time.ticks_ms()
        dt = time.ticks_diff(current_time, self.last_time) / 1000.0
        self.last_time = current_time
        dt = min(dt, 0.1)  # Cap dt to avoid huge jumps
        
        # 1. Get input
        input_state = self.input_handler.poll()
        
        # 2. Update all entities
        self.entity_manager.update(dt, input_state)
        
        # 3. Check collisions
        enemies = self.entity_manager.get_by_type(Enemy)
        coins = self.entity_manager.get_by_type(Coin)
        
        for enemy in enemies:
            if check_collision(self.player, enemy):
                enemy.active = False  # Simple: remove enemy on hit
        
        for coin in coins:
            if check_collision(self.player, coin):
                coin.active = False
                self.player.score += 10
        
        self.entity_manager.remove_inactive()
        
        # Spawn new coin if needed
        if len(coins) < 3:
            x = random.randint(40, WIDTH - 40)
            y = random.randint(40, HEIGHT - 40)
            self.entity_manager.create_entity(Coin, x, y)
        
        # 4. Render
        display.set_pen(BLACK)
        display.clear()
        
        self.entity_manager.render(display)
        
        # Draw UI
        display.set_pen(WHITE)
        display.text(f"Score: {self.player.score}", 5, 5, scale=2)
        display.text("A/B:Move X:Up Y:Down", 5, HEIGHT - 15, scale=1)
        
        display.update()
    
    def run(self):
        self.setup()
        while self.running:
            self.loop()
            time.sleep(0.016)  # ~60 FPS


if __name__ == "__main__":
    game = Game()
    game.run()
