# client.py
import socket

def mqtt_connect(sock):
    client_id = "client123"
    payload = bytearray()
    payload.extend(b"\x00\x04MQTT")         # Protocol name
    payload.append(0x04)                    # Protocol level 4
    payload.append(0x02)                    # Clean session
    payload.extend(b"\x00\x3C")             # Keep-alive (60s)
    payload.extend(len(client_id).to_bytes(2, 'big'))
    payload.extend(client_id.encode())

    fixed_header = bytearray()
    fixed_header.append(0x10)               # CONNECT
    fixed_header.append(len(payload))       # Remaining length

    sock.send(fixed_header + payload)
    connack = sock.recv(4)
    print("CONNACK:", connack)

def mqtt_publish(sock, topic, message):
    topic_bytes = topic.encode()
    msg_bytes = message.encode()
    variable_header = len(topic_bytes).to_bytes(2, 'big') + topic_bytes
    payload = msg_bytes
    remaining_length = len(variable_header) + len(payload)

    fixed_header = bytearray()
    fixed_header.append(0x30)               # PUBLISH, QoS 0
    fixed_header.append(remaining_length)

    sock.send(fixed_header + variable_header + payload)

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 1883))
    mqtt_connect(sock)
    mqtt_publish(sock, "test/topic", "Hello from Python MQTT client!")
    sock.close()
