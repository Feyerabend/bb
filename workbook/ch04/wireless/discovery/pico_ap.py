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
