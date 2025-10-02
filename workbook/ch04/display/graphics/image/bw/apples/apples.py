from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_PACK_2
import uos
import sdcard
import machine

# check first!
# sck = machine.Pin(18)?
# miso = machine.Pin(16)?
# mosi = machine.Pin(19)?
# cd = machine.Pin(17)?

# Init SD card
spi = machine.SPI(0, baudrate=1000000, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
sd = sdcard.SDCard(spi, machine.Pin(17))  # CS pin
uos.mount(sd, "/sd")

# Initialize display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_PACK_2)
display.set_backlight(1.0)  # Full brightness

# List BMP files
bmp_files = [f for f in uos.listdir("/sd/images") if f.endswith(".bmp")]

# Stream and display each BMP
for bmp in bmp_files:
    display.load_sprite(f"/sd/images/{bmp}", format="bitmap")  # 1-bit BMP
    display.update()  # Render to display
    machine.delay(100)  # Adjust for frame rate (e.g., 10 FPS)
