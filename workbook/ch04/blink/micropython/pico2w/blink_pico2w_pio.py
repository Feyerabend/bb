# Raspberry Pi Pico 2 W - PIO External LED Blink
# The onboard LED (WL_GPIO0) cannot be controlled by PIO
# This program uses an external LED on a regular GPIO pin

import machine
import rp2
from machine import Pin
import time

# Hardware setup required:
# - Connect LED long leg (anode) to GPIO 2
# - Connect 220-330 ohm resistor from LED short leg (cathode) to GND
# - Alternative: Use any GPIO pin 0-28 (change LED_PIN below)

LED_PIN = 2  # Change this to any regular GPIO pin you prefer

print(f"Pico 2 W PIO External LED Blink - Using GPIO {LED_PIN}")
print("Hardware needed:")
print(f"  GPIO {LED_PIN} -> 330 ohm resistor -> LED -> GND")
print()

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def slow_blink():
    """PIO program for slow, visible LED blink"""
    wrap_target()
    
    # Turn LED ON
    set(pins, 1)
    
    # Long delay for ON state (nested loops)
    set(x, 31)              # Outer loop counter
    label("on_outer")
    set(y, 31)              # Inner loop counter  
    label("on_inner")
    nop()            [31]   # Delay 32 cycles
    jmp(y_dec, "on_inner")  # Inner loop
    jmp(x_dec, "on_outer")  # Outer loop
    
    # Turn LED OFF
    set(pins, 0)
    
    # Long delay for OFF state (nested loops)
    set(x, 31)              # Outer loop counter
    label("off_outer") 
    set(y, 31)              # Inner loop counter
    label("off_inner")
    nop()            [31]   # Delay 32 cycles
    jmp(y_dec, "off_inner") # Inner loop
    jmp(x_dec, "off_outer") # Outer loop
    
    wrap()

def test_external_led():
    """Test external LED with regular GPIO first"""
    print("Testing external LED with regular GPIO...")
    
    try:
        led = Pin(LED_PIN, Pin.OUT)
        
        # Blink 5 times to test
        for i in range(5):
            led.on()
            print(f"LED ON (test {i+1}/5)")
            time.sleep(0.3)
            led.off()
            print(f"LED OFF (test {i+1}/5)")
            time.sleep(0.3)
            
        print("GPIO test complete!")
        return True
        
    except Exception as e:
        print(f"GPIO test failed: {e}")
        return False

def pio_external_blink():
    """Run PIO blink on external LED"""
    
    # First test with regular GPIO
    if not test_external_led():
        print("Cannot proceed with PIO - GPIO test failed")
        return
    
    print(f"\nStarting PIO blink on GPIO {LED_PIN}")
    
    try:
        # Create PIO state machine
        sm = rp2.StateMachine(
            0,                      # State machine 0
            slow_blink,             # PIO program
            freq=50000,             # 50kHz PIO frequency
            set_base=Pin(LED_PIN)   # Base pin for 'set' instructions
        )
        
        # Start the state machine
        sm.active(1)
        print("PIO started - LED should be blinking slowly")
        print("Press Ctrl+C to stop...")
        
        # Keep program running
        try:
            while True:
                time.sleep(1)
                print("PIO running...")
                
        except KeyboardInterrupt:
            print("\nStopping PIO...")
            sm.active(0)
            print("PIO stopped")
            
    except Exception as e:
        print(f"PIO failed: {e}")
        print("Make sure you're using a regular GPIO pin (0-28)")

# Alternative: Faster blink pattern
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def fast_blink():
    """PIO program for faster blink"""
    wrap_target()
    set(pins, 1)
    set(x, 15)              # Shorter delay
    label("on_delay")
    nop()            [31]
    jmp(x_dec, "on_delay")
    
    set(pins, 0) 
    set(x, 15)              # Shorter delay
    label("off_delay")
    nop()            [31]
    jmp(x_dec, "off_delay")
    wrap()

def pio_fast_blink():
    """Alternative: Faster PIO blink"""
    print(f"Fast PIO blink on GPIO {LED_PIN}")
    
    try:
        sm = rp2.StateMachine(0, fast_blink, freq=100000, set_base=Pin(LED_PIN))
        sm.active(1)
        
        print("Fast blink started - Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            sm.active(0)
            print("Fast blink stopped")
            
    except Exception as e:
        print(f"Fast blink failed: {e}")

# Main program
if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run slow PIO blink")
    print("2. Run fast PIO blink") 
    print("3. Just test GPIO")
    print()
    
    # For automatic testing, run slow blink
    # Change this to test different modes:
    
    # Uncomment ONE of these lines:
    pio_external_blink()     # Slow PIO blink
    # pio_fast_blink()       # Fast PIO blink  
    # test_external_led()    # GPIO test only
