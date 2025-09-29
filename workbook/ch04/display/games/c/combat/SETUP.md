

## Dogfight


#### Server
- *1× Raspberry Pi Pico W* (WiFi version required)
- USB cable for power and debugging

#### Clients (2 required for gameplay)
- *2× Raspberry Pi Pico W* (WiFi version required)
- *2× Pimoroni Display Pack 2.0* (320×240 ST7789 display)
- 2× USB cables


### Software Requirements

- Pico SDK (latest version)
- CMake (3.13+)
- ARM GCC compiler
- Git


### Directory Structure

```
dogfight/
├── server/
│   ├── CMakeLists.txt
│   ├── main.c
│   └── pico_sdk_import.cmake
├── client/
│   ├── CMakeLists.txt
│   ├── main.c
│   ├── display.c
│   └── display.h
└── docs/
    └── protocol.md
```


### Building the Server

#### 1. Create server directory

```bash
mkdir -p dogfight/server
cd dogfight/server
```


#### 2. Copy files

- Copy `server.c` to this directory
- Copy `CMakeLists.txt` for server
- Copy `pico_sdk_import.cmake` from Pico SDK examples


#### 3. Build

```bash
mkdir build
cd build
cmake ..
make -j4
```

This generates `dogfight_server.uf2`


#### 4. Flash to Pico W

1. Hold BOOTSEL button on Pico W

2. Connect USB cable

3. Pico appears as USB drive

4. Copy `dogfight_server.uf2` to the drive

5. Pico automatically reboots


#### 5. Verify server is running

Connect to serial console (115200 baud):
```bash
# Linux/Mac
screen /dev/ttyACM0 115200

# Windows
# Use PuTTY or similar
```

You should see:
```
Dogfight Server Starting..
Access Point 'DOGFIGHT_SERVER' started
Server IP: 192.168.4.1
UDP server listening on port 4242
```


### Building the Clients

#### 1. Create client directory

```bash
mkdir -p dogfight/client
cd dogfight/client
```


#### 2. Copy files

- Copy `client.c`

- Copy `display.c` and `display.h`

- Copy `CMakeLists.txt` for client

- Copy `pico_sdk_import.cmake`


#### 3. Build

```bash
mkdir build
cd build
cmake ..
make -j4
```

This generates `dogfight_client.uf2`


#### 4. Flash to both Pico W units

Repeat for each client:

1. Connect Display Pack to Pico W

2. Hold BOOTSEL button

3. Connect USB

4. Copy `dogfight_client.uf2` to USB drive

5. Pico reboots and starts client


### Running the Game

#### 1. Power up server
- Connect server Pico W to power
- Wait for WiFi AP to start (~5 seconds)


#### 2. Power up clients
- Connect both client Pico W units
- They automatically connect to server
- Display shows "Connecting..." then "Waiting for opponent..."

#### 3. Start playing
- When 2 clients connect, game starts automatically
- *Player 1 controls:* A=turn left, B=turn right, X=fire
- *Player 2 controls:* A=turn left, B=turn right, X=fire

#### 4. Reset game
- Hold A+Y on any client to restart


### Troubleshooting

#### Server won't start AP
- Check you're using Pico *W* (with WiFi)
- Verify `pico_cyw43_arch` library is linked
- Check serial output for error messages

#### Client can't connect
- Verify server AP is visible on other devices
- Check WiFi credentials match (`DOGFIGHT_SERVER` / `picopico`)
- Ensure server is fully booted before starting clients
- Check server serial output shows "Player X joined"

#### Display not working
- Verify Display Pack is properly seated
- Check SPI pins are correct (CLK=18, MOSI=19, CS=17, DC=16)
- Test with `display_clear(COLOR_RED)` to verify display works

#### Game is laggy
- Ensure good WiFi signal (keep devices close)
- Check server serial output for timeouts
- Reduce `sleep_ms()` in client main loop if needed
- Check network packet rate with serial debug

#### No opponent found
- Ensure both clients successfully connected
- Check server serial: should show "Player 0 joined" and "Player 1 joined"
- Only 2 clients can connect (server full protection)


### Network Configuration

#### Changing WiFi credentials
Edit in server.c:
```c
#define WIFI_SSID "DOGFIGHT_SERVER"
#define WIFI_PASSWORD "picopico"
```

Edit in client.c:
```c
#define SERVER_SSID "DOGFIGHT_SERVER"
#define SERVER_PASSWORD "picopico"
```

#### Changing server IP
Edit DHCP configuration in server.c:
```c
IP4_ADDR(&gw, 192, 168, 4, 1);
```

Edit client.c:
```c
#define SERVER_IP "192.168.4.1"
```

#### Changing game port
Edit both files:
```c
#define UDP_PORT 4242  // or SERVER_PORT in client
```


### Performance Tuning

#### Client frame rate
In `client.c`, adjust:
```c
sleep_ms(50);  // Lower = faster updates (min ~16ms for 60fps)
```

#### Server update rate
In `server.c`, adjust:
```c
if (now - last_update >= 100) {  // Game logic update (10Hz)
if (now - last_broadcast >= 50) {  // Network broadcast (20Hz)
```

#### Shot speed/range
In `server.c`:
```c
player->shots[i].range = 15;  // Frames before shot expires
```

In update_shot():
```c
shot->x += dir_dx[shot->dir] * 3;  // Shot speed multiplier
```


### Tips

#### Enable debug output
Add to both client and server:
```c
printf("Debug: player x=%d y=%d\n", player->x, player->y);
```

#### Monitor network packets
In `udp_recv_callback()`:
```c
printf("RX: type=0x%02x len=%d\n", packet_type, p->len);
```

#### Test single player
Modify server to start with 1 player:
```c
if (server.num_players >= 1) {  // Changed from == 2
    server.game_active = true;
}
```


### Known Limitations

- Maximum 2 players (can be extended with more complex player management)
- No game lobby/matchmaking
- No reconnection after disconnect (must restart)
- UDP = no guaranteed delivery (acceptable for real-time game)
- No client-side prediction (uses server authority)


### Next Steps

- Add client-side prediction for smoother movement
- Implement lobby system for player matchmaking
- Add power-ups and different weapons
- Create tournament mode with multiple rounds
- Add sound effects using PWM
