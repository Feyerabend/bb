import socket
import time
import json
from machine import Pin

class UDPBroadcastServer:    
    def __init__(self, port=8081):
        self.port = port
        self.socket = None
        self.setup_socket()
    
    def setup_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        print(f"UDP Broadcast Server listening on port {self.port}")
    
    def send_status_broadcast(self):
        status_data = {
            'device': 'Pico W',
            'timestamp': time.time(),
            'uptime': time.ticks_ms(),
            'free_memory': gc.mem_free(),
            'temperature': 25.0  # Placeholder - could read actual sensor
        }
        
        message = json.dumps(status_data)
        
        # Send to broadcast address
        try:
            self.socket.sendto(message.encode('utf-8'), ('255.255.255.255', 9999))
            print(f"Broadcast sent: {message}")
        except Exception as e:
            print(f"Broadcast error: {e}")
    
    def handle_incoming(self):
        try:
            self.socket.settimeout(1.0)  # Non-blocking with 1 second timeout
            data, addr = self.socket.recvfrom(1024)
            
            message = data.decode('utf-8')
            print(f"UDP message from {addr}: {message}")
            
            # Send acknowledgment
            response = f"ACK: Received '{message}'"
            self.socket.sendto(response.encode('utf-8'), addr)
            
        except socket.timeout:
            pass  # No data received, continue
        except Exception as e:
            print(f"UDP receive error: {e}")
    
    def run(self):
        last_broadcast = time.time()
        broadcast_interval = 5.0  # 5 seconds
        
        while True:
            try:
                # Handle incoming messages
                self.handle_incoming()
                
                # Send periodic broadcasts
                current_time = time.time()
                if current_time - last_broadcast >= broadcast_interval:
                    self.send_status_broadcast()
                    last_broadcast = current_time
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"UDP server error: {e}")
                time.sleep(1)
        
        self.socket.close()

# UDP server usage
import gc
udp_server = UDPBroadcastServer()
udp_server.run()

