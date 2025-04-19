# websocket server
import socket
import threading
import base64
import hashlib

GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

def create_response_key(key):
    sha1 = hashlib.sha1()
    sha1.update((key + GUID).encode('utf-8'))
    return base64.b64encode(sha1.digest()).decode('utf-8')

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    data = conn.recv(1024).decode()
    lines = data.split("\r\n")
    key = ""
    for line in lines:
        if line.startswith("Sec-WebSocket-Key"):
            key = line.split(": ")[1]
            break

    if not key:
        conn.close()
        return

    response_key = create_response_key(key)

    handshake = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {response_key}\r\n"
        "\r\n"
    )
    conn.send(handshake.encode())

    # echo loop
    try:
        while True:
            frame = conn.recv(1024)
            if not frame:
                break

            # basic frame decoding (text only, no fragmentation, no mask from client)
            payload_len = frame[1] & 127
            mask = frame[2:6]
            encoded = frame[6:6+payload_len]
            decoded = bytes(b ^ mask[i % 4] for i, b in enumerate(encoded))

            message = decoded.decode('utf-8')
            print(f"Received: {message}")

            # send back (text frame)
            response = b'\x81' + bytes([len(decoded)]) + decoded
            conn.send(response)
    finally:
        conn.close()

def run_server(host='localhost', port=8765):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    print(f"WebSocket server running on ws://{host}:{port}")

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()

