# Troubleshooting Guide

## Problem: "Failed to load resource: Could not connect to the server"

This means the browser can't reach the Python server. Here's how to fix it:

### Solution 1: Make sure the server is running

1. Open a terminal
2. Navigate to the directory containing the files:
   ```bash
   cd /path/to/displaypack-simulator
   ```
3. Start the server:
   ```bash
   python3 basic_server.py
   ```
4. Look for this message:
   ```
   Web display: http://localhost:8080
   ```
5. Open your browser to `http://localhost:8080`

### Solution 2: Run from the correct directory

The server needs to be started from the directory containing both `basic_server.py` AND `client.html`:

```bash
# Check you're in the right place
ls -la
# You should see: basic_server.py, client.html, *.bas files

# Then start the server
python3 basic_server.py bounce.bas --run
```

### Solution 3: Use the test script

```bash
chmod +x test.sh
./test.sh
```

This will verify everything and start the server automatically.

### Solution 4: Check if port 8080 is already in use

If port 8080 is taken, use a different port:

```bash
python3 basic_server.py --port 9000
```

Then open `http://localhost:9000` in your browser.

### Solution 5: Embedded Fallback Client

The latest version includes an embedded fallback client. Even if `client.html` is missing, the server will work! You'll see this message:

```
⚠ client.html not found - will use embedded fallback
```

This is fine - the embedded client has all the same features.

## Problem: Server starts but browser shows blank screen

1. Open browser console (F12 → Console tab)
2. Check for error messages
3. You should see:
   ```
   Fetched data: {graphics: [...], output: []}
   Drawing X commands
   ```

If you see `No graphics to draw`, the BASIC program hasn't generated any graphics yet. Try:

```
> CLS 0
> TEXT 100, 100, "TEST", 65535
> CIRCLE 160, 120, 50, 31
```

## Problem: Animation runs but nothing displays

The animation might be running too fast. Make sure it includes `WAIT` commands:

```basic
110 CLS 0
120 CIRCLEF X, Y, 15, 63488
130 WAIT 50    <-- This is essential!
140 LET X = X + DX
```

## Quick Test

Run this to test everything:

```bash
python3 basic_server.py
```

Then in another terminal or the REPL prompt:
```
> CLS 0
> TEXT 10, 10, "Hello World", 65535
```

Refresh your browser - you should see white text!

## Still having issues?

1. Check Python version: `python3 --version` (needs 3.6+)
2. Check the terminal for error messages
3. Make sure no firewall is blocking localhost:8080
4. Try a different browser (Chrome, Firefox, Safari, Edge all work)
