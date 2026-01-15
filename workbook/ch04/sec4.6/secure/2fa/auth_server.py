
# auth_server.py testing..

import network
import socket
import time
import machine
import json
import urequests
from pimoroni import RGBLED
import picographics

# Display setup
display = picographics.PicoGraphics(display=picographics.DISPLAY_PICO_DISPLAY_2)
display.set_backlight(0.8)
WIDTH, HEIGHT = display.get_bounds()

# LED setup
led = RGBLED(6, 7, 8)

# Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
TOKEN_SERVICE_IP = "192.168.1.100"  # IP of Device A
TOKEN_SERVICE_PORT = 8080

# User database (in real app, use hashed passwords)
USERS = {
    "alice": "password123",
    "bob": "secret456"
}

# Session storage
active_sessions = {}
session_counter = 0

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    display.text("Connecting WiFi...", 10, 50, scale=2)
    display.update()
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        led.set_rgb(50, 50, 0)
        time.sleep(0.5)
        led.set_rgb(0, 0, 0)
        time.sleep(0.5)
    
    if wlan.status() != 3:
        led.set_rgb(255, 0, 0)
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("WiFi Failed!", 10, 50, scale=2)
        display.update()
        raise RuntimeError('WiFi connection failed')
    else:
        led.set_rgb(0, 255, 0)
        time.sleep(1)
        led.set_rgb(0, 0, 0)
        status = wlan.ifconfig()
        print('IP:', status[0])
        return status[0]

def draw_screen(ip_addr, message="", auth_count=0):
    """Draw the server status screen"""
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    
    # Title
    display.text("Auth Server", 10, 10, scale=2)
    display.text(ip_addr, 10, 30, scale=1)
    
    # Status
    display.text(f"Sessions: {len(active_sessions)}", 10, 60, scale=2)
    display.text(f"Auth OK: {auth_count}", 10, 85, scale=2)
    
    # Activity message
    if message:
        display.set_pen(10)
        display.text(message[:30], 10, 120, scale=1)
        if len(message) > 30:
            display.text(message[30:60], 10, 135, scale=1)
    
    # Status indicator
    display.set_pen(8)
    display.text("Listening on :9090", 10, 200, scale=1)
    
    display.update()

def validate_token_with_service(token):
    """Validate token with Token Service (Device A)"""
    try:
        url = f"http://{TOKEN_SERVICE_IP}:{TOKEN_SERVICE_PORT}/validate?token={token}"
        response = urequests.get(url, timeout=5)
        data = response.json()
        response.close()
        return data.get("valid", False)
    except Exception as e:
        print(f"Token validation error: {e}")
        return False

def handle_login(data):
    """Handle login request (Step 1: password verification)"""
    global session_counter
    
    username = data.get("username")
    password = data.get("password")
    
    # Verify username and password
    if username not in USERS or USERS[username] != password:
        return {"status": "error", "message": "Invalid credentials"}
    
    # Create session
    session_counter += 1
    session_id = f"sess_{session_counter}_{int(time.time())}"
    
    active_sessions[session_id] = {
        "username": username,
        "authenticated": False,
        "created": time.time()
    }
    
    led.set_rgb(0, 0, 255)
    time.sleep(0.2)
    led.set_rgb(0, 0, 0)
    
    return {
        "status": "pending",
        "message": "Password OK. Enter token from Device A",
        "session_id": session_id
    }

def handle_verify(data):
    """Handle token verification (Step 2: 2FA verification)"""
    session_id = data.get("session_id")
    token = data.get("token")
    
    # Check session exists
    if session_id not in active_sessions:
        return {"status": "error", "message": "Invalid session"}
    
    # Validate token with Device A
    if validate_token_with_service(token):
        active_sessions[session_id]["authenticated"] = True
        
        led.set_rgb(0, 255, 0)
        time.sleep(0.5)
        led.set_rgb(0, 0, 0)
        
        return {
            "status": "success",
            "message": "Authentication successful!",
            "session_id": session_id,
            "username": active_sessions[session_id]["username"]
        }
    else:
        led.set_rgb(255, 0, 0)
        time.sleep(0.5)
        led.set_rgb(0, 0, 0)
        
        return {"status": "error", "message": "Invalid token"}

def handle_status(data):
    """Check authentication status"""
    session_id = data.get("session_id")
    
    if session_id not in active_sessions:
        return {"status": "error", "message": "Invalid session"}
    
    session = active_sessions[session_id]
    
    return {
        "status": "ok",
        "authenticated": session["authenticated"],
        "username": session["username"]
    }

def handle_request(conn):
    """Handle incoming HTTP requests"""
    global message_display
    
    try:
        request = conn.recv(2048).decode()
        
        # Parse request
        lines = request.split('\r\n')
        request_line = lines[0]
        
        if "POST /login" in request_line:
            # Extract JSON body
            body_start = request.find('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            
            message_display = f"Login: {data.get('username')}"
            response_data = handle_login(data)
            
        elif "POST /verify" in request_line:
            body_start = request.find('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            
            message_display = f"Verify token"
            response_data = handle_verify(data)
            
        elif "POST /status" in request_line:
            body_start = request.find('\r\n\r\n') + 4
            body = request[body_start:]
            data = json.loads(body)
            
            response_data = handle_status(data)
            
        else:
            response_data = {"status": "error", "message": "Unknown endpoint"}
        
        # Send response
        response_json = json.dumps(response_data)
        conn.send('HTTP/1.1 200 OK\r\n')
        conn.send('Content-Type: application/json\r\n')
        conn.send('Connection: close\r\n\r\n')
        conn.send(response_json)
        
    except Exception as e:
        print(f"Request error: {e}")
        conn.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')
    
    conn.close()

def cleanup_old_sessions():
    """Remove sessions older than 5 minutes"""
    current_time = time.time()
    to_remove = []
    
    for session_id, session_data in active_sessions.items():
        if current_time - session_data["created"] > 300:  # 5 minutes
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del active_sessions[session_id]

def main():
    """Main server loop"""
    global message_display
    message_display = "Ready"
    auth_count = 0
    
    # Connect to WiFi
    ip = connect_wifi()
    
    # Setup socket server
    addr = socket.getaddrinfo('0.0.0.0', 9090)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    
    print(f'Auth server listening on {ip}:9090')
    print(f'Token service at {TOKEN_SERVICE_IP}:{TOKEN_SERVICE_PORT}')
    
    last_cleanup = time.time()
    
    while True:
        # Handle incoming connections
        try:
            conn, addr = s.accept()
            print('Connection from', addr)
            handle_request(conn)
            
            # Count successful authentications
            auth_count = sum(1 for s in active_sessions.values() if s["authenticated"])
            
        except OSError:
            pass
        
        # Cleanup old sessions every 60 seconds
        if time.time() - last_cleanup > 60:
            cleanup_old_sessions()
            last_cleanup = time.time()
        
        # Update display
        draw_screen(ip, message_display, auth_count)
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()