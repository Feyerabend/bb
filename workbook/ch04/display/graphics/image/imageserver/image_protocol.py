# Custom Image Transfer Protocol (CITP)
# Simple message-based protocol for transferring compressed images

import socket
import struct
import time
import hashlib

class ImageProtocol:
    
    # Protocol constants
    MAX_CHUNK_SIZE = 1024  # Maximum chunk size in bytes
    TIMEOUT = 10           # Socket timeout in seconds
    RETRY_COUNT = 3        # Number of retries for failed operations
    
    # Message types
    MSG_REQUEST = b'REQ'
    MSG_HEADER = b'HDR'
    MSG_DATA = b'DAT'
    MSG_END = b'END'
    MSG_ERROR = b'ERR'
    MSG_ACK = b'ACK'
    MSG_RETRY = b'RTY'

    # Format: [msg_type(3 bytes)][length(2 bytes)][data]
    @staticmethod
    def create_message(msg_type, data=b''):
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        length = len(data)
        header = msg_type + struct.pack('<H', length)
        return header + data

    # Returns: (msg_type, data) or (None, None) on error
    @staticmethod
    def parse_message(raw_data):
        if len(raw_data) < 5:  # Minimum message size
            return None, None
        
        msg_type = raw_data[:3]
        length = struct.unpack('<H', raw_data[3:5])[0]
        
        if len(raw_data) < 5 + length:
            return None, None
        
        data = raw_data[5:5+length]
        return msg_type, data
    
    @staticmethod
    def calculate_checksum(data):
        return hashlib.md5(data).digest()



class ImageServer:    
    def __init__(self, port=8080):
        self.port = port
        self.socket = None
        self.images = {}  # Dictionary to store loaded images
        
    def load_compressed_image(self, filename, image_id):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            self.images[image_id] = data
            print(f"Loaded image '{image_id}' ({len(data)} bytes)")
            return True
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return False
    
    def start_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            
            print(f"Image server started on port {self.port}")
            return True
            
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def handle_client(self, client_socket):
        client_socket.settimeout(ImageProtocol.TIMEOUT)
        
        try:
            # Receive request
            request_data = self._receive_message(client_socket)
            if not request_data:
                return False
            
            msg_type, data = ImageProtocol.parse_message(request_data)
            
            if msg_type == ImageProtocol.MSG_REQUEST:
                image_id = data.decode('utf-8')
                print(f"Client requested image: {image_id}")
                
                if image_id in self.images:
                    return self._send_image(client_socket, image_id)
                else:
                    # Send error
                    error_msg = ImageProtocol.create_message(
                        ImageProtocol.MSG_ERROR, 
                        f"Image '{image_id}' not found"
                    )
                    client_socket.send(error_msg)
                    return False
            
        except Exception as e:
            print(f"Error handling client: {e}")
            return False
    
    def _send_image(self, client_socket, image_id):
        try:
            image_data = self.images[image_id]
            
            # Send header with image info
            header_info = f"{image_id}:{len(image_data)}"
            header_msg = ImageProtocol.create_message(
                ImageProtocol.MSG_HEADER, 
                header_info
            )
            client_socket.send(header_msg)
            
            # Wait for ACK
            ack_data = self._receive_message(client_socket)
            if not ack_data or ImageProtocol.parse_message(ack_data)[0] != ImageProtocol.MSG_ACK:
                return False
            
            # Send image data in chunks!
            bytes_sent = 0
            while bytes_sent < len(image_data):
                chunk_size = min(ImageProtocol.MAX_CHUNK_SIZE, len(image_data) - bytes_sent)
                chunk_data = image_data[bytes_sent:bytes_sent + chunk_size]
                
                data_msg = ImageProtocol.create_message(ImageProtocol.MSG_DATA, chunk_data)
                client_socket.send(data_msg)
                
                # Wait for ACK
                ack_data = self._receive_message(client_socket)
                if not ack_data or ImageProtocol.parse_message(ack_data)[0] != ImageProtocol.MSG_ACK:
                    print("Client didn't acknowledge chunk")
                    return False
                
                bytes_sent += chunk_size
                print(f"Sent chunk: {bytes_sent}/{len(image_data)} bytes")
            
            # Send end message
            end_msg = ImageProtocol.create_message(ImageProtocol.MSG_END)
            client_socket.send(end_msg)
            
            print(f"Successfully sent image '{image_id}'")
            return True
            
        except Exception as e:
            print(f"Error sending image: {e}")
            return False
    
    def _receive_message(self, client_socket):
        try:
            # First receive the header (5 bytes)
            header_data = b''
            while len(header_data) < 5:
                chunk = client_socket.recv(5 - len(header_data))
                if not chunk:
                    return None
                header_data += chunk
            
            # Parse length from header
            length = struct.unpack('<H', header_data[3:5])[0]
            
            # Receive the data
            data = b''
            while len(data) < length:
                chunk = client_socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            return header_data + data
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def run(self):
        if not self.start_server():
            return
        
        try:
            while True:
                print("Waiting for client connection ..")
                client_socket, addr = self.socket.accept()
                print(f"Client connected from {addr}")
                
                self.handle_client(client_socket)
                client_socket.close()
                print("Client disconnected")
                
        except KeyboardInterrupt:
            print("Server shutting down ..")
        finally:
            if self.socket:
                self.socket.close()



class ImageClient:
    def __init__(self, server_host, server_port=8080):
        self.server_host = server_host
        self.server_port = server_port
    
    def request_image(self, image_id, save_filename=None):        
        for attempt in range(ImageProtocol.RETRY_COUNT):
            try:
                # Connect to server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(ImageProtocol.TIMEOUT)
                sock.connect((self.server_host, self.server_port))
                
                print(f"Connected to server {self.server_host}:{self.server_port}")
                
                # Send request
                request_msg = ImageProtocol.create_message(
                    ImageProtocol.MSG_REQUEST, 
                    image_id
                )
                sock.send(request_msg)
                
                # Receive and process response
                image_data = self._receive_image(sock)
                
                sock.close()
                
                if image_data:
                    print(f"Successfully received image '{image_id}' ({len(image_data)} bytes)")
                    
                    if save_filename:
                        with open(save_filename, 'wb') as f:
                            f.write(image_data)
                        print(f"Saved to {save_filename}")
                    
                    return image_data
                else:
                    print(f"Failed to receive image (attempt {attempt + 1})")
                    
            except Exception as e:
                print(f"Connection error (attempt {attempt + 1}): {e}")
                time.sleep(1)  # Wait before retry
        
        print("Failed to receive image after all retries")
        return None
    
    def _receive_image(self, sock):
        try:
            # Receive header
            header_data = self._receive_message(sock)
            if not header_data:
                return None
            
            msg_type, data = ImageProtocol.parse_message(header_data)
            
            if msg_type == ImageProtocol.MSG_ERROR:
                print(f"Server error: {data.decode('utf-8')}")
                return None
            
            if msg_type != ImageProtocol.MSG_HEADER:
                print("Expected header message")
                return None
            
            # Parse header info
            header_info = data.decode('utf-8')
            image_id, total_size = header_info.split(':')
            total_size = int(total_size)
            
            print(f"Receiving image '{image_id}', size: {total_size} bytes")
            
            # Send ACK
            ack_msg = ImageProtocol.create_message(ImageProtocol.MSG_ACK)
            sock.send(ack_msg)
            
            # Receive data chunks
            received_data = b''
            
            while True:
                chunk_data = self._receive_message(sock)
                if not chunk_data:
                    return None
                
                msg_type, data = ImageProtocol.parse_message(chunk_data)
                
                if msg_type == ImageProtocol.MSG_END:
                    break
                elif msg_type == ImageProtocol.MSG_DATA:
                    received_data += data
                    
                    # Send ACK
                    ack_msg = ImageProtocol.create_message(ImageProtocol.MSG_ACK)
                    sock.send(ack_msg)
                    
                    print(f"Received: {len(received_data)}/{total_size} bytes")
                else:
                    print(f"Unexpected message type: {msg_type}")
                    return None
            
            if len(received_data) != total_size:
                print(f"Size mismatch: expected {total_size}, got {len(received_data)}")
                return None
            
            return received_data
            
        except Exception as e:
            print(f"Error receiving image: {e}")
            return None
    
    def _receive_message(self, sock):
        try:
            # Receive header (5 bytes)
            header_data = b''
            while len(header_data) < 5:
                chunk = sock.recv(5 - len(header_data))
                if not chunk:
                    return None
                header_data += chunk
            
            # Parse length
            length = struct.unpack('<H', header_data[3:5])[0]
            
            # Receive data
            data = b''
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            return header_data + data
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None


# Test and demo code
def test_protocol():
    import threading
    import time
    
    # Create a test server in a separate thread
    def run_test_server():
        server = ImageServer(port=8081)
        
        # Create some test data
        test_data = b"This is test image data" * 100  # Simulate compressed image
        with open("test_compressed.img", "wb") as f:
            f.write(test_data)
        
        server.load_compressed_image("test_compressed.img", "test_image")
        server.start_server()
        
        # Handle one client then stop
        client_socket, addr = server.socket.accept()
        server.handle_client(client_socket)
        client_socket.close()
        server.socket.close()
    
    # Start server thread
    server_thread = threading.Thread(target=run_test_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    # Test client
    print("Testing image transfer protocol ..")
    client = ImageClient("localhost", 8081)
    
    # Request the test image
    received_data = client.request_image("test_image", "received_test.img")
    
    if received_data:
        print("Protocol test successful!")
        
        # Verify data integrity
        with open("test_compressed.img", "rb") as f:
            original_data = f.read()
        
        if original_data == received_data:
            print("Data integrity verified!")
        else:
            print("Data integrity check failed!")
    else:
        print("Protocol test failed!")

if __name__ == "__main__":
    test_protocol()


