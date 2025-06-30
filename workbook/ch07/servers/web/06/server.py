# server.py
import socket
import threading
import base64
import hashlib

GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
clients = []

def create_response_key(key):
    sha1 = hashlib.sha1()
    sha1.update((key + GUID).encode('utf-8'))
    return base64.b64encode(sha1.digest()).decode('utf-8')

def broadcast(sender_conn, message_bytes):
    frame = b'\x81' + bytes([len(message_bytes)]) + message_bytes
    for client in clients:
        if client != sender_conn:
            try:
                client.send(frame)
            except:
                clients.remove(client)

def handle_client(conn, addr):
    try:
        print(f"New connection from {addr}")
        data = conn.recv(1024).decode()
        key_line = [line for line in data.split("\r\n") if "Sec-WebSocket-Key" in line]
        if not key_line:
            conn.close()
            return
        key = key_line[0].split(": ")[1]
        response_key = create_response_key(key)

        handshake = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {response_key}\r\n\r\n"
        )
        conn.send(handshake.encode())
        clients.append(conn)

        while True:
            frame = conn.recv(1024)
            if not frame:
                break
            payload_len = frame[1] & 127
            mask = frame[2:6]
            encoded = frame[6:6+payload_len]
            decoded = bytes(b ^ mask[i % 4] for i, b in enumerate(encoded))
            broadcast(conn, decoded)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn in clients:
            clients.remove(conn)
        conn.close()
        print(f"Connection from {addr} closed")

def run_server(host='localhost', port=8765):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Chat server running on ws://{host}:{port}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    run_server()
