"""
Dogfight Game Server for Raspberry Pi Pico W
- Creates WiFi Access Point
- Runs game logic
- Sends state updates to clients via UDP
- Displays game status on Pimoroni Display Pack 2.0
"""

import network
import socket
import time
import _thread
from machine import Pin
from pimoroni import Button, RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import protocol

# WiFi AP Configuration
SSID = "DOGFIGHT_SERVER"
PASSWORD = "dogfight123" # skip for test
SERVER_IP = "192.168.4.1"
UDP_PORT = 8888

# Display setup
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 100, 255)
CYAN = display.create_pen(0, 200, 200)
ORANGE = display.create_pen(255, 128, 0)

# Buttons
button_y = Button(15)

# LED
led = RGBLED(6, 7, 8)

class Shot:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.dir = direction
        self.range = 18
        self.active = True
        self.owner = owner  # 1 or 2
    
    def update(self):
        if not self.active:
            return
        
        # Move shot (2x speed)
        for _ in range(2):
            self.x += protocol.DIR_DX[self.dir]
            self.y += protocol.DIR_DY[self.dir]
        
        # Wrap around
        if self.x < 0: self.x = protocol.GAME_WIDTH - 1
        if self.x >= protocol.GAME_WIDTH: self.x = 0
        if self.y < 0: self.y = protocol.GAME_HEIGHT - 1
        if self.y >= protocol.GAME_HEIGHT: self.y = 0
        
        self.range -= 1
        if self.range <= 0:
            self.active = False
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'dir': self.dir,
            'range': self.range,
            'owner': self.owner
        }

class Player:
    def __init__(self, player_id, start_x, start_y, start_dir):
        self.id = player_id
        self.x = start_x
        self.y = start_y
        self.dir = start_dir
        self.alive = True
        self.shots = []
        self.fire_cooldown = 0
        self.turn_counter = 0
        
        # Input state
        self.btn_a = False
        self.btn_b = False
        self.btn_x = False
        self.btn_y = False
        self.prev_fire = False
    
    def update_input(self, btn_a, btn_b, btn_x, btn_y):
        self.btn_a = btn_a
        self.btn_b = btn_b
        self.btn_x = btn_x
        self.btn_y = btn_y
    
    def update(self):
        if not self.alive:
            return False  # No position change
        
        old_x, old_y, old_dir = self.x, self.y, self.dir
        
        # Handle turning
        if self.btn_a and self.btn_b:
            # Fire
            if not self.prev_fire:
                self.fire()
            self.prev_fire = True
        else:
            if self.btn_a:
                self.turn_left()
            elif self.btn_b:
                self.turn_right()
            self.prev_fire = False
        
        # Move
        self.x += protocol.DIR_DX[self.dir]
        self.y += protocol.DIR_DY[self.dir]
        
        # Wrap
        if self.x < 4: self.x = protocol.GAME_WIDTH - 5
        if self.x >= protocol.GAME_WIDTH - 4: self.x = 4
        if self.y < 4: self.y = protocol.GAME_HEIGHT - 5
        if self.y >= protocol.GAME_HEIGHT - 4: self.y = 4
        
        # Update shots
        for shot in self.shots[:]:
            shot.update()
            if not shot.active:
                self.shots.remove(shot)
        
        # Update cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        
        # Return True if position or direction changed
        return (old_x != self.x or old_y != self.y or old_dir != self.dir)
    
    def fire(self):
        if self.fire_cooldown == 0 and len(self.shots) < 3:
            nose_x = self.x + protocol.DIR_DX[self.dir] * 4
            nose_y = self.y + protocol.DIR_DY[self.dir] * 4
            self.shots.append(Shot(nose_x, nose_y, self.dir, self.id))
            self.fire_cooldown = 12
            return True
        return False
    
    def turn_left(self):
        self.turn_counter += 1
        if self.turn_counter >= 2:
            self.dir = (self.dir - 1) % 8
            self.turn_counter = 0
    
    def turn_right(self):
        self.turn_counter += 1
        if self.turn_counter >= 2:
            self.dir = (self.dir + 1) % 8
            self.turn_counter = 0
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'dir': self.dir,
            'alive': self.alive
        }

class GameServer:
    def __init__(self):
        self.players = {}
        self.player1 = Player(1, protocol.GAME_WIDTH - 15, protocol.GAME_HEIGHT - 15, protocol.DIR_W)
        self.player2 = Player(2, 15, 15, protocol.DIR_E)
        self.players[1] = self.player1
        self.players[2] = self.player2
        
        self.clients = {}  # client_addr -> player_id
        self.game_over = False
        self.winner = 0
        self.seq = 0
        
        self.last_full_sync = 0
        self.full_sync_interval = 30  # Full sync every 30 frames
        
        # Track previous state for delta detection
        self.prev_state = {}
        self.prev_shots = {}
    
    def reset(self):
        self.player1 = Player(1, protocol.GAME_WIDTH - 15, protocol.GAME_HEIGHT - 15, protocol.DIR_W)
        self.player2 = Player(2, 15, 15, protocol.DIR_E)
        self.players[1] = self.player1
        self.players[2] = self.player2
        self.game_over = False
        self.winner = 0
        self.seq = 0
        self.prev_state = {}
        self.prev_shots = {}

    # Handle incoming packets from clients
    def handle_input(self, data, addr):
        if len(data) < 1:
            return
        
        pkt_type = data[0]
        
        if pkt_type == protocol.PKT_CLIENT_CONNECT:
            # Assign player ID
            if addr not in self.clients:
                player_id = 1 if len(self.clients) == 0 else 2
                self.clients[addr] = player_id
                print(f"Client connected: {addr} -> Player {player_id}")
            return protocol.ConnectPacket.pack_ack(self.clients[addr])
        
        elif pkt_type == protocol.PKT_CLIENT_INPUT:
            if addr in self.clients:
                input_data = protocol.ClientInputPacket.unpack(data)
                player_id = self.clients[addr]
                player = self.players.get(player_id)
                if player:
                    player.update_input(
                        input_data['btn_a'],
                        input_data['btn_b'],
                        input_data['btn_x'],
                        input_data['btn_y']
                    )
        
        return None

    # Game state update
    def update(self):
        if self.game_over:
            return
        
        # Update both players
        p1_changed = self.player1.update()
        p2_changed = self.player2.update()
        
        # Check collisions
        if not self.game_over:
            # Player 1 shots hit player 2
            for shot in self.player1.shots:
                if self.check_shot_hit(shot, self.player2):
                    self.game_over = True
                    self.winner = 1
                    self.player2.alive = False
                    break
            
            # Player 2 shots hit player 1
            if not self.game_over:
                for shot in self.player2.shots:
                    if self.check_shot_hit(shot, self.player1):
                        self.game_over = True
                        self.winner = 2
                        self.player1.alive = False
                        break
    
    # Check if a shot hits a target player
    def check_shot_hit(self, shot, target):
        if not shot.active or not target.alive:
            return False
        
        # Check if shot is near target (simplified - no sprite checking)
        dx = abs(shot.x - target.x)
        dy = abs(shot.y - target.y)
        
        if dx < 4 and dy < 4:
            shot.active = False
            return True
        return False
    
    # Generate state packet (full or delta)
    def get_state_packet(self, force_full=False):
        self.seq += 1
        
        # Force full sync periodically or on game state change
        if force_full or self.seq - self.last_full_sync >= self.full_sync_interval or self.game_over:
            self.last_full_sync = self.seq
            return self.get_full_state_packet()
        else:
            return self.get_delta_packet()
    
    def get_full_state_packet(self):
        p1_shots = [s.to_dict() for s in self.player1.shots if s.active]
        p2_shots = [s.to_dict() for s in self.player2.shots if s.active]
        
        # Store current state
        self.prev_state = {
            1: (self.player1.x, self.player1.y, self.player1.dir),
            2: (self.player2.x, self.player2.y, self.player2.dir)
        }
        self.prev_shots = {
            1: set((s.x, s.y) for s in self.player1.shots if s.active),
            2: set((s.x, s.y) for s in self.player2.shots if s.active)
        }
        
        return protocol.FullStatePacket.pack(
            self.seq,
            self.player1.to_dict(),
            self.player2.to_dict(),
            p1_shots,
            p2_shots,
            self.game_over,
            self.winner
        )

    # changes only
    def get_delta_packet(self):
        p1_pos = None
        p2_pos = None
        shots_added = []
        shots_removed = []
        
        # Check player position changes
        if 1 in self.prev_state:
            px, py, pd = self.prev_state[1]
            if px != self.player1.x or py != self.player1.y or pd != self.player1.dir:
                p1_pos = {'x': self.player1.x, 'y': self.player1.y}
                if pd != self.player1.dir:
                    p1_pos['dir'] = self.player1.dir
        
        if 2 in self.prev_state:
            px, py, pd = self.prev_state[2]
            if px != self.player2.x or py != self.player2.y or pd != self.player2.dir:
                p2_pos = {'x': self.player2.x, 'y': self.player2.y}
                if pd != self.player2.dir:
                    p2_pos['dir'] = self.player2.dir
        
        # Check shot changes
        current_p1_shots = set((s.x, s.y) for s in self.player1.shots if s.active)
        current_p2_shots = set((s.x, s.y) for s in self.player2.shots if s.active)
        
        # Shots added
        if 1 in self.prev_shots:
            new_shots = current_p1_shots - self.prev_shots[1]
            for sx, sy in new_shots:
                for shot in self.player1.shots:
                    if shot.active and shot.x == sx and shot.y == sy:
                        shots_added.append(shot.to_dict())
                        break
        
        if 2 in self.prev_shots:
            new_shots = current_p2_shots - self.prev_shots[2]
            for sx, sy in new_shots:
                for shot in self.player2.shots:
                    if shot.active and shot.x == sx and shot.y == sy:
                        shots_added.append(shot.to_dict())
                        break
        
        # Shots removed
        if 1 in self.prev_shots:
            removed = self.prev_shots[1] - current_p1_shots
            shots_removed.extend(list(removed))
        
        if 2 in self.prev_shots:
            removed = self.prev_shots[2] - current_p2_shots
            shots_removed.extend(list(removed))
        
        # Update previous state
        self.prev_state = {
            1: (self.player1.x, self.player1.y, self.player1.dir),
            2: (self.player2.x, self.player2.y, self.player2.dir)
        }
        self.prev_shots = {
            1: current_p1_shots,
            2: current_p2_shots
        }
        
        return protocol.DeltaStatePacket.pack(
            self.seq,
            p1_pos,
            p2_pos,
            shots_added,
            shots_removed,
            self.game_over,
            self.winner
        )

# access point
def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f"AP Active: {SSID}")
    print(f"IP: {ap.ifconfig()[0]}")
    return ap

# game status
def display_status(game, client_count):
    display.set_pen(BLACK)
    display.clear()
    
    # Title
    display.set_pen(CYAN)
    display.text("DOGFIGHT SERVER", 10, 10, scale=2)
    
    # Connection status
    display.set_pen(WHITE)
    display.text(f"Clients: {client_count}/2", 10, 40, scale=2)
    
    # Player status
    display.set_pen(BLUE)
    p1_status = "ALIVE" if game.player1.alive else "DEAD"
    display.text(f"P1(Blue): {p1_status}", 10, 70, scale=2)
    
    display.set_pen(RED)
    p2_status = "ALIVE" if game.player2.alive else "DEAD"
    display.text(f"P2(Red): {p2_status}", 10, 95, scale=2)
    
    # Game state
    if game.game_over:
        display.set_pen(GREEN)
        winner_color = "BLUE" if game.winner == 1 else "RED"
        display.text(f"{winner_color} WINS!", 10, 130, scale=3)
    else:
        display.set_pen(ORANGE)
        display.text(f"Frame: {game.seq}", 10, 130, scale=2)
    
    # Shot counts
    display.set_pen(WHITE)
    display.text(f"P1 Shots: {len(game.player1.shots)}", 10, 160, scale=1)
    display.text(f"P2 Shots: {len(game.player2.shots)}", 10, 175, scale=1)
    
    display.update()

def main():
    print("Starting Dogfight Server..")
    
    # Setup AP
    ap = setup_ap()
    led.set_rgb(0, 255, 0)  # Green = ready
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, UDP_PORT))
    sock.setblocking(False)
    
    print(f"Listening on {SERVER_IP}:{UDP_PORT}")
    
    # Initialize game
    game = GameServer()
    
    frame_count = 0
    last_display_update = 0
    
    while True:
        frame_start = time.ticks_ms()
        
        # Check reset button
        if button_y.read():
            print("Reset game")
            game.reset()
            led.set_rgb(255, 255, 0)  # Yellow = reset
            time.sleep(0.2)
            led.set_rgb(0, 255, 0)
        
        # Receive input from clients
        try:
            while True:
                data, addr = sock.recvfrom(256)
                response = game.handle_input(data, addr)
                if response:
                    sock.sendto(response, addr)
        except OSError:
            pass  # No data available
        
        # Update game logic
        game.update()
        
        # Generate and send state packet
        state_packet = game.get_state_packet()
        
        # Broadcast to all connected clients
        for addr in game.clients.keys():
            try:
                sock.sendto(state_packet, addr)
            except:
                pass
        
        # Update display every 5 frames
        if frame_count - last_display_update >= 5:
            display_status(game, len(game.clients))
            last_display_update = frame_count
        
        # LED indicator
        if game.game_over:
            if game.winner == 1:
                led.set_rgb(0, 0, 255)  # Blue wins
            else:
                led.set_rgb(255, 0, 0)  # Red wins
        else:
            intensity = 50 if len(game.clients) == 2 else 10
            led.set_rgb(0, intensity, intensity)
        
        frame_count += 1
        
        # Target ~10 FPS (100ms per frame)
        elapsed = time.ticks_diff(time.ticks_ms(), frame_start)
        sleep_time = max(0, 100 - elapsed)
        time.sleep_ms(sleep_time)

if __name__ == "__main__":
    main()
