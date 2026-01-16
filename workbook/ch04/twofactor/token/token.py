
# SKETCH FOR A 2FA TOKEN PROVIDER USING PICO DISPLAY 2
# NOT TESTED!


import machine
import network
import socket
import time
import random
import ujson
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2

SSID = "Pico2FA-Server"
PASSWORD = "your_strong_password_here"  # Change this!
MY_IP = "192.168.4.2"
ALLOWED_IP = "192.168.4.1"  # Only accept requests from the server Pico


class DisplayManager:
    def __init__(self):
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2)
        self.display.set_backlight(0.8)
        self.white = self.display.create_pen(255, 255, 255)
        self.black = self.display.create_pen(0, 0, 0)

    def clear(self):
        self.display.set_pen(self.black)
        self.display.clear()
        self.display.update()

    def show_message(self, text, y=100, scale=4):
        self.clear()
        self.display.set_pen(self.white)
        self.display.text(text, 10, y, scale=scale)
        self.display.update()

    def show_token(self, user, client_ip, token):
        self.clear()
        self.display.set_pen(self.white)
        self.display.text("2FA Request", 10, 10, scale=3)
        self.display.text(f"User: {user}", 10, 50, scale=2)
        self.display.text(f"From IP: {client_ip}", 10, 80, scale=2)
        self.display.text(f"{token:06d}", 40, 120, scale=5)
        self.display.text("A = Approve", 10, 180, scale=2)
        self.display.text("X = Deny", 10, 210, scale=2)
        self.display.update()


class Buttons:
    def __init__(self):
        self.a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)  # A button
        self.x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)  # X button

    def a_pressed(self):
        return not self.a.value()

    def x_pressed(self):
        return not self.x.value()


class TokenProvider:
    def __init__(self):
        self.display = DisplayManager()
        self.buttons = Buttons()

        self.display.show_message("Connecting...")
        self._connect_wifi()
        self.display.show_message("Ready", scale=3)

        self._run_server()

    def _connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)

        while not wlan.isconnected():
            time.sleep(0.5)

        wlan.ifconfig((MY_IP, "255.255.255.0", "192.168.4.1", "192.168.4.1"))
        print("Connected:", wlan.ifconfig())

    def _run_server(self):
        addr = socket.getaddrinfo(MY_IP, 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)

        while True:
            conn, client_addr = s.accept()
            request = ""
            while True:
                chunk = conn.recv(512)
                if not chunk:
                    break
                request += chunk.decode()

            response = self._handle_request(request, client_addr[0])
            conn.send(response)
            conn.close()

    def _handle_request(self, request, client_ip):
        if client_ip != ALLOWED_IP:
            return "HTTP/1.1 403 Forbidden\r\n\r\n"

        if "POST /generate_token" not in request:
            return "HTTP/1.1 404 Not Found\r\n\r\n"

        body_start = request.find("\r\n\r\n") + 4
        if body_start < 4:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        try:
            data = ujson.loads(request[body_start:])
            user = data.get("user", "?")
            client_ip = data.get("client_ip", "?")
        except:
            return "HTTP/1.1 400 Bad Request\r\n\r\n"

        token = random.randint(0, 999999)
        self.display.show_token(user, client_ip, token)

        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < 90000:  # 90 seconds
            if self.buttons.a_pressed():
                self.display.show_message("Approved!")
                time.sleep(1)
                return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'approved', 'token': token})}"

            if self.buttons.x_pressed():
                self.display.show_message("Denied")
                time.sleep(1)
                return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'denied'})}"

            time.sleep(0.05)

        self.display.show_message("Timeout")
        time.sleep(1)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{ujson.dumps({'status': 'timeout'})}"


TokenProvider()
