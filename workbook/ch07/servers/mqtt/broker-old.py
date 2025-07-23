import socket
import struct
import threading
from collections import defaultdict

class MQTTBroker:
    def __init__(self, host='localhost', port=1883):
        self.host = host
        self.port = port
        self.subscriptions = defaultdict(list)  # topic -> list of client sockets
        self.clients = {}  # client_id -> socket
        self.lock = threading.Lock()

    def parse_connect(self, data):
        """Parse CONNECT packet and extract client ID."""
        protocol_name_len = struct.unpack('!H', data[2:4])[0]
        idx = 4 + protocol_name_len
        proto_version = data[idx]
        idx += 1
        connect_flags = data[idx]
        idx += 1
        keep_alive = struct.unpack('!H', data[idx:idx+2])[0]
        idx += 2
        client_id_len = struct.unpack('!H', data[idx:idx+2])[0]
        idx += 2
        client_id = data[idx:idx+client_id_len].decode()
        return client_id, keep_alive

    def parse_publish(self, data):
        """Parse PUBLISH packet and extract topic and payload."""
        topic_length = struct.unpack('!H', data[2:4])[0]
        topic = data[4:4+topic_length].decode()
        payload = data[4+topic_length:].decode()
        return topic, payload

    def parse_subscribe(self, data):
        """Parse SUBSCRIBE packet and extract topic."""
        topic_length = struct.unpack('!H', data[2:4])[0]
        topic = data[4:4+topic_length].decode()
        return topic

    def send_to_subscribers(self, topic, payload):
        """Forward message to all subscribers of the topic."""
        with self.lock:
            for client_socket in self.subscriptions.get(topic, []):
                try:
                    # Construct PUBLISH packet
                    topic_bytes = topic.encode()
                    payload_bytes = payload.encode()
                    packet = bytearray()
                    packet.append(0x30)  # PUBLISH packet type
                    remaining_length = len(topic_bytes) + 2 + len(payload_bytes)
                    packet.append(remaining_length)
                    packet.extend(struct.pack('!H', len(topic_bytes)))
                    packet.extend(topic_bytes)
                    packet.extend(payload_bytes)
                    client_socket.send(packet)
                except (ConnectionError, BrokenPipeError):
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        """Remove client and its subscriptions."""
        with self.lock:
            client_id = None
            for cid, sock in self.clients.items():
                if sock == client_socket:
                    client_id = cid
                    break
            if client_id:
                del self.clients[client_id]
            for topic in self.subscriptions:
                self.subscriptions[topic] = [
                    sock for sock in self.subscriptions[topic]
                    if sock != client_socket
                ]
            try:
                client_socket.close()
            except:
                pass

    def handle_client(self, conn):
        """Handle individual client connection."""
        try:
            data = conn.recv(1024)
            if not data:
                return

            packet_type = data[0] >> 4

            if packet_type == 1:  # CONNECT
                client_id, _ = self.parse_connect(data)
                with self.lock:
                    self.clients[client_id] = conn
                conn.send(bytes([0x20, 0x02, 0x00, 0x00]))  # CONNACK
                print(f"Client {client_id} connected")

            elif packet_type == 3:  # PUBLISH
                topic, payload = self.parse_publish(data)
                print(f"Received PUBLISH - Topic: {topic}, Payload: {payload}")
                self.send_to_subscribers(topic, payload)

            elif packet_type == 8:  # SUBSCRIBE
                topic = self.parse_subscribe(data)
                with self.lock:
                    self.subscriptions[topic].append(conn)
                conn.send(bytes([0x90, 0x03, 0x00, 0x01, 0x00]))  # SUBACK
                print(f"Client subscribed to {topic}")

            elif packet_type == 10:  # UNSUBSCRIBE
                topic = self.parse_subscribe(data)
                with self.lock:
                    self.subscriptions[topic] = [
                        sock for sock in self.subscriptions[topic]
                        if sock != conn
                    ]
                conn.send(bytes([0xB0, 0x02, 0x00, 0x01]))  # UNSUBACK
                print(f"Client unsubscribed from {topic}")

            elif packet_type == 12:  # PINGREQ
                conn.send(bytes([0xD0, 0x00]))  # PINGRESP
                print("Received PINGREQ, sent PINGRESP")

        except (ConnectionError, BrokenPipeError):
            self.remove_client(conn)
        except Exception as e:
            print(f"Error handling client: {e}")
            self.remove_client(conn)

    def start(self):
        """Start the MQTT broker."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"MQTT broker listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                print(f"New connection from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_client, args=(conn,), daemon=True
                )
                client_thread.start()

if __name__ == "__main__":
    broker = MQTTBroker()
    broker.start()