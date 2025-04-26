
## AJAX Demo

This implementation consists of an HTML/JavaScript client and a Python server that
communicate through AJAX to create an interactive collection game.


### Python Server

This Python server uses `http.server.SimpleHTTPRequestHandler` with a custom handler
class `AjaxHandler`, processing HTTP requests for both static files and API endpoints.
The server maintains a *game state* that tracks player position, collectible items,
and score.

The server defines several API endpoints:
- `/api/game-state` - Responds with the current game state
- `/api/move-player` - Updates player position and checks for item collection
- `/api/reset-game` - Resets the game with randomized item positions
- Any other path without `/api/` serves static files

It implements *CORS headers* for all responses, allowing cross-origin requests, which
is essential for local development.


### HTML/JavaScript Client

The HTML file (`index.html`) provides an interactive game interface with:
- A game area where players move using arrow keys or clicks
- Visual representation of the player (red circle) and collectible items (green circles)
- Score display that updates when items are collected
- Reset button to restart the game
- AJAX status indicator showing current connection state

The JavaScript handles:
- *Throttled AJAX calls* to prevent overwhelming the server
- Real-time position updates and collision detection
- DOM manipulation to render game elements
- Event listeners for keyboard and mouse input

| Feature | Python Server | HTML/JavaScript Client |
|----|----|----| 
| Language | Python | HTML, CSS, JavaScript |
| Purpose | Maintain game state and handle API requests | Provide interactive game interface |
| Key Components | Game state management, Item collection logic | Player movement, UI rendering, AJAX communication |
| API Endpoints | `/api/game-state`, `/api/move-player`, `/api/reset-game` | N/A (consumes these endpoints) |
| Use Case | Backend for simple collection game | Frontend game interface |

This implementation demonstrates a complete client-server architecture using
AJAX for real-time communication between browser and server, suitable for
simple web-based games.
