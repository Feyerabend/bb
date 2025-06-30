
## Worker

__1. Creating the worker__

```javascript
const worker = new Worker('worker.js')
```

This creates a new worker that runs the script in 'worker.js'.
This file contains the logic for the game's engine (like physics,
raycasting, player movement, etc.).


__2. Sending data to the worker__

```javascript
worker.postMessage({ type: 'keys', keys })
worker.postMessage({ type: 'mouse', dx: e.movementX })
worker.postMessage({ type: 'resize', w: canvas.width, h: canvas.height })
```

Messages are sent to the worker whenever:
- a key is pressed/released (keydown, keyup)
- the mouse moves (mousemove)
- the window is resized (resize)

Each message has a type so the worker knows how to handle it.


__3. Receiving data from the worker__

```javascript
worker.onmessage = e => {
  currentState = e.data
  drawFrame(currentState)
}
```

The worker responds by sending updated game state (like rays, map,
player position). This is drawn on the canvas by calling `drawFrame(..)`.


### Summary

Thus, the main page:
- Listens for input (keyboard, mouse)
- Sends those inputs to a background thread (the worker)
- The worker calculates what the game should look like
- It sends back the new frame
- The main page then draws that frame on the canvas

And the 'noworker.html' have no workers, but works without workers. Go figure.

| Feature               | `worker` version 'client.html'             | 'noworker.html' version         |
|----|----|----|
| Game logic location   | `worker.js` (background)     | In main script                  |
| Threading             | Multi-threaded (Web Worker)  | Single-threaded                 |
| Performance impact    | Better under load            | Can lag with heavy logic        |
| Complexity            | Higher (needs message passing) | Lower (easier to trace)        |
