import network
import socket
import time
import struct
import random
from machine import Pin, Timer

# Network Configuration
SSID = "PicoGPU_Test"
PASSWORD = "testgpu123"
UDP_PORT = 8080
UDP_RESPONSE_PORT = 8081

# Network Command Types (matching C implementation)
NET_MOVE_OBJECT = 0
NET_DRAW_SPRITE = 1
NET_UPDATE_TILEMAP = 2
NET_CLEAR_SCREEN = 3
NET_SET_PALETTE = 4

# Network Response Types (matching C implementation)
NET_COLLISION_DETECTED = 0
NET_OBJECT_OUT_OF_BOUNDS = 1
NET_RENDER_COMPLETE = 2
NET_HEARTBEAT = 3
NET_ERROR = 4

# Game state
class GameObject:
    def __init__(self, obj_id, x=0, y=0):
        self.id = obj_id
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.frame = 0
        self.active = True

# Global game objects
game_objects = {}
client_address = None

# LED for status indication
led = Pin("LED", Pin.OUT)

def setup_access_point():
    """Set up the Pico W as an access point"""
    print("Setting up Access Point...")
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD, authmode=3)  # WPA2
    
    # Wait for AP to be active
    while not ap.active():
        time.sleep(0.1)
    
    print(f"Access Point '{SSID}' created")
    print(f"IP Address: {ap.ifconfig()[0]}")
    print(f"Connect your GPU Pico W to this network")
    
    return ap

def create_network_packet(command, object_id=0, x=0, y=0, velocity_x=0, velocity_y=0, frame=0):
    """Create a network packet matching the C struct"""
    # Pack as: command(1), object_id(1), x(2), y(2), velocity_x(2), velocity_y(2), frame(1)
    # Total: 11 bytes, but pad to match C struct alignment
    return struct.pack('<BBHHHHHB', command, object_id, 
                       x & 0xFFFF, y & 0xFFFF, 
                       velocity_x & 0xFFFF, velocity_y & 0xFFFF, frame, 0)

def parse_response_packet(data):
    """Parse response packet from GPU Pico W"""
    if len(data) >= 10:  # Minimum expected size
        try:
            # response(1), object1_id(1), object2_id(1), x(2), y(2), timestamp(4)
            response, obj1, obj2, x, y, timestamp = struct.unpack('<BBBHHI', data[:11])
            return {
                'response': response,
                'object1_id': obj1,
                'object2_id': obj2,
                'x': x,
                'y': y,
                'timestamp': timestamp
            }
        except:
            pass
    return None

def handle_client_response(sock):
    """Handle responses from the GPU Pico W"""
    global client_address
    
    try:
        data, addr = sock.recvfrom(1024)
        if not client_address:
            client_address = addr
            print(f"GPU Client connected from: {addr}")
            led.on()  # Turn on LED when client connects
        
        response = parse_response_packet(data)
        if response:
            resp_type = response['response']
            if resp_type == NET_COLLISION_DETECTED:
                print(f"COLLISION: Object {response['object1_id']} hit Object {response['object2_id']}")
            elif resp_type == NET_HEARTBEAT:
                print("Heartbeat received from GPU")
            elif resp_type == NET_ERROR:
                print(f"GPU Error: {response}")
            else:
                print(f"Unknown response: {response}")
                
    except OSError:
        pass  # No data available

def send_command(sock, command, object_id=0, x=0, y=0, velocity_x=0, velocity_y=0, frame=0):
    """Send a command to the GPU Pico W"""
    if client_address:
        packet = create_network_packet(command, object_id, x, y, velocity_x, velocity_y, frame)
        try:
            sock.sendto(packet, (client_address[0], UDP_PORT))
            return True
        except:
            print("Failed to send command")
    return False

def run_test_scenario_1(sock):
    """Test Scenario 1: Basic sprite creation and movement"""
    print("\n=== Test Scenario 1: Basic Sprite Movement ===")
    
    # Clear screen
    send_command(sock, NET_CLEAR_SCREEN)
    time.sleep(0.1)
    
    # Create a few sprites
    for i in range(3):
        x = 20 + i * 50
        y = 20 + i * 30
        send_command(sock, NET_DRAW_SPRITE, object_id=i, x=x, y=y, frame=0)
        print(f"Created sprite {i} at ({x}, {y})")
        time.sleep(0.2)
    
    # Move sprites around
    for step in range(20):
        for i in range(3):
            x = 50 + int(30 * math.cos(step * 0.3 + i))
            y = 50 + int(20 * math.sin(step * 0.2 + i))
            send_command(sock, NET_MOVE_OBJECT, object_id=i, x=x, y=y, frame=step % 4)
        
        time.sleep(0.1)
        handle_client_response(sock)

def run_test_scenario_2(sock):
    """Test Scenario 2: Collision testing"""
    print("\n=== Test Scenario 2: Collision Testing ===")
    
    # Clear screen
    send_command(sock, NET_CLEAR_SCREEN)
    time.sleep(0.1)
    
    # Create two sprites that will collide
    send_command(sock, NET_DRAW_SPRITE, object_id=0, x=50, y=50, frame=0)
    send_command(sock, NET_DRAW_SPRITE, object_id=1, x=150, y=50, frame=1)
    time.sleep(0.2)
    
    # Move them towards each other
    for step in range(25):
        x1 = 50 + step * 2
        x2 = 150 - step * 2
        
        send_command(sock, NET_MOVE_OBJECT, object_id=0, x=x1, y=50, frame=0)
        send_command(sock, NET_MOVE_OBJECT, object_id=1, x=x2, y=50, frame=1)
        
        print(f"Step {step}: Sprite 0 at x={x1}, Sprite 1 at x={x2}")
        
        time.sleep(0.1)
        handle_client_response(sock)

def run_test_scenario_3(sock):
    """Test Scenario 3: Stress test with many sprites"""
    print("\n=== Test Scenario 3: Multiple Sprite Stress Test ===")
    
    # Clear screen
    send_command(sock, NET_CLEAR_SCREEN)
    time.sleep(0.1)
    
    # Create many sprites
    num_sprites = 8
    for i in range(num_sprites):
        x = random.randint(10, 200)
        y = random.randint(10, 100)
        send_command(sock, NET_DRAW_SPRITE, object_id=i, x=x, y=y, frame=i % 4)
        time.sleep(0.05)
    
    # Move all sprites randomly
    for step in range(50):
        for i in range(num_sprites):
            x = random.randint(0, 220)
            y = random.randint(0, 120)
            send_command(sock, NET_MOVE_OBJECT, object_id=i, x=x, y=y, frame=random.randint(0, 3))
            
            if step % 5 == 0:  # Check for responses every few moves
                handle_client_response(sock)
        
        if step % 10 == 0:
            print(f"Stress test step {step}/50")
        
        time.sleep(0.05)

def run_interactive_mode(sock):
    """Interactive mode for manual testing"""
    print("\n=== Interactive Mode ===")
    print("Commands:")
    print("  'c' - Clear screen")
    print("  'd <id> <x> <y>' - Draw sprite")
    print("  'm <id> <x> <y>' - Move sprite")
    print("  'q' - Quit interactive mode")
    
    while True:
        try:
            # Check for responses
            handle_client_response(sock)
            
            # Simple input simulation (in real implementation, you'd have actual input)
            # For demo, we'll just run a simple sequence
            commands = [
                ('c', []),
                ('d', [0, 50, 50]),
                ('d', [1, 100, 75]),
                ('m', [0, 60, 60]),
                ('m', [1, 90, 65]),
                ('q', [])
            ]
            
            for cmd, args in commands:
                if cmd == 'c':
                    send_command(sock, NET_CLEAR_SCREEN)
                    print("Screen cleared")
                elif cmd == 'd' and len(args) >= 3:
                    send_command(sock, NET_DRAW_SPRITE, object_id=args[0], x=args[1], y=args[2])
                    print(f"Drew sprite {args[0]} at ({args[1]}, {args[2]})")
                elif cmd == 'm' and len(args) >= 3:
                    send_command(sock, NET_MOVE_OBJECT, object_id=args[0], x=args[1], y=args[2])
                    print(f"Moved sprite {args[0]} to ({args[1]}, {args[2]})")
                elif cmd == 'q':
                    return
                
                time.sleep(1)
                handle_client_response(sock)
            
            return
            
        except KeyboardInterrupt:
            return

def blink_led():
    """Blink LED to show the server is running"""
    led.toggle()

def main():
    """Main server loop"""
    print("Pico W GPU Test Server Starting...")
    
    # Set up access point
    ap = setup_access_point()
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_RESPONSE_PORT))
    sock.settimeout(0.1)  # Non-blocking with short timeout
    
    print(f"UDP server listening on port {UDP_RESPONSE_PORT}")
    print("Waiting for GPU Pico W to connect...")
    
    # Set up LED blinking timer
    timer = Timer()
    timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: blink_led())
    
    # Wait for client connection
    connected = False
    while not connected:
        handle_client_response(sock)
        if client_address:
            connected = True
        time.sleep(0.5)
    
    print("GPU Client connected! Starting tests...")
    timer.deinit()  # Stop blinking
    led.on()  # Solid on when connected
    
    try:
        while True:
            print("\n" + "="*50)
            print("GPU Test Server - Main Menu")
            print("="*50)
            
            # Auto-run test scenarios
            run_test_scenario_1(sock)
            time.sleep(2)
            
            run_test_scenario_2(sock)
            time.sleep(2)
            
            run_test_scenario_3(sock)
            time.sleep(2)
            
            run_interactive_mode(sock)
            time.sleep(5)
            
            # Continue monitoring for responses
            for _ in range(50):  # Monitor for 5 seconds
                handle_client_response(sock)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        sock.close()
        ap.active(False)
        led.off()

# Import math for test scenarios
import math

if __name__ == "__main__":
    main()