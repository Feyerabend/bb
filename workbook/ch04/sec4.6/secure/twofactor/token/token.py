
# SKETCH FOR A 2FA TOKEN PROVIDER USING PICO DISPLAY 2
# NOT TESTED!

import network
import time

SSID = "Pico2FA-Server"
PASSWORD = "your_strong_password_here"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connection
while not wlan.isconnected():
    time.sleep(1)

# Set static IP so A always knows where to reach B
wlan.ifconfig(('192.168.4.2', '255.255.255.0', '192.168.4.1', '192.168.4.1'))

print("Connected to AP:", wlan.ifconfig())

BUTTON_A = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)  # A button
BUTTON_X = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)  # X button (deny)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
display.set_backlight(0.8)

def clear_display():
    display.set_pen(display.create_pen(0, 0, 0))
    display.clear()
    display.update()

def show_token(details):
    clear_display()
    display.set_pen(display.create_pen(255, 255, 255))
    display.text("2FA Request", 10, 10, scale=3)
    display.text(f"User: {details['user']}", 10, 50, scale=2)
    display.text(f"From IP: {details['client_ip']}", 10, 80, scale=2)
    display.text(f"Token: {details['token']:06d}", 10, 120, scale=4)
    display.text("A = Approve", 10, 180, scale=2)
    display.text("X = Deny", 10, 210, scale=2)
    display.update()

def handle_request(request, client_addr):
    if client_addr[0] != A_IP:
        return "HTTP/1.1 403 Forbidden\r\n\r\n"

    lines = request.split("\r\n")
    if lines[0] != "POST /generate_token HTTP/1.1":
        return "HTTP/1.1 404 Not Found\r\n\r\n"

    # Find and parse JSON body
    body_start = request.find("\r\n\r\n") + 4
    body = ujson.loads(request[body_start:])

    # Generate token
    token = random.randint(100000, 999999)
    details = {
        "token": token,
        "user": body.get("user", "?"),
        "client_ip": body.get("client_ip", "?")
    }
    show_token(details)

    # Wait for button press (up to 90s)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < 90000:
        if not BUTTON_A.value():  # Pressed (active low)
            clear_display()
            display.text("Approved!", 10, 100, scale=4)
            display.update()
            time.sleep(1)
            clear_display()
            return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'approved', 'token': token})}"
        if not BUTTON_X.value():
            clear_display()
            display.text("Denied", 10, 100, scale=4)
            display.update()
            time.sleep(1)
            clear_display()
            return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'denied'})}"
        time.sleep(0.05)

    clear_display()
    display.text("Timeout", 10, 100, scale=4)
    display.update()
    time.sleep(1)
    clear_display()
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'timeout'})}"

# Simple HTTP server loop
addr = socket.getaddrinfo(MY_IP, 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

clear_display()
display.text("Token Provider Ready", 10, 100, scale=2)
display.update()

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    response = handle_request(request, addr)
    conn.send(response)
    conn.close()
