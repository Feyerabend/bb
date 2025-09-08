
## Raspberry Pi Pico W "GPU" Architecture Design

This document outlines the design for a Raspberry Pi Pico W-based graphics processing unit that acts as a dedicated display controller for games and animations. The system uses a dual-core architecture with server-authoritative game logic.


### Hardware Foundation

- *Microcontroller*: Raspberry Pi Pico W (RP2040)
- *CPU*: Dual ARM Cortex-M0+ cores @ 133MHz
- *Memory*: 264KB SRAM
- *Display*: Pimoroni Pico Display (240x135 pixels, 16-bit color)
- *Network*: Built-in WiFi capability



### System Architecture

#### Core Division Strategy

__Core 0: Network Communication & Local Processing__
*Primary Responsibilities:*
- UDP packet reception and transmission
- Command parsing and interpretation
- Simple collision detection (AABB, point-in-rectangle)
- Local game state caching
- Inter-core communication management
- Network error handling and reconnection

__Core 1: Graphics Engine & Rendering__
*Primary Responsibilities:*
- Bytecode virtual machine execution
- Sprite rendering and blitting
- Framebuffer management
- Display driver communication
- Animation frame processing
- Complex collision detection (when needed)


### Communication Protocols

#### Network Communication (Server Authoritative)

__Incoming UDP Packets (Server → Pico W)__
```
MOVE_OBJECT, object_id, x, y, velocity_x, velocity_y
DRAW_SPRITE, sprite_id, x, y, frame
UPDATE_TILEMAP, tile_x, tile_y, tile_id
CLEAR_SCREEN
SET_PALETTE, color_index, rgb_value
```

__Outgoing UDP Packets (Pico W → Server)__
```
COLLISION_DETECTED, object1_id, object2_id, collision_point_x, collision_point_y
OBJECT_OUT_OF_BOUNDS, object_id, last_position_x, last_position_y
RENDER_COMPLETE, frame_number
HEARTBEAT, timestamp
ERROR, error_code, description
```

__Network Configuration__
- *Protocol*: UDP (bidirectional)
- *Incoming Port*: 8080 (commands from server)
- *Outgoing Port*: 8081 (responses to server)
- *Packet Size*: Maximum 512 bytes
- *Error Handling*: Timeout-based reconnection, packet sequence numbers


#### Inter-Core Communication

Hardware FIFO Usage
- *FIFO A*: Core 0 → Core 1 (Graphics Commands)
- *FIFO B*: Core 1 → Core 0 (Collision Results & Status)

__Core 0 -> Core 1 Commands__
```
RENDER_SPRITE, sprite_id, x, y, frame, flags
CHECK_COLLISION, object_id, new_x, new_y, width, height
UPDATE_ANIMATION, object_id, animation_id, frame_rate
CLEAR_BUFFER
SWAP_BUFFERS
```

__Core 1 -> Core 0 Responses__
```
COLLISION_RESULT, object_id, collision_detected, collision_object_id
RENDER_STATUS, frame_ready, objects_rendered, render_time_ms
BUFFER_FULL
ERROR, error_type
```

### Graphics System Design

#### Bytecode Virtual Machine

Instruction Set (Future: optimised for graphics!)
```
LOAD_SPRITE     sprite_id, memory_address
DRAW            sprite_id, x, y
MOVE            sprite_id, delta_x, delta_y
ANIMATE         sprite_id, frame_count, frame_rate
SET_PALETTE     index, color_value
CLEAR_RECT      x, y, width, height
COPY_RECT       src_x, src_y, dst_x, dst_y, width, height
```

Memory Management
- *Framebuffer*: 65KB (240×135×16bit)
- *Sprite Cache*: 100KB
- *VM Stack*: 16KB
- *Command Queue*: 32KB
- *Remaining*: ~50KB for variables and buffers

#### Rendering Pipeline

1. *Command Reception* (Core 0 receives UDP packets)
2. *Command Translation* (Convert network commands to graphics bytecode)
3. *Inter-Core Transfer* (Send bytecode to Core 1 via FIFO)
4. *VM Execution* (Core 1 processes graphics commands)
5. *Collision Detection* (During/after rendering)
6. *Result Reporting* (Core 1 → Core 0 → Network)
7. *Display Update* (Core 1 updates physical display)


### Performance Characteristics

#### Expected Performance Metrics
- *Frame Rate*: 15-30 FPS
- *Sprite Count*: 10-20 concurrent moving objects
- *Network Latency*: <10ms local network response
- *Collision Detection*: Simple AABB at 60Hz, complex at 15Hz

#### Optimisation Strategies
- *Dirty Rectangle Rendering*: Only update changed screen areas
- *Sprite Caching*: Keep frequently used sprites in fast memory
- *Palette-Based Graphics*: Reduce memory bandwidth
- *Command Batching*: Process multiple network commands per frame
- *Double Buffering*: Prevent screen tearing


### Game Types Suited

#### Recommended Game Categories
- *Tile-based puzzle games* (Tetris, match-3)
- *Simple arcade games* (Pong, Snake, basic shooters)
- *Turn-based strategy* (chess, checkers)
- *2D platformers* (simple physics)
- *Real-time data visualization*

#### Graphics Capabilities
- *2D sprites* with basic transformations
- *Tile-based backgrounds* with scrolling
- *Simple particle effects*
- *UI elements and text rendering*
- *Basic animation* (frame-based, not real-time transformation)


### Implementation Phases

#### Phase 1: Core Infrastructure
1. Set up dual-core communication
2. Implement basic UDP networking
3. Create simple bytecode VM
4. Basic sprite rendering

#### Phase 2: Graphics Engine
1. Advanced rendering pipeline
2. Collision detection system
3. Animation system
4. Memory optimization

#### Phase 3: Game Integration
1. Complete network protocol
2. Error handling and recovery
3. Performance profiling and optimization
4. Game-specific features


### Technical Considerations

#### Limitations
- *Processing Power*: M0+ cores limit complex operations
- *Memory Constraints*: Careful resource management required
- *Network Dependency*: Gameplay affected by network issues
- *Single Display*: One Pico W per display

#### Advantages
- *Low Latency*: Hardware-optimized communication paths
- *Dedicated Processing*: No OS overhead
- *Cost Effective*: Inexpensive hardware platform
- *Expandable*: Easy to add multiple display units


### Sample Game Flow

1. Server sends: `MOVE_OBJECT, player_id, 100, 50, 2, 0`
2. Core 0 receives command and forwards: `RENDER_SPRITE, player_sprite, 100, 50, frame_0`
3. Core 1 renders sprite and checks collision at new position
4. If collision detected, Core 1 sends: `COLLISION_RESULT, player_id, true, wall_id`
5. Core 0 transmits to server: `COLLISION_DETECTED, player_id, wall_id, 100, 50`
6. Server responds with corrected position or damage calculation
7. Process repeats for next frame

This architecture provides a foundation for creating responsive, networked games
that leverage the Pico W's dual-core capabilities while maintaining smooth graphics performance.



### T E S T

Setup Instructions:

__Pico W #1 (Access Point + Python Test Server):__

1. Flash MicroPython firmware to the first Pico W
2. Copy the Python script to the Pico W (save as main.py)
3. Power on - it will automatically:
    - Create WiFi access point "PicoGPU_Test"
    - Start UDP server on port 8081
    - Wait for the GPU client to connect


__Pico W #2 (GPU Client):__

1. Set up the Pico SDK environment
2. Compile the C code with the Pico SDK
3. Flash the compiled binary to the second Pico W
4. Power on - it will automatically:
    - Connect to "PicoGPU_Test" access point
    - Start dual-core graphics engine
    - Begin listening for UDP commands on port 8080


What the Test Does:
The Python server runs 4 automated test scenarios:

- Basic Sprite Movement - Creates 3 sprites and moves them in circular patterns
- Collision Testing - Creates 2 sprites that move toward each other to trigger collision detection
- Stress Test - Creates 8 sprites moving randomly to test performance
- Interactive Mode - Demonstrates various commands (clear, draw, move)


Visual Feedback:

- Python Server: LED blinks while waiting, solid when connected, console shows all activity
- C Client: Console output shows frame updates, collision detection, and network status
- Network Traffic: Both devices exchange UDP packets with game commands and collision responses

Expected Behavior:

- Server creates access point and waits
- Client connects and both cores start
- Server sends movement commands
- Client processes graphics and reports collisions
- Console shows real-time communication between devices

This gives an isolated test environment to verify the dual-core GPU architecture is working
correctly before integrating with larger (game) systems.

