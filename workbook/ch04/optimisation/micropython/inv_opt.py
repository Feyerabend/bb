from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB565
from pimoroni import Button
from time import sleep
import random

# init display (try DISPLAY_PICO_DISPLAY_2 for 2.0", fall back to DISPLAY_PICO_DISPLAY for 1.14")
try:
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB565)
except ValueError:
    from picographics import DISPLAY_PICO_DISPLAY
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565)

display.set_backlight(0.8)

# display dimensions
WIDTH, HEIGHT = display.get_bounds()
SCALE = 1 if WIDTH == 240 else 1.5

# colours - preloaded pens
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
YELLOW = display.create_pen(255, 255, 0)

# precomputed constants to avoid repeated calculations
SCALE_INT = int(SCALE)
PLAYER_SPEED = int(3 * SCALE)
BULLET_SPEED = int(-5 * SCALE)
BOMB_SPEED = int(4 * SCALE)
BULLET_SIZE = int(2 * SCALE)
BOMB_SIZE = int(2 * SCALE)
INVADER_SPEED = int(1 * SCALE)
INVADER_DROP = int(5 * SCALE)
SPACING_X = int(20 * SCALE)
SPACING_Y = int(15 * SCALE)

# player
player = {
    'x': WIDTH // 2, 
    'y': int(HEIGHT * 0.9), 
    'width': int(10 * SCALE), 
    'height': int(7 * SCALE)
}

# precomputed player triangle points for efficiency
PLAYER_TRIANGLE = [
    (0, player['height']),  # bottom left
    (player['width'] // 2, 0),  # top
    (player['width'], player['height'])  # bottom right
]

# game objects
bullets = []
bombs = []
invaders = []
bunkers = []

# game state
game_over = False
win = False
frame_count = 0
invader_direction = 1
invader_move_interval = 20
bomb_fire_rate = 0.005
last_shoot_time = 0
shoot_cooldown = 0.2

# precomputed invader types with cached pixel data
invader_types = [
    {
        'pixels': [[0,1,0], [1,1,1], [1,0,1]], 
        'width': int(10 * SCALE), 
        'height': int(10 * SCALE), 
        'color': GREEN,
        'pixel_size_x': int(10 * SCALE) / 3,
        'pixel_size_y': int(10 * SCALE) / 3
    },
    {
        'pixels': [[0,0,1,1,0,0], [1,1,1,1,1,1], [1,0,0,0,0,1]], 
        'width': int(15 * SCALE), 
        'height': int(10 * SCALE), 
        'color': RED,
        'pixel_size_x': int(15 * SCALE) / 6,
        'pixel_size_y': int(10 * SCALE) / 3
    }
]

# precomputed bunker type with cached pixel data
bunker_type = {
    'pixels': [[1,1,1,1,1], [1,1,1,1,1], [0,1,1,1,0]], 
    'width': int(20 * SCALE), 
    'height': int(10 * SCALE), 
    'color': GREEN,
    'pixel_size_x': int(20 * SCALE) / 5,
    'pixel_size_y': int(10 * SCALE) / 3
}

# buttons
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)

def check_collision_fast(x1, y1, w1, h1, x2, y2, w2, h2):
    """Fast collision detection without caching"""
    return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

# .. also precomputed positions
def init_invaders():
    invaders.clear()
    for row in range(3):  # hardcoded for performance
        for col in range(5):  # hardcoded for performance
            type_idx = row % 2  # len(invader_types) is always 2
            inv_type = invader_types[type_idx]
            invaders.append({
                'x': int(50 * SCALE) + col * SPACING_X,
                'y': int(20 * SCALE) + row * SPACING_Y,
                'type_idx': type_idx,  # store index instead of full type for memory efficiency
                'width': inv_type['width'],
                'height': inv_type['height'],
                'alive': True
            })

# also precomp
def init_bunkers():
    bunkers.clear()
    bunker_count = 2
    bunker_spacing = WIDTH // (bunker_count + 1)
    for i in range(1, bunker_count + 1):
        # deep copy pixels for independent erosion
        pixels_copy = [row[:] for row in bunker_type['pixels']]
        bunkers.append({
            'x': int(i * bunker_spacing - bunker_type['width'] // 2),
            'y': int(HEIGHT * 0.75),
            'pixels': pixels_copy,  # store pixels directly for faster access
            'width': bunker_type['width'],
            'height': bunker_type['height']
        })

def update_input():
    global last_shoot_time
    
    # movement input
    if button_a.read() and player['x'] > 0:
        player['x'] -= PLAYER_SPEED
    if button_b.read() and player['x'] < WIDTH - player['width']:
        player['x'] += PLAYER_SPEED
    
    # shooting with time-based cooldown instead of sleep
    current_time = frame_count * 0.02  # approximate time
    if button_x.read() and len(bullets) < 3 and current_time - last_shoot_time > shoot_cooldown:
        bullets.append({'x': player['x'] + player['width'] // 2, 'y': player['y'] - BULLET_SIZE})
        last_shoot_time = current_time

def update_projectiles():
    global bullets, bombs
    
    # update bullets and filter out off-screen ones
    new_bullets = []
    for bullet in bullets:
        bullet['y'] += BULLET_SPEED
        if bullet['y'] >= 0:
            new_bullets.append(bullet)
    bullets = new_bullets
    
    # update bombs and filter out off-screen ones  
    new_bombs = []
    for bomb in bombs:
        bomb['y'] += BOMB_SPEED
        if bomb['y'] <= HEIGHT:
            new_bombs.append(bomb)
    bombs = new_bombs

def update_invaders():
    global invader_direction, game_over
    
    if frame_count % invader_move_interval != 0:
        return
    
    hit_edge = False
    alive_invaders = [inv for inv in invaders if inv['alive']]
    
    for invader in alive_invaders:
        invader['x'] += INVADER_SPEED * invader_direction
        
        # check edge collision
        if invader['x'] <= 0 or invader['x'] + invader['width'] >= WIDTH:
            hit_edge = True
        
        # check game over condition
        if invader['y'] + invader['height'] >= player['y']:
            game_over = True
        
        # generate bombs with reduced random calls
        if random.random() < bomb_fire_rate:
            bombs.append({
                'x': invader['x'] + invader['width'] // 2, 
                'y': invader['y'] + invader['height']
            })
    
    if hit_edge:
        invader_direction *= -1
        for inv in alive_invaders:
            inv['y'] += INVADER_DROP

def check_collisions():
    global game_over, win, bullets, bombs
    
    # bullets vs invaders - use indices for safe removal
    for bi in range(len(bullets) - 1, -1, -1):
        bullet = bullets[bi]
        for invader in invaders:
            if (invader['alive'] and 
                check_collision_fast(bullet['x'], bullet['y'], BULLET_SIZE, BULLET_SIZE,
                                   invader['x'], invader['y'], invader['width'], invader['height'])):
                invader['alive'] = False
                bullets.pop(bi)
                break
    
    # bullets vs bunkers
    for bi in range(len(bullets) - 1, -1, -1):
        bullet = bullets[bi]
        for bunker in bunkers:
            if check_bunker_hit(bullet['x'], bullet['y'], BULLET_SIZE, BULLET_SIZE, bunker):
                erode_bunker_fast(bunker, bullet['x'] - bunker['x'], bullet['y'] - bunker['y'])
                bullets.pop(bi)
                break
    
    # bombs vs bunkers
    for bi in range(len(bombs) - 1, -1, -1):
        bomb = bombs[bi]
        for bunker in bunkers:
            if check_bunker_hit(bomb['x'], bomb['y'], BOMB_SIZE, BOMB_SIZE, bunker):
                erode_bunker_fast(bunker, bomb['x'] - bunker['x'], bomb['y'] - bunker['y'])
                bombs.pop(bi)
                break
    
    # bombs vs player
    for bi in range(len(bombs) - 1, -1, -1):
        bomb = bombs[bi]
        if check_collision_fast(bomb['x'], bomb['y'], BOMB_SIZE, BOMB_SIZE,
                              player['x'], player['y'], player['width'], player['height']):
            game_over = True
            bombs.pop(bi)
    
    # bullets vs bombs
    for bi in range(len(bullets) - 1, -1, -1):
        bullet = bullets[bi]
        for boi in range(len(bombs) - 1, -1, -1):
            bomb = bombs[boi]
            if check_collision_fast(bullet['x'], bullet['y'], BULLET_SIZE, BULLET_SIZE,
                                  bomb['x'], bomb['y'], BOMB_SIZE, BOMB_SIZE):
                bullets.pop(bi)
                bombs.pop(boi)
                break
    
    # check win condition (optimized)
    if not any(inv['alive'] for inv in invaders):
        win = True

def check_bunker_hit(proj_x, proj_y, proj_w, proj_h, bunker):
    # early exit for obvious misses
    if (proj_x + proj_w < bunker['x'] or proj_x > bunker['x'] + bunker['width'] or
        proj_y + proj_h < bunker['y'] or proj_y > bunker['y'] + bunker['height']):
        return False
    
    # use precomputed pixel sizes
    col = int((proj_x - bunker['x'] + proj_w // 2) / bunker_type['pixel_size_x'])
    row = int((proj_y - bunker['y'] + proj_h // 2) / bunker_type['pixel_size_y'])
    
    return (0 <= row < len(bunker['pixels']) and 
            0 <= col < len(bunker['pixels'][0]) and 
            bunker['pixels'][row][col] == 1)

def erode_bunker_fast(bunker, hit_x, hit_y):
    hit_col = int(hit_x / bunker_type['pixel_size_x'])
    hit_row = int(hit_y / bunker_type['pixel_size_y'])
    
    # precompute bounds
    min_row = max(0, hit_row - 1)
    max_row = min(len(bunker['pixels']), hit_row + 2)
    min_col = max(0, hit_col - 1)
    max_col = min(len(bunker['pixels'][0]), hit_col + 2)
    
    for row in range(min_row, max_row):
        for col in range(min_col, max_col):
            bunker['pixels'][row][col] = 0

def draw_invader_fast(invader):
    if not invader['alive']:
        return
    
    inv_type = invader_types[invader['type_idx']]
    display.set_pen(inv_type['color'])
    
    # use precomputed pixel sizes
    pixel_size_x = inv_type['pixel_size_x']
    pixel_size_y = inv_type['pixel_size_y']
    
    for y, row in enumerate(inv_type['pixels']):
        for x, pixel in enumerate(row):
            if pixel:
                display.rectangle(
                    int(invader['x'] + x * pixel_size_x),
                    int(invader['y'] + y * pixel_size_y),
                    int(pixel_size_x),
                    int(pixel_size_y)
                )

def draw_bunker_fast(bunker):
    display.set_pen(bunker_type['color'])
    pixel_size_x = bunker_type['pixel_size_x']
    pixel_size_y = bunker_type['pixel_size_y']
    
    for y, row in enumerate(bunker['pixels']):
        for x, pixel in enumerate(row):
            if pixel:
                display.rectangle(
                    int(bunker['x'] + x * pixel_size_x),
                    int(bunker['y'] + y * pixel_size_y),
                    int(pixel_size_x),
                    int(pixel_size_y)
                )

# precompute text positions and scales
GAME_OVER_TEXT_X = WIDTH // 4
GAME_OVER_TEXT_Y = HEIGHT // 2
TEXT_SCALE = 2

def draw_optimized():
    display.set_pen(BLACK)
    display.clear()

    # player - use precomputed triangle points
    display.set_pen(WHITE)
    px, py = player['x'], player['y']
    display.triangle(
        px + PLAYER_TRIANGLE[0][0], py + PLAYER_TRIANGLE[0][1],
        px + PLAYER_TRIANGLE[1][0], py + PLAYER_TRIANGLE[1][1],
        px + PLAYER_TRIANGLE[2][0], py + PLAYER_TRIANGLE[2][1]
    )

    # bullets - batch drawing with single pen set
    if bullets:
        display.set_pen(YELLOW)
        for bullet in bullets:
            display.rectangle(bullet['x'], bullet['y'], BULLET_SIZE, BULLET_SIZE)

    # bombs - batch drawing with single pen set
    if bombs:
        display.set_pen(RED)
        for bomb in bombs:
            display.rectangle(bomb['x'], bomb['y'], BOMB_SIZE, BOMB_SIZE)

    # invaders - only draw alive ones
    for invader in invaders:
        if invader['alive']:
            draw_invader_fast(invader)

    # bunkers
    for bunker in bunkers:
        draw_bunker_fast(bunker)

    # game state text
    if game_over:
        display.set_pen(RED)
        display.text("Game Over", GAME_OVER_TEXT_X, GAME_OVER_TEXT_Y, scale=TEXT_SCALE)
    elif win:
        display.set_pen(GREEN)
        display.text("You Win!", GAME_OVER_TEXT_X, GAME_OVER_TEXT_Y, scale=TEXT_SCALE)

    display.update()

def update_optimized():
    global frame_count
    
    frame_count += 1
    
    update_input()
    update_projectiles()
    update_invaders()
    check_collisions()

# initialize game objects
init_invaders()
init_bunkers()

# main game loop
while True:
    if not game_over and not win:
        update_optimized()
        draw_optimized()
    else:
        draw_optimized()
    # sleep(0.02)  # ~50 FPS
