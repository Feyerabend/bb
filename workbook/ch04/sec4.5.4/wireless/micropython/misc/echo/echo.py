import socket
import network
import time
from machine import Pin

class TCPEchoServer:    
    def __init__(self, port=8080):
        self.port = port
        self.server_socket = None
        self.setup_socket()
    
    def setup_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"TCP Echo Server listening on port {self.port}")
    
    def handle_client(self, client_socket, client_addr):
        print(f"TCP client connected: {client_addr}")
        
        try:
            client_socket.send(b"TCP Echo Server - Enter messages to echo back\n")
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                print(f"Received: {message}")
                
                if message.upper() == 'QUIT':
                    client_socket.send(b"Goodbye!\n")
                    break
                
                # Echo message back to client
                echo_response = f"Echo: {message}\n"
                client_socket.send(echo_response.encode('utf-8'))
                
        except Exception as e:
            print(f"TCP client error: {e}")
        finally:
            client_socket.close()
            print(f"TCP client {client_addr} disconnected")
    
    def run(self):
        while True:
            try:
                client_socket, client_addr = self.server_socket.accept()
                self.handle_client(client_socket, client_addr)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"TCP server error: {e}")
                time.sleep(1)
        
        self.server_socket.close()

# TCP server usage
tcp_server = TCPEchoServer()
tcp_server.run()
