import network
import socket
import ussl  # Not needed since we're using HTTP
import ucryptolib  # For AES decryption
import json
import machine  # For potential GPIO or HID simulation

# WiFi credentials
SSID = 'your_wifi_ssid'
PASSWORD = 'your_wifi_password'

# Shared key (must match client)
SHARED_KEY = b'mysecretkey12345'  # Bytes for ucryptolib

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    pass
print('Connected to WiFi:', wlan.ifconfig())

# Simple HTTP server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
print('Listening on', addr)

def decrypt_data(encrypted_hex):
    encrypted = bytes.fromhex(encrypted_hex)
    iv = encrypted[:12]
    ciphertext = encrypted[12:]
    cipher = ucryptolib.aes(SHARED_KEY, 6, iv)  # Mode 6 is GCM
    decrypted = cipher.decrypt(ciphertext)
    # GCM in ucryptolib doesn't handle auth tag automatically; for simplicity, assuming no tag issues in demo
    return decrypted.decode('utf-8')

while True:
    conn, addr = s.accept()
    print('Connection from', addr)
    request = conn.recv(1024).decode('utf-8')
    if 'POST /keystrokes' in request:
        # Parse body
        body_start = request.find('\r\n\r\n') + 4
        body = request[body_start:]
        if len(body) == 0:
            # If body is incomplete, recv more
            body = conn.recv(1024).decode('utf-8')
        data = json.loads(body)
        encrypted = data['encrypted']
        try:
            keystrokes = decrypt_data(encrypted)
            print('Received keystrokes:', keystrokes)
            # Here, process keystrokes, e.g., simulate keyboard input
            # Example: Print for now; (custom C for true HID?)
            response = 'OK'
        except Exception as e:
            print('Decryption error:', e)
            response = 'Error'
    else:
        response = 'Not Found'
    
    conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n')
    conn.send(response)
    conn.close()
