
## Raspberry Pi Pico UART Communication in C

This project provides C implementations of the Python UART communication
programs for Raspberry Pi Pico, with both standard UART and WiFi-enabled versions.


### Hardware
- 2x Raspberry Pi Pico (or 1x Pico + 1x Pico W for WiFi version)
- Jumper wires for UART connection
- USB cables for programming

### Software
- Raspberry Pi Pico SDK
- CMake (3.13 or later)
- GCC ARM toolchain
- Git



### 1. Install Pico SDK

```bash
# Clone the SDK
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init

# Set environment variable (add to ~/.bashrc)
export PICO_SDK_PATH=/path/to/pico-sdk
```


### 2. Install Dependencies

*Ubuntu/Debian:*
```bash
sudo apt update
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
```


*macOS:*
```bash
brew install cmake
brew tap ArmMbed/homebrew-formulae
brew install arm-none-eabi-gcc
```

*Windows:*
- Install CMAKE from cmake.org
- Install ARM GCC toolchain from ARM website
- Use Git Bash or WSL for building


### 3. Get Required Files

You need these files in your project directory:
- `full_duplex.c` - Main device program
- `controller.c` - Controller program  
- `wifi_controller.c` - WiFi-enabled controller (for Pico W)
- `CMakeLists.txt` - Build configuration
- `pico_sdk_import.cmake` - SDK import script

Get the SDK import script:
```bash
cp $PICO_SDK_PATH/external/pico_sdk_import.cmake .
```



### 1. Create Build Directory
```bash
mkdir build
cd build
```

### 2. Configure CMake
```bash
cmake ..
```

### 3. Build Programs
```bash
# Build all programs
make -j4

# Or build specific programs
make full_duplex
make controller
make wifi_controller  # Only if you have Pico W support
```

This creates `.uf2` files in the build directory:
- `full_duplex.uf2` - Main device program
- `controller.uf2` - Controller program
- `wifi_controller.uf2` - WiFi controller (Pico W only)



### UART Connection Between Two Picos

```
  Pico 1 (full_duplex)    Pico 2 (controller)
  GP4 (TX) ────────────── GP5 (RX)
  GP5 (RX) ────────────── GP4 (TX)
  GND ─────────────────── GND
```

### Pin Assignments
- *UART TX:* GPIO 4
- *UART RX:* GPIO 5  
- *LED:* GPIO 25 (built-in LED)
- *Baud Rate:* 9600



### 1. Flash the Programs

*Method 1: Bootsel Mode*
1. Hold BOOTSEL button while connecting USB
2. Drag `.uf2` file to RPI-RP2 drive
3. Pico reboots automatically

*Method 2: Using picotool*
```bash
# Flash full_duplex to first Pico
picotool load full_duplex.uf2

# Flash controller to second Pico
picotool load controller.uf2
```

### 2. Connect and Monitor

Connect via serial terminal (115200 baud):
```bash
# Linux/macOS
screen /dev/ttyACM0 115200

# Windows
# Use PuTTY or similar terminal program
```



### full_duplex.c (Main Device)
- Dual-core operation (Core 0: main logic, Core 1: UART)
- Thread-safe message queues
- Temperature sensor reading
- LED control
- Command/request processing
- Periodic temperature broadcasts

### controller.c (Controller)
- Interactive command mode
- Monitor-only mode
- Command history (20 entries)
- Message timestamps
- Thread-safe UART handling



### Build Issues

*CMake can't find SDK:*
```bash
export PICO_SDK_PATH=/path/to/pico-sdk
```

*Missing toolchain:*
- Install `gcc-arm-none-eabi`
- Check PATH includes toolchain binaries

*Permission errors on Linux:*
```bash
sudo usermod -a -G dialout $USER
# Logout and login again
```

### Runtime Issues

*No UART communication:*
- Check wiring (TX-RX, RX-TX, GND-GND)
- Verify baud rate (9600)
- Ensure both programs are running

*WiFi not working:*
- Ensure using Pico W (not regular Pico)
- Check WiFi credentials
- Verify web browser can reach 192.168.4.1

*Program crashes:*
- Check serial output for error messages
- Verify sufficient power supply
- Try reflashing with fresh .uf2 files



### Python vs C Performance

The C versions offer several advantages over Python:

*Speed:*
- Much faster execution
- Lower latency UART processing
- More efficient memory usage

*Reliability:*
- More predictable timing
- Better real-time performance
- Fewer garbage collection pauses

*Resources:*
- Uses less RAM
- More flash memory available
- Better power efficiency

*Challenges:*
- More complex to develop/debug
- Manual memory management
- Platform-specific networking code


__Message Protocol__

Both Python and C versions use the same message format:

```
Format: #MESSAGE_CONTENT*
Commands: CMD:STATUS, CMD:PING, CMD:LED_ON, CMD:LED_OFF
Requests: REQ:TEMP
Responses: STATUS:TEMP=21.5C,COUNT=42, PONG, ACK:LED_ON, etc.
```



### Adding New Commands
1. Add command handling in `process_command()`
2. Update web interface (for WiFi version)
3. Add to help text in interactive mode

### Debugging
- Use printf() for debugging output
- Check serial terminal for error messages
- Use LED blink patterns for status indication

### Optimization
- Adjust buffer sizes in header defines
- Modify timing delays for your use case
- Enable/disable features to save memory
