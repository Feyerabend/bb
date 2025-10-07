import machine
import st7789  # From Pimoroni UF2 or copy lib?
import random
import math
import time
import _thread
import array

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
MAX_PARTICLES = 800
GRAVITY = 0.15
BOUNCE_DAMPING = 0.85
PARTICLE_RADIUS = 2
BOUNDS_LEFT = 0
BOUNDS_RIGHT = DISPLAY_WIDTH
BOUNDS_TOP = 30  # Space for status
BOUNDS_BOTTOM = DISPLAY_HEIGHT

COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_YELLOW = 0xFFE0
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F

BUTTON_A = 12
BUTTON_B = 13
BUTTON_X = 14
BUTTON_Y = 15

# Particle structure (use arrays for speed: [x, y, vx, vy, color, core_id] per particle)
particles = []  # List of arrays
particle_count = MAX_PARTICLES

# Colors
particle_colors = [COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW, COLOR_CYAN, COLOR_MAGENTA, 0xFD20, 0x07FF, 0xF81F, 0xFFE0]

# Globals
wind_x = 0.0
wind_y = 0.0
core1_ready = False
rendering_done = True
current_fps = 0.0

# Display setup (using Pimoroni/ST7789 lib .. or write own?)
spi = machine.SPI(0, baudrate=31250000, sck=machine.Pin(18), mosi=machine.Pin(19))
display = st7789.ST7789(
    spi,
    DISPLAY_HEIGHT,  # Note: Often rotated
    DISPLAY_WIDTH,
    reset=machine.Pin(21, machine.Pin.OUT),
    cs=machine.Pin(17, machine.Pin.OUT),
    dc=machine.Pin(16, machine.Pin.OUT),
    backlight=machine.Pin(20, machine.Pin.OUT),
    rotation=1  # Adjust if needed for orientation
)
display.init()
display.fill(COLOR_BLACK)
display.backlight(1)  # On

# Framebuffer (RGB565 bytes)
framebuffer = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT * 2)
fb = framebuf.FrameBuffer(framebuffer, DISPLAY_WIDTH, DISPLAY_HEIGHT, framebuf.RGB565)

# Buttons
buttons = {
    'A': machine.Pin(BUTTON_A, machine.Pin.IN, machine.Pin.PULL_UP),
    'B': machine.Pin(BUTTON_B, machine.Pin.IN, machine.Pin.PULL_UP),
    'X': machine.Pin(BUTTON_X, machine.Pin.IN, machine.Pin.PULL_UP),
    'Y': machine.Pin(BUTTON_Y, machine.Pin.IN, machine.Pin.PULL_UP)
}
prev_buttons = {'A': 1, 'B': 1, 'X': 1, 'Y': 1}  # Pulled high = 1 (not pressed)

def randf(min_val, max_val):
    return min_val + random.random() * (max_val - min_val)

def init_particles():
    global particles
    particles = []
    for _ in range(MAX_PARTICLES):
        p = array.array('f', [randf(BOUNDS_LEFT + 10, BOUNDS_RIGHT - 10),
                              randf(BOUNDS_TOP + 10, BOUNDS_BOTTOM - 10),
                              randf(-2.0, 2.0),
                              randf(-2.0, 2.0)])
        p.append(random.choice(particle_colors))  # color (int)
        p.append(0)  # core_id (int)
        particles.append(p)

def update_particles_range(start, end, core_id):
    for i in range(start, end):
        p = particles[i]
        # Gravity and wind
        p[3] += GRAVITY  # vy
        p[2] += wind_x * 0.1  # vx
        p[3] += wind_y * 0.1  # vy
        
        # Position
        p[0] += p[2]  # x += vx
        p[1] += p[3]  # y += vy
        
        # Boundaries
        if p[0] <= BOUNDS_LEFT + PARTICLE_RADIUS:
            p[0] = BOUNDS_LEFT + PARTICLE_RADIUS
            p[2] = -p[2] * BOUNCE_DAMPING
        if p[0] >= BOUNDS_RIGHT - PARTICLE_RADIUS:
            p[0] = BOUNDS_RIGHT - PARTICLE_RADIUS
            p[2] = -p[2] * BOUNCE_DAMPING
        if p[1] <= BOUNDS_TOP + PARTICLE_RADIUS:
            p[1] = BOUNDS_TOP + PARTICLE_RADIUS
            p[3] = -p[3] * BOUNCE_DAMPING
        if p[1] >= BOUNDS_BOTTOM - PARTICLE_RADIUS:
            p[1] = BOUNDS_BOTTOM - PARTICLE_RADIUS
            p[3] = -p[3] * BOUNCE_DAMPING
            p[2] *= 0.95  # Friction
        
        p[5] = core_id

def render_particles():
    # Clear game area
    fb.fill_rect(0, BOUNDS_TOP, DISPLAY_WIDTH, DISPLAY_HEIGHT - BOUNDS_TOP, COLOR_BLACK)
    
    # Draw particles (3x3 rect for visibility)
    for p in particles[:particle_count]:
        px, py = int(p[0]), int(p[1])
        if 0 <= px < DISPLAY_WIDTH and BOUNDS_TOP <= py < DISPLAY_HEIGHT:
            fb.fill_rect(px - 1, py - 1, 3, 3, int(p[4]))  # color

def draw_status_bar():
    # Simplified: Text instead of bars
    fb.fill_rect(0, 0, DISPLAY_WIDTH, BOUNDS_TOP - 2, COLOR_BLACK)
    fb.text(f'FPS: {current_fps:.1f}', 5, 5, COLOR_WHITE)
    fb.text(f'Particles: {particle_count}', 100, 5, COLOR_WHITE)
    # Add core cycles if you measure them

def handle_input():
    global wind_x, wind_y, particle_count, prev_buttons
    
    # Read buttons (0 = pressed)
    curr = {k: b.value() for k, b in buttons.items()}
    
    # A: Reset
    if curr['A'] == 0 and prev_buttons['A'] == 1:
        init_particles()
        print("Particles reset!")
    
    # B: Cycle particle count
    if curr['B'] == 0 and prev_buttons['B'] == 1:
        particle_count += 100
        if particle_count > MAX_PARTICLES:
            particle_count = 100
        print(f"Particle count: {particle_count}")
    
    # X: Wind right
    if curr['X'] == 0:
        wind_x = 0.5
    else:
        wind_x *= 0.95
    
    # Y: Wind up
    if curr['Y'] == 0:
        wind_y = -0.3
    else:
        wind_y *= 0.95
    
    prev_buttons = curr

def core1_entry():
    global core1_ready, rendering_done
    print("Core 1 started")
    while True:
        while not core1_ready:
            pass
        start = time.ticks_ms()
        mid = particle_count // 2
        update_particles_range(mid, particle_count, 1)
        core1_cycles = time.ticks_diff(time.ticks_ms(), start)  # Approximate
        core1_ready = False
        rendering_done = True

# Main
print("--- MicroPython Particle System ---")
init_particles()
display.fill(COLOR_BLACK)

# Start core 1
_thread.start_new_thread(core1_entry, ())

last_fps_time = time.ticks_ms()
frame_count = 0

while True:
    handle_input()
    
    # Core 0 updates
    start = time.ticks_ms()
    mid = particle_count // 2
    update_particles_range(0, mid, 0)
    core0_cycles = time.ticks_diff(time.ticks_ms(), start)
    
    # Signal core 1
    rendering_done = False
    core1_ready = True
    
    # Wait for core 1
    while not rendering_done:
        pass
    
    # Render (core 0 only)
    render_particles()
    draw_status_bar()
    
    # Blit to display
    display.blit_buffer(framebuffer, 0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT)
    
    # FPS
    frame_count += 1
    now = time.ticks_ms()
    if time.ticks_diff(now, last_fps_time) >= 1000:
        current_fps = frame_count * 1000 / time.ticks_diff(now, last_fps_time)
        frame_count = 0
        last_fps_time = now
        print(f"FPS: {current_fps:.1f} | Particles: {particle_count}")
    
    time.sleep_ms(16)  # ~60 FPS target
