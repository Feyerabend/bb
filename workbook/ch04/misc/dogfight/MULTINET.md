
### Multicore Usage

This client code runs on the Raspberry Pi Pico 2 W, which has a dual-core RP2350 microcontroller.
It leverages multicore processing to separate concerns between the two cores, improving performance
by allowing parallel execution of rendering/input handling and network operations. Synchronisation
between cores is managed through a `SharedState` class, which uses a thread lock (`_thread.allocate_lock()`)
to safely read/write shared data like game state, player inputs, and connection status. This prevents
race conditions when one core reads while the other writes.


- *Core 0 (Main Core)*: Handles the primary game loop, including display rendering,
  button input polling, and local state updates.
  - Runs the `main()` function.
  - Initializes the shared state and starts the network thread on Core 1 via
    `_thread.start_new_thread(network_thread, (shared_state,))`.
  - In its loop (running at ~10 FPS with `time.sleep(0.1)`):
    - Polls buttons (A, B, X, Y) using `Button.read()`.
    - Updates shared input state with `shared_state.set_input(...)`.
    - Grabs a snapshot of the game state via `shared_state.get_display_state()`.
    - Renders the game (planes, shots, text) using `render_game()`, which draws
      to a PicoGraphics display.
    - Updates the RGB LED based on connection/game status.
  - This core focuses on real-time user interaction and visuals, which benefit
    from consistent timing without network delays.

- *Core 1 (Secondary Core)*: Dedicated to all networking tasks, keeping it isolated
  from rendering to avoid blocking the UI.
  - Runs the `network_thread(shared_state)` function.
  - Connects to WiFi using `connect_wifi()`, then creates a non-blocking UDP socket.
  - Requests a player ID from the server by sending connect packets and parsing responses.
  - In its main loop (running at 20 Hz with `time.sleep_ms(50)`):
    - Grabs input snapshot from shared state with `shared_state.get_input()`.
    - Sends player input packets to the server.
    - Receives and unpacks full or delta game state packets, updating shared state with
      `shared_state.update_game_state(...)`.
    - Handles connection status updates via `shared_state.set_connected(...)`.
  - If errors occur (e.g., connection failure), it updates the shared state accordingly.

This division ensures that network latency or WiFi operations don't stall the display or
input responsiveness on Core 0. The shared state acts as a bridge, with locks ensuring
thread-safe access (e.g., `with self.lock:` blocks).


### Networking

The networking is implemented using UDP for low-latency communication in a client-server model,
where this device acts as a client connecting to a game server (likely another Pico or similar
acting as an access point). It uses the `network` and `socket` modules from MicroPython.
The protocol details are handled by an imported `protocol.py` module.
Networking runs exclusively on Core 1 to isolate it from rendering.

- *WiFi Connection*:
  - Uses `network.WLAN(network.STA_IF)` in station mode to connect to the server's
    access point (SSID: "DOGFIGHT_SERVER", password: "dogfight123").
  - Retries for up to 10 seconds; raises an error if it fails.
  - Server IP is hardcoded as "192.168.4.1" (typical for an AP's default gateway),
    with UDP port 8888.

- *Socket Setup*:
  - Creates a UDP socket (`socket.AF_INET, socket.SOCK_DGRAM`) and sets it
    non-blocking (`sock.setblocking(False)`).
  - This allows polling for data without halting the loop.

- *Initial Connection*:
  - Sends a connect request packet (via `protocol.ConnectPacket.pack_request()`)
    up to 5 times, waiting 200ms between attempts.
  - Listens for a `PKT_CLIENT_ACK` response to get the assigned `player_id`
    (1 or 2, presumably).
  - Updates shared state if successful; otherwise, marks as disconnected.

- *Main Communication Loop*:
  - *Sending Inputs*: At 20 Hz, packs and sends a `ClientInputPacket` with the
    player's button states and ID to the server.
  - *Receiving Updates*: Tries to receive data (up to 512 bytes). If available:
    - Checks packet type (`PKT_FULL_STATE` or `PKT_DELTA_STATE`).
    - Unpacks using protocol methods and applies to shared state (e.g., player
      positions, directions, shots, game over status).
    - For shots, it handles full lists, additions, or removals (removals use
      approximate position matching with a 3-unit tolerance).
  - If no data, it skips via `except OSError` (non-blocking behavior).
  - Sleeps 50ms to control rate.

- *Error Handling*:
  - Catches general exceptions in the thread, printing them and setting
    disconnected state.
  - No retransmission or reliability beyond UDP's basics—suitable for
    real-time games where dropped packets are tolerable, and local prediction
    (enabled via `self.local_predict = True`, though not actively used in this
    snippet) could smooth inconsistencies.

This setup assumes a local network (via the server's AP) for minimal latency,
for a multiplayer dogfight game with real-time state syncing?

