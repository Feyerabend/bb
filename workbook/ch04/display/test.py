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

display.set_backlight(0.8) # or 1.0

# display dimensions
WIDTH, HEIGHT = display.get_bounds()
SCALE = 1 if WIDTH == 240 else 1.5  # scale for larger Display Pack 2

# colours
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
YELLOW = display.create_pen(255, 255, 0)

# player
player = {'x': WIDTH // 2, 'y': int(HEIGHT * 0.9), 'width': int(10 * SCALE), 'height': int(7 * SCALE), 'speed': int(3 * SCALE)}

# bullets (from player)
bullets = []
bullet_speed = int(-5 * SCALE)
bullet_size = int(2 * SCALE)

# bombs (from invaders)
bombs = []
bomb_speed = int(4 * SCALE)
bomb_size = int(2 * SCALE)
bomb_fire_rate = 0.005

# invader types (custom pixel art)
invader_types = [
    {'pixels': [[0,1,0], [1,1,1], [1,0,1]], 'width': int(10 * SCALE), 'height': int(10 * SCALE), 'color': GREEN},
    {'pixels': [[0,0,1,1,0,0], [1,1,1,1,1,1], [1,0,0,0,0,1]], 'width': int(15 * SCALE), 'height': int(10 * SCALE), 'color': RED}
]

# invaders
invaders = []
invader_speed = int(1 * SCALE)
invader_direction = 1
invader_drop = int(5 * SCALE)
rows, cols = 3, 5
spacing_x, spacing_y = int(20 * SCALE), int(15 * SCALE)
frame_count = 0
invader_move_interval = 20

# bunker type (custom pixel art)
bunker_type = {'pixels': [[1,1,1,1,1], [1,1,1,1,1], [0,1,1,1,0]], 'width': int(20 * SCALE), 'height': int(10 * SCALE), 'color': GREEN}

# bunkers
bunkers = []

# init invaders
def init_invaders():
    for row in range(rows):
        for col in range(cols):
            type_idx = row % len(invader_types)
            inv_type = invader_types[type_idx]
            invaders.append({
                'x': int(50 * SCALE + col * spacing_x),
                'y': int(20 * SCALE + row * spacing_y),
                'type': inv_type,
                'width': inv_type['width'],
                'height': inv_type['height'],
                'alive': True
            })

# init bunkers
def init_bunkers():
    bunker_count = 2
    bunker_spacing = WIDTH // (bunker_count + 1)
    for i in range(1, bunker_count + 1):
        pixels_copy = [row[:] for row in bunker_type['pixels']]
        bunkers.append({
            'x': int(i * bunker_spacing - bunker_type['width'] / 2),
            'y': int(HEIGHT * 0.75),
            'type': {'pixels': pixels_copy, 'width': bunker_type['width'], 'height': bunker_type['height'], 'color': bunker_type['color']},
            'width': bunker_type['width'],
            'height': bunker_type['height']
        })

# buttons
button_a = Button(12)  # left
button_b = Button(13)  # right
button_x = Button(14)  # shoot

# game state
game_over = False
win = False


def update():
    global invader_direction, frame_count, game_over, win

    if button_a.read() and player['x'] > 0:
        player['x'] -= player['speed']
    if button_b.read() and player['x'] < WIDTH - player['width']:
        player['x'] += player['speed']
    if button_x.read() and len(bullets) < 3:
        bullets.append({'x': player['x'] + player['width'] // 2, 'y': player['y'] - bullet_size})
        sleep(0.2)  # debounce shooting


    for i, bullet in enumerate(bullets[:]):
        bullet['y'] += bullet_speed
        if bullet['y'] < 0:
            bullets.pop(i)

    frame_count += 1
    if frame_count % invader_move_interval == 0:
        hit_edge = False
        for invader in invaders:
            if not invader['alive']:
                continue
            invader['x'] += invader_speed * invader_direction
            if invader['x'] <= 0 or invader['x'] + invader['width'] >= WIDTH:
                hit_edge = True
            if invader['y'] + invader['height'] >= player['y']:
                game_over = True
            if random.random() < bomb_fire_rate:
                bombs.append({'x': invader['x'] + invader['width'] // 2, 'y': invader['y'] + invader['height']})

        if hit_edge:
            invader_direction *= -1
            for inv in invaders:
                inv['y'] += invader_drop

    for i, bomb in enumerate(bombs[:]):
        bomb['y'] += bomb_speed
        if bomb['y'] > HEIGHT:
            bombs.pop(i)

    # collisions: bullets vs invaders
    for bi, bullet in enumerate(bullets[:]):
        for invader in invaders:
            if not invader['alive']:
                continue
            if (bullet['x'] < invader['x'] + invader['width'] and
                bullet['x'] + bullet_size > invader['x'] and
                bullet['y'] < invader['y'] + invader['height'] and
                bullet['y'] + bullet_size > invader['y']):
                invader['alive'] = False
                bullets.pop(bi)
                break

    # collisions: bullets vs bunkers
    for bi, bullet in enumerate(bullets[:]):
        for bunker in bunkers:
            if check_hit(bullet['x'], bullet['y'], bullet_size, bullet_size, bunker):
                erode_bunker(bunker, bullet['x'] - bunker['x'], bullet['y'] - bunker['y'])
                bullets.pop(bi)
                break

    # collisions: bombs vs bunkers
    for bi, bomb in enumerate(bombs[:]):
        for bunker in bunkers:
            if check_hit(bomb['x'], bomb['y'], bomb_size, bomb_size, bunker):
                erode_bunker(bunker, bomb['x'] - bunker['x'], bomb['y'] - bunker['y'])
                bombs.pop(bi)
                break

    # collisions: bombs vs player
    for bi, bomb in enumerate(bombs[:]):
        if (bomb['x'] < player['x'] + player['width'] and
            bomb['x'] + bomb_size > player['x'] and
            bomb['y'] < player['y'] + player['height'] and
            bomb['y'] + bomb_size > player['y']):
            game_over = True
            bombs.pop(bi)

    # collisions: bullets vs bombs
    for bi, bullet in enumerate(bullets[:]):
        for boi, bomb in enumerate(bombs[:]):
            if (bullet['x'] < bomb['x'] + bomb_size and
                bullet['x'] + bullet_size > bomb['x'] and
                bullet['y'] < bomb['y'] + bomb_size and
                bullet['y'] + bullet_size > bomb['y']):
                bullets.pop(bi)
                bombs.pop(boi)
                break

    # check win condition
    if all(not inv['alive'] for inv in invaders):
        win = True

# check if projectile hits bunker
def check_hit(proj_x, proj_y, proj_w, proj_h, bunker):
    if (proj_x + proj_w < bunker['x'] or proj_x > bunker['x'] + bunker['width'] or
        proj_y + proj_h < bunker['y'] or proj_y > bunker['y'] + bunker['height']):
        return False
    pixel_size_x = bunker['width'] / len(bunker['type']['pixels'][0])
    pixel_size_y = bunker['height'] / len(bunker['type']['pixels'])
    col = int((proj_x - bunker['x'] + proj_w / 2) / pixel_size_x)
    row = int((proj_y - bunker['y'] + proj_h / 2) / pixel_size_y)
    if (row >= 0 and row < len(bunker['type']['pixels']) and
        col >= 0 and col < len(bunker['type']['pixels'][0]) and
        bunker['type']['pixels'][row][col] == 1):
        return True
    return False

# erode bunker
def erode_bunker(bunker, hit_x, hit_y):
    pixel_size_x = bunker['width'] / len(bunker['type']['pixels'][0])
    pixel_size_y = bunker['height'] / len(bunker['type']['pixels'])
    hit_col = int(hit_x / pixel_size_x)
    hit_row = int(hit_y / pixel_size_y)
    for r in range(-1, 2):
        for c in range(-1, 2):
            row, col = hit_row + r, hit_col + c
            if (row >= 0 and row < len(bunker['type']['pixels']) and
                col >= 0 and col < len(bunker['type']['pixels'][0])):
                bunker['type']['pixels'][row][col] = 0


def draw_invader(invader):
    if not invader['alive']:
        return
    pixel_size_x = invader['width'] / len(invader['type']['pixels'][0])
    pixel_size_y = invader['height'] / len(invader['type']['pixels'])
    display.set_pen(invader['type']['color'])
    for y in range(len(invader['type']['pixels'])):
        for x in range(len(invader['type']['pixels'][y])):
            if invader['type']['pixels'][y][x]:
                display.rectangle(
                    int(invader['x'] + x * pixel_size_x),
                    int(invader['y'] + y * pixel_size_y),
                    int(pixel_size_x),
                    int(pixel_size_y)
                )


def draw_bunker(bunker):
    pixel_size_x = bunker['width'] / len(bunker['type']['pixels'][0])
    pixel_size_y = bunker['height'] / len(bunker['type']['pixels'])
    display.set_pen(bunker['type']['color'])
    for y in range(len(bunker['type']['pixels'])):
        for x in range(len(bunker['type']['pixels'][y])):
            if bunker['type']['pixels'][y][x]:
                display.rectangle(
                    int(bunker['x'] + x * pixel_size_x),
                    int(bunker['y'] + y * pixel_size_y),
                    int(pixel_size_x),
                    int(pixel_size_y)
                )


def draw():
    display.set_pen(BLACK)
    display.clear()

    # player
    display.set_pen(WHITE)
    display.triangle(
        player['x'], player['y'] + player['height'],
        player['x'] + player['width'] // 2, player['y'],
        player['x'] + player['width'], player['y'] + player['height']
    )

    # bullets
    display.set_pen(YELLOW)
    for bullet in bullets:
        display.rectangle(bullet['x'], bullet['y'], bullet_size, bullet_size)

    # bombs
    display.set_pen(RED)
    for bomb in bombs:
        display.rectangle(bomb['x'], bomb['y'], bomb_size, bomb_size)

    # invaders
    for invader in invaders:
        draw_invader(invader)

    # bunkers
    for bunker in bunkers:
        draw_bunker(bunker)

    # game over or win
    if game_over:
        display.set_pen(RED)
        display.text("Game Over", WIDTH // 4, HEIGHT // 2, scale=2)
    elif win:
        display.set_pen(GREEN)
        display.text("You Win!", WIDTH // 4, HEIGHT // 2, scale=2)

    display.update()


init_invaders()
init_bunkers()
while True:
    if not game_over and not win:
        update()
        draw()
    else:
        draw()
    sleep(0.02)  # ~50 FPS
