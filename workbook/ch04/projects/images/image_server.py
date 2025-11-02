import machine
import sdcard
import uos
import ujson
import utime
import network
import socket

# ============= VFS Component =============
class SimpleVFS:
    def __init__(self, mount_point="/sd"):
        self.mount_point = mount_point
        self.metadata_file = f"{mount_point}/.vfs_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        try:
            with open(self.metadata_file, "r") as f:
                return ujson.load(f)
        except:
            return {}
    
    def _save_metadata(self):
        with open(self.metadata_file, "w") as f:
            ujson.dump(self.metadata, f)
    
    def create_file(self, filename, data, permissions="rw"):
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "wb") as f:
            if isinstance(data, str):
                f.write(data.encode())
            else:
                f.write(data)
        
        self.metadata[filename] = {
            "permissions": permissions,
            "created": utime.time(),
            "size": len(data)
        }
        self._save_metadata()
        print(f"Created: {filename} ({len(data)} bytes)")
    
    def read_file(self, filename):
        if filename not in self.metadata:
            raise FileNotFoundError(f"File not found: {filename}")
        
        if 'r' not in self.metadata[filename]["permissions"]:
            raise OSError(f"No read permission: {filename}")
        
        full_path = f"{self.mount_point}/{filename}"
        with open(full_path, "rb") as f:
            return f.read()
    
    def list_files(self):
        return [{"name": f, "size": m["size"]} 
                for f, m in self.metadata.items()]
    
    def file_exists(self, filename):
        return filename in self.metadata
    
    def get_file_size(self, filename):
        if filename not in self.metadata:
            return None
        return self.metadata[filename]["size"]


# ============= Compression =============
class RLECompressor:
    """Simple Run-Length Encoding for image data"""
    
    @staticmethod
    def compress(data):
        """Compress bytes using RLE"""
        if len(data) == 0:
            return bytes()
        
        compressed = bytearray()
        i = 0
        while i < len(data):
            current = data[i]
            count = 1
            
            # Count consecutive identical bytes (max 255)
            while i + count < len(data) and data[i + count] == current and count < 255:
                count += 1
            
            compressed.append(count)
            compressed.append(current)
            i += count
        
        return bytes(compressed)
    
    @staticmethod
    def decompress(data):
        """Decompress RLE data"""
        decompressed = bytearray()
        i = 0
        while i < len(data) - 1:
            count = data[i]
            value = data[i + 1]
            decompressed.extend([value] * count)
            i += 2
        return bytes(decompressed)


# ============= Network Server =============
class ImageServer:
    def __init__(self, vfs, ssid="PicoImageServer", password="pico12345", port=8080):
        self.vfs = vfs
        self.ssid = ssid
        self.password = password
        self.port = port
        self.ap = None
        self.server_socket = None
        
    def start_access_point(self):
        """Start WiFi Access Point"""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(essid=self.ssid, password=self.password)
        self.ap.active(True)
        
        # Wait for AP to be active
        while not self.ap.active():
            utime.sleep(0.1)
        
        print(f"AP Started: {self.ssid}")
        print(f"IP: {self.ap.ifconfig()[0]}")
        print(f"Connect with password: {self.password}")
        
    def start_server(self):
        """Start TCP server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(1)
        print(f"Server listening on port {self.port}")
    
    def handle_list_request(self, conn):
        """Send list of available files"""
        files = self.vfs.list_files()
        response = ujson.dumps(files)
        conn.send(f"OK|{len(response)}|".encode())
        conn.send(response.encode())
        
    def handle_get_request(self, conn, filename):
        """Send image file with compression"""
        try:
            if not self.vfs.file_exists(filename):
                conn.send(b"ERROR|File not found")
                return
            
            print(f"Reading: {filename}")
            raw_data = self.vfs.read_file(filename)
            
            # Compress data
            print(f"Compressing {len(raw_data)} bytes...")
            compressed = RLECompressor.compress(raw_data)
            ratio = len(compressed) / len(raw_data) * 100
            print(f"Compressed to {len(compressed)} bytes ({ratio:.1f}%)")
            
            # Send header: OK|original_size|compressed_size|
            header = f"OK|{len(raw_data)}|{len(compressed)}|".encode()
            conn.send(header)
            
            # Send compressed data in chunks
            chunk_size = 1024
            for i in range(0, len(compressed), chunk_size):
                chunk = compressed[i:i+chunk_size]
                conn.send(chunk)
                
            print("Transfer complete")
            
        except Exception as e:
            error_msg = f"ERROR|{str(e)}"
            conn.send(error_msg.encode())
            print(f"Error: {e}")
    
    def run(self):
        """Main server loop"""
        self.start_access_point()
        self.start_server()
        
        print("\nWaiting for clients...")
        
        while True:
            try:
                conn, addr = self.server_socket.accept()
                print(f"\nClient connected: {addr}")
                
                # Receive request
                request = conn.recv(256).decode().strip()
                print(f"Request: {request}")
                
                if request.startswith("LIST"):
                    self.handle_list_request(conn)
                    
                elif request.startswith("GET|"):
                    filename = request.split("|")[1]
                    self.handle_get_request(conn, filename)
                    
                else:
                    conn.send(b"ERROR|Invalid request format")
                
                conn.close()
                print("Connection closed")
                
            except Exception as e:
                print(f"Error handling client: {e}")
                try:
                    conn.close()
                except:
                    pass


# ============= Main Setup =============
def main():
    # Initialize SD card
    try:
        cs = machine.Pin(1, machine.Pin.OUT)
        spi = machine.SPI(0,
                          baudrate=1000000,
                          polarity=0,
                          phase=0,
                          bits=8,
                          firstbit=machine.SPI.MSB,
                          sck=machine.Pin(2),
                          mosi=machine.Pin(3),
                          miso=machine.Pin(4))
        sd = sdcard.SDCard(spi, cs)
        vfs_fat = uos.VfsFat(sd)
        uos.mount(vfs_fat, "/sd")
        print("SD card mounted")
    except Exception as e:
        print(f"SD card error: {e}")
        raise
    
    # Create VFS wrapper
    vfs = SimpleVFS("/sd")
    
    # Create some test images (replace with real image data)
    # For DisplayPack 2.0: 320x240 pixels, RGB565 format (2 bytes per pixel)
    # Total: 153,600 bytes per full image
    test_data = bytes([i % 256 for i in range(1000)])  # Dummy data
    vfs.create_file("test.img", test_data)
    
    print("\nStarting image server...")
    server = ImageServer(vfs, ssid="PicoImages", password="raspberry")
    server.run()

if __name__ == "__main__":
    main()