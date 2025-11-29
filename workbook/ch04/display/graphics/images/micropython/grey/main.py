import time
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB565
from pimoroni import Button, RGBLED
import image_data  # converted image file, living at the same level


def main():
    print("Init Pimoroni Display Pack 2.0...")
    
    # Init display with PicoGraphics
    # DISPLAY_PICO_DISPLAY_2 is for both 2.0" and 2.8" displays
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB565, rotate=0)
    
    # Set backlight to full brightness
    display.set_backlight(1.0)
    
    # Get display dimensions
    WIDTH, HEIGHT = display.get_bounds()
    print(f"Display initialized: {WIDTH}x{HEIGHT} pixels")
    
    # Init buttons (GPIO 12, 13, 14, 15)
    button_a = Button(12)
    button_b = Button(13)
    button_x = Button(14)
    button_y = Button(15)
    
    # Init RGB LED (GPIO 6=R, 7=G, 8=B)
    led = RGBLED(6, 7, 8)
    led.set_rgb(0, 255, 0)  # Green = ready
    
    # Display converted image
    print("Loading image ..")
    print(f"Image size: {image_data.WIDTH}x{image_data.HEIGHT}")
    print(f"Data size: {len(image_data.IMAGE_DATA)} bytes")
    
    print("Displaying image ..")
    
    # Copy image data directly to display buffer
    # The image_data is already in RGB565 format, matching PEN_RGB565
    display_buffer = display.get_buffer()
    
    # Ensure the image matches display size
    if image_data.WIDTH == WIDTH and image_data.HEIGHT == HEIGHT:
        # Direct copy for matching sizes
        for i in range(len(image_data.IMAGE_DATA)):
            display_buffer[i] = image_data.IMAGE_DATA[i]
    else:
        print(f"Warning: Image size mismatch! Converting ..") # or die?
        # Convert pixel by pixel if sizes don't match
        for y in range(min(HEIGHT, image_data.HEIGHT)):
            for x in range(min(WIDTH, image_data.WIDTH)):
                rgb565 = image_data.get_pixel(x, y)
                # Convert RGB565 to RGB888 for PicoGraphics
                r = ((rgb565 >> 11) & 0x1F) << 3
                g = ((rgb565 >> 5) & 0x3F) << 2
                b = (rgb565 & 0x1F) << 3
                pen = display.create_pen(r, g, b)
                display.set_pen(pen)
                display.pixel(x, y)
    
    # Update display to show the image
    display.update()
    
    led.set_rgb(0, 0, 255)  # Blue = done
    print("Image displayed!")
    
    # Simple button interaction loop
    print("\nButtons:")
    print("  A - Increase brightness")
    print("  B - Decrease brightness") 
    print("  X - Show image info")
    print("  Y - Clear screen")
    
    brightness = 1.0
    
    while True:
        if button_a.read():
            brightness = min(1.0, brightness + 0.1)
            display.set_backlight(brightness)
            led.set_rgb(255, 255, 255)
            print(f"Brightness: {brightness:.1f}")
            time.sleep(0.2)
            
        elif button_b.read():
            brightness = max(0.1, brightness - 0.1)
            display.set_backlight(brightness)
            led.set_rgb(128, 128, 128)
            print(f"Brightness: {brightness:.1f}")
            time.sleep(0.2)
            
        elif button_x.read():
            led.set_rgb(255, 255, 0)
            # Show info overlay
            BLACK = display.create_pen(0, 0, 0)
            WHITE = display.create_pen(255, 255, 255)
            display.set_pen(BLACK)
            display.rectangle(10, 10, 200, 60)
            display.set_pen(WHITE)
            display.set_font("bitmap8")
            display.text(f"{WIDTH}x{HEIGHT}", 15, 15, scale=2)
            display.text(f"{len(image_data.IMAGE_DATA)}B", 15, 35, scale=2)
            display.update()
            time.sleep(2)
            # Redisplay image
            for i in range(len(image_data.IMAGE_DATA)):
                display_buffer[i] = image_data.IMAGE_DATA[i]
            display.update()
            
        elif button_y.read():
            led.set_rgb(255, 0, 0)
            BLACK = display.create_pen(0, 0, 0)
            display.set_pen(BLACK)
            display.clear()
            display.update()
            print("Screen cleared - press A to restore")
            time.sleep(0.5)
        
        # Small delay to prevent button bounce
        time.sleep(0.01)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.print_exception(e)
