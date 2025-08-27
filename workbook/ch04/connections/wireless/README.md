
## Raspberry Pi Pico W

Raspberry Pi Pico W can act as a Wi-Fi Access Point (AP) on its own,
without needing an external router.

The wireless chip on the Pico W (Infineon CYW43439) supports both *station mode*
(connect to an existing Wi-Fi network) and *access point mode* (create its own
Wi-Fi network). In *AP* mode, the Pico W creates a Wi-Fi network (SSID) that other
devices--laptops, phones, or another Pico W--can connect to directly.


### Sample

AP

```python
import network

# AP = access point
ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")  # WPA2 password required (8+ chars)
ap.active(True)

print("AP active, SSID:", ap.config("essid"))
print("AP IP:", ap.ifconfig()[0])
```

STA

1.
```python
import network, time

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")

while not sta.isconnected():
    time.sleep(1)
print("Connected, IP:", sta.ifconfig()[0])
```



### TCP


#### AP

```python
import network
import socket
import time

# AP
ap = network.WLAN(network.AP_IF)
ap.config(essid="PicoAP", password="pico1234")  # WPA2, password ≥ 8 chars
ap.active(True)

print("Access Point active")
print("AP IP:", ap.ifconfig()[0])

# Wait a moment .. to stabilise
time.sleep(2)

# Create TCP server socket
addr = socket.getaddrinfo("0.0.0.0", 1234)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

while True:
    cl, remote = s.accept()
    print("Client connected from", remote)
    data = cl.recv(1024)
    print("Received:", data.decode())
    cl.send(b"Hello from Pico Server")
    cl.close()
```

#### STA

```python
import network
import socket
import time

# Connect to PicoAP
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("PicoAP", "pico1234")

print("Connecting..")
while not sta.isconnected():
    time.sleep(1)
print("Connected, IP:", sta.ifconfig()[0])

# Replace with the server’s IP (printed by AP Pico) if need
server_ip = "192.168.4.1"   # default AP IP on Pico W
server_port = 1234

# Connect and send message
addr = socket.getaddrinfo(server_ip, server_port)[0][-1]
s = socket.socket()
s.connect(addr)
s.send(b"Hello from Pico Client")

# Receive reply
data = s.recv(1024)
print("Received:", data.decode())
s.close()
```


- The server Pico W starts in AP mode and creates a Wi-Fi network called PicoAP.
- It runs a TCP server on port 1234 and waits for connections.
- The client Pico W connects to that SSID in STA mode, then opens a
  TCP connection to 192.168.4.1 (the AP’s default IP).
- They exchange simple text messages over sockets.



By default, when a Pico W acts as an access point, it creates a tiny private network with:
- AP Pico W (server) at IP 192.168.4.1 (always this by default in MicroPython).
- Client Pico W (station) gets assigned an IP automatically via DHCP (e.g. 192.168.4.2).

So if one Pico is always the AP, you don’t really need to guess or hardcode its IP.
You can safely assume it will be 192.168.4.1. That’s why in the client example above,
the server is set server_ip = "192.168.4.1".



### Discovery


Common approaches for this in embedded/Wi-Fi contexts:

1. Static addressing (simplest).
Decide that the AP always has 192.168.4.1, and clients always use whatever DHCP gives them. They just connect to 192.168.4.1 without discovery.

2. Well-known port + broadcast.
The client can send a UDP broadcast like “Who is the server?” on a fixed port, and the server replies with its IP. (This is a minimal discovery protocol.)

3. mDNS / Zeroconf (Bonjour/Avahi).
Some MicroPython builds support this, but it’s heavier. It lets you reach devices by name (e.g. pico.local) without knowing the IP. The RP2040 + CYW43439 doesn’t have it by default, but people have hacked simple mDNS responders in MicroPython.

4. Pre-shared role convention.
Decide in advance that one Pico will always be the AP/server, the other always the STA/client. No discovery is needed — just use the fixed AP IP.


So,

1. One fixed AP, others are clients (simplest)

- Pick one Pico W to always act as AP (say “node A”).
- It will always have IP 192.168.4.1.
- The others connect as clients and use that address.
- Roles (server vs. client) can still be decided by a discovery handshake after they are connected.

This is easy to set up and avoids chaos, but it means one device has a "special" role (server).


2. Discovery over broadcast (no fixed AP knowledge)

- Designate any Pico that boots first as AP.
- Others boot in STA mode, and first try to connect to known SSIDs (PicoAP for example).
- Once joined, each Pico sends a UDP broadcast packet (e.g. “I am node B, available”).
- Every Pico that hears it responds with its ID and role.
- Now each node knows who else is on the network.

This lets you build a 2- or 3-node cluster without hardcoding which one is server/client.


3. True peer-to-peer (Wi-Fi Direct)

The CYW43439 chip in the Pico W supports Wi-Fi Direct (P2P), but MicroPython (and even the C SDK)
doesn’t expose it yet(?). So right now, you can’t have three Picos negotiate without one acting as an AP.



Practical demo idea (Option 2)

You could do something like this:
- Server Pico (AP):
- Brings up AP PicoAP.
- Starts UDP listener on port 5000.
- When it receives “HELLO” from a client, it replies with “I am server at 192.168.4.1”.
- Client Picos (STA):
- Connect to PicoAP.
- Broadcast “HELLO” on UDP port 5000.
- Wait for replies and record who is present.
- They can then decide roles (e.g. the first to reply is “server”, the rest are “clients”).


### Three Way Scenario

Once connected, the clients broadcast a UDP “HELLO” message, and the AP replies so everyone knows who’s on the network. From there you can build your own role negotiation logic (e.g. one acts as master, the rest as workers).


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

Here’s a way to extend the AP + discovery approach so clients can talk directly to each other once they know each other’s IPs. The AP still exists as a discovery server, but after that clients can communicate peer-to-peer.


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

If MASTER fails though ..





