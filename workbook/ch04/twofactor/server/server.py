
# UNTESTED CODE -
# Pico2FA Server A - WiFi AP + Login Interface


import network
import socket
import time
import urequests
import ubinascii
import os

SSID = "Pico2FA-Server"
PASSWORD = "your_strong_password_here"  # Change this! (min 8 chars)
TOKEN_PROVIDER_IP = "192.168.4.2"

VALID_USER = "admin"      # Change these!
VALID_PASS = "secret123"


class LoginServer:
    def __init__(self):
        self.pending = {}  # attempt_id -> {"token": int, "expire": time, "user": str}
        self._setup_ap()
        self._run_server()

    def _setup_ap(self):
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=SSID, password=PASSWORD, channel=6)
        ap.active(True)
        ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))

        while not ap.active():
            time.sleep(0.1)

        print("AP running:", SSID, ap.ifconfig())

    def _run_server(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)

        while True:
            conn, client_addr = s.accept()
            request = ""
            while True:
                data = conn.recv(512)
                if not data:
                    break
                request += data.decode("utf-8", "ignore")

            status, ctype, body = self._handle_request(request, client_addr[0])
            response = f"HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
            conn.send(response)
            conn.close()

    def _parse_form(self, body):
        params = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v.replace("+", " ")
        return params

    def _handle_request(self, request, client_ip):
        lines = request.split("\r\n")
        if not lines:
            return "400 Bad Request", "text/plain", ""

        method, path = lines[0].split()[:2]

        body_start = request.find("\r\n\r\n") + 4
        form_body = request[body_start:] if body_start > 3 else ""

        # Login page
        if path in ("/", "/login") and method == "GET":
            html = """<html><body style="font-family:sans-serif">
                      <h1>2FA Login</h1>
                      <form action="/login" method="post">
                        Username: <input name="user"><br><br>
                        Password: <input name="pass" type="password"><br><br>
                        <input type="submit" value="Login">
                      </form>
                      </body></html>"""
            return "200 OK", "text/html", html

        # Process login
        if path == "/login" and method == "POST":
            params = self._parse_form(form_body)
            user = params.get("user", "")
            pw = params.get("pass", "")

            if user != VALID_USER or pw != VALID_PASS:
                return "200 OK", "text/html", "<html><body><h1>Invalid credentials</h1></body></html>"

            # Request token from provider
            try:
                payload = {"user": user, "client_ip": client_ip}
                r = urequests.post(f"http://{TOKEN_PROVIDER_IP}/generate_token",
                                   json=payload, timeout=120)
                result = r.json()
                r.close()

                if result.get("status") == "approved":
                    attempt_id = ubinascii.hexlify(os.urandom(8)).decode()
                    token = result["token"]
                    self.pending[attempt_id] = {
                        "token": token,
                        "expire": time.time() + 90,
                        "user": user
                    }
                    html = f"""<html><body style="font-family:sans-serif">
                               <h1>Enter Token</h1>
                               <p>Check the token device and press A if legitimate.</p>
                               <form action="/verify" method="post">
                                 Token: <input name="token" type="number"><br><br>
                                 <input type="hidden" name="attempt_id" value="{attempt_id}">
                                 <input type="submit" value="Verify">
                               </form>
                               </body></html>"""
                    return "200 OK", "text/html", html
                else:
                    msg = result.get("status", "failed").capitalize()
                    return "200 OK", "text/html", f"<html><body><h1>{msg}</h1></body></html>"
            except:
                return "200 OK", "text/html", "<html><body><h1>Token device unreachable</h1></body></html>"

        # Verify token
        if path == "/verify" and method == "POST":
            params = self._parse_form(form_body)
            attempt_id = params.get("attempt_id", "")
            entered = params.get("token", "")

            if (attempt_id in self.pending and
                time.time() < self.pending[attempt_id]["expire"] and
                entered.isdigit() and
                int(entered) == self.pending[attempt_id]["token"]):

                user = self.pending[attempt_id]["user"]
                del self.pending[attempt_id]
                return "200 OK", "text/html", f"<html><body><h1>Success!<br>Logged in as {user}</h1></body></html>"

            return "200 OK", "text/html", "<html><body><h1>Invalid or expired token</h1></body></html>"

        return "404 Not Found", "text/plain", "Not found"


LoginServer()
