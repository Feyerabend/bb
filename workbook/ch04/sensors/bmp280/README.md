
## BME280

SPI
- CS (CSB): Physical pin 30 (GPIO 22). Use any free GPIO if 22 is unavailable (e.g., GPIO 17, physical pin 22).
- SCK: Physical pin 14 (GPIO 10).
- SDI (MOSI): Physical pin 15 (GPIO 11).
- SDO (MISO): Physical pin 16 (GPIO 12).
- VIN: Physical pin 36 (3.3V, confirm your BMP280 module supports 3.3V; most do).
- GND: Physical pin 3.
- SDO Address: Connect the BMP280’s SDO pin to GND (for address 0x76)
  or 3.3V (for 0x77, update BMP280_ADDR to 0x77 in the code).


