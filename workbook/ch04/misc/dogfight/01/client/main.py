"""
Dogfight Game Client for Raspberry Pi Pico 2 W
- Dual core architecture:
  - Core 0: Display rendering and button input
  - Core 1: UDP networking
- Connects to server AP
- Renders game state with local prediction
"""

import network
import socket
import time
import _thread
from machine import Pin
from pimoroni import Button, RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import protocol

# WiFi Configuration
SSID = "DOGFIGHT_SERVER"
PASSWORD = "dogfight123"
SERVER_IP = "192.168.4.1" # default IP for AP mode
UDP_PORT = 8888

# Display setup
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
WIDTH, HEIGHT = display.get_bounds()

# Colors
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 100, 255)
CYAN = display.create_pen(0, 200, 200)
ORANGE = display.create_pen(255, 128, 0)
YELLOW = display.create_pen(255, 255, 0)

# Buttons
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# LED
led = RGBLED(6, 7, 8)

# Display constants
PIXEL_SIZE = 2
SCREEN_WIDTH = protocol.GAME_WIDTH * PIXEL_SIZE
SCREEN_HEIGHT = protocol.GAME_HEIGHT * PIXEL_SIZE

# Plane sprite data (same as original)
PLANE0_SHAPES = [
    # 0
    [0,0,0,1,0,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,1,1,1,0,0,0,
     0,1,1,1,1,1,0,0,
     1,1,1,1,1,1,1,0,
     1,1,1,1,1,1,1,0,
     0,0,0,1,0,0,0,0],
    # 1
    [0,0,0,0,0,0,0,0,
     1,1,0,0,0,0,0,1,
     1,1,1,1,1,1,1,0,
     0,1,1,1,1,1,0,0,
     0,1,1,1,1,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0],
    # 2
    [0,1,1,0,0,0,0,0,
     0,1,1,1,0,0,0,0,
     0,1,1,1,1,0,0,0,
     1,1,1,1,1,1,1,1,
     0,1,1,1,1,0,0,0,
     0,1,1,1,0,0,0,0,
     0,1,1,0,0,0,0,0,
     0,0,0,0,0,0,0,0],
    # 3
    [0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,1,1,1,1,0,0,0,
     0,1,1,1,1,1,0,0,
     1,1,1,1,1,1,1,0,
     1,1,0,0,0,0,0,1,
     0,0,0,0,0,0,0,0],
    # 4
    [0,0,0,1,0,0,0,0,
     1,1,1,1,1,1,1,0,
     1,1,1,1,1,1,1,0,
     0,1,1,1,1,1,0,0,
     0,0,1,1,1,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,0,0,0,0,0,0],
    # 5
    [0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,1,1,1,1,0,
     0,0,1,1,1,1,1,0,
     0,1,1,1,1,1,1,1,
     1,0,0,0,0,0,1,1,
     0,0,0,0,0,0,0,0],
    # 6
    [0,0,0,0,0,1,1,0,
     0,0,0,0,1,1,1,0,
     0,0,0,1,1,1,1,0,
     1,1,1,1,1,1,1,1,
     0,0,0,1,1,1,1,0,
     0,0,0,0,1,1,1,0,
     0,0,0,0,0,1,1,0,
     0,0,0,0,0,0,0,0],
    # 7
    [0,0,0,0,0,0,0,0,
     1,0,0,0,0,0,1,1,
     0,1,1,1,1,1,1,1,
     0,0,1,1,1,1,1,0,
     0,0,0,1,1,1,1,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0],
]

PLANE1_SHAPES = [
    # 0
    [0,0,0,1,0,0,0,0,
     0,0,1,1,1,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,1,1,1,0,0,0,
     0,1,1,1,1,1,0,0,
     1,1,1,1,1,1,1,0,
     1,1,1,1,1,1,1,0,
     0,0,0,1,0,0,0,0],
    # 1
    [0,0,0,0,0,0,0,0,
     1,1,0,0,0,1,0,1,
     1,1,1,1,1,1,1,0,
     0,1,1,1,1,1,0,1,
     0,1,1,1,1,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0],
    # 2
    [0,1,1,0,0,0,0,0,
     0,1,1,1,0,0,0,0,
     0,1,1,1,1,0,1,0,
     1,1,1,1,1,1,1,1,
     0,1,1,1,1,0,1,0,
     0,1,1,1,0,0,0,0,
     0,1,1,0,0,0,0,0,
     0,0,0,0,0,0,0,0],
    # 3
    [0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,0,1,1,0,0,0,0,
     0,1,1,1,1,0,0,0,
     0,1,1,1,1,1,0,1,
     1,1,1,1,1,1,1,0,
     1,1,0,0,0,1,0,1,
     0,0,0,0,0,0,0,0],
    # 4
    [0,0,0,1,0,0,0,0,
     1,1,1,1,1,1,1,0,
     1,1,1,1,1,1,1,0,
     0,1,1,1,1,1,0,0,
     0,0,1,1,1,0,0,0,
     0,0,0,1,0,0,0,0,
     0,0,1,1,1,0,0,0,
     0,0,0,1,0,0,0,0],
    # 5
    [0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,1,1,1,1,0,
     1,0,1,1,1,1,1,0,
     0,1,1,1,1,1,1,1,
     1,0,1,0,0,0,1,1,
     0,0,0,0,0,0,0,0],
    # 6
    [0,0,0,0,0,1,1,0,
     0,0,0,0,1,1,1,0,
     0,1,0,1,1,1,1,0,
     1,1,1,1,1,1,1,1,
     0,1,0,1,1,1,1,0,
     0,0,0,0,1,1,1,0,
     0,0,0,0,0,1,1,0,
     0,0,0,0,0,0,0,0],
    # 7
    [0,0,0,0,0,0,0,0,
     1,0,1,0,0,0,1,1,
     0,1,1,1,1,1,1,1,
     1,0,1,1,1,1,1,0,
     0,0,0,1,1,1,1,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0,
     0,0,0,0,1,1,0,0],
]

# Shared state between cores
class SharedState:
    def __init__(self):
        self.lock = _thread.allocate_lock()
        
        # Network state
        self.connected = False
        self.player_id = 0
        
        # Game state
        self.p1_x = 0
        self.p1_y = 0
        self.p1_dir = 0
        self.p1_alive = True
        
        self.p2_x = 0
        self.p2_y = 0
        self.p2_dir = 0
        self.p2_alive = True
        
        self.shots = []  # List of {x, y, dir, range, owner}
        
        self.game_over = False
        self.winner = 0
        self.last_seq = 0
        
        # Input state (written by core 0, read by core 1)
        self.btn_a = False
        self.btn_b = False
        self.btn_x = False
        self.btn_y = False
        
        # Prediction state
        self.local_predict = True
    
    # Update from network packet (called by core 1)
    def update_game_state(self, state):
        with self.lock:
            if 'seq' in state:
                self.last_seq = state['seq']
            
            if 'p1' in state:
                if 'x' in state['p1']:
                    self.p1_x = state['p1']['x']
                if 'y' in state['p1']:
                    self.p1_y = state['p1']['y']
                if 'dir' in state['p1']:
                    self.p1_dir = state['p1']['dir']
                if 'alive' in state['p1']:
                    self.p1_alive = state['p1']['alive']
            
            if 'p2' in state:
                if 'x' in state['p2']:
                    self.p2_x = state['p2']['x']
                if 'y' in state['p2']:
                    self.p2_y = state['p2']['y']
                if 'dir' in state['p2']:
                    self.p2_dir = state['p2']['dir']
                if 'alive' in state['p2']:
                    self.p2_alive = state['p2']['alive']
            
            if 'shots' in state:
                self.shots = state['shots']
            
            if 'shots_added' in state:
                self.shots.extend(state['shots_added'])
            
            if 'shots_removed' in state:
                # Remove shots by approximate position
                for rem_x, rem_y in state['shots_removed']:
                    self.shots = [s for s in self.shots 
                                 if not (abs(s['x'] - rem_x) < 3 and abs(s['y'] - rem_y) < 3)]
            
            if 'game_over' in state:
                self.game_over = state['game_over']
                if 'winner' in state:
                    self.winner = state['winner']
    

    # Get state snapshot for rendering (called by core 0)
    def get_display_state(self):
        with self.lock:
            return {
                'p1': {'x': self.p1_x, 'y': self.p1_y, 'dir': self.p1_dir, 'alive': self.p1_alive},
                'p2': {'x': self.p2_x, 'y': self.p2_y, 'dir': self.p2_dir, 'alive': self.p2_alive},
                'shots': list(self.shots),
                'game_over': self.game_over,
                'winner': self.winner,
                'player_id': self.player_id,
                'connected': self.connected
            }
    
    # Update input state (called by core 0)
    def set_input(self, a, b, x, y):
        with self.lock:
            self.btn_a = a
            self.btn_b = b
            self.btn_x = x
            self.btn_y = y
    
    def get_input(self):
        """Get input snapshot (called by core 1)"""
        with self.lock:
            return (self.btn_a, self.btn_b, self.btn_x, self.btn_y)
    
    def set_connected(self, connected, player_id=0):
        """Update connection state (called by core 1)"""
        with self.lock:
            self.connected = connected
            self.player_id = player_id

# connect AP
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print(f"Waiting for connection.. {max_wait}")
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError("Network connection failed")
    
    print(f"Connected: {wlan.ifconfig()}")
    return wlan

# Network thread
def network_thread(shared_state):
    print("Network thread starting..")
    
    try:
        # Connect to WiFi
        wlan = connect_wifi()
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        
        # Request player ID
        server_addr = (SERVER_IP, UDP_PORT)
        connect_packet = protocol.ConnectPacket.pack_request()
        
        for _ in range(5):
            sock.sendto(connect_packet, server_addr)
            time.sleep(0.2)
            
            try:
                data, addr = sock.recvfrom(256)
                if len(data) > 0 and data[0] == protocol.PKT_CLIENT_ACK:
                    ack = protocol.ConnectPacket.unpack(data)
                    player_id = ack['player_id']
                    shared_state.set_connected(True, player_id)
                    print(f"Connected as Player {player_id}")
                    break
            except:
                pass
        
        if not shared_state.connected:
            print("Failed to get player ID")
            return
        
        # Main network loop
        while True:
            # Send input
            btn_a, btn_b, btn_x, btn_y = shared_state.get_input()
            input_packet = protocol.ClientInputPacket.pack(
                shared_state.player_id, btn_a, btn_b, btn_x, btn_y
            )
            sock.sendto(input_packet, server_addr)
            
            # Receive state updates
            try:
                data, addr = sock.recvfrom(512)
                if len(data) > 0:
                    pkt_type = data[0]
                    
                    if pkt_type == protocol.PKT_FULL_STATE:
                        state = protocol.FullStatePacket.unpack(data)
                        shared_state.update_game_state(state)
                    
                    elif pkt_type == protocol.PKT_DELTA_STATE:
                        delta = protocol.DeltaStatePacket.unpack(data)
                        shared_state.update_game_state(delta)
            
            except OSError:
                pass  # No data
            
            time.sleep_ms(50)  # 20Hz network updates
    
    except Exception as e:
        print(f"Network thread error: {e}")
        shared_state.set_connected(False)


def draw_plane(x, y, dir, plane_type, color):
    shapes = PLANE1_SHAPES if plane_type == 1 else PLANE0_SHAPES
    shape = shapes[dir]
    
    for dy in range(8):
        for dx in range(8):
            if shape[dy * 8 + dx]:
                px = (x + dx - 4) * PIXEL_SIZE
                py = (y + dy - 4) * PIXEL_SIZE
                if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                    display.set_pen(color)
                    display.rectangle(px, py, PIXEL_SIZE, PIXEL_SIZE)

def render_game(state):
    # Clear
    display.set_pen(BLACK)
    display.clear()
    
    # Draw player 1 (Blue)
    if state['p1']['alive']:
        draw_plane(state['p1']['x'], state['p1']['y'], state['p1']['dir'], 0, BLUE)
    
    # Draw player 2 (Red)
    if state['p2']['alive']:
        draw_plane(state['p2']['x'], state['p2']['y'], state['p2']['dir'], 1, RED)
    
    # Draw shots
    for shot in state['shots']:
        if shot['owner'] == 1:
            display.set_pen(CYAN)
        else:
            display.set_pen(ORANGE)
        
        x = shot['x'] * PIXEL_SIZE
        y = shot['y'] * PIXEL_SIZE
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            display.rectangle(x, y, PIXEL_SIZE, PIXEL_SIZE)
    
    # Draw game over
    if state['game_over']:
        display.set_pen(BLACK)
        display.rectangle(60, 95, 200, 50)
        winner_color = BLUE if state['winner'] == 1 else RED
        display.set_pen(winner_color)
        winner_text = "BLUE WINS!" if state['winner'] == 1 else "RED WINS!"
        display.text(winner_text, 70, 110, scale=3)
    
    # Draw connection status
    if not state['connected']:
        display.set_pen(YELLOW)
        display.text("CONNECTING..", 80, 5, scale=2)
    else:
        # Show player ID
        display.set_pen(BLUE if state['player_id'] == 1 else RED)
        display.text(f"P{state['player_id']}", 5, 5, scale=2)
    
    display.update()

# render and input
def main():
    print("Starting Dogfight Client..")
    
    # Init shared state
    shared_state = SharedState()
    
    # Start network thread on core 1
    _thread.start_new_thread(network_thread, (shared_state,))
    
    # Show startup screen
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(CYAN)
    display.text("DOGFIGHT", 80, 80, scale=4)
    display.set_pen(WHITE)
    display.text("Connecting...", 90, 130, scale=2)
    display.update()
    time.sleep(2)
    
    led.set_rgb(0, 0, 255)  # Blue = starting
    
    # Main render loop
    while True:
        # Read buttons
        btn_a = button_a.read()
        btn_b = button_b.read()
        btn_x = button_x.read()
        btn_y = button_y.read()
        
        # Update shared input state
        shared_state.set_input(btn_a, btn_b, btn_x, btn_y)
        
        # Get game state snapshot
        state = shared_state.get_display_state()
        
        # Update LED
        if state['connected']:
            if state['game_over']:
                if state['winner'] == state['player_id']:
                    led.set_rgb(0, 255, 0)  # Green = won
                else:
                    led.set_rgb(255, 0, 0)  # Red = lost
            else:
                led.set_rgb(0, 100, 100)  # Cyan = playing
        else:
            led.set_rgb(255, 255, 0)  # Yellow = connecting
        
        # Render
        render_game(state)
        
        # ~10 FPS
        time.sleep(0.1)

if __name__ == "__main__":
    main()
