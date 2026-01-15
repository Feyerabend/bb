
# UNTESTED CODE -
# Pico2FA Server A - WiFi AP + Login Interface

import network
import time

# AP config
SSID = "Pico2FA-Server"
PASSWORD = "your_strong_password_here"  # At least 8 chars
CHANNEL = 6

wlan = network.WLAN(network.AP_IF)
wlan.config(essid=SSID, password=PASSWORD, channel=CHANNEL)
wlan.active(True)

# Optional: Set static IP (default is 192.168.4.1 anyway)
wlan.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

while not wlan.active():
    time.sleep(0.1)

print("AP started:", SSID, wlan.ifconfig())


pending = {}  # attempt_id -> {"token": int, "expire": timestamp, "user": str}

def parse_form_body(body):
    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = v
    return params

# HTML templates (keep simple)
LOGIN_HTML = """<html><body><h1>Login</h1>
<form method="post" action="/login">
Username: <input name="user"><br>
Password: <input name="pass" type="password"><br>
<input type="submit">
</form></body></html>"""

TOKEN_HTML = lambda attempt_id: f"""<html><body><h1>Enter Token</h1>
<p>Check the token provider display and approve if legitimate.</p>
<form method="post" action="/verify">
Token: <input name="token"><br>
<input type="hidden" name="attempt_id" value="{attempt_id}">
<input type="submit">
</form></body></html>"""

def handle_request(request, client_addr):
    client_ip = client_addr[0]
    lines = request.split("\r\n")
    method_path = lines[0]
    method, path, _ = method_path.split()

    body = ""
    if "Content-Length" in request:
        cl_idx = request.find("Content-Length: ") + 16
        cl = int(request[cl_idx:request.find("\r\n", cl_idx)])
        body = request[-cl:]

    if path == "/" or path == "/login" and method == "GET":
        return "200 OK", "text/html", LOGIN_HTML

    if path == "/login" and method == "POST":
        params = parse_form_body(body)
        user = params.get("user", "")
        pw = params.get("pass", "")
        if user != VALID_USER or pw != VALID_PASS:
            return "200 OK", "text/html", "<h1>Bad credentials</h1>"

        # Generate attempt
        attempt_id = ubinascii.hexlify(os.urandom(8)).decode()
        data = {"user": user, "client_ip": client_ip, "attempt_id": attempt_id}

        try:
            r = urequests.post(f"http://{TOKEN_B_IP}/generate_token", json=data, timeout=120)
            res = r.json()
            r.close()
            if res.get("status") == "approved":
                token = res["token"]
                pending[attempt_id] = {"token": token, "expire": time.time() + 90, "user": user}
                return "200 OK", "text/html", TOKEN_HTML(attempt_id)
            else:
                return "200 OK", "text/html", f"<h1>Login {res.get('status', 'failed')}</h1>"
        except:
            return "200 OK", "text/html", "<h1>Token provider unreachable</h1>"

    if path == "/verify" and method == "POST":
        params = parse_form_body(body)
        attempt_id = params.get("attempt_id", "")
        entered = params.get("token", "")
        if attempt_id in pending and time.time() < pending[attempt_id]["expire"]:
            if int(entered) == pending[attempt_id]["token"]:
                user = pending[attempt_id]["user"]
                del pending[attempt_id]
                return "200 OK", "text/html", f"<h1>Success! Logged in as {user}</h1>"
        return "200 OK", "text/html", "<h1>Invalid/expired token</h1>"

    return "404 Not Found", "text/plain", "Not found"

# Server loop (similar to B)
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(2048).decode()
    status, ctype, content = handle_request(request, addr)
    conn.send(f"HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\nConnection: close\r\n\r\n{content}")
    conn.close()


