import machine
import time

# Set up the onboard LED - Pico 2 specific approaches
try:
    # Method 1: Use "LED" identifier (preferred for Pico 2)
    led = machine.Pin("LED", machine.Pin.OUT)
    print("Using LED identifier - this should work for Pico 2")
except ValueError as e:
    print(f"LED identifier failed: {e}")
    try:
        # Method 2: For Pico 2 W, try WL_GPIO0
        import network
        led = machine.Pin("WL_GPIO0", machine.Pin.OUT)
        print("Using WL_GPIO0 for Pico 2 W")
    except:
        try:
            # Method 3: Try GPIO 25 (original Pico)  
            led = machine.Pin(25, machine.Pin.OUT)
            print("Using GPIO 25 (fallback)")
        except:
            print("Could not initialize LED - check your board type")
            led = None

if led:
    print("Starting GPIO blink...")
    for i in range(10):  # Blink 10 times for testing
        led.on()
        print("LED ON")
        time.sleep(0.5)
        led.off()
        print("LED OFF")
        time.sleep(0.5)
else:
    print("LED init failed - cannot blink")