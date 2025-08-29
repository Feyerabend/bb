
## Raspberry Pi Pico W Image Transfer System

A complete example of wireless image transfer between two Raspberry Pi Pico W
devices using PPM3 format, custom RLE compression, and a custom transfer protocol.

*Server Pico W (with SD card):*
- Stores PPM3 images on SD card
- Compresses images using custom RLE algorithm
- Serves images over WiFi using custom protocol
- Handles multiple client requests

*Client Pico W (with Pimoroni Display Pack):*
- Connects to server via WiFi
- Requests images using custom protocol
- Decompresses and displays images on ST7789 display
- Interactive controls via buttons

## Hardware Requirements

### Server Pico W:
- Raspberry Pi Pico W
- MicroSD card module (SPI)
- SD card with images

### Client Pico W:  
- Raspberry Pi Pico W
- Pimoroni Display Pack (ST7789 240x135 display)

## Software Components

### 1. PPM3 Image Format (`ppm_utils.py`)
- Human-readable ASCII format
- Simple header: `P3 width height maxval`
- RGB triplets: `255 0 0` for red pixel
- Easy to generate and debug

### 2. Custom RLE Compression (`rle_compression.py`)
- Run-length encoding optimized for displays
- Format: `[count][R][G][B]` repeated
- Works well with solid colors and gradients
- Includes compression analysis tools

### 3. Custom Transfer Protocol (`image_protocol.py`)
- Message-based protocol over TCP
- Reliability features: ACK/RETRY, timeouts
- Chunked transfer for large images
- Error handling and flow control

### 4. Display Driver (`display_pack_driver.py`)
- ST7789 display driver
- RGB888 to RGB565 conversion
- Image scaling and positioning
- Loading/error screens

### 5. Complete Applications
- *Server* (`server_main.py`): Full server with WiFi management
- *Client* (`client_main.py`): Interactive client with button controls

## Setup Instructions

### 1. Server Setup

```python
# Configure WiFi credentials in server_main.py
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourWiFiPassword"
SERVER_PORT = 8080

# Upload files to server Pico W:
# - server_main.py (main file)
# - image_protocol.py  
# - ppm_utils.py
# - rle_compression.py

# Create test images or copy your PPM3 files to SD card
```

### 2. Client Setup

```python
# Configure network settings in client_main.py
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourWiFiPassword"  
SERVER_IP = "192.168.1.100"  # Server's IP address
SERVER_PORT = 8080

# Upload files to client Pico W:
# - client_main.py (main file)
# - display_pack_driver.py
# - image_protocol.py
# - rle_compression.py
# - pmp_utils.py
```

### 3. Wiring

*Server Pico W + SD Card:*
```
SD Card Module -> Pico W
VCC -> 3.3V
GND -> GND
MISO -> GP16
MOSI -> GP19
SCK -> GP18
CS -> GP17
```

*Client Pico W + Display Pack:*
- Connect Display Pack directly to Pico W (designed to fit)
- No additional wiring required

## Usage

### 1. Start Server
1. Power up server Pico W
2. It will connect to WiFi and display its IP address
3. Server loads and compresses images automatically
4. Waits for client connections on port 8080

### 2. Start Client  
1. Power up client Pico W with Display Pack
2. It connects to WiFi and the server
3. Automatically loads first image from playlist

### 3. Client Controls
- *Button A*: Next image
- *Button B*: Previous image  
- *Button X*: Toggle auto-advance mode
- *Button Y*: Refresh current image

## Creating PPM3 Images

### Using the provided utilities:
```python
from ppm_utils import PPM3Image

# Create test patterns
img = PPM3Image()
img.create_test_pattern(240, 135)  # Color blocks
img.save_to_file("test.ppm")

img.create_gradient(240, 135)     # Color gradient  
img.save_to_file("gradient.ppm")

# Create solid colors
img = PPM3Image(240, 135)
img.pixels = [(255, 0, 0)] * (240 * 135)  # Solid red
img.save_to_file("red.ppm")
```

### Converting from other formats:
Use ImageMagick or similar tools:
```bash
convert image.jpg -resize 240x135 image.ppm
```

## Protocol Details

### Message Format:
```
[Message Type: 3 bytes][Length: 2 bytes][Data: variable]
```

### Message Types:
- `REQ`: Request image by ID
- `HDR`: Header with image info  
- `DAT`: Image data chunk
- `END`: Transfer complete
- `ACK`: Acknowledge
- `ERR`: Error message

### Transfer Flow:
1. Client sends `REQ` with image ID
2. Server responds with `HDR` containing size info
3. Client sends `ACK`
4. Server sends image in `DAT` chunks
5. Client `ACK`s each chunk
6. Server sends `END` when complete

## Compression Analysis

The system includes tools to analyze how well images compress:

```python
from rle_compression import RLEAnalyzer

# Analyze an image
img = PPM3Image()
img.load_from_file("test.ppm")
RLEAnalyzer.print_analysis(img.pixels)
```

### Compression Performance:
- *Solid colors*: 99%+ compression ratio
- *Simple patterns*: 70-90% compression  
- *Gradients*: 30-60% compression
- *Complex photos*: May expand (not suitable for RLE)

## Troubleshooting

### WiFi Connection Issues:
- Check SSID and password spelling
- Ensure 2.4GHz network (Pico W doesn't support 5GHz)
- Check WiFi signal strength

### Display Issues:
- Verify Display Pack connections
- Check SPI wiring if using separate display
- Test with `test_display_only()` function

### Transfer Issues:
- Verify server IP address
- Check firewall settings
- Test with smaller images first
- Monitor serial output for error messages

### Image Quality:
- PPM3 format may look different due to RGB565 conversion
- Consider dithering for better color representation
- Optimize images for the 240x135 display resolution

## Educational Aspects

This project demonstrates:

1. *Image Formats*: PPM3 as a learning format
2. *Compression*: Run-length encoding principles  
3. *Networking*: Custom protocol design
4. *Hardware*: SPI displays and SD cards
5. *Embedded Programming*: Memory management, real-time constraints
6. *System Design*: Client-server architecture

## Extensions

### Possible Improvements:
- Add more sophisticated compression (JPEG, PNG)
- Implement image caching on client
- Add authentication/security
- Support for animated sequences  
- Web interface for server management
- Multiple client support
- Image metadata and thumbnails

### Advanced Features:
- Progressive image loading
- Image manipulation (rotation, scaling)
- Real-time image streaming
- Power management optimizations
- Error recovery and reconnection

## File Structure

```
server_pico_w/
├── main.py -> server_main.py
├── image_protocol.py
├── ppm_utils.py  
├── rle_compression.py
└── images/
    ├── test_pattern.ppm
    ├── test_gradient.ppm
    └── custom_images...

client_pico_w/
├── main.py -> client_main.py
├── display_pack_driver.py
├── image_protocol.py
├── ppm_utils.py
└── rle_compression.py
```

## Performance Notes

- *Transfer Speed*: ~10-50KB/s depending on WiFi
- *Compression Time*: <1s for 240x135 images
- *Display Refresh*: ~100ms for full screen
- *Memory Usage*: ~100KB RAM for full image
- *Power Consumption*: ~200mW total system

This system provides a working example of embedded image processing and wireless
communication for learning a bit on embedded systems, networking protocols, and image
processing concepts.

