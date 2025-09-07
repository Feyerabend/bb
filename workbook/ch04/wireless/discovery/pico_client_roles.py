# pico_client_roles.py
import network, socket, time, _thread

# Connect to AP
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")
while not sta.isconnected():
    time.sleep(1)
my_ip = sta.ifconfig()[0]
print("Connected, IP:", my_ip)

peer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peer_sock.bind((my_ip, 5001))
peer_sock.settimeout(0.5)

role = None
peer_roles = {}  # IP -> role

# Listen for peer messages
def listen_peers():
    while True:
        try:
            data, addr = peer_sock.recvfrom(1024)
            print("Peer message from", addr[0], ":", data.decode())
        except OSError:
            pass

_thread.start_new_thread(listen_peers, ())

ap_ip = "192.168.4.1"
peer_list = []

def discover_peers():
    global peer_list, role, peer_roles
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(2)
    try:
        udp.sendto(b"HELLO", (ap_ip, 5000))
        data, _ = udp.recvfrom(1024)
        nodes = data.decode().split(",")
        # assign roles based on order
        peer_roles = {}
        for i, ip in enumerate(nodes):
            peer_roles[ip] = "MASTER" if i == 0 else f"WORKER{i}"
        peer_list = [ip for ip in nodes if ip != my_ip]
        role = peer_roles[my_ip]
        print("Discovered peers:", peer_roles)
        print("My role:", role)
    except OSError:
        print("Discovery failed")
    udp.close()

# Main loop
while True:
    discover_peers()
    # send a heartbeat/message to each peer
    for peer_ip in peer_list:
        msg = f"Hello from {my_ip} ({role})"
        try:
            peer_sock.sendto(msg.encode(), (peer_ip, 5001))
        except OSError:
            pass
    time.sleep(5)
