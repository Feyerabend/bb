
## Raspberry Pi Pico

Wire --



### Three Way Scenario

Once connected, the clients broadcast a UDP “HELLO” message, and the AP replies so everyone
knows who’s on the network. From there you can build your own role negotiation logic
(e.g. one acts as master, the rest as workers).


SIMPLE

Pico A (Access Point + Discovery Responder)

```python
# pico_ap.py
import network, socket, time

# bring up AP
ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")
ap.active(True)
print("AP started:", ap.ifconfig())

# UDP socket
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 5000))

while True:
    data, addr = udp.recvfrom(1024)
    msg = data.decode()
    print("Got:", msg, "from", addr)

    if msg.startswith("HELLO"):
        reply = "WELCOME from AP @ 192.168.4.1"
        udp.sendto(reply.encode(), addr)
```


Pico B and C (Clients with Discovery)
```python
# pico_client.py
import network, socket, time

sta = network.WLAN(network.STA_IF)
sta.active(True)

sta.connect("PicoAP", "pico1234")
while not sta.isconnected():
    time.sleep(1)
print("Connected:", sta.ifconfig())

# UDP socket
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(3)

# broadcast "HELLO"
server_ip = "192.168.4.1"   # AP always has this
udp.sendto(b"HELLO from client", (server_ip, 5000))

try:
    data, addr = udp.recvfrom(1024)
    print("Reply:", data.decode(), "from", addr)
except OSError:
    print("No reply")
```




How it works
1. Pico A starts an AP with SSID "PicoAP". Its IP is always 192.168.4.1.
2. Pico B and C connect as STAs.
3. Each client sends "HELLO" to port 5000 on the AP.
4. The AP replies "WELCOME" and can log who’s connected.
5. From here, you could:
- Maintain a list of connected nodes on the AP.
- Have the AP assign roles (e.g. "YOU ARE WORKER1", "YOU ARE WORKER2").
- Or let the clients negotiate roles by comparing IDs they send in HELLO.


This way, three Picos discover each other automatically, without manually set IP addresses.



LIST BROADCAST

Extend it so the AP keeps track of all connected nodes and periodically broadcasts the list back to everyone. That way, each Pico knows who’s in the “cluster”.

Pico A (Access Point + Node Manager)
```python
# pico_ap.py
import network, socket, time

# Bring up AP
ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")
ap.active(True)
print("AP started:", ap.ifconfig())

# UDP socket for discovery
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 5000))
udp.settimeout(0.5)

nodes = set()   # store IPs of connected clients

while True:
    try:
        data, addr = udp.recvfrom(1024)
        msg = data.decode()
        print("Got:", msg, "from", addr)

        if msg.startswith("HELLO"):
            nodes.add(addr[0])  # store IP of sender
            reply = "WELCOME, I see you: " + addr[0]
            udp.sendto(reply.encode(), addr)

    except OSError:
        # no data received during timeout, that’s fine
        pass

    # every few seconds, broadcast list of nodes
    if nodes:
        broadcast = "NODES: " + ", ".join(nodes)
        for ip in list(nodes):
            try:
                udp.sendto(broadcast.encode(), (ip, 5000))
            except OSError:
                pass
        time.sleep(3)
```


Pico B and C (Clients that discover + listen for node list)
```python
# pico_client.py
import network, socket, time

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")
while not sta.isconnected():
    time.sleep(1)
print("Connected:", sta.ifconfig())

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(5)

server_ip = "192.168.4.1"   # AP IP
udp.sendto(b"HELLO from client", (server_ip, 5000))

while True:
    try:
        data, addr = udp.recvfrom(1024)
        msg = data.decode()
        print("Got:", msg, "from", addr)
    except OSError:
        print("No message, retrying HELLO")
        udp.sendto(b"HELLO again", (server_ip, 5000))
```

- When each client connects, it sends "HELLO" to the AP.
- The AP logs the client IP in its nodes set.
- Every few seconds, the AP sends "NODES: ..." to all registered clients.
- Each client sees both its own IP and the others in the message, giving a global view of the group.



### The Wireless Bus

Here’s a way to extend the AP + discovery approach so clients can talk directly to each
other once they know each other’s IPs. The AP still exists as a discovery server, but after
that clients can communicate peer-to-peer.


1. AP (Discovery Server)

Same as before, but it only handles discovery, not messaging:
```python
# pico_ap.py
import network, socket, time

ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")
ap.active(True)
print("AP started:", ap.ifconfig())

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 5000))
udp.settimeout(0.5)

nodes = set()

while True:
    try:
        data, addr = udp.recvfrom(1024)
        msg = data.decode()
        if msg.startswith("HELLO"):
            nodes.add(addr[0])
            udp.sendto(",".join(nodes).encode(), addr)
    except OSError:
        pass
```

2. Clients (Peer-to-Peer Messaging)

After discovery, clients know all other nodes and can open direct UDP connections:
```python
# pico_client.py
import network, socket, time

# Connect to AP
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")
while not sta.isconnected():
    time.sleep(1)
my_ip = sta.ifconfig()[0]
print("Connected, IP:", my_ip)

# UDP socket
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(2)

# Discovery: send HELLO to AP
ap_ip = "192.168.4.1"
udp.sendto(b"HELLO", (ap_ip, 5000))

try:
    data, addr = udp.recvfrom(1024)
    nodes = data.decode().split(",")
    print("Discovered nodes:", nodes)
except OSError:
    nodes = []

# Remove self from the list
nodes = [ip for ip in nodes if ip != my_ip]

# Send a direct message to each peer
for peer_ip in nodes:
    udp.sendto(b"Hi from " + my_ip.encode(), (peer_ip, 5001))

# Listen for messages from peers
udp.bind((my_ip, 5001))  # listen on port 5001 for incoming peer messages
while True:
    try:
        data, addr = udp.recvfrom(1024)
        print("Peer message from", addr, ":", data.decode())
    except OSError:
        pass
```

1. Discovery: Each client sends "HELLO" to the AP and receives the current list of IPs.
2. Peer-to-peer messaging: Each client then opens a direct UDP connection to the other clients using their IPs.
3. Listening: Clients bind to a separate port (5001) to receive messages from peers.

This allows multiple Pico Ws to communicate directly, without routing messages
through the AP after discovery. The AP’s role is now only dynamic IP discovery.


### UDP more ..

3-node example where each Pico can both send and receive messages to/from every other
node continuously--basically a tiny mesh-like setup using just UDP. This would show
exactly how three (or more) Picos could communicate as equals.


1. AP Pico.  Discovery Only

```python
# pico_ap.py
import network, socket, time

# Start AP
ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")
ap.active(True)
print("AP IP:", ap.ifconfig()[0])

# UDP socket for discovery
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 5000))
udp.settimeout(0.5)

nodes = set()  # IPs of connected clients

while True:
    try:
        data, addr = udp.recvfrom(1024)
        if data.decode().startswith("HELLO"):
            nodes.add(addr[0])
            # reply with full node list
            udp.sendto(",".join(nodes).encode(), addr)
    except OSError:
        pass
```


2. Client Pico — Dynamic Peer List + Messaging
```python
# pico_client_dynamic.py
import network, socket, time, _thread

# Connect to AP
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")
while not sta.isconnected():
    time.sleep(1)
my_ip = sta.ifconfig()[0]
print("Connected, IP:", my_ip)

# UDP socket for sending/receiving peer messages
peer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peer_sock.bind((my_ip, 5001))
peer_sock.settimeout(0.5)

peer_list = []

# Thread to listen for incoming messages from peers
def listen_peers():
    while True:
        try:
            data, addr = peer_sock.recvfrom(1024)
            print("Peer message from", addr[0], ":", data.decode())
        except OSError:
            pass

_thread.start_new_thread(listen_peers, ())

ap_ip = "192.168.4.1"

def discover_peers():
    global peer_list
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(2)
    try:
        udp.sendto(b"HELLO", (ap_ip, 5000))
        data, _ = udp.recvfrom(1024)
        nodes = data.decode().split(",")
        # remove self IP
        peer_list = [ip for ip in nodes if ip != my_ip]
        print("Discovered peers:", peer_list)
    except OSError:
        print("Discovery failed")
    udp.close()

# Main loop: periodically discover and send messages
while True:
    discover_peers()
    for peer_ip in peer_list:
        msg = "Hello from " + my_ip
        try:
            peer_sock.sendto(msg.encode(), (peer_ip, 5001))
        except OSError:
            pass
    time.sleep(5)
```

1. Each client re-discovers peers every 5 seconds via the AP.
2. Peer list is updated dynamically: new clients are added, disconnected clients are automatically ignored.
3. Each client continues sending messages to all known peers.
4. The AP still only handles discovery; all messaging is direct between clients.
5. Adding more Picos just works--as long as they connect to the AP and send "HELLO", they appear in every client’s list.


This gives a fully dynamic, small mesh-like network with:
- Automatic joining and leaving of nodes.
- Direct peer-to-peer messaging.
- Scalable beyond three devices.


#### Master - Clients

1. AP Pico. Discovery Server (SAME)
```python
# pico_ap.py
import network, socket, time

ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")
ap.active(True)
print("AP IP:", ap.ifconfig()[0])

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 5000))
udp.settimeout(0.5)

nodes = []  # store client IPs in order

while True:
    try:
        data, addr = udp.recvfrom(1024)
        if data.decode().startswith("HELLO"):
            ip = addr[0]
            if ip not in nodes:
                nodes.append(ip)  # keep order for role assignment
            # reply with ordered node list
            udp.sendto(",".join(nodes).encode(), addr)
    except OSError:
        pass
```



2. Client Pico. Discovery + Automatic Roles

```python
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
```


1. AP keeps nodes in order of first discovery.
2. First IP in the list → MASTER, the rest become WORKER1, WORKER2, etc.
3. Each Pico maintains its own role and a map of all peers’ roles.
4. After discovery, all Picos can communicate directly (peer-to-peer) using the list of IPs.


- No need to manually assign MASTER/WORKER.
- Supports dynamic joining: new clients discover the AP and are assigned a WORKER role automatically.
- Clients leaving is handled automatically: after a failed send/timeout or re-discovery, the peer list updates.

If MASTER fails though .. all collapse!





