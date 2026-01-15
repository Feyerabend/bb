
# Token Service for MicroPython on Raspberry Pi Pico W
# This script connects to WiFi, generates TOTP tokens, and serves them over HTTP

import network
import socket
import time
import machine
from pimoroni import RGBLED
import picographics

# Display setup
display = picographics.PicoGraphics(display=picographics.DISPLAY_PICO_DISPLAY_2)
display.set_backlight(0.8)
WIDTH, HEIGHT = display.get_bounds()

# Button setup
button_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
button_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# LED setup
led = RGBLED(6, 7, 8)

# TOTP Configuration
TOTP_SECRET = b"JBSWY3DPEHPK3PXP"  # Shared secret with server B
TOTP_INTERVAL = 30  # 30 second windows

# PIN Configuration
CORRECT_PIN = "1234"  # Map buttons: A=1, B=2, X=3, Y=4
current_pin = ""
pin_locked = False
last_button_time = 0
DEBOUNCE_MS = 300

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

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

def base32_decode(s):
    """Simple base32 decoder for TOTP secret"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    result = []
    bits = 0
    value = 0
    
    for char in s.decode('ascii'):
        if char not in alphabet:
            continue
        value = (value << 5) | alphabet.index(char)
        bits += 5
        
        if bits >= 8:
            result.append((value >> (bits - 8)) & 0xFF)
            bits -= 8
    
    return bytes(result)

def hmac_sha1(key, msg):
    """Simplified HMAC-SHA1 (you'll need to import hashlib or use uhashlib)"""
    # This is a placeholder - MicroPython needs uhashlib
    import uhashlib
    
    blocksize = 64
    if len(key) > blocksize:
        key = uhashlib.sha1(key).digest()
    if len(key) < blocksize:
        key = key + bytes(blocksize - len(key))
    
    o_key_pad = bytes((x ^ 0x5C) for x in key)
    i_key_pad = bytes((x ^ 0x36) for x in key)
    
    return uhashlib.sha1(o_key_pad + uhashlib.sha1(i_key_pad + msg).digest()).digest()

def generate_totp(secret, time_step=30):
    """Generate TOTP token"""
    key = base32_decode(secret)
    timestamp = int(time.time()) // time_step
    msg = timestamp.to_bytes(8, 'big')
    
    hmac = hmac_sha1(key, msg)
    offset = hmac[-1] & 0x0F
    code = int.from_bytes(hmac[offset:offset+4], 'big') & 0x7FFFFFFF
    
    return str(code % 1000000).zfill(6)

def draw_screen(ip_addr, token=None, pin_display="", message=""):
    """Draw the main screen"""
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    
    # Title
    display.text("Token Service", 10, 10, scale=2)
    display.text(ip_addr, 10, 30, scale=1)
    
    # PIN Entry Area
    if not pin_locked:
        display.text("Enter PIN:", 10, 60, scale=2)
        display.text("*" * len(pin_display), 10, 80, scale=3)
    else:
        # Token display
        if token:
            display.text("TOKEN:", 10, 60, scale=2)
            display.text(token, 30, 90, scale=4)
            
            # Time remaining
            remaining = TOTP_INTERVAL - (int(time.time()) % TOTP_INTERVAL)
            display.text(f"Valid: {remaining}s", 10, 130, scale=2)
    
    # Message area
    if message:
        display.set_pen(10)
        display.text(message, 10, 170, scale=1)
    
    # Button guide
    display.set_pen(8)
    display.text("A=1 B=2 X=3 Y=4", 10, 200, scale=1)
    
    display.update()

def check_buttons():
    """Check button presses with debouncing"""
    global current_pin, pin_locked, last_button_time
    
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_button_time) < DEBOUNCE_MS:
        return
    
    if not button_a.value():
        current_pin += "1"
        last_button_time = current_time
        led.set_rgb(0, 0, 255)
        time.sleep(0.1)
        led.set_rgb(0, 0, 0)
    elif not button_b.value():
        current_pin += "2"
        last_button_time = current_time
        led.set_rgb(0, 0, 255)
        time.sleep(0.1)
        led.set_rgb(0, 0, 0)
    elif not button_x.value():
        current_pin += "3"
        last_button_time = current_time
        led.set_rgb(0, 0, 255)
        time.sleep(0.1)
        led.set_rgb(0, 0, 0)
    elif not button_y.value():
        current_pin += "4"
        last_button_time = current_time
        led.set_rgb(0, 0, 255)
        time.sleep(0.1)
        led.set_rgb(0, 0, 0)
    
    # Check PIN length
    if len(current_pin) >= len(CORRECT_PIN):
        if current_pin == CORRECT_PIN:
            pin_locked = True
            led.set_rgb(0, 255, 0)
            time.sleep(0.5)
            led.set_rgb(0, 0, 0)
        else:
            led.set_rgb(255, 0, 0)
            time.sleep(0.5)
            led.set_rgb(0, 0, 0)
            current_pin = ""

def handle_request(conn):
    """Handle HTTP requests for token validation"""
    request = conn.recv(1024).decode()
    
    if "GET /validate" in request:
        # Extract token from query string
        try:
            token_start = request.find("token=") + 6
            token_end = request.find(" ", token_start)
            if token_end == -1:
                token_end = request.find("&", token_start)
            if token_end == -1:
                token_end = len(request)
            
            provided_token = request[token_start:token_end]
            current_token = generate_totp(TOTP_SECRET)
            
            # Check current and previous window for clock drift
            prev_token = generate_totp(TOTP_SECRET, TOTP_INTERVAL)
            
            valid = (provided_token == current_token)
            
            response = f'{{"valid": {str(valid).lower()}}}'
            conn.send('HTTP/1.1 200 OK\r\n')
            conn.send('Content-Type: application/json\r\n')
            conn.send('Connection: close\r\n\r\n')
            conn.send(response)
        except Exception as e:
            conn.send('HTTP/1.1 400 Bad Request\r\n\r\n')
    else:
        conn.send('HTTP/1.1 404 Not Found\r\n\r\n')
    
    conn.close()

def main():
    """Main program loop"""
    global current_pin, pin_locked
    
    # Connect to WiFi
    ip = connect_wifi()
    
    # Setup socket server
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    
    print(f'Token service listening on {ip}:8080')
    
    last_token = ""
    
    while True:
        # Handle incoming connections (non-blocking)
        try:
            conn, addr = s.accept()
            print('Connection from', addr)
            handle_request(conn)
        except OSError:
            pass
        
        # Check buttons
        check_buttons()
        
        # Generate and display token if PIN is correct
        if pin_locked:
            token = generate_totp(TOTP_SECRET)
            if token != last_token:
                last_token = token
            draw_screen(ip, token=token)
        else:
            draw_screen(ip, pin_display=current_pin, message="Enter PIN to unlock")
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()