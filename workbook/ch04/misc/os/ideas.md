

OS ILLUSTRATION IDEA
scheduling, isolation, I/O, and interface — the key OS ideas in miniature

* A microkernel with message-passing + a simple shell.
* Processes = separate tasks (e.g., logging, display, sensor).
* Communication = messages (students see "no globals").
* Shell = user interacts with OS concepts.



Message-Passing Microkernel
- Principle: Isolation, IPC (inter-process communication).

- Define processes as tasks.
- They communicate only by sending messages (mailbox) through a central kernel "post office".
- Example: one process reads sensor, one logs to SD, one updates display.

- Very close to modern microkernel ideas.
- Stretch: Add message queues, priorities, or "drivers" as separate processes.




Interactive Shell
- Principle: User interface, command interpretation.

- One Pico runs a shell process on the display pack.
- Students type commands (via Wi-Fi "keyboard" from ordinary comp).
- Commands can be "apps" (processes) managed by the kernel.

- Shows interaction between kernel, filesystem, user space.
- Stretch: Add scripting, or combine with scheduler so commands run in background.






## Tiny Distributed OS (TDOS)

IDEAS IDEAS IDEAS

A lightweight abstraction layer that makes multiple
Raspberry Pi Pico W boards behave like one system.
- One Pico W (Display Node) runs the kernel, manages the Pimoroni display,
  and provides the API for user programs.
- One Pico W (Sensor Node) runs a driver service for a temperature sensor.
- The nodes communicate over Wi-Fi using a simple message protocol (JSON over UDP).
- To the user program, resources (display, sensors, etc.) look like local
  devices accessed via open(), read(), and write() calls.
- Nodes automatically discover each other: no hard-coded IP addresses.

Stretch goal: add fault detection so the system notices when a node disappears.



### High-Level API

A user program sees this unified interface:
```python
import tinyos
import time

tinyos.init()

display = tinyos.open_display()
temp_sensor = tinyos.open_temp_sensor()

while True:
    temp = tinyos.read(temp_sensor)
    tinyos.write(display, f"Temp: {temp:.1f} °C")
    time.sleep(2)
```
This is the "illusion" of one OS spanning multiple boards.



#### Architecture

1. Kernel (Display Node)
- Provides the tinyos API.
- Knows how to handle local devices (the display).
- For remote devices, it sends RPCs to other nodes.

2. Driver Nodes (e.g., Temp Sensor Node)
- On boot, each driver node broadcasts service announcements like:

```json
{"service": "temp_sensor", "ip": "192.168.4.12", "port": 5000}
```

- The kernel stores these in a service registry.

3. Communication
- UDP broadcast for service discovery.
- UDP unicast for RPCs (e.g., “get temperature”).



#### Implementation Sketch

1. Common Service Protocol

```python
# protocol.py
import json

def encode(msg):
    return json.dumps(msg).encode()

def decode(data):
    return json.loads(data.decode())
```


2. Driver Node (Temp Sensor)

```python
# temp_node.py
import network, socket, time, machine, protocol

# fake temp sensor for now
def read_temp():
    return 20.0 + (time.time() % 10)

SSID = "TDOS"
PASSWORD = "12345678"

# Wi-Fi station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

# UDP socket for serving
srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
srv.bind(("", 5000))

# announce service
bc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

announce = protocol.encode({"service":"temp_sensor","port":5000})
bc.sendto(announce, ("255.255.255.255", 4000))

while True:
    data, addr = srv.recvfrom(1024)
    req = protocol.decode(data)
    if req["op"] == "get_temp":
        resp = protocol.encode({"temp": read_temp()})
        srv.sendto(resp, addr)
```


3. Kernel Node (Display + OS API)
```python
# tinyos.py
import socket, time, protocol
from pimoroni import Display

services = {}

def init():
    # listen for service announcements
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", 4000))
    udp.settimeout(0.5)
    start = time.time()
    while time.time() - start < 5:   # wait a few seconds
        try:
            data, addr = udp.recvfrom(1024)
            msg = protocol.decode(data)
            services[msg["service"]] = (addr[0], msg["port"])
        except OSError:
            pass

display = Display()

def open_display():
    return "display"

def open_temp_sensor():
    return "temp_sensor"

def write(handle, message):
    if handle == "display":
        display.clear()
        display.text(message, 10, 10, 240, 240, scale=3)
        display.update()

def read(handle):
    if handle == "temp_sensor":
        ip, port = services[handle]
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.settimeout(1)
        udp.sendto(protocol.encode({"op":"get_temp"}), (ip, port))
        data, _ = udp.recvfrom(1024)
        return protocol.decode(data)["temp"]
```


4. User Program (Runs on Kernel Node)
```python
# app.py
import tinyos, time

tinyos.init()

display = tinyos.open_display()
temp_sensor = tinyos.open_temp_sensor()

while True:
    temp = tinyos.read(temp_sensor)
    if temp is not None:
        tinyos.write(display, f"Temp: {temp:.1f} °C")
    else:
        tinyos.write(display, "Temp sensor offline")
    time.sleep(2)
```


Tiny Distributed OS:
- Resources are virtualised (open, read, write)
- Remote and local devices look the same
- Service discovery means no hard-coding of IPs
- Fault tolerance is possible by handling timeouts

