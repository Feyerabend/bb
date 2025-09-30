
- Client sends PKT_CLIENT_CONNECT
- Server responds with PKT_CLIENT_ACK + player ID (1 or 2)
- Client starts sending input packets every 50ms
- Server broadcasts state every 100ms


Delta Updates:
- Server tracks previous positions and shot lists
- Only sends changed data (positions, direction changes, new/removed shots)
- Clients merge deltas into their local state
- Full sync every 3 seconds to prevent drift

Next Steps: When move to C:

- Prediction Enhancement: Clients can predict movement between server updates using the direction vectors
- Interpolation: Smooth out position updates with linear interpolation
- Client-side Shot Rendering: Fire shots immediately, wait for server confirmation
- Bandwidth Optimisation: Pack multiple deltas if direction doesn't change
- Latency Compensation: Timestamp packets and adjust rendering


Testing Tips

- Test server alone first: Check display updates and AP creation
- Connect one client: Verify it gets player ID 1 and renders correctly
- Add second client: Should get player ID 2 automatically
- Monitor server display: Shows connection count and game state
- Check LEDs: Color coding helps debug connection states


If clients don't connect:
- Check SSID/password match
- Verify server AP is active (check LED is green)
- Try power cycling the Picos
- Rewrite connection protocol


If game state is jumpy:
- Reduce network update rate on client (increase sleep time)
- Add interpolation between updates
- Check WiFi signal strength (just for test: close!)

If packets are lost:
- The full sync every 30 frames will resynchronize
- Delta updates are stateless, so losses are recoverable


Variables to Tune
In server.py:
- full_sync_interval = 30 - How often to send complete state
- Frame sleep time 100ms - Server tick rate

In client.py:
- Network thread sleep 50ms - Input send rate
- Main loop sleep 100ms - Render rate

In protocol.py:
- GAME_WIDTH/HEIGHT - Playfield size
- Packet formats - Add compression if needed

---
Debug logging/statistics
Packet loss visualization
Latency measurements
Client-side prediction implementation
Better collision detection using the actual sprite shapes
