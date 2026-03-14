# MicroPython Dual-Core File Server

A complete file server implementation for MicroPython using dual-core architecture with WebDAV-like HTTP interface.

## Architecture

### Core 1 (File Handler)
- Handles all file operations (read, write, delete)
- Manages metadata and SD card access
- Processes requests from Core 0 via queue system
- Thread-safe with locking mechanisms

### Core 0 (TCP Server)
- Runs HTTP server on port 8080 (configurable)
- Implements WebDAV-like REST API
- Handles client connections
- Routes requests to Core 1

## Features

✅ **Dual-core design** - Separate file I/O from network handling  
✅ **REST API** - Simple HTTP interface  
✅ **File operations** - Upload, download, list, delete  
✅ **Metadata tracking** - File sizes, timestamps  
✅ **SD card stats** - Space usage, file count  
✅ **Thread-safe** - Queue-based inter-core communication  
✅ **Web client** - Beautiful HTML/JS interface  

## API Endpoints

### GET /
List all files on SD card
```json
[
  {
    "name": "hello.txt",
    "size": 12,
    "created": 1234567890,
    "modified": 1234567890
  }
]
```

### GET /stats
Get SD card statistics
```json
{
  "files": 5,
  "used_by_vfs": 1024,
  "total_space": 8000000,
  "free_space": 7998976,
  "used_percent": 0.0128
}
```

### GET /file/{filename}
Download a file
- Returns: Binary file data
- Status: 200 OK or 404 Not Found

### PUT /file/{filename}
Upload a file
- Body: Binary file data
- Status: 201 Created or 500 Error

### DELETE /file/{filename}
Delete a file
- Status: 200 OK or 404 Not Found

### HEAD /file/{filename}
Check if file exists
- Status: 200 OK or 404 Not Found

## Installation

### 1. Hardware Setup
Connect SD card to Raspberry Pi Pico:
- CS (Chip Select) → GP1
- SCK (Clock) → GP2
- MOSI (Data In) → GP3
- MISO (Data Out) → GP4
- VCC → 3.3V
- GND → GND

### 2. Upload to MicroPython

Copy `file_server.py` to your MicroPython device:

```python
# Upload via Thonny, rshell, or mpremote
mpremote cp file_server.py :file_server.py
```

### 3. Configure Network (WiFi)

Add WiFi configuration to your `main.py` or boot script:

```python
import network
import time

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected!')
        status = wlan.ifconfig()
        print('IP:', status[0])
        return status[0]

# Connect to WiFi
ip = connect_wifi('YOUR_SSID', 'YOUR_PASSWORD')

# Start file server
import file_server
server = file_server.FileServer(mount_point="/sd", port=8080)
server.start()
```

### 4. Run the Server

```python
# Option 1: Auto-start with main.py
# The server will start automatically on boot

# Option 2: Manual start via REPL
>>> import file_server
>>> server = file_server.FileServer("/sd", 8080)
>>> server.start()
```

## Using the Web Client

1. Open `file_server_client.html` in a web browser
2. Enter your MicroPython device IP address
3. Click "Connect"
4. Upload, download, and manage files!

### Features:
- 📊 Real-time SD card statistics
- ⬆️ Drag & drop file upload
- ⬇️ One-click download
- 🗑️ File deletion
- 📝 Activity log
- 🎨 Beautiful gradient UI

## Example Usage

### Python Client Example

```python
import requests

server = "http://192.168.1.100:8080"

# List files
files = requests.get(f"{server}/").json()
print("Files:", files)

# Upload a file
with open("test.txt", "rb") as f:
    requests.put(f"{server}/file/test.txt", data=f.read())

# Download a file
response = requests.get(f"{server}/file/test.txt")
with open("downloaded.txt", "wb") as f:
    f.write(response.content)

# Get stats
stats = requests.get(f"{server}/stats").json()
print(f"Files: {stats['files']}, Used: {stats['used_by_vfs']} bytes")

# Delete a file
requests.delete(f"{server}/file/test.txt")
```

### JavaScript Client Example

```javascript
const server = 'http://192.168.1.100:8080';

// List files
fetch(`${server}/`)
  .then(r => r.json())
  .then(files => console.log('Files:', files));

// Upload a file
const fileData = new Uint8Array([72, 101, 108, 108, 111]); // "Hello"
fetch(`${server}/file/hello.txt`, {
  method: 'PUT',
  body: fileData
});

// Download a file
fetch(`${server}/file/hello.txt`)
  .then(r => r.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hello.txt';
    a.click();
  });

// Delete a file
fetch(`${server}/file/hello.txt`, { method: 'DELETE' });
```

### cURL Examples

```bash
# List files
curl http://192.168.1.100:8080/

# Get stats
curl http://192.168.1.100:8080/stats

# Upload a file
curl -X PUT --data-binary @myfile.txt http://192.168.1.100:8080/file/myfile.txt

# Download a file
curl http://192.168.1.100:8080/file/myfile.txt -o downloaded.txt

# Delete a file
curl -X DELETE http://192.168.1.100:8080/file/myfile.txt

# Check if file exists
curl -I http://192.168.1.100:8080/file/myfile.txt
```

## Customization

### Change Port
```python
server = FileServer("/sd", port=9000)
```

### Different Mount Point
```python
server = FileServer("/flash", port=8080)
```

### Custom SD Card Pins
Edit the `initialize_sd_card()` function:
```python
cs = machine.Pin(5, machine.Pin.OUT)  # Change CS pin
sck = machine.Pin(6)                   # Change SCK pin
# etc...
```

## Memory Considerations

- Uses thread-safe queues for inter-core communication
- Garbage collection after each client connection
- Efficient binary file handling
- Metadata cached in memory, persisted to JSON

## Troubleshooting

### SD Card Not Mounting
- Check wiring connections
- Verify SD card is formatted as FAT32
- Try lower SPI baudrate (500000 instead of 1000000)

### Can't Connect from Client
- Verify device IP address (check REPL output)
- Ensure device and client on same network
- Check firewall settings
- Try pinging the device

### Out of Memory Errors
- Reduce file buffer sizes
- Add more `gc.collect()` calls
- Use smaller files for testing

### Files Not Showing
- Verify metadata file exists: `/sd/.vfs_metadata.json`
- Check file permissions
- Restart the server

## Performance Notes

- **Max file size**: Limited by available RAM (~2MB on Pico W)
- **Concurrent connections**: 1 at a time (queue-based)
- **Throughput**: ~50-100 KB/s depending on SD card
- **Response time**: <100ms for file list, varies for large files

## Security Considerations

⚠️ **This is a development/educational tool**

- No authentication implemented
- No encryption (use on trusted networks only)
- No input validation beyond basic checks
- No rate limiting
- Suitable for local networks, IoT projects, testing

## License

MIT License - Feel free to modify and use in your projects!

## Credits

Built for MicroPython on Raspberry Pi Pico W with dual-core architecture.
