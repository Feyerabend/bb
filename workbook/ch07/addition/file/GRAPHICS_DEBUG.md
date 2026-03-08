# Graphics Debug Guide

## Testing if Graphics Work

### Step 1: Start the server
```bash
python3 basic_server.py
```

### Step 2: Open browser to http://localhost:8080

### Step 3: In the terminal REPL, type these commands ONE AT A TIME:

```
> CLS 0
```
(Screen should turn black)

```
> TEXT 100, 100, "HELLO", 65535
```
(You should see white "HELLO" text appear)

```
> CIRCLE 160, 120, 50, 63488
```
(You should see a red circle)

### What to check:

1. **Does the console in the browser show commands?**
   - Look at the right side panel in the browser
   - You should see each command listed as you type them

2. **Does the canvas update?**
   - Look at the left side (the black 320x240 display)
   - Graphics should appear there

3. **Check browser console (F12)**
   - Look for error messages
   - Should see "Drawing X commands" messages

## Using SAVE and LOAD

### Save your program:
```
> 10 CLS 0
> 20 TEXT 100, 100, "TEST", 65535
> 30 CIRCLE 160, 120, 50, 31
> SAVE mytest
Program saved to mytest.bas
```

### Load it back:
```
> LOAD mytest
Program loaded from mytest.bas
Loaded 3 lines
> LIST
10 CLS 0
20 TEXT 100, 100, "TEST", 65535
30 CIRCLE 160, 120, 50, 31
> RUN
```

## Quick Graphics Test

Load the test program:
```
> LOAD gfxtest
> RUN
```

You should immediately see:
- White text "GRAPHICS TEST"
- Red circle
- Green rectangle

If you see these, graphics ARE working!

## Common Issues

### Issue: Commands show in console but nothing on canvas
- Check browser console (F12) for JavaScript errors
- Try refreshing the page (F5)
- Make sure canvas is visible (should be on the left)

### Issue: Nothing appears at all
- Wait a moment - browser polls every 500ms
- Try entering another command to force an update
- Check if server is actually running (look at terminal)

### Issue: "Syntax error" messages
- Make sure you're using correct syntax
- Use HELP to see command list
- Remember: colors are 0-65535 (RGB565 format)

## Test Commands to Try

```
> CLS 0
> TEXT 10, 10, "Line 1", 65535
> TEXT 10, 30, "Line 2", 63488
> TEXT 10, 50, "Line 3", 2016
> LINE 0, 100, 320, 100, 31
> RECTF 50, 120, 100, 80, 65504
> CIRCLE 200, 160, 40, 2047
```

Each command should update the display within 500ms.
